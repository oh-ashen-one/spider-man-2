#!/usr/bin/env python3
"""Turn unrigged Tripo citizen GLBs into GPU-skinned crowd variants for src/world/npc/crowd.js.

The city crowd is an 18-bone skeleton whose 27 clips are baked into one animation texture (people.bin, meta.anim).
A crowd mesh is stored in that skeleton's rest pose (arms straight down, 1.70 m, facing +Z) with 4 bone weights per
vertex. For every citizen this tool:

  1. DECIMATE   Blender (headless) cuts the Tripo mesh into 3 LODs (default 5000 / 1500 / 400 triangles).
  2. POSE-FIT   poses an existing crowd variant (a male or a female source body) with world-axis bone rotations and
                uniform bone scales, mirrored L/R, until it overlaps the citizen (two-way nearest-point distance, Powell).
                Tripo citizens stand in an A-pose, so the arm range is wide.
  3. TRANSFER   each citizen vertex takes weights from the nearest normal-compatible posed source vertices, top 4 kept,
                smoothed over the citizen mesh.
  4. UN-POSE    exact inverse of linear blend skinning maps the citizen into the crowd rest pose.
  5. PACK       all citizens go into citizens.bin / citizens.json (same LOD layout idea as people.json) and one texture
                atlas citizens_atlas.webp (1024 px tile per citizen).

usage (on the Studio):
  python3 tools/crowdfit/crowdfit.py manifest.json --out public/assets/city/npc
manifest.json: [{"glb": "~/Downloads/citizen_05.glb", "name": "05_black_tee", "female": false}, ...]
"""
import argparse, io, json, math, os, struct, subprocess, sys, tempfile, time
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'skinfit'))
from skinfit import read_glb, accessor, image_bytes, axis_angle  # noqa: E402

BLENDER = os.environ.get('BLENDER', '/Applications/Blender.app/Contents/MacOS/Blender')
HERE = os.path.dirname(os.path.abspath(__file__))
LOD_TRIS = [5000, 1500, 400]
TILE = 1024


# ------------------------------------------------------------------------------------------------ crowd source body
class Crowd:
    def __init__(self, npc_dir, variant):
        self.meta = json.load(open(os.path.join(npc_dir, 'people.json')))
        self.bin = open(os.path.join(npc_dir, 'people.bin'), 'rb').read()
        bones = self.meta['bones']
        self.names = [b['name'] for b in bones]
        self.parent = [b['parent'] for b in bones]
        self.head = np.array([b['head'] for b in bones], float)
        v = next(v for v in self.meta['variants'] if v['name'] == variant)
        L = v['lods'][0]
        nv = L['nv']; b = self.bin
        P = np.frombuffer(b, np.float32, nv * 3, L['pos']).reshape(-1, 3).astype(float)
        N = np.frombuffer(b, np.float32, nv * 3, L['nrm']).reshape(-1, 3).astype(float)
        J = np.frombuffer(b, np.uint8, nv * 4, L['si']).reshape(-1, 4).astype(np.int64)
        W = np.frombuffer(b, np.uint8, nv * 4, L['sw']).reshape(-1, 4).astype(float) / 255.0
        opt = np.frombuffer(b, np.uint8, nv, L['opt']) if 'opt' in L else np.zeros(nv, np.uint8)
        keep = opt == 0                                   # base body only (no optional hair / hat / bag parts)
        self.P, self.N, self.J = P[keep], N[keep], J[keep]
        W = W[keep]; self.W = W / np.maximum(W.sum(1, keepdims=True), 1e-6)
        self.height = self.P[:, 1].max() - self.P[:, 1].min()

    def skin_mats(self, pose):
        """pose: {bone name: (R 3x3 world rotation about the bone head, s uniform scale)} -> (18, 4, 4) bind->pose."""
        n = len(self.names); M = [None] * n; S = np.zeros((n, 4, 4))
        for j in range(n):                                # bones are listed parent-first in people.json
            p = self.parent[j]
            if p < 0: W = np.eye(4); W[:3, 3] = self.head[j]
            else:
                L = np.eye(4); L[:3, 3] = self.head[j] - self.head[p]
                W = M[p] @ L
            if self.names[j] in pose:
                R, s = pose[self.names[j]]
                W = W.copy(); W[:3, :3] = R @ W[:3, :3] * s
            M[j] = W
            Rinv = np.eye(4); Rinv[:3, 3] = -self.head[j]
            S[j] = W @ Rinv
        return S

    def deform(self, S, P=None, N=None, J=None, W=None):
        P = self.P if P is None else P; J = self.J if J is None else J; W = self.W if W is None else W
        B = np.einsum('vk,vkij->vij', W, S[J])
        Pd = np.einsum('vij,vj->vi', B[:, :3, :3], P) + B[:, :3, 3]
        Nd = None
        if N is not None:
            Nd = np.einsum('vij,vj->vi', B[:, :3, :3], N); Nd /= np.linalg.norm(Nd, axis=1, keepdims=True) + 1e-12
        return Pd, Nd


