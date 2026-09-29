#!/usr/bin/env python3
"""Turn textured Tripo GLBs into game-ready street props and animals (instanced, atlas-textured).

For every manifest entry this tool:
  1. DECIMATE  Blender (headless, tools/crowdfit/decimate_lods.py) turns the model so Tripo's front (+X) faces glTF +Z
               and cuts the LODs (triangle targets per entry).
  2. SCALE     puts it on the ground (y = 0), centres it in x/z and scales it to a real-world size: height `h`, length
               along the facing axis `l`, or width along x `w` (metres).
  3. TAG       animals only: every vertex gets a rigid part id + weight for the vertex-shader animation
               (quadruped: head / tail / 4 legs; bird: head; flight: 2 wings), plus the pivot of each part.
  4. PACK      one .bin/.json per group and one texture atlas (TILE px per entry, glTF uv convention: origin top-left,
               the runtime loads the atlas with flipY = false).

Entries whose GLB has no texture (e.g. Tripo geometry-only exports) get a painted tile from `paint` with planar uvs.

usage (on the Studio):
  python3 tools/critterfit/critterfit.py tools/critterfit/manifest.json
"""
import argparse, io, json, math, os, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'crowdfit'))
sys.path.insert(0, os.path.join(HERE, '..', 'skinfit'))
from crowdfit import decimate  # noqa: E402

TILE = 1024
PART = {'body': 0, 'head': 1, 'tail': 2, 'legFL': 3, 'legFR': 4, 'legBL': 5, 'legBR': 6, 'wingL': 7, 'wingR': 8}


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------------------------------------------------ tagging
def tag_quadruped(P, rig):
    """Rigid parts from normalised coordinates: u = 0 (rear) .. 1 (nose) along z, v = 0 .. 1 of the height.
    rig: leg_v (top of the legs), tail_u (tail is behind this), head_u (head is ahead of this), mid_u (front/back legs)."""
    z0, z1 = P[:, 2].min(), P[:, 2].max(); H = P[:, 1].max(); L = z1 - z0
    u = (P[:, 2] - z0) / L; v = P[:, 1] / H
    leg_v, tail_u, head_u = rig['leg_v'], rig['tail_u'], rig['head_u']
    mid_u = rig.get('mid_u', (tail_u + head_u) / 2); head_v = rig.get('head_v', leg_v)
    part = np.zeros(len(P), np.uint8); w = np.zeros(len(P))
    ramp = rig.get('ramp', 0.06)
    tail = u < tail_u
    part[tail] = PART['tail']; w[tail] = smooth(tail_u, tail_u - ramp, u[tail])
    head = (u > head_u) & (v > head_v)
    part[head] = PART['head']; w[head] = smooth(head_u, head_u + ramp, u[head])
    leg = (v < leg_v) & ~tail & ~head
    front = u > mid_u; left = P[:, 0] > 0          # facing +Z, y up: +x is the animal's left
    for name, m in (('legFL', front & left), ('legFR', front & ~left), ('legBL', ~front & left), ('legBR', ~front & ~left)):
        sel = leg & m
        part[sel] = PART[name]; w[sel] = smooth(leg_v, leg_v - ramp * 1.5, v[sel])
    piv = {}
    for name in ('legFL', 'legFR', 'legBL', 'legBR'):
        sel = part == PART[name]
        c = P[sel].mean(0) if sel.any() else np.zeros(3)
        piv[name] = [round(float(c[0]), 4), round(float(leg_v * H), 4), round(float(c[2]), 4)]
    band = lambda uu: P[np.abs(u - uu) < 0.04]
    tb, hb = band(tail_u), band(head_u)
    piv['tail'] = [0.0, round(float(tb[:, 1].mean() if len(tb) else H * 0.6), 4), round(float(z0 + tail_u * L), 4)]
    hy = hb[hb[:, 1] > head_v * H][:, 1] if len(hb) else np.array([H * 0.7])
    piv['head'] = [0.0, round(float(hy.mean() if len(hy) else H * 0.7), 4), round(float(z0 + head_u * L), 4)]
    return part, w, piv


def tag_bird(P, rig):
    z0, z1 = P[:, 2].min(), P[:, 2].max(); H = P[:, 1].max(); L = z1 - z0
    u = (P[:, 2] - z0) / L; v = P[:, 1] / H
    head = (u > rig['head_u']) & (v > rig['head_v'])
    part = np.where(head, PART['head'], PART['body']).astype(np.uint8)
    w = np.where(head, smooth(rig['head_u'], rig['head_u'] + 0.08, u), 0.0)
    hb = P[(np.abs(u - rig['head_u']) < 0.05) & (v > rig['head_v'])]
    piv = {'head': [0.0, round(float(hb[:, 1].mean() if len(hb) else H * 0.7), 4), round(float(z0 + rig['head_u'] * L), 4)]}
    return part, w, piv


