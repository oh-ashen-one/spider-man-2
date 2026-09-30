"""Crowd citizen under-layer (round 05, CH18): a smooth hull that follows every citizen mesh a little inside the cloth, so that a crack
in the garment shells shows cloth instead of the wall behind.  Fan homage project, not official Marvel/Sony/Insomniac; no affiliation.

Why: the shipped citizens (public/assets/city/npc, 5000 triangles each) are shredded garment shells: 3000-4400 open boundary edges
per mesh after welding by position (pockets, lapels, hems are separate overlapping pieces), and the LOD decimation moved the pieces
independently, so thin gaps (1-20 mm) show the background.  Welding cannot close them (a weld tolerance big enough to seal the gaps
collapses the mesh), so the mesh gets a backing hull:

  1. sample every triangle at 3 mm (points + outward face normals; the winding agrees with the vertex normals for 99.5 % of the area)
  2. signed distance to the garment on a 6 mm grid, |d| < RB, sign = (p - nearest sample) . its normal (negative = under the cloth).
     Unlike a filled solid this has no webs between an arm and the torso: a point in that gap is OUTSIDE both surfaces.
  3. iso-surface at d = -INSET (surface nets, numpy only, on a 24 mm subsample) = a smooth hull that follows the garment 5 mm inside it
     and continues across the cracks (measured by crack_probe.py: 60-85 % of the see-through pixels of the walk poses get a hull behind them).
     Hull vertices that mix limb groups (armpit / hip / wrist) or belong to a hand are dropped: they would stretch into webs when the limbs move.
  4. every hull triangle gets ONE uv (all three corners the same) = the atlas texel of the nearest garment vertex, so it renders in the
     local garment colour with the citizen's own material (no palette, no second material slot)
  5. skin weights of a hull vertex come from its 4 nearest garment vertices (citizen_rig.build applies them)

  python3 tools/ue_char/eval/underlayer.py NAME [NAME ...] [--json OUT]      -> <scratch>/eval/hull/NAME.npz
"""
import json, os, sys
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from p2paths import WT, scr  # noqa: E402

NPC = os.path.join(WT, 'public/assets/city/npc')
H = 0.006      # distance-field voxel (m)
SAMPLE = 0.003 # surface sample spacing (m)
RB = 0.06      # band: distances beyond this are not resolved (sign only)
INSET = 0.005  # hull depth under the cloth (m)
STEP = 4       # hull grid = STEP * H (24 mm): ~7-10k hull triangles
PURITY = 0.55  # a hull vertex needs >= 55 % of its skin weight in one limb group (torso+head / arm L / arm R / leg L / leg R)
CULL = 0.05    # a hull triangle with no garment within 5 cm along its outward normal is dropped


def load(name, lod=0):
    m = json.load(open(os.path.join(NPC, 'citizens.json')))
    b = open(os.path.join(NPC, 'citizens.bin'), 'rb').read()
    v = next(x for x in m['variants'] if x['name'] == name)
    L = v['lods'][lod]; nv, nt = L['nv'], L['nt']
    pos = np.frombuffer(b, np.float32, nv * 3, L['pos']).reshape(-1, 3).astype(float)
    uv = np.frombuffer(b, np.float32, nv * 2, L['uv']).reshape(-1, 2).astype(float)
    nrm = np.frombuffer(b, np.float32, nv * 3, L['nrm']).reshape(-1, 3).astype(float)
    idx = np.frombuffer(b, np.uint32 if L.get('idx32') else np.uint16, nt * 3, L['idx']).reshape(-1, 3).astype(int)
    gx, gy = m['grid']; c, r = v['tile']
    tuv = np.c_[uv[:, 0] * gx - c, 1.0 - (uv[:, 1] * gy - r)]   # tile-local, v up (same convention as citizen_rig.build)
    si = np.frombuffer(b, np.uint8, nv * 4, L['si']).reshape(-1, 4).astype(int)
    sw = np.frombuffer(b, np.uint8, nv * 4, L['sw']).reshape(-1, 4).astype(float) / 255.0
    return pos, tuv, idx, nrm, (si, sw)