PARAMS = [  # name, start, half-range. Angles about WORLD axes (+X character's left, +Y up, +Z forward), mirrored L/R
    ('arm_abduct', 0.9, 1.1),   # upperArm about Z: crowd rest has arms down, Tripo citizens are in an A-pose
    ('arm_swing', 0.0, 0.5),
    ('elbow', 0.0, 0.6),
    ('ua_s', 1.0, 0.25), ('fa_s', 1.0, 0.25), ('hand_s', 1.0, 0.3),
    ('thigh_abduct', 0.05, 0.3), ('thigh_s', 1.0, 0.2), ('shin_s', 1.0, 0.2),
    ('spine_s', 1.0, 0.2), ('chest_s', 1.0, 0.25), ('neck_s', 1.0, 0.3), ('head_s', 1.0, 0.3),
]


def pose_from(x):
    v = {k: x[i] for i, (k, _, _) in enumerate(PARAMS)}
    X, Z = np.array([1., 0, 0]), np.array([0, 0, 1.])
    pose = {}
    for side, sg in (('L', 1.0), ('R', -1.0)):
        pose['upperArm' + side] = (axis_angle(Z, sg * v['arm_abduct']) @ axis_angle(X, v['arm_swing']), v['ua_s'])
        pose['forearm' + side] = (axis_angle(X, v['elbow']), v['fa_s'])
        pose['hand' + side] = (np.eye(3), v['hand_s'])
        pose['thigh' + side] = (axis_angle(Z, sg * v['thigh_abduct']), v['thigh_s'])
        pose['shin' + side] = (np.eye(3), v['shin_s'])
    pose['spine'] = (np.eye(3), v['spine_s']); pose['chest'] = (np.eye(3), v['chest_s'])
    pose['neck'] = (np.eye(3), v['neck_s']); pose['head'] = (np.eye(3), v['head_s'])
    return pose


def fit_pose(crowd, T, log):
    rng = np.random.default_rng(0)
    gi = rng.choice(len(crowd.P), min(5000, len(crowd.P)), replace=False)
    ti = rng.choice(len(T), min(8000, len(T)), replace=False)
    Ts = T[ti]; tt = cKDTree(Ts)
    Pg, Jg, Wg = crowd.P[gi], crowd.J[gi], crowd.W[gi]
    x0 = np.array([p[1] for p in PARAMS]); lo = x0 - np.array([p[2] for p in PARAMS]); hi = x0 + np.array([p[2] for p in PARAMS])
    # legs may only open outward (or stay straight): a negative spread crosses the source legs, a false match that
    # un-poses into bowed, gapped legs. Tripo citizens stand with the feet slightly apart.
    ta = [k for k, _, _ in PARAMS].index('thigh_abduct'); lo[ta] = -0.02; hi[ta] = 0.35

    def cost(x):
        x = np.clip(x, lo, hi)
        D, _ = crowd.deform(crowd.skin_mats(pose_from(x)), Pg, None, Jg, Wg)
        return np.mean(tt.query(D)[0] ** 2) + np.mean(cKDTree(D).query(Ts)[0] ** 2)

    c0 = cost(x0); t = time.time()
    # coarse arm search first (the biggest difference), then a full Powell polish
    best = min(((cost(np.r_[a, x0[1:]]), a) for a in np.linspace(0.0, 1.6, 17)))
    x0 = np.r_[best[1], x0[1:]]
    res = minimize(cost, x0, method='Powell', options={'maxiter': 5000, 'xtol': 1e-4, 'ftol': 1e-7})
    x = np.clip(res.x, lo, hi); c1 = cost(x)
    log(f'  pose fit: rms {math.sqrt(c0) * 100:.1f} cm -> {math.sqrt(c1) * 100:.1f} cm in {time.time() - t:.0f}s; '
        + ', '.join(f'{k}={x[i]:+.2f}' for i, (k, _, _) in enumerate(PARAMS)))
    return x, math.sqrt(c1)