def tag_flight(P, rig):
    span = P[:, 0].max() - P[:, 0].min(); xb = rig.get('root', 0.09) * span
    ax = np.abs(P[:, 0])
    wing = ax > xb * 0.6
    part = np.where(wing, np.where(P[:, 0] > 0, PART['wingL'], PART['wingR']), PART['body']).astype(np.uint8)
    w = np.where(wing, smooth(xb * 0.6, xb * 1.6, ax), 0.0)
    near = P[(ax > xb * 0.8) & (ax < xb * 1.2)]
    y = float(near[:, 1].mean()) if len(near) else float(P[:, 1].mean())
    return part, w, {'wingL': [round(xb, 4), round(y, 4), 0.0], 'wingR': [round(-xb, 4), round(y, 4), 0.0]}


TAGGERS = {'quadruped': tag_quadruped, 'bird': tag_bird, 'flight': tag_flight}


# ---------------------------------------------------------------------------------------------------------- painting
def paint_tile(kind):
    """Planar top-view tile for an untextured flight model: x -> image u (0.5 = spine), nose at the bottom (v = 1)."""
    S = TILE; im = Image.new('RGB', (S, S)); d = ImageDraw.Draw(im)
    if kind == 'pigeon':
        body, wing, dark, head = (112, 116, 128), (134, 139, 150), (38, 40, 46), (82, 88, 104)
    else:                                                               # gull
        body, wing, dark, head = (236, 236, 232), (176, 184, 192), (26, 26, 28), (240, 240, 236)
    d.rectangle([0, 0, S, S], fill=wing)
    d.rectangle([int(S * 0.4), 0, int(S * 0.6), S], fill=body)                         # body strip
    for x0, x1 in ((0, int(S * 0.13)), (int(S * 0.87), S)):
        d.rectangle([x0, 0, x1, S], fill=dark)                                         # primaries / wing tips
    if kind == 'pigeon':
        for b in (0.38, 0.47):                                                         # the two black wing bars
            y0, y1 = int(S * b), int(S * (b + 0.035))
            d.rectangle([int(S * 0.16), y0, int(S * 0.38), y1], fill=dark); d.rectangle([int(S * 0.62), y0, int(S * 0.84), y1], fill=dark)
        d.rectangle([int(S * 0.38), 0, int(S * 0.62), int(S * 0.07)], fill=dark)       # tail band
        d.rectangle([int(S * 0.4), int(S * 0.78), int(S * 0.6), S], fill=head)
        d.ellipse([int(S * 0.43), int(S * 0.76), int(S * 0.57), int(S * 0.86)], fill=(78, 112, 96))  # iridescent neck
    else:
        for k in range(5):                                                             # white mirrors on the black tips
            y = int(S * (0.2 + k * 0.12)); d.ellipse([int(S * 0.03), y, int(S * 0.08), y + 24], fill=(235, 235, 235)); d.ellipse([int(S * 0.92), y, int(S * 0.97), y + 24], fill=(235, 235, 235))
        d.rectangle([int(S * 0.47), int(S * 0.96), int(S * 0.53), S], fill=(222, 178, 48))  # beak
    im = im.filter(ImageFilter.GaussianBlur(6))
    n = (np.random.default_rng(1).normal(0, 7, (S, S, 1))).astype(np.int16)             # feather grain
    return Image.fromarray(np.clip(np.asarray(im).astype(np.int16) + n, 0, 255).astype(np.uint8))


# -------------------------------------------------------------------------------------------------------------- main
def normalise(P0, size):
    lo, hi = P0.min(0), P0.max(0); dim = hi - lo
    if 'h' in size: s = size['h'] / dim[1]
    elif 'l' in size: s = size['l'] / dim[2]
    else: s = size['w'] / dim[0]
    off = np.array([-(lo[0] + hi[0]) / 2, -lo[1], -(lo[2] + hi[2]) / 2])
    return lambda P: (P + off) * s


