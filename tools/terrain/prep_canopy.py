#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""r06 canopy sky occlusion, baked into the ALPHA channel of <PREP>/pathmask.png (run after prep_terrain.py, idempotent: alpha is rewritten from scratch).
Why: under the golden rig most of the Great Lawn in p4 lies in the West Side skyline's shadow (the 9 deg sun reaches only a strip of it; the city-only baseline VB_p4 shows the
same strip), so a tree cannot cast a sun shadow there; what darkens the ground under a real tree in that light is the crown blocking the sky. Per tree of the browser's
trees-<kind>-near pools (the same instances UE draws): crown footprint = the near-card mesh's horizontal extent (GLB accessor min / max, x instance scale), centred on the
crown's own centre (rotated with the tree); coverage c(d) = 1 - smoothstep(0.55 R, 1.2 R, d); trees combine as 1 - prod(1 - c). alpha = 255 x (1 - coverage)
(255 = open sky, the r01-r05 value everywhere). M_TerrainPark multiplies its sky occlusion (material AO, sky / Lumen indirect only, never the sun) by lerp(1, CANOPY_OCC, 1 - alpha).
usage: prep_canopy.py [prep dir] [export dir]"""
import sys, os, json, struct, math
import numpy as np
from PIL import Image
S = '/Users/midir/sm2-n1/_scratch/terrain'
PREP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(S, 'prep'); EXPORT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(S, 'export')
pm = json.load(open(os.path.join(PREP, 'pathmask.json'))); TJ = json.load(open(os.path.join(EXPORT, 'terrain.json')))
img = np.array(Image.open(os.path.join(PREP, 'pathmask.png')).convert('RGBA'))
H, W = img.shape[:2]; tx = pm['texel']
def extent(kind):
    b = open(os.path.join(EXPORT, 'proto', 'trees_%s_near.glb' % kind), 'rb').read()
    n = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + n])
    lo = np.array([1e9] * 3); hi = -lo
    for m in j['meshes']:
        for p in m['primitives']:
            a = j['accessors'][p['attributes']['POSITION']]; lo = np.minimum(lo, a['min']); hi = np.maximum(hi, a['max'])
    return (lo + hi) / 2, (hi - lo) / 2   # centre, half extent (browser x, y, z)
keep = np.ones((H, W), np.float64); n = 0
for kind in ('park', 'elm', 'conifer'):
    items = (TJ['instances'].get('trees-%s-near' % kind) or {}).get('items') or []
    c, he = extent(kind); R0 = 0.5 * (he[0] + he[2])
    for it in items:
        s = it.get('s', 1.0); s3 = it.get('s3') or [1, 1, 1]; ry = it.get('ry', 0.0)
        ox, oz = c[0] * s * s3[0], c[2] * s * s3[2]
        cx = it['x'] + ox * math.cos(ry) + oz * math.sin(ry); cz = it['z'] - ox * math.sin(ry) + oz * math.cos(ry)   # rotation about +y (right-handed, y up)
        R = R0 * s * 0.5 * (s3[0] + s3[2])
        u, v = (cx - pm['x0']) / tx, (cz - pm['z0']) / tx; r = 1.2 * R / tx
        if u < -r or v < -r or u > W + r or v > H + r: continue
        x0, x1 = max(0, int(u - r)), min(W, int(u + r) + 2); y0, y1 = max(0, int(v - r)), min(H, int(v + r) + 2)
        if x0 >= x1 or y0 >= y1: continue
        yy, xx = np.mgrid[y0:y1, x0:x1]; d = np.hypot((xx + 0.5 - u) * tx, (yy + 0.5 - v) * tx)
        t = np.clip((d - 0.55 * R) / (0.65 * R), 0, 1); cov = 1 - t * t * (3 - 2 * t)
        keep[y0:y1, x0:x1] *= 1 - cov; n += 1
img[..., 3] = np.clip(np.round(255 * keep), 0, 255).astype(np.uint8)
Image.fromarray(img, 'RGBA').save(os.path.join(PREP, 'pathmask.png'))
print('canopy occlusion: %d trees in the park rectangle, covered share %.1f %% (alpha < 128), mean coverage %.3f' % (n, 100 * (keep < 0.5).mean(), 1 - keep.mean()))
