#!/usr/bin/env python3
"""P1 city (r10): the far-shore band of the S4 perch view (critic r09: 'white box plateau', silhouette-top std 6.1 px, 'grey wall embankment').
Pure Python on the exporter's data (no browser, no Unreal): writes the extra far-field content that build_city.py imports (step `fsky`) into
<export>/mesh/farsky/*.glb, <export>/proto/farsky_clump.glb and <export>/farsky.json.

  1. Plateau towers  : Fort-Lee / Cliffside-like high-rise clusters on the Palisades plateau (60-280 m, podium + shaft + crown + spire, mid-grey / stone tones),
                       M_CityFarMass (window grid, same vertex-colour convention as the exporter's farCityMass: rgb = tone, alpha = 0 plain / 0.5 windows / 1 glass).
  2. Hinterland towers: 5-sided boxes in the browser's hinterland item format (x y z sx sy sz rot wall rgb roof rgb), 6-17 km west / north-west, 70-330 m:
                       the far horizon gets a real, uneven skyline (S4 silhouette-top std).
  3. Bluff           : replaces the flat Palisades face (`palisadesCliff`, one vertical quad per 80 m) by a displaced face (talus, ledges, ravines, wooded patches
                       through vertex colour R) + tree clumps on its wooded parts and along the brow.
  4. Shoreline       : seawall + cap + promenade on the New-Jersey shore, extra piers with sheds where the browser's piers stop (z < -2600), tree row on the promenade.
  5. Lawn trees      : tree clumps on the green (lawn / park) pixels of the far-land ground map: the browser's far canopy is not exported, the far shores had no trees.
Deterministic (seeded). Re-run after any change; then `build_city.py steps=fsky,map`.
usage: python3 tools/export/far_skyline.py
"""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from citypaths import EXPORT
from glbio import write_glb

FAR_Y, PAL_Y, WATER_Y = 1.2, 58.0, -1.6
OUT = os.path.join(EXPORT, 'mesh', 'farsky'); os.makedirs(OUT, exist_ok=True)
POUT = os.path.join(EXPORT, 'proto'); os.makedirs(POUT, exist_ok=True)

# ---------------------------------------------------------------- the browser's Palisades line (farshore.js PAL_KEY / PAL_CLIFF, same wiggle)
PAL_KEY = [[-1880, -5200], [-1885, -3400], [-1905, -2300], [-1945, -1300], [-1985, -350], [-2030, 450], [-2120, 900], [-2330, 1150]]
def _pal_cliff():
    out = []
    for i in range(len(PAL_KEY) - 1):
        (ax, az), (bx, bz) = PAL_KEY[i], PAL_KEY[i + 1]
        n = max(1, int(math.floor(math.hypot(bx - ax, bz - az) / 80 + 0.5)))
        for k in range(n):
            t = k / n; z = az + (bz - az) * t
            e = 0 if i == 0 and k == 0 else 30 * math.sin(z * 0.0093 + 0.6) + 17 * math.sin(z * 0.031 + 2.3) + 9 * math.sin(z * 0.087 + 4.1)
            out.append([ax + (bx - ax) * t + e - 20, z])
    out.append(PAL_KEY[-1]); return np.array(out, float)
PAL = _pal_cliff()
def cliff_x(z): return float(np.interp(z, PAL[:, 1], PAL[:, 0]))
# NJ shoreline (farshore.js FAR_LANDS 'nj' east edge, z increasing)
NJ_SHORE = np.array([[-1500, -12000], [-1480, -5000], [-1510, -3500], [-1610, -2000], [-1690, -600], [-1735, 600], [-1760, 1600], [-1860, 2400]], float)
def shore_x(z): return float(np.interp(z, NJ_SHORE[:, 1], NJ_SHORE[:, 0]))