# bone groups of the 18-bone crowd skeleton (people.json): a hull vertex must belong to ONE group, or it would stretch when limbs move apart
GROUP = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2, 10: 2, 17: 2, 11: 3, 12: 3, 13: 3, 14: 4, 15: 4, 16: 4}
HANDS = (7, 10)


def dense_weights(pos, si, sw, nb=18):
    """(nv, nb) skin weights with the UV-seam duplicates welded by position (identical to citizen_rig.build)."""
    w = sw / sw.sum(1, keepdims=True)
    dense = np.zeros((len(w), nb))
    for k in range(4): np.add.at(dense, (np.arange(len(w)), si[:, k]), w[:, k])
    key = np.round(pos / 1e-5).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.reshape(-1)
    acc = np.zeros((inv.max() + 1, nb)); np.add.at(acc, inv, dense)
    return acc[inv] / np.bincount(inv).astype(float)[inv][:, None]


def surface_samples(pos, idx, nrm, sp=SAMPLE):
    """Points on the triangles (spacing ~sp) with the triangle's outward unit normal (oriented by the vertex normals)."""
    P0, P1, P2 = pos[idx[:, 0]], pos[idx[:, 1]], pos[idx[:, 2]]
    fn = np.cross(P1 - P0, P2 - P0)
    ln = np.linalg.norm(fn, axis=1)
    ok = ln > 1e-12
    fn[ok] /= ln[ok][:, None]
    vn = nrm[idx].mean(1)
    flip = (fn * vn).sum(1) < 0
    fn[flip] *= -1
    ed = np.maximum.reduce([np.linalg.norm(P1 - P0, axis=1), np.linalg.norm(P2 - P1, axis=1), np.linalg.norm(P0 - P2, axis=1)])
    n = np.maximum(2, np.ceil(ed / sp).astype(int) + 1)
    pts, nn = [], []
    for k in np.unique(n):
        sel = np.where(ok & (n == k))[0]
        u, v = np.meshgrid(np.linspace(0, 1, k), np.linspace(0, 1, k))
        m = (u + v) <= 1.0
        u, v = u[m], v[m]
        w = np.c_[1 - u - v, u, v]
        pts.append((w[None, :, 0:1] * P0[sel][:, None] + w[None, :, 1:2] * P1[sel][:, None] + w[None, :, 2:3] * P2[sel][:, None]).reshape(-1, 3))
        nn.append(np.repeat(fn[sel], len(w), axis=0))
    return np.vstack(pts), np.vstack(nn)


def signed_distance(pos, idx, nrm, org, shape):
    """d(p) = signed distance to the nearest garment sample (negative = under the cloth), band |d| < RB; beyond the band the sign comes
    from a flood fill of the un-banded region (components touching the border = outside, enclosed ones = deep inside)."""
    S, N = surface_samples(pos, idx, nrm)
    tree = cKDTree(S)
    gi = np.stack(np.meshgrid(*[np.arange(n) for n in shape], indexing='ij'), -1).reshape(-1, 3)
    G = org + (gi + 0.5) * H
    d, i = tree.query(G, k=1, distance_upper_bound=RB, workers=-1)
    ok = np.isfinite(d)
    sd = np.full(len(G), np.nan)
    q = (G[ok] - S[i[ok]])
    sgn = np.sign((q * N[i[ok]]).sum(1)); sgn[sgn == 0] = 1
    sd[ok] = sgn * d[ok]
    sd = sd.reshape(shape)
    far = np.isnan(sd)
    lab, n = ndimage.label(far)
    border = np.unique(np.concatenate([lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(), lab[:, :, 0].ravel(), lab[:, :, -1].ravel()]))
    outside = np.isin(lab, border[border > 0]) & far
    sd[far & outside] = RB
    sd[far & ~outside] = -RB
    return sd