def transfer(crowd, S, T, TN, F, k=12, smooth=3):
    Pd, Nd = crowd.deform(S, None, crowd.N)
    dist, idx = cKDTree(Pd).query(T, k=k)
    nb = len(crowd.names)
    dense = np.zeros((len(T), nb))
    ok = np.einsum('vkc,vc->vk', Nd[idx], TN) > 0.2; ok[~ok.any(1), 0] = True
    w = np.where(ok, 1.0 / (dist + 1e-4) ** 2, 0.0)
    for kk in range(k):
        np.add.at(dense, (np.arange(len(T))[:, None], crowd.J[idx[:, kk]]), w[:, kk:kk + 1] * crowd.W[idx[:, kk]])
    dense /= np.maximum(dense.sum(1, keepdims=True), 1e-9)
    if smooth and len(F):
        e = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]); e = np.concatenate([e, e[:, ::-1]])
        deg = np.bincount(e[:, 0], minlength=len(T)).astype(float)[:, None]
        for _ in range(smooth):
            acc = np.zeros_like(dense); np.add.at(acc, e[:, 0], dense[e[:, 1]])
            dense = 0.5 * dense + 0.5 * acc / np.maximum(deg, 1)
    # limbs never borrow weight from the other side of the body: a Tripo A-pose stance is wider than the crowd body's,
    # so a nearest-vertex search can reach across (inner thigh -> other leg), which crosses the legs once un-posed
    side = np.array([1 if n.endswith('L') else -1 if n.endswith('R') else 0 for n in crowd.names])
    cx = T[:, 0]
    dense[np.ix_(cx > 0.03, side < 0)] = 0.0              # +x is the character's left
    dense[np.ix_(cx < -0.03, side > 0)] = 0.0
    pi = crowd.names.index('prop')                         # the prop bone is for held items only: hand it to its parent
    dense[:, crowd.parent[pi]] += dense[:, pi]; dense[:, pi] = 0.0
    dead = dense.sum(1) < 1e-6; dense[dead, 0] = 1.0           # guard: a vertex never ends up weightless (hips)
    top = np.argsort(-dense, axis=1)[:, :4]
    tw = np.take_along_axis(dense, top, 1); tw /= np.maximum(tw.sum(1, keepdims=True), 1e-9)
    return top, tw


def unpose(S, T, TN, J, W):
    B = np.einsum('vk,vkij->vij', W, S[J]); Bi = np.linalg.inv(B)
    R = np.einsum('vij,vj->vi', Bi[:, :3, :3], T) + Bi[:, :3, 3]
    N = np.einsum('vji,vj->vi', B[:, :3, :3], TN); N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    return R, N