def build_group(gname, entries, out, wd, log):
    buf = bytearray(); items = []; tiles = []
    cols = math.ceil(math.sqrt(len(entries))); rows = math.ceil(len(entries) / cols)
    def put(arr):
        nonlocal buf
        while len(buf) % 4: buf += b'\0'
        off = len(buf); buf += np.ascontiguousarray(arr).tobytes(); return off
    for n, it in enumerate(entries):
        glb = os.path.expanduser(it['glb'])
        log(f"[{gname} {n + 1}/{len(entries)}] {it['name']} <- {os.path.basename(glb)}")
        try:
            lods, tex = decimate(glb, wd, it['lods'], it.get('yaw', -90))
        except (KeyError, IndexError, TypeError):
            lods, tex = decimate_untextured(glb, wd, it), None
        norm = normalise(lods[0][0], it['size'])
        P0 = norm(lods[0][0]); lo, hi = P0.min(0), P0.max(0)
        tile = (n % cols, n // cols)
        L_out = []; pivots = None
        for li, (P, N, UV, F) in enumerate(lods):
            P = norm(P)
            if tex is None:                                 # painted tile, planar top-view uvs (nose at v = 1)
                UV = np.stack([(P[:, 0] - lo[0]) / (hi[0] - lo[0]), (P[:, 2] - lo[2]) / (hi[2] - lo[2])], 1)
            uv = np.stack([(tile[0] + np.clip(UV[:, 0], 0, 1)) / cols, (tile[1] + np.clip(UV[:, 1], 0, 1)) / rows], 1)
            L = {'nv': int(len(P)), 'nt': int(len(F)), 'pos': put(P.astype(np.float32)), 'nrm': put(N.astype(np.float32)),
                 'uv': put(uv.astype(np.float32)), 'idx': put(F.astype(np.uint16 if len(P) < 65536 else np.uint32)), 'idx32': bool(len(P) >= 65536)}
            if it.get('rig'):
                part, w, piv = TAGGERS[it['rig']['type']](P, it['rig'])
                if li == 0: pivots = piv
                L['part'] = put(part); L['pw'] = put(np.round(w * 255).astype(np.uint8))
                log(f"    LOD{li} parts: " + ', '.join(f'{k}={int((part == v).sum())}' for k, v in PART.items() if (part == v).any()))
            L_out.append(L)
            log(f'    LOD{li}: {len(P)} verts, {len(F)} tris')
        ent = {'name': it['name'], 'tile': list(tile), 'size': [round(float(x), 3) for x in hi - lo], 'lods': L_out}
        for k in ('part', 'kind'):
            if k in it: ent[k] = it[k]
        if pivots: ent['pivots'] = pivots
        items.append(ent)
        im = paint_tile(it.get('paint', 'pigeon')) if tex is None else Image.open(io.BytesIO(tex)).convert('RGB').resize((TILE, TILE), Image.LANCZOS)
        tiles.append(im)
    atlas = Image.new('RGB', (cols * TILE, rows * TILE), (90, 90, 90))
    for n, im in enumerate(tiles): atlas.paste(im, ((n % cols) * TILE, (n // cols) * TILE))
    os.makedirs(out, exist_ok=True)
    atlas.save(os.path.join(out, f'{gname}_atlas.webp'), 'WEBP', quality=88, method=6)
    open(os.path.join(out, f'{gname}.bin'), 'wb').write(bytes(buf))
    json.dump({'version': 1, 'atlas': f'{gname}_atlas', 'grid': [cols, rows], 'items': items}, open(os.path.join(out, f'{gname}.json'), 'w'), indent=1)
    log(f'wrote {len(items)} -> {out}/{gname}.json/.bin + {gname}_atlas.webp ({len(buf) / 1e6:.1f} MB)')


def decimate_untextured(glb, wd, it):
    """crowdfit.decimate reads the base colour texture; geometry-only GLBs just take the LODs."""
    import subprocess
    from crowdfit import BLENDER, read_lod
    out = os.path.join(wd, 'lod')
    subprocess.run([BLENDER, '-b', '--factory-startup', '--python', os.path.join(HERE, '..', 'crowdfit', 'decimate_lods.py'), '--',
                    glb, out, ','.join(map(str, it['lods'])), str(it.get('yaw', -90))], capture_output=True, text=True, check=True)
    return [read_lod(f'{out}{i}.glb') for i in range(len(it['lods']))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('manifest'); ap.add_argument('--only', default='')
    a = ap.parse_args()
    man = json.load(open(a.manifest))
    with tempfile.TemporaryDirectory() as wd:
        for gname, g in man.items():
            if a.only and gname not in a.only.split(','): continue
            build_group(gname, g['items'], g['out'], wd, print)


if __name__ == '__main__':
    main()