def surface_nets(f, origin, sp):
    """Naive surface nets on scalar field f (inside > 0); f[i,j,k] sits at origin + (i,j,k)*sp.
    Returns vertices (n,3) and outward-oriented triangles (the vertex of a cell is the mean of its edge crossings)."""
    s = f > 0
    nx, ny, nz = s.shape
    corner = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1)]
    c = np.zeros((nx - 1, ny - 1, nz - 1, 8), bool)
    fv = np.zeros((nx - 1, ny - 1, nz - 1, 8))
    for k, (a, b, d) in enumerate(corner):
        c[..., k] = s[a:nx - 1 + a, b:ny - 1 + b, d:nz - 1 + d]
        fv[..., k] = f[a:nx - 1 + a, b:ny - 1 + b, d:nz - 1 + d]
    mixed = c.any(-1) & ~c.all(-1)
    cid = -np.ones(mixed.shape, np.int64)
    ci = np.argwhere(mixed)
    cid[mixed] = np.arange(len(ci))
    edges = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
    acc = np.zeros((len(ci), 3)); cnt = np.zeros(len(ci))
    cf = fv[mixed]; cc = c[mixed]
    off = np.array(corner, float)
    for a, b in edges:
        cross = cc[:, a] != cc[:, b]
        t = cf[:, a] / (cf[:, a] - cf[:, b] + 1e-12)
        p = off[a][None] + (off[b] - off[a])[None] * t[:, None]
        acc[cross] += p[cross]; cnt[cross] += 1
    verts = origin + (ci + acc / np.maximum(cnt, 1)[:, None]) * sp
    out = []
    for ax in range(3):
        sl0 = [slice(None)] * 3; sl1 = [slice(None)] * 3
        sl0[ax] = slice(0, -1); sl1[ax] = slice(1, None)
        ei = np.argwhere(s[tuple(sl0)] != s[tuple(sl1)])
        a1, a2 = [(1, 2), (0, 2), (0, 1)][ax]
        ok = np.ones(len(ei), bool); cells = []
        for da, db in ((0, 0), (1, 0), (1, 1), (0, 1)):
            q = ei.copy(); q[:, a1] -= da; q[:, a2] -= db
            ok &= np.all((q >= 0) & (q < np.array(cid.shape)), axis=1)
            cells.append(q)
        ei = ei[ok]; cells = [q[ok] for q in cells]
        ids = np.stack([cid[q[:, 0], q[:, 1], q[:, 2]] for q in cells], 1)
        good = np.all(ids >= 0, axis=1)
        ins = s[ei[:, 0], ei[:, 1], ei[:, 2]]
        for i in np.where(good)[0]:
            a, b, c_, d = ids[i]
            n = np.cross(verts[b] - verts[a], verts[c_] - verts[a])
            axis = np.zeros(3); axis[ax] = 1.0 if ins[i] else -1.0   # inside -> outside direction along the edge
            if n @ axis < 0: b, d = d, b
            out.append((a, b, c_)); out.append((a, c_, d))
    return verts, np.array(out, int)


def ray_first_hit(O, D, pos, idx, tmax):
    """Distance of the first triangle hit along each ray (Moller-Trumbore, chunked), inf when none within tmax."""
    P0 = pos[idx[:, 0]]; E1 = pos[idx[:, 1]] - P0; E2 = pos[idx[:, 2]] - P0
    best = np.full(len(O), np.inf)
    for s in range(0, len(O), 256):
        o = O[s:s + 256, None, :]; d = D[s:s + 256, None, :]
        h = np.cross(d, E2[None]); a = (E1[None] * h).sum(-1)
        ok = np.abs(a) > 1e-12
        f = 1.0 / np.where(ok, a, 1); sv = o - P0[None]; u = f * (sv * h).sum(-1)
        q = np.cross(sv, E1[None]); v = f * (d * q).sum(-1); t = f * (E2[None] * q).sum(-1)
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-4) & (t < tmax)
        best[s:s + 256] = np.where(hit, t, np.inf).min(1)
    return best