# ---------------------------------------------------------------- deterministic value noise
def _h(ix, iy, seed):
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0
def vnoise(x, y, seed=0):
    x = np.asarray(x, float); y = np.asarray(y, float)
    x0 = np.floor(x); y0 = np.floor(y); fx = x - x0; fy = y - y0
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    a = _h(x0, y0, seed); b = _h(x0 + 1, y0, seed); c = _h(x0, y0 + 1, seed); d = _h(x0 + 1, y0 + 1, seed)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy
def sstep(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

# ---------------------------------------------------------------- mesh builder
class Mesh:
    def __init__(self): self.P = []; self.N = []; self.C = []; self.I = []; self.n = 0
    def quad(self, p, nrm, col):
        p = np.asarray(p, float)
        if np.dot(np.cross(p[1] - p[0], p[2] - p[0]), np.asarray(nrm, float)) < 0: p = p[[0, 3, 2, 1]]   # counter-clockwise seen from outside whatever order the caller used
        self.P.append(p); self.N.append(np.tile(np.asarray(nrm, float), (4, 1))); self.C.append(np.tile(np.asarray(col, float), (4, 1)))
        self.I.append(np.array([0, 1, 2, 0, 2, 3]) + self.n); self.n += 4
    def box(self, x0, z0, x1, z1, y0, y1, col_side, col_top=None, flag=0.0, bottom=False):
        """axis-aligned box in browser coordinates (x east, y up, z south); sides + top (no bottom) with outward counter-clockwise faces"""
        cs = list(col_side[:3]) + [flag]; ct = list((col_top or col_side)[:3]) + [0.0 if flag < 0.75 else 0.0]
        self.quad([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]], [0, 0, -1], cs)   # north face (z0) seen from -z
        self.quad([[x1, y0, z0], [x1, y0, z1], [x1, y1, z1], [x1, y1, z0]], [1, 0, 0], cs)
        self.quad([[x1, y0, z1], [x0, y0, z1], [x0, y1, z1], [x1, y1, z1]], [0, 0, 1], cs)
        self.quad([[x0, y0, z1], [x0, y0, z0], [x0, y1, z0], [x0, y1, z1]], [-1, 0, 0], cs)
        self.quad([[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], [0, 1, 0], ct)
    def arrays(self, ox=0.0, oz=0.0):
        P = np.concatenate(self.P).astype(np.float32); P[:, 0] -= ox; P[:, 2] -= oz
        return P, np.concatenate(self.N).astype(np.float32), np.concatenate(self.C).astype(np.float32), np.concatenate(self.I).astype(np.int64)
    def write(self, path, name, center, rgba=True):
        P, N, C, I = self.arrays(center[0], center[2])
        if not rgba: C = C[:, :3]
        # winding: the quads above are wound so that (p1-p0) x (p2-p0) points along the outward normal in a RIGHT-handed frame with y up; glTF is right-handed, so nothing to flip
        write_glb(path, {'POSITION': P, 'NORMAL': N, 'TEXCOORD_0': np.zeros((len(P), 2), np.float32), 'COLOR_0': C}, I, name)

def check_winding():
    """quad winding self-test: geometric normal of the first triangle must agree with the stored normal"""
    m = Mesh(); m.box(0, 0, 10, 10, 0, 10, [.5, .5, .5]); P, N, C, I = m.arrays(); bad = 0
    for t in range(0, len(I), 3):
        a, b, c = P[I[t]], P[I[t + 1]], P[I[t + 2]]; g = np.cross(b - a, c - a)
        if np.dot(g, N[I[t]]) <= 0: bad += 1
    return bad

rng = np.random.default_rng(1010)
files = []          # [{'name','file','center','mat'}]
stats = {}
def tile_key(x, z, cell=1500.0): return (int(math.floor(x / cell)), int(math.floor(z / cell)))
def flush(meshes, prefix, mat, cell=1500.0):
    for (ix, iz), m in sorted(meshes.items()):
        if not m.n: continue
        cx, cz = (ix + 0.5) * cell, (iz + 0.5) * cell
        name = f'{prefix}__t{ix}_{iz}'; path = os.path.join(OUT, name + '.glb')
        m.write(path, name, (cx, 0, cz))
        files.append({'name': name, 'file': f'mesh/farsky/{name}.glb', 'center': [cx, 0.0, cz], 'mat': mat, 'verts': m.n, 'tris': int(sum(len(i) for i in m.I) // 3)})

# ================================================================ 1. plateau towers
# vertex colours in the farCityMass convention (linear, multiplied by MPC FarGain in M_CityFarMass): neutral mid-grey concrete / pale stone / warm brick / dark glass
TONES = [(0.150, 0.150, 0.158), (0.135, 0.138, 0.145), (0.175, 0.170, 0.160), (0.120, 0.120, 0.125), (0.185, 0.160, 0.135), (0.150, 0.120, 0.100), (0.100, 0.110, 0.125), (0.205, 0.200, 0.190)]
CLUSTERS = [  # name, z centre, z spread, count, h min, h max, supertall count, supertall h range
    ('Weehawken', -700, 260, 14, 60, 135, 0, (0, 0)),
    ('Union City', -1800, 330, 16, 70, 160, 1, (165, 205)),
    ('North Bergen', -2800, 330, 18, 80, 190, 2, (190, 235)),
    ('Fort Lee', -3800, 380, 24, 90, 220, 3, (215, 255)),
    ('Cliffside', -4700, 300, 14, 65, 140, 1, (150, 185)),
]
def tower(m, x, z, w, d, h, rg):
    t = TONES[rg.integers(len(TONES))]; glass = rg.random() < 0.5
    tone = t if not glass else (0.085, 0.100, 0.118)
    pod = rg.uniform(14, 26)
    pt = TONES[rg.integers(len(TONES))]
    m.box(x - w * 0.62, z - d * 0.62, x + w * 0.62, z + d * 0.62, PAL_Y, PAL_Y + pod, pt, pt, 0.5)
    y1 = PAL_Y + h
    m.box(x - w / 2, z - d / 2, x + w / 2, z + d / 2, PAL_Y + pod, y1, tone, tone, 1.0 if glass else 0.5)
    if rg.random() < 0.5:   # setback crown
        cw, cd, ch = w * rg.uniform(0.5, 0.7), d * rg.uniform(0.5, 0.7), h * rg.uniform(0.06, 0.12) + 5
        m.box(x - cw / 2, z - cd / 2, x + cw / 2, z + cd / 2, y1, y1 + ch, tone, tone, 0.5 if not glass else 1.0); y1 += ch
    if rg.random() < 0.18 and h > 100:  # spire / mast
        s = rg.uniform(2.0, 3.2); m.box(x - s, z - s, x + s, z + s, y1, y1 + rg.uniform(25, 60), (0.1, 0.1, 0.105), (0.1, 0.1, 0.105), 0.0)
def plateau_towers():
    meshes = {}; placed = []; rg = np.random.default_rng(2024)
    tot = 0
    for name, zc, zs, n, h0, h1, ns, hs in CLUSTERS:
        todo = [(False, 0, 0)] * n + [(True, hs[0], hs[1])] * ns
        for sup, a, b in todo:
            for _ in range(40):
                z = float(np.clip(zc + rg.normal(0, zs), -5100, 1000))
                off = 38 + 400 * rg.random() ** 1.7
                w, d = rg.uniform(26, 54), rg.uniform(26, 54)
                x = cliff_x(z) - off - w / 2
                if any(abs(x - px) < (w + pw) / 2 + 14 and abs(z - pz) < (d + pd) / 2 + 14 for px, pz, pw, pd in placed): continue
                h = rg.uniform(a, b) if sup else h0 + (h1 - h0) * rg.random() ** 1.6
                m = meshes.setdefault(tile_key(x, z), Mesh()); tower(m, x, z, w, d, h, rg); placed.append((x, z, w, d)); tot += 1; break
    flush(meshes, 'farsky_towers', 'towers')
    stats['plateau_towers'] = tot
plateau_towers()

# ================================================================ 2. hinterland skyline (items in the exporter's hinterland.json format)
# camera of S4 (city_shots.json): used only to PLACE clusters at chosen screen columns; the clusters stay in the world for every other view
S4_POS = np.array([182, 306, -92.0]); S4_TGT = np.array([-120, 150, -470.0]); S4_FOV = 75.0
def s4_ray(px):
    f = S4_TGT - S4_POS; f /= np.linalg.norm(f); r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r)
    a = (px - 960) / ((1920 / 2) / math.tan(math.radians(S4_FOV / 2)))
    d = f + a * r; d[1] = 0; return d / np.linalg.norm(d)
HIN = []   # [x, y, z, sx, sy, sz, rot, wall rgb, roof rgb]
def hin_box(x, z, w, d, h, wall, roof): HIN.append([x, 0.7, z, w, h, d, 0.0, *wall, *roof])
HWALL = [(0.34, 0.34, 0.35), (0.30, 0.30, 0.32), (0.38, 0.36, 0.33), (0.26, 0.27, 0.30), (0.42, 0.38, 0.33), (0.30, 0.25, 0.22), (0.22, 0.25, 0.30), (0.46, 0.45, 0.43)]
HROOF = [(0.30, 0.30, 0.30), (0.36, 0.35, 0.33), (0.25, 0.25, 0.27), (0.40, 0.39, 0.37)]
# (screen column at 1080p of the S4 view, distance m, tower count, tall max m, mid m)
HCL = [(60, 6200, 22, 210, 110), (250, 9000, 30, 270, 130), (430, 7000, 20, 170, 95), (600, 12500, 34, 330, 150), (780, 8200, 26, 240, 120),
       (930, 15500, 36, 330, 160), (1090, 10500, 30, 280, 140), (1240, 7600, 22, 190, 100), (1400, 13500, 28, 260, 130), (1560, 6600, 16, 150, 90)]
def hinterland():
    rg = np.random.default_rng(777); n = 0
    for px, D, cnt, hmax, hmid in HCL:
        d0 = s4_ray(px); c = S4_POS[[0, 2]] + d0[[0, 2]] * D; R = 0.085 * D
        for i in range(cnt):
            a = rg.uniform(0, 2 * math.pi); r = R * math.sqrt(rg.random())
            x, z = c[0] + math.cos(a) * r * 1.3, c[1] + math.sin(a) * r * 0.6
            u = rg.random(); h = hmid * (0.45 + 0.9 * u * u) if u < 0.8 else hmax * rg.uniform(0.55, 1.0)
            wd = rg.uniform(26, 58) * (1 + D / 30000); dp = rg.uniform(26, 58) * (1 + D / 30000)
            wall = HWALL[rg.integers(len(HWALL))]; roof = HROOF[rg.integers(len(HROOF))]
            hin_box(x, z, wd, dp, h, wall, roof)
            if h > 110 and rg.random() < 0.55:  # setback crown
                hin_box(x, z, wd * 0.6, dp * 0.6, h * 0.12, wall, roof); HIN[-1][1] = 0.7 + h; n += 1
            n += 1
    stats['hinterland_boxes'] = n
hinterland()

# ================================================================ 3. bluff (displaced Palisades face)
def bluff():
    # one continuous strip along the polyline PAL (z increasing), 14 m columns, 24 rows
    pts = PAL.copy()
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    ns = int(s[-1] / 12.0)
    ss = np.linspace(0, s[-1], ns + 1)
    X = np.interp(ss, s, pts[:, 0]); Z = np.interp(ss, s, pts[:, 1])
    tx = np.gradient(X, ss); tz = np.gradient(Z, ss); L = np.hypot(tx, tz); tx /= L; tz /= L
    nx, nz = tz, -tx                      # normal: face toward +x (river)
    flip = nx < 0; nx = np.where(flip, -nx, nx); nz = np.where(flip, -nz, nz)
    R = 26; Y = np.concatenate([[0.7], np.linspace(1.5, 12, 7), np.linspace(14, 55, 14), [58.0]])  # heights of the rows
    NR = len(Y)
    # displacement toward the river (+) / into the hill (-)
    Sg, Yg = np.meshgrid(ss, Y, indexing='ij')
    zc = np.interp(Sg, ss, Z)
    talus = 15.0 * np.clip(1 - Yg / 24.0, 0, 1) ** 1.5
    led = vnoise(Yg / 8.5, zc / 90.0, 3)                           # ledge phase
    saw = np.abs(((Yg / 9.0 + 0.35 * led) % 1.0) - 0.5) * 2.0       # 0..1 triangular
    ledge = 4.0 * (sstep(0.0, 1.0, saw) - 0.5) * sstep(6, 16, Yg) * (1 - sstep(48, 58, Yg))
    bay = np.clip(vnoise(zc / 130.0, Yg * 0 + 1.0, 5) - 0.52, 0, None) / 0.48
    bays = -16.0 * bay * sstep(4, 20, Yg) * (1 - sstep(50, 58, Yg))
    head = 7.0 * np.clip(vnoise(zc / 210.0, Yg * 0 + 2.0, 8) - 0.45, 0, None) * sstep(2, 14, Yg) * (1 - sstep(40, 58, Yg))
    rough = 2.2 * (vnoise(zc / 14.0, Yg / 5.0, 9) - 0.5) * sstep(3, 12, Yg) * (1 - sstep(52, 58, Yg))
    off = np.maximum(talus + ledge + bays + head + rough, -14.0)
    off[:, -1] = 0.0; off[:, 0] = np.maximum(off[:, 0], 6.0)                       # brow exactly on the plateau edge, foot a little out in the shallows
    PX = X[:, None] + nx[:, None] * off; PZ = Z[:, None] + nz[:, None] * off; PY = np.broadcast_to(Y[None, :], PX.shape).copy()
    # vegetation fraction: wooded talus + brow, patches on the face (vertex colour R), rock tone G, tree-clump candidates
    veg = np.clip(0.30 + 0.9 * (vnoise(zc / 40.0, Yg / 7.0, 11) - 0.45) + 0.55 * np.clip(1 - Yg / 20.0, 0, 1) + 0.5 * sstep(44, 58, Yg), 0, 1)
    tone = 0.75 + 0.5 * vnoise(zc / 33.0, Yg / 11.0, 12)
    C = np.stack([veg, np.clip(tone, 0, 1), np.ones_like(veg), np.ones_like(veg)], -1)
    P = np.stack([PX, PY, PZ], -1).reshape(-1, 3)
    # normals from the displaced grid
    dPs = np.gradient(np.stack([PX, PY, PZ], -1), axis=0); dPy = np.gradient(np.stack([PX, PY, PZ], -1), axis=1)
    Nn = np.cross(dPy, dPs).reshape(-1, 3)   # (d/dy) x (d/ds): for s along z-ish, y up -> +x
    Nn /= np.maximum(np.linalg.norm(Nn, axis=1, keepdims=True), 1e-9)
    ref = np.stack([nx[:, None].repeat(NR, 1), np.zeros((len(ss), NR)), nz[:, None].repeat(NR, 1)], -1).reshape(-1, 3)
    Nn = np.where((Nn * ref).sum(1, keepdims=True) < 0, -Nn, Nn)
    idx = []
    for i in range(len(ss) - 1):
        for j in range(NR - 1):
            a = i * NR + j; b = (i + 1) * NR + j; c = (i + 1) * NR + j + 1; d = i * NR + j + 1
            idx += [a, b, c, a, c, d]
    I = np.array(idx, np.int64).reshape(-1, 3)
    # winding agrees with the outward normal?
    g = np.cross(P[I[:, 1]] - P[I[:, 0]], P[I[:, 2]] - P[I[:, 0]]); sgn = (g * Nn[I[:, 0]]).sum(1)
    I[sgn < 0] = I[sgn < 0][:, [0, 2, 1]]
    I = I.reshape(-1)
    # tiles: split the strip by z into 1500 m tiles (separate GLBs, own centre)
    tiles = {}
    cz_of_vert = P[:, 2]; tz_of_tri = np.floor(P[I.reshape(-1, 3)[:, 0], 2] / 1500.0).astype(int)
    for t in np.unique(tz_of_tri):
        sel = I.reshape(-1, 3)[tz_of_tri == t]; used = np.unique(sel); remap = -np.ones(len(P), np.int64); remap[used] = np.arange(len(used))
        cx, cz = -1900.0, (t + 0.5) * 1500.0
        Pv = P[used].astype(np.float32); Pv[:, 0] -= cx; Pv[:, 2] -= cz
        name = f'farsky_bluff__t0_{t}'
        write_glb(os.path.join(OUT, name + '.glb'), {'POSITION': Pv, 'NORMAL': Nn[used].astype(np.float32), 'TEXCOORD_0': np.zeros((len(used), 2), np.float32), 'COLOR_0': C.reshape(-1, 4)[used].astype(np.float32)}, remap[sel].reshape(-1), name)
        files.append({'name': name, 'file': f'mesh/farsky/{name}.glb', 'center': [cx, 0.0, cz], 'mat': 'bluff', 'verts': int(len(used)), 'tris': int(len(sel))})
    stats['bluff_tris'] = int(len(I) // 3)
    # tree clump candidates on the wooded parts of the face
    cl = []
    Pg = np.stack([PX, PY, PZ], -1)
    for i in range(0, len(ss), 1):
        for j in range(1, NR - 1):
            v = veg[i, j]
            if v < 0.5: continue
            pr = (0.35 if Y[j] < 20 else 0.18) * (v - 0.4) / 0.6 + (0.55 if Y[j] > 52 else 0.0)
            if rng.random() > pr: continue
            p = Pg[i, j] + np.array([nx[i], 0, nz[i]]) * 1.0
            cl.append([p[0] + rng.uniform(-4, 4), p[1], p[2] + rng.uniform(-4, 4), rng.uniform(3.2, 6.8) * (1.0 if Y[j] < 52 else 1.3), rng.uniform(0.7, 1.15), rng.uniform(0.45, 0.8)])
    return cl
CLUMPS = bluff()
stats['bluff_clumps'] = len(CLUMPS)

# brow trees (plateau side of the lip) and talus-foot trees
for i in range(len(PAL) - 1):
    (ax, az), (bx, bz) = PAL[i], PAL[i + 1]; L = math.hypot(bx - ax, bz - az)
    for u in np.arange(0, L, 7.0):
        t = u / L; x = ax + (bx - ax) * t; z = az + (bz - az) * t
        wb = math.sin(z * 0.019 + 0.4) + 0.7 * math.sin(z * 0.047 + 2.2) + 0.4 * math.sin(z * 0.11)
        if rng.random() < (0.9 if wb > 0.3 else 0.5 if wb > -0.4 else 0.16):
            CLUMPS.append([x - rng.uniform(2, 30), PAL_Y, z + rng.uniform(-5, 5), rng.uniform(3.4, 6.2), rng.uniform(0.75, 1.15), rng.uniform(0.5, 0.8)])
stats['clumps_after_brow'] = len(CLUMPS)

# ================================================================ 4. shoreline: seawall, cap, promenade, piers, tree row
def shoreline():
    meshes = {}
    z_lo, z_hi = -5100.0, 2300.0
    zs = np.arange(z_lo, z_hi, 25.0)
    wall_dark = (0.11, 0.115, 0.12); cap = (0.40, 0.395, 0.38); prom = (0.43, 0.42, 0.395); pave = (0.30, 0.30, 0.30)
    # edge normal (toward the river, +x): the shore runs along z, so n ~ (1, 0, -dx/dz)
    def edge(z):
        x = shore_x(z); dx = shore_x(z + 5) - shore_x(z - 5); n = np.array([1.0, -dx / 10.0]); n /= np.linalg.norm(n); return x, n
    for z in zs:
        x0, n0 = edge(z); x1, n1 = edge(z + 25.0)
        m = meshes.setdefault(tile_key(x0, z), Mesh())
        a = np.array([x0 + 0.8 * n0[0], z + 0.8 * n0[1]]); b = np.array([x1 + 0.8 * n1[0], z + 25.0 + 0.8 * n1[1]])
        # seawall face (toward the river)
        m.quad([[a[0], WATER_Y - 0.3, a[1]], [b[0], WATER_Y - 0.3, b[1]], [b[0], FAR_Y + 1.5, b[1]], [a[0], FAR_Y + 1.5, a[1]]], [n0[0], 0, n0[1]], list(wall_dark) + [1])
        # cap (2 m wide strip on top of the wall)
        ai = a - n0 * 2.0; bi = b - n1 * 2.0
        m.quad([[ai[0], FAR_Y + 1.5, ai[1]], [bi[0], FAR_Y + 1.5, bi[1]], [b[0], FAR_Y + 1.5, b[1]], [a[0], FAR_Y + 1.5, a[1]]], [0, 1, 0], list(cap) + [1])
        # promenade 13 m wide, slightly above the far-land slab, pale pavers
        aj = a - n0 * 15.0; bj = b - n1 * 15.0
        m.quad([[aj[0], FAR_Y + 0.35, aj[1]], [bj[0], FAR_Y + 0.35, bj[1]], [bi[0], FAR_Y + 0.35, bi[1]], [ai[0], FAR_Y + 0.35, ai[1]]], [0, 1, 0], list(prom if (int(z) // 25) % 2 == 0 else pave) + [1])
        # (quads above are wound for a top view where +x is east, +z south, normal +y: p0 -> p1 along +z, p3 -> p0 toward the river = +x ... checked below by check_winding_quads)
    # piers where the browser's piers stop (z < -2600): perpendicular to the shore, 28-42 m wide, 90-200 m long, 70 % with a long shed
    rg = np.random.default_rng(31)
    z = -5000.0; npier = 0
    while z < -2650:
        x0, n0 = edge(z); w = rg.uniform(28, 42); ln = rg.uniform(90, 200); tdir = np.array([-n0[1], n0[0]])  # along the shore
        c0 = np.array([x0, z]); p = [c0 + tdir * (-w / 2) + n0 * 0.5, c0 + tdir * (w / 2) + n0 * 0.5, c0 + tdir * (w / 2) + n0 * ln, c0 + tdir * (-w / 2) + n0 * ln]
        m = meshes.setdefault(tile_key(x0, z), Mesh())
        yd = 2.4
        for k in range(4):   # dark fascia (piles) on the three seaward sides
            a, b = p[k], p[(k + 1) % 4]
            if k == 0 and False: continue
            nn = np.array([b[1] - a[1], -(b[0] - a[0])]); nn /= np.linalg.norm(nn)
            m.quad([[a[0], WATER_Y - 0.3, a[1]], [b[0], WATER_Y - 0.3, b[1]], [b[0], yd, b[1]], [a[0], yd, a[1]]], [nn[0], 0, nn[1]], [0.10, 0.10, 0.105, 1])
        m.quad([[p[0][0], yd, p[0][1]], [p[1][0], yd, p[1][1]], [p[2][0], yd, p[2][1]], [p[3][0], yd, p[3][1]]], [0, 1, 0], [0.34, 0.335, 0.32, 1])
        if rg.random() < 0.72:
            sw = w * rg.uniform(0.55, 0.78); sl = ln * rg.uniform(0.62, 0.86); sh = rg.uniform(9, 14)
            q0 = c0 + n0 * (ln * 0.1 + 6)
            wall = [(0.38, 0.39, 0.41, 1), (0.42, 0.26, 0.19, 1), (0.46, 0.45, 0.42, 1), (0.28, 0.33, 0.38, 1)][rg.integers(4)]
            roof = [0.26, 0.26, 0.27, 1]
            # shed body (axis-aligned footprint approximation: the shore is nearly N-S, so the pier points along +x)
            xa, xb = q0[0], q0[0] + sl * abs(n0[0]); za, zb = q0[1] - sw / 2, q0[1] + sw / 2
            m.box(xa, za, xb, zb, yd, yd + sh, wall[:3], roof[:3], 0.0)
            m.box(xa + 1, za + sw * 0.28, xb - 1, zb - sw * 0.28, yd + sh, yd + sh + 3.2, roof[:3], roof[:3], 0.0)   # ridge
        npier += 1; z += rg.uniform(150, 240)
    stats['new_piers'] = npier
    flush(meshes, 'farsky_shore', 'shore')
    # tree row on the promenade
    rg = np.random.default_rng(32); nt = 0
    for z in np.arange(z_lo, z_hi, 17.0):
        x0, n0 = edge(z + rg.uniform(-4, 4))
        c = np.array([x0, z]) - n0 * rg.uniform(7, 12)
        CLUMPS.append([c[0], FAR_Y + 0.3, c[1], rg.uniform(2.6, 4.2), rg.uniform(0.9, 1.3), rg.uniform(0.35, 0.6)]); nt += 1
    stats['promenade_trees'] = nt
shoreline()

# ================================================================ 5. trees on the lawns of the far-land ground map (farshore.js bakes parks / lawns / yards in it; no canopy is exported)
def lawn_trees():
    from PIL import Image
    mp = os.path.join(EXPORT, 'farland_map.png')
    if not os.path.exists(mp): stats['lawn_trees'] = 0; return
    a = np.asarray(Image.open(mp).convert('RGB')).astype(int)
    MAPX0, MAPZ0, PX = -6000.0, -7600.0, 5.0
    rg = np.random.default_rng(55); n = 0
    for z in np.arange(-5200.0, 2500.0, 11.0):
        for x in np.arange(-3300.0, -1300.0, 11.0):
            if x > shore_x(z) - 14: continue
            ix = int((x - MAPX0) / PX); iz = int((z - MAPZ0) / PX)
            if not (0 <= iz < a.shape[0] and 0 <= ix < a.shape[1]): continue
            r, g, b = a[iz, ix]; gr = g - max(r, b)
            if gr < 6: continue
            if rg.random() > min(1.0, 0.18 + gr / 30.0): continue
            y = PAL_Y if x < cliff_x(z) else FAR_Y
            CLUMPS.append([x + rg.uniform(-5, 5), y, z + rg.uniform(-5, 5), rg.uniform(3.0, 5.6), rg.uniform(0.8, 1.2), rg.uniform(0.3, 0.7)]); n += 1
    stats['lawn_trees'] = n
lawn_trees()

# ================================================================ clump proto: a lumpy ellipsoid (radius 1, height 1.25, sitting on y = 0), 80 triangles
def clump_proto():
    t = (1 + 5 ** 0.5) / 2
    V = np.array([[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t], [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]], float)
    F = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8], [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    # one midpoint subdivision -> 80 faces
    verts = [v for v in V]; cache = {}
    def mid(i, j):
        k = (min(i, j), max(i, j))
        if k not in cache: v = verts[i] + verts[j]; verts.append(v / np.linalg.norm(v)); cache[k] = len(verts) - 1
        return cache[k]
    F2 = []
    for a, b, c in F:
        ab, bc, ca = mid(a, b), mid(b, c), mid(c, a); F2 += [[a, ab, ca], [b, bc, ab], [c, ca, bc], [ab, bc, ca]]
    V = np.array(verts); rg2 = np.random.default_rng(3)
    V = V * (0.82 + 0.3 * rg2.random(len(V)))[:, None]
    V[:, 1] = V[:, 1] * 0.62 + 0.62; V[:, 1] = np.maximum(V[:, 1], 0.0)   # base on the ground, lumpy top
    F2 = np.array(F2)
    # outward winding
    for k, (a, b, c) in enumerate(F2):
        g = np.cross(V[b] - V[a], V[c] - V[a]); ctr = (V[a] + V[b] + V[c]) / 3 - np.array([0, 0.62, 0])
        if np.dot(g, ctr) < 0: F2[k] = [a, c, b]
    N = V - np.array([0, 0.5, 0]); N /= np.linalg.norm(N, axis=1, keepdims=True)
    write_glb(os.path.join(POUT, 'farsky_clump.glb'), {'POSITION': V.astype(np.float32), 'NORMAL': N.astype(np.float32), 'TEXCOORD_0': np.zeros((len(V), 2), np.float32), 'COLOR_0': np.ones((len(V), 4), np.float32)}, F2.reshape(-1), 'farsky_clump')
    stats['clump_tris'] = int(len(F2))
clump_proto()

# ================================================================ manifest
CL = np.array(CLUMPS); CL[:, 4] *= 1.9   # height scale of the unit blob (radius 1, height 1.24): crowns 7-25 m tall
json.dump({'note': 'P1 city r10 far skyline (tools/export/far_skyline.py)', 'files': files, 'clumps': np.round(CL, 2).tolist(), 'hinterland': np.round(np.array(HIN), 3).tolist(),
           'clump_proto': 'proto/farsky_clump.glb', 'stats': stats}, open(os.path.join(EXPORT, 'farsky.json'), 'w'))
print('winding self-test, bad triangles:', check_winding())
print(json.dumps(stats, indent=1)); print(len(files), 'glb files,', len(CLUMPS), 'clumps,', len(HIN), 'hinterland boxes')