# ------------------------------------------------------------------------------------------------------ decimation
def decimate(glb, workdir, targets=None, orient='auto'):
    """Blender headless: 3 LODs as GLB (glTF axes: +Y up, facing +Z; UV origin top-left) + the base colour texture."""
    targets = targets or LOD_TRIS
    out = os.path.join(workdir, 'lod')
    for f in os.listdir(workdir):
        if f.startswith('lod'): os.remove(os.path.join(workdir, f))
    r = subprocess.run([BLENDER, '-b', '--factory-startup', '--python', os.path.join(HERE, 'decimate_lods.py'), '--',
                        glb, out, ','.join(map(str, targets)), str(orient)], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(f'{out}0.glb'):
        raise RuntimeError('blender decimation failed: ' + (r.stderr or r.stdout)[-800:])
    lods = [read_lod(f'{out}{i}.glb') for i in range(len(targets))]
    j, b = read_glb(glb)
    mat = j['materials'][0]; ti = mat['pbrMetallicRoughness']['baseColorTexture']['index']
    tex = image_bytes(j, b, j['images'][j['textures'][ti]['source']])
    return lods, tex


def read_lod(path):
    j, b = read_glb(path)
    P, N, UV, F = [], [], [], []; base = 0
    for node in j['nodes']:
        if 'mesh' not in node: continue
        for p in j['meshes'][node['mesh']]['primitives']:
            A = p['attributes']
            P.append(accessor(j, b, A['POSITION'])); N.append(accessor(j, b, A['NORMAL']))
            UV.append(accessor(j, b, A['TEXCOORD_0']) if 'TEXCOORD_0' in A else np.zeros((len(P[-1]), 2)))
            F.append(accessor(j, b, p['indices']).reshape(-1, 3).astype(np.int64) + base); base += len(P[-1])
    return np.concatenate(P), np.concatenate(N), np.concatenate(UV), np.concatenate(F)



# ------------------------------------------------------------------------------------------------------ accessories
# Accessories are rigid meshes skinned 100% to one crowd bone, placed on the crowd REST body (citizens are un-posed into
# that same rest body, so one placement fits everyone). Each rule: slot (for per-citizen exclusions), bone, how the
# accessory is scaled (to a fraction of head width or to a height in metres) and where its box goes.
ACC_TRIS = [900, 300]
ACC_RULES = {
    'cap':        dict(slot='hat', bone='head', w=1.18, top=0.035, dz=0.035),
    'bucket':     dict(slot='hat', bone='head', w=1.55, top=0.05, dz=0.0),
    'fedora':     dict(slot='hat', bone='head', w=1.95, top=0.075, dz=0.0),
    'beanie':     dict(slot='hat', bone='head', w=1.12, top=0.07, dz=0.0),
    'headphones': dict(slot='headphones', bone='head', w=1.32, top=0.015, dz=0.0),
    'sunglasses': dict(slot='glasses', bone='head', w=1.05, eye=True),
    'backpack':   dict(slot='back', bone='chest', h=0.46, back=True),
    'bag':        dict(slot='bag', bone='hips', h=0.34, hip=True),
}


def body_metrics(crowd):
    dom = crowd.J[np.arange(len(crowd.J)), crowd.W.argmax(1)]
    head = crowd.P[dom == crowd.names.index('head')]
    chest = crowd.P[dom == crowd.names.index('chest')]
    hipband = crowd.P[np.abs(crowd.P[:, 1] - 0.95) < 0.06]
    return dict(headTop=head[:, 1].max(), headW=head[:, 0].max() - head[:, 0].min(),
                headCz=(head[:, 2].max() + head[:, 2].min()) / 2, headFront=head[:, 2].max(),
                eyeY=head[:, 1].max() - 0.085, back=chest[:, 2].min(), hipX=hipband[:, 0].max())


def place_accessory(P, kind, M):
    R = ACC_RULES[kind]; lo, hi = P.min(0), P.max(0); size = hi - lo
    s = (R['w'] * M['headW'] / size[0]) if 'w' in R else (R['h'] / size[1])
    Q = (P - (lo + hi) / 2) * s; lo, hi = Q.min(0), Q.max(0)
    if R.get('eye'):  off = np.array([0, M['eyeY'], M['headFront'] + 0.012 - hi[2]])
    elif R.get('back'): off = np.array([0, 1.20, M['back'] - 0.005 - hi[2]])
    elif R.get('hip'):  off = np.array([M['hipX'] + 0.005 - lo[0], 0.93, 0.02])
    else:               off = np.array([0, M['headTop'] + R['top'] - hi[1], M['headCz'] + R['dz']])
    return Q + off, s

# ------------------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('manifest'); ap.add_argument('--out', default='public/assets/city/npc')
    ap.add_argument('--npc', default='public/assets/city/npc')
    ap.add_argument('--male-src', default='m_tee'); ap.add_argument('--female-src', default='f_casual')
    a = ap.parse_args()
    man = json.load(open(a.manifest))
    items = man if isinstance(man, list) else man.get('citizens', [])
    accs = [] if isinstance(man, list) else man.get('accessories', [])
    src = {False: Crowd(a.npc, a.male_src), True: Crowd(a.npc, a.female_src)}
    log = print
    buf = bytearray(); variants = []; accessories = []; tiles = []
    cols = 6 if len(items) + len(accs) > 25 else 5; rows = math.ceil((len(items) + len(accs)) / cols)
    def put(arr):
        nonlocal buf
        while len(buf) % 4: buf += b'\0'
        off = len(buf); buf += np.ascontiguousarray(arr).tobytes(); return off
    with tempfile.TemporaryDirectory() as wd:
        for n, it in enumerate(items):
            glb = os.path.expanduser(it['glb']); female = bool(it.get('female'))
            crowd = src[female]
            log(f"[{n + 1}/{len(items)}] {it['name']} ({'f' if female else 'm'}) <- {glb}")
            lods, tex = decimate(glb, wd, LOD_TRIS, it.get('yaw', -90))   # Tripo multi-view models face +X
            # fit on LOD0 (normalised into the crowd frame), reuse the pose for every LOD
            P0 = normalise_like(lods[0][0], lods[0][0], crowd)
            # front vs back: the orientation step can only be sure of the facing AXIS; fit both ways, keep the better
            flip = np.array([-1.0, 1.0, -1.0])
            cb = np.abs(crowd.P[:, 1] - 0.72 * crowd.height) < 0.05
            zc = (crowd.P[cb, 2].max() + crowd.P[cb, 2].min()) / 2      # torso depth centre the citizen was aligned to
            turn = lambda Q: (Q - [0, 0, zc]) * flip + [0, 0, zc]       # 180 deg about the vertical axis through it
            x, rms = fit_pose(crowd, P0, log); back = False
            if it.get('test_flip'):                          # optional: fit turned around too, keep the better
                xb, rmsb = fit_pose(crowd, turn(P0), log)
                if rmsb < rms: x, rms, back = xb, rmsb, True
                log(f'  facing: {"turned 180" if back else "as oriented"}')
            S = crowd.skin_mats(pose_from(x))
            tile = (n % cols, n // cols)
            L_out = []
            for li, (P, N, UV, F) in enumerate(lods):
                P = normalise_like(P, lods[0][0], crowd)
                if back: P, N = turn(P), N * flip
                J, W = transfer(crowd, S, P, N, F)
                R, RN = unpose(S, P, N, J, W)
                # atlas uv, glTF convention (origin top-left; the runtime loads the atlas with flipY = false)
                uv = np.stack([(tile[0] + np.clip(UV[:, 0], 0, 1)) / cols, (tile[1] + np.clip(UV[:, 1], 0, 1)) / rows], 1)
                L_out.append({'nv': int(len(R)), 'nt': int(len(F)),
                              'pos': put(R.astype(np.float32)), 'nrm': put(RN.astype(np.float32)),
                              'uv': put(uv.astype(np.float32)), 'si': put(J.astype(np.uint8)),
                              'sw': put(np.round(W * 255).astype(np.uint8)),
                              'idx': put(F.astype(np.uint16 if len(R) < 65536 else np.uint32)), 'idx32': bool(len(R) >= 65536)})
                log(f'    LOD{li}: {len(R)} verts, {len(F)} tris')
            variants.append({'name': it['name'], 'female': female, 'textured': True, 'tile': list(tile), 'no': it.get('no', []), 'fit_rms_cm': round(rms * 100, 2), 'lods': L_out})
            im = Image.open(io.BytesIO(tex)).convert('RGB').resize((TILE, TILE), Image.LANCZOS); tiles.append(im)
        M = body_metrics(src[False])
        for k, ac in enumerate(accs):
            n = len(items) + k; glb = os.path.expanduser(ac['glb']); kind = ac['kind']; R = ACC_RULES[kind]
            log(f"[acc {k + 1}/{len(accs)}] {ac['name']} ({kind}) <- {glb}")
            lods, tex = decimate(glb, wd, ACC_TRIS, ac.get('yaw', -90))
            tile = (n % cols, n // cols); bone = src[False].names.index(R['bone'])
            # one transform for every LOD, taken from LOD0's box: R = (P - c0) * s0 + off
            P0 = lods[0][0]; c0 = (P0.min(0) + P0.max(0)) / 2
            Q0, s0 = place_accessory(P0, kind, M); off = Q0[0] - (P0[0] - c0) * s0
            L_out = []
            for li, (P, N, UV, F) in enumerate(lods):
                R_ = (P - c0) * s0 + off
                J = np.zeros((len(P), 4), np.uint8); J[:, 0] = bone
                W = np.zeros((len(P), 4), np.uint8); W[:, 0] = 255
                uv = np.stack([(tile[0] + np.clip(UV[:, 0], 0, 1)) / cols, (tile[1] + np.clip(UV[:, 1], 0, 1)) / rows], 1)
                L_out.append({'nv': int(len(P)), 'nt': int(len(F)), 'pos': put(R_.astype(np.float32)), 'nrm': put(N.astype(np.float32)),
                              'uv': put(uv.astype(np.float32)), 'si': put(J), 'sw': put(W),
                              'idx': put(F.astype(np.uint16 if len(P) < 65536 else np.uint32)), 'idx32': bool(len(P) >= 65536)})
                log(f'    LOD{li}: {len(P)} verts, {len(F)} tris')
            accessories.append({'name': ac['name'], 'kind': kind, 'slot': R['slot'], 'bone': R['bone'], 'tile': list(tile), 'lods': L_out})
            tiles.append(Image.open(io.BytesIO(tex)).convert('RGB').resize((TILE, TILE), Image.LANCZOS))
    atlas = Image.new('RGB', (cols * TILE, rows * TILE), (90, 90, 90))
    for n, im in enumerate(tiles): atlas.paste(im, ((n % cols) * TILE, (n // cols) * TILE))
    os.makedirs(a.out, exist_ok=True)
    atlas.save(os.path.join(a.out, 'citizens_atlas.webp'), 'WEBP', quality=88, method=6)
    open(os.path.join(a.out, 'citizens.bin'), 'wb').write(bytes(buf))
    json.dump({'version': 2, 'atlas': 'citizens_atlas', 'grid': [cols, rows], 'variants': variants, 'accessories': accessories},
              open(os.path.join(a.out, 'citizens.json'), 'w'), indent=1)
    log(f'wrote {len(variants)} citizens + {len(accessories)} accessories -> {a.out}/citizens.json/.bin + citizens_atlas.webp ({len(buf) / 1e6:.1f} MB)')


def normalise_like(P, P0_raw, crowd):
    """Move a citizen LOD into the crowd frame using LOD0's bounds: feet on y=0, crowd height, centred in x, torso depth aligned."""
    T0 = P0_raw.copy(); y0 = T0[:, 1].min(); s = crowd.height / (T0[:, 1].max() - y0)
    T0[:, 1] -= y0; T0 *= s; x0 = (T0[:, 0].max() + T0[:, 0].min()) / 2; T0[:, 0] -= x0
    band = np.abs(T0[:, 1] - 0.72 * crowd.height) < 0.05; cb = np.abs(crowd.P[:, 1] - 0.72 * crowd.height) < 0.05
    dz = (crowd.P[cb, 2].max() + crowd.P[cb, 2].min()) / 2 - (T0[band, 2].max() + T0[band, 2].min()) / 2
    Q = P.copy(); Q[:, 1] -= y0; Q *= s; Q[:, 0] -= x0; Q[:, 2] += dz
    return Q


if __name__ == '__main__':
    main()