def build_hull(name, inset=None, step=None, cull=None, min_comp=60):
    inset = INSET if inset is None else inset; step = STEP if step is None else step; cull = CULL if cull is None else cull
    pos, tuv, idx, nrm, (si, sw) = load(name)
    org = pos.min(0) - 0.08
    shape = tuple(np.ceil((pos.max(0) + 0.08 - org) / H).astype(int))
    sd = signed_distance(pos, idx, nrm, org, shape)
    sd = ndimage.gaussian_filter(sd, 0.8)
    f = (-sd - inset)[::step, ::step, ::step]                             # > 0 deeper than `inset` under the cloth
    V, T = surface_nets(f, org + 0.5 * H, H * step)                        # grid point (i,j,k) = centre of voxel (i*step, j*step, k*step)
    n_raw = len(T)
    used = np.unique(T); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used)); V = V[used]; T = remap[T]
    par = np.arange(len(V))
    def fnd(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for a, b, c in T:
        ra, rb, rc = fnd(a), fnd(b), fnd(c); par[rb] = ra; par[rc] = ra
    roots = np.array([fnd(i) for i in range(len(V))])
    cnts = np.bincount(roots)
    kv = np.array([cnts[r] > min_comp for r in roots])
    T = T[kv[T].all(1)]
    used = np.unique(T); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used)); V = V[used]; T = remap[T]
    # cull triangles that lie under no cloth (hull pieces the field produced where the garment has a big hole)
    fn0 = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]); fn0 /= np.linalg.norm(fn0, axis=1, keepdims=True) + 1e-12
    hit = ray_first_hit(V[T].mean(1) + fn0 * 0.001, fn0, pos, idx, cull)
    n_before = len(T)
    T = T[np.isfinite(hit)]
    used = np.unique(T); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used)); V = V[used]; T = remap[T]
    # limb purity: a hull vertex whose nearest garment vertices belong to two limb groups (armpit, hip, wrist) or to a hand would stretch
    # into a web when the limbs move apart; triangles touching such a vertex are dropped (joint bands stay uncovered, hands never get a hull)
    dense = dense_weights(pos, si, sw)
    tr0 = cKDTree(pos)
    d4_, i4_ = tr0.query(V, k=4)
    w4_ = 1.0 / (d4_ + 5e-3); w4_ /= w4_.sum(1, keepdims=True)
    dv = np.einsum('nk,nkb->nb', w4_, dense[i4_])
    gsum = np.zeros((len(V), 5))
    for bi, gi in GROUP.items(): gsum[:, gi] += dv[:, bi]
    purity = gsum.max(1) / gsum.sum(1)
    bad = (purity < PURITY) | (dv[:, list(HANDS)].sum(1) > 0.2)
    n_pure = len(T)
    T = T[~bad[T].any(1)]
    used = np.unique(T); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used)); V = V[used]; T = remap[T]
    # light Taubin smoothing (removes residual stair steps, keeps the volume)
    nb = [set() for _ in range(len(V))]
    for a, b, c in T:
        nb[a].update((b, c)); nb[b].update((a, c)); nb[c].update((a, b))
    nbl = [np.array(sorted(x), int) for x in nb]
    for it in range(4):
        Vn = V.copy(); lam = 0.5 if it % 2 == 0 else -0.53
        for i, l in enumerate(nbl):
            if len(l): Vn[i] = V[i] + lam * (V[l].mean(0) - V[i])
        V = Vn
    fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    N = np.zeros_like(V)
    for k in range(3): np.add.at(N, T[:, k], fn)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    tree = cKDTree(pos)
    d4, i4 = tree.query(V, k=4)
    w4 = 1.0 / (d4 + 5e-3); w4 /= w4.sum(1, keepdims=True)
    cen = V[T].mean(1); cn = N[T].mean(1)
    _, near = tree.query(cen + cn * (inset + 0.004))                        # pushed out to about the garment surface
    tri_uv = tuv[near]                                                       # (nt, 2): the same uv for all three corners
    dd, _ = tree.query(V)
    stats = dict(name=name, garment_verts=len(pos), garment_tris=len(idx), hull_verts=len(V), hull_tris=len(T), hull_tris_raw=n_raw,
                 hull_tris_before_cull=n_before, hull_tris_before_purity=n_pure, hull_to_garment_vertex_mm_median=float(np.median(dd) * 1000),
                 hull_to_garment_vertex_mm_max=float(dd.max() * 1000), hull_height_m=float(V[:, 1].max() - V[:, 1].min()))
    return dict(V=V, T=T, N=N, nn=i4, nw=w4, tri_uv=tri_uv), stats


