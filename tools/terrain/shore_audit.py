#!/usr/bin/env python3
"""Shoreline continuity audit (SPEC E3): rasterises the walkable shoreline surface of the exported browser coast (top faces of coast_m* + the island land polygon) at 1 m,
finds its outer boundary and checks that every boundary cell has a vertical shore element (seawall / bulkhead / platform skirt / riprap face) within 1.5 m.
A gap = a connected run of boundary cells without one; its length ~ number of cells. Reports max gap, count of gaps > 5 m, and the worst 15.
usage: shore_audit.py [city_export_dir] [terrain_export_dir] [out.json]"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'tools', 'export'))
from glbio import read_glb
SCR = os.environ.get('SM2_TERRAIN_SCRATCH', '/Users/midir/sm2-n1/_scratch/terrain')
CITY = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SCR, 'manhattan', 'export', 'midtown3x3')
TEXP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(SCR, 'export')
OUTJ = sys.argv[3] if len(sys.argv) > 3 else os.path.join(SCR, 'shore_audit.json')
X0, Z0, W, H = -1100.0, -3600.0, 2200, 7000     # 1 m cells over the island
T = json.load(open(os.path.join(TEXP, 'terrain.json')))
man = json.load(open(os.path.join(CITY, 'manifest.json')))
top = Image.new('L', (W, H), 0); wall = Image.new('L', (W, H), 0)
dt, dw = ImageDraw.Draw(top), ImageDraw.Draw(wall)
px = lambda x, z: ((x - X0), (z - Z0))
dt.polygon([px(x, z) for x, z in T['landPoly']], fill=255)
ntop = nwall = 0
for r in man['meshes']:
    if not r['name'].startswith('coast_m'): continue
    g = read_glb(os.path.join(CITY, r['file'])); P = g['attrs']['POSITION'] + np.array(r['center']); N = g['attrs']['NORMAL']; I = g['index'].reshape(-1, 3)
    ny = N[I[:, 0], 1]
    for tri in I[ny > 0.9]:
        ys = P[tri, 1]
        if ys.max() < -0.3: continue                      # decks / fill only, not the sea-bed skirts
        dt.polygon([px(*P[v][[0, 2]]) for v in tri], fill=255); ntop += 1
    for tri in I[(np.abs(ny) < 0.3) | ((ny >= 0.3) & (ny <= 0.9))]:   # vertical faces + sloped riprap / chamfers
        ys = P[tri, 1]
        if ys.max() - ys.min() < 0.3: continue
        dw.polygon([px(*P[v][[0, 2]]) for v in tri], outline=255); nwall += 1
TOP = np.array(top) > 0; WALL = np.array(wall) > 0
# dilate the wall mask by 1 cell (4 steps of the 8-neighbourhood -> 1.5 m tolerance)
def dil(m):
    o = m.copy(); o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]; o[1:, 1:] |= m[:-1, :-1]; o[:-1, :-1] |= m[1:, 1:]; o[1:, :-1] |= m[:-1, 1:]; o[:-1, 1:] |= m[1:, :-1]; return o
WALLD = dil(dil(WALL))
er = TOP.copy(); er[1:] &= TOP[:-1]; er[:-1] &= TOP[1:]; er[:, 1:] &= TOP[:, :-1]; er[:, :-1] &= TOP[:, 1:]
BND = TOP & ~er
# pier decks (ground.js PIERS) are separate structures out in the river: their open deck edges are not part of the shore walk
PIER = np.zeros((H, W), bool)
for pr in T.get('piers', []):
    a, b = int(pr['x0'] - X0) - 2, int(pr['x1'] - X0) + 2; c, d = int(pr['z0'] - Z0) - 2, int(pr['z1'] - Z0) + 2
    PIER[max(c, 0):d, max(a, 0):b] = True
BND &= ~PIER
gap = BND & ~WALLD
# connected components of gap cells (8-neighbourhood), iterative flood on the sparse list
ys, xs = np.nonzero(gap); idx = {(int(y), int(x)): i for i, (y, x) in enumerate(zip(ys, xs))}
seen = np.zeros(len(ys), bool); comps = []
for i in range(len(ys)):
    if seen[i]: continue
    st = [i]; seen[i] = True; cells = []
    while st:
        k = st.pop(); y, x = int(ys[k]), int(xs[k]); cells.append((y, x))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                j = idx.get((y + dy, x + dx))
                if j is not None and not seen[j]: seen[j] = True; st.append(j)
    comps.append(cells)
def length(cells):
    a = np.array(cells); return float(len(cells))   # 1 m cells: boundary cells ~ metres of edge
rows = sorted(({'len_m': length(c), 'x': float(np.mean([p[1] for p in c]) + X0), 'z': float(np.mean([p[0] for p in c]) + Z0)} for c in comps), key=lambda r: -r['len_m'])
res = {'boundary_cells': int(BND.sum()), 'gap_cells': int(gap.sum()), 'top_tris': ntop, 'wall_tris': nwall, 'gaps_over_5m': sum(1 for r in rows if r['len_m'] > 5),
       'piers_excluded': len(T.get('piers', [])), 'max_gap_m': rows[0]['len_m'] if rows else 0.0, 'worst': rows[:15], 'cell_m': 1.0, 'wall_tolerance_m': 1.5}
json.dump(res, open(OUTJ, 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'worst'}, indent=1)); print('worst:', [(round(r['x']), round(r['z']), r['len_m']) for r in rows[:10]])