EXPAND = 0.0025   # metres: every garment triangle grows by this much on each edge (closes hairline gaps up to twice this wide)


def expand_triangles(pos, idx, uv, eps=EXPAND, smax=1.6):
    """Per-triangle expansion about the incentre: every edge moves out by `eps` in the triangle plane (scale s = 1 + eps / inradius, capped);
    uv is scaled identically about the same point, so the texture stays put.  Returns corner positions (nt, 3, 3) and uvs (nt, 3, 2)."""
    A, B, C = pos[idx[:, 0]], pos[idx[:, 1]], pos[idx[:, 2]]
    a = np.linalg.norm(B - C, axis=1); b = np.linalg.norm(C - A, axis=1); c = np.linalg.norm(A - B, axis=1)
    per = a + b + c + 1e-15
    area = np.linalg.norm(np.cross(B - A, C - A), axis=1) / 2
    r_in = 2 * area / per
    s = np.minimum(1 + eps / np.maximum(r_in, 1e-6), smax)
    inc = (a[:, None] * A + b[:, None] * B + c[:, None] * C) / per[:, None]
    corners = np.stack([A, B, C], 1)
    P3 = inc[:, None, :] + (corners - inc[:, None, :]) * s[:, None, None]
    uvc = uv[idx]                                                             # (nt, 3, 2)
    uinc = (a[:, None] * uvc[:, 0] + b[:, None] * uvc[:, 1] + c[:, None] * uvc[:, 2]) / per[:, None]
    UV3 = uinc[:, None, :] + (uvc - uinc[:, None, :]) * s[:, None, None]
    return P3, UV3


def build_layers(name, insets=None):
    """Three hulls (4, 12 and 30 mm under the cloth) merged into one: the deeper ones are smoother (a crack narrower than twice their depth does not
    break them), so they back the places where the shallow one has holes (joint bands, thin double layers).  Measured with crack_render.py + the
    critic's cracks.py on 9 dark walkers: wall-coloured slivers 35 (garment only) -> 13 (2 layers) -> 9 (3 layers)."""
    if insets is None: insets = tuple(float(x) for x in os.environ.get('HULL_LAYERS', '0.004,0.012,0.030').split(','))
    parts, stats = [], []
    for k, ins in enumerate(insets):
        global PURITY
        keep = PURITY
        if k > 0: PURITY = min(PURITY, 0.35)
        try:
            H_, st = build_hull(name, inset=ins)
        finally:
            PURITY = keep
        parts.append(H_); stats.append(st)
    out = {}
    off = 0; Vs, Ts, Ns, NNs, NWs, UVs = [], [], [], [], [], []
    for H_ in parts:
        Vs.append(H_['V']); Ts.append(H_['T'] + off); Ns.append(H_['N']); NNs.append(H_['nn']); NWs.append(H_['nw']); UVs.append(H_['tri_uv']); off += len(H_['V'])
    out = dict(V=np.vstack(Vs), T=np.vstack(Ts), N=np.vstack(Ns), nn=np.vstack(NNs), nw=np.vstack(NWs), tri_uv=np.vstack(UVs))
    st = dict(stats[0]); st['hull_tris'] = int(sum(x['hull_tris'] for x in stats)); st['hull_verts'] = int(sum(x['hull_verts'] for x in stats)); st['layers_mm'] = [round(i * 1000, 1) for i in insets]
    return out, st


if __name__ == '__main__':
    args = sys.argv[1:]
    js = None
    if '--json' in args:
        k = args.index('--json'); js = args[k + 1]; args = args[:k] + args[k + 2:]
    outd = scr('eval', 'hull'); os.makedirs(outd, exist_ok=True)
    allst = {}
    for nme in args:
        H_, st = build_layers(nme)
        np.savez_compressed(os.path.join(outd, nme + '.npz'), **H_)
        allst[nme] = st
        print(json.dumps(st), flush=True)
    if js: json.dump(allst, open(js, 'w'), indent=1)
