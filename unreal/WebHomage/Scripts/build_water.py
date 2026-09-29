# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# Piece P6 water (blind A/B build, Sonnet 5.5): the river water of the Unreal port. Idempotent, headless, applied on top of
# Scripts/build_manhattan.py. Owns /Game/Water, this file and docs/night1/water/. No .uasset / .umap is committed (CONTENT.md).
#
# Two modes in one file (same convention as build_manhattan.py):
#   * plain python3 (run from anywhere, YOUR editor closed):
#         python3 unreal/WebHomage/Scripts/build_water.py [--steps base,assets,water,views]
#     base    build_manhattan.py steps cpp, city_export, city_prep, city, look, map (everything the water needs: city geometry, the
#             golden / midday / night rigs, /Game/Maps/Manhattan_View_S4). The traversal and characters steps are not run (the water
#             does not depend on them). Runs on this piece's own scratch dir and vite port, every Unreal launch through gpu_slot.sh.
#     assets  numpy / PIL / scipy: tileable noise + ripple-normal textures, shore-distance + contact maps from the browser layout
#             (LAND_POLY + FAR_LANDS, src/world/layout.js, farshore.js), the polar water mesh (GLB)  -> <SCR>/water/
#     water   headless Unreal commandlet (this file inside Unreal): imports the assets into /Game/Water, builds M_WaterRiver, swaps the
#             city's flat WaterPlane for the wave surface in City_Midtown_Geo, builds the view maps and the dolly sequence
#     views   writes docs/night1/water/views.json (the two capture views) from the browser layout
#   * inside Unreal (-run=pythonscript -script=<this file>): step 'water'.
#
# Design (details in docs/night1/water/HANDOFF.md):
#   surface   ONE static polar grid mesh centred on the origin whose vertices the material moves to the camera (WPO) and displaces with
#             the browser's 12 Gerstner waves (src/world/waves.js, same constants); waves shorter than ~4 vertex spacings fade out and
#             live on in the per-pixel normal + roughness (as waves.js waveSlope does).  Rings widen with distance: ~1 m at 50 m, the
#             last ring reaches 60 km, so no flat plane and no horizon seam.
#   shading   Default Lit (opaque): analytic Gerstner slopes + capillary normal layers per pixel, roughness from the unresolved slope
#             variance (Cox-Munk / Toksvig), Fresnel from the engine (F0 0.02), Lumen reflections for the sky + skyline, the sun's GGX
#             glint from the engine's directional light, an analytic turbid-medium body colour (silt near shore) as base colour, foam
#             from the baked contact / shore distance maps + whitecaps.
import os, sys, json, subprocess, time, shutil, math

HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/Users/midir/sm2-n1/water-ab-sonnet/unreal/WebHomage/Scripts'
PROJ = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(PROJ))
UPROJECT = os.path.join(PROJ, 'WebHomage.uproject')
UE = '/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
SCR = os.environ.get('SM2_WATER_SCR', '/Users/midir/sm2-n1/_scratch/water-sonnet')
WSCR = os.path.join(SCR, 'water')            # generated water assets (textures, mesh)
DEV_PORT = 5219                               # vite port of this piece's city export (build_manhattan.py's 5208 belongs to piece C)
GPU = '/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh'
LABEL = 'water-sonnet'
WATER_Y = -1.6                                # browser G.WATER_Y (m)
DOCS = os.path.join(WT, 'docs', 'night1', 'water')

try:
    import unreal  # noqa: F401
    IN_UE = hasattr(unreal, 'EditorAssetLibrary')
except ImportError:
    IN_UE = False


# ================================================================================================ orchestrator (plain python3)
def log(*a):
    print('[build_water %s]' % time.strftime('%H:%M:%S'), *a, flush=True)


def load_manhattan():
    """build_manhattan.py as a module, retargeted to this piece's scratch dir / vite port and to the GPU lock (its own defaults
    belong to piece C: scratch _scratch/manhattan, port 5208, unwrapped Unreal launches)."""
    import importlib.util
    os.environ['SM2_MANHATTAN_SCR'] = SCR
    spec = importlib.util.spec_from_file_location('build_manhattan', os.path.join(HERE, 'build_manhattan.py'))
    bm = importlib.util.module_from_spec(spec); spec.loader.exec_module(bm)
    bm.DEV_PORT = DEV_PORT
    wrapper = os.path.join(SCR, 'ue_slot.sh')
    os.makedirs(SCR, exist_ok=True)
    open(wrapper, 'w').write('#!/bin/bash\n# every Unreal launch of this piece goes through the shared GPU lock (RULES.md hard GPU cap)\n'
                             'exec "%s" capture --label %s -- "%s" "$@"\n' % (GPU, LABEL, UE))
    os.chmod(wrapper, 0o755)
    bm.UE = wrapper
    bm.wait_slot = lambda: None                # the lock enforces the instance cap
    return bm


def step_base():
    bm = load_manhattan()
    os.makedirs(os.path.join(SCR, 'logs'), exist_ok=True)
    for s in ('cpp', 'city_export', 'city_prep', 'city', 'look', 'map'):
        log('=== base step', s); t = time.time()
        getattr(bm, 'step_' + s)()
        log('=== base step %s done in %.0f s' % (s, time.time() - t))



# ---------------------------------------------------------------------------------------------------------------- step assets
WAVE_SPEC = [  # src/world/waves.js SPEC: [wavelength m, amplitude m, direction deg (0 = +x east, 90 = +z south), steepness Q, phase]
    [31.0, 0.06, -38, 0.2, 0.0], [16.5, 0.055, -62, 0.35, 5.1], [11.2, 0.065, -24, 0.45, 1.7], [7.9, 0.05, -83, 0.5, 4.1],
    [5.6, 0.042, -47, 0.55, 2.3], [4.3, 0.03, -2, 0.5, 3.9], [3.3, 0.026, -71, 0.55, 5.6], [2.45, 0.019, -28, 0.5, 0.9],
    [1.8, 0.014, -104, 0.45, 3.3], [1.33, 0.01, -52, 0.4, 6.0], [0.97, 0.0072, 8, 0.35, 2.0], [0.71, 0.005, -66, 0.3, 4.6]]
GRAV = 9.81
WAVES = []
for _L, _A, _d, _q, _ph in WAVE_SPEC:
    _k = 2 * math.pi / _L; _dr = math.radians(_d)
    WAVES.append(dict(L=_L, A=_A, k=_k, w=math.sqrt(GRAV * _k), dx=math.cos(_dr), dz=math.sin(_dr), Q=_q / (_k * _A * len(WAVE_SPEC)), ph=_ph))
WAVE_MAX = sum(w['A'] for w in WAVES)


def wave_dispersion_check():
    """sanity: the table is the browser's (12 waves, the same constants)"""
    assert len(WAVES) == 12 and abs(WAVE_MAX - 0.3832) < 5e-4, WAVE_MAX


SHORE_BOX = (-6400.0, -8000.0, 12800.0, 17600.0)   # browser shoreMap(): x0, z0, width, height (m), 8 m/px, 8 bit (m / 400)
CONTACT_BOX = (-1800.0, -4300.0, 3800.0, 8800.0)   # browser contactMap(): 2 m/px; here a SIGNED distance (edge = 0.5, +-16 m in 8 bit)
CONTACT_CAP = 16.0


def dump_layout():
    """LAND_POLY (layout.js) and FAR_LANDS (farshore.js: sliced out of the source, the file itself imports three + the facade builders)
    -> <WSCR>/layout_dump.json, evaluated by node."""
    js = r"""
import fs from 'fs';
const WT = process.argv[2];
const L = await import(WT + '/src/world/layout.js');
const src = fs.readFileSync(WT + '/src/world/farshore.js', 'utf8');
const a = src.indexOf('export const FAR_LANDS = ['); const b = src.indexOf('\n];', a);
const far = (new Function('return ' + src.slice(a + 'export const FAR_LANDS = '.length, b + 2)))();
const west = {}; for (const z of [-512, -384, -256, -128, 0, 128, 256]) west[z] = L.shoreX(z);
console.log(JSON.stringify({ waterY: L.G.WATER_Y, land: L.LAND_POLY, far: far.map(f => ({ name: f.name, pts: f.pts })), shoreX: west }));
"""
    os.makedirs(WSCR, exist_ok=True)
    jp = os.path.join(WSCR, 'dump_layout.mjs'); open(jp, 'w').write(js)
    r = subprocess.run(['node', jp, WT], capture_output=True, text=True, cwd=WT)
    if r.returncode: raise SystemExit('layout dump failed: ' + r.stderr[-2000:])
    d = json.loads(r.stdout); json.dump(d, open(os.path.join(WSCR, 'layout_dump.json'), 'w'))
    return d


def coast_triangles():
    """(n, 3, 2) float32 array of browser-frame (x, z) triangle footprints of everything the export builds that stands above the water:
    coast meshes (esplanade fill / seawalls / riprap / platforms: waterfront.js builds them OUTWARD of layout.LAND_POLY by a varying offset,
    so the polygon alone is not the waterline) and the bridge piers, each clipped at the water plane (a bank that slopes below the
    water line only counts down to the line)."""
    import numpy as np
    sys.path.insert(0, os.path.join(WT, 'tools', 'export'))
    from glbio import read_glb
    E = os.path.join(SCR, 'export', 'midtown3x3')
    man = json.load(open(os.path.join(E, 'manifest.json')))
    out = []
    for r in man['meshes']:
        if not (r['name'].startswith('coast_') or r['name'] == 'bridgeStone'): continue
        g = read_glb(os.path.join(E, r['file']))
        P = g['attrs']['POSITION'].astype(np.float64); I = g['index'].reshape(-1, 3)
        P[:, 0] += r['center'][0]; P[:, 2] += r['center'][2]
        T = P[I]                                               # (n, 3, 3) x y z
        up = T[:, :, 1] > WATER_Y + 0.05
        nup = up.sum(1)
        out.append(T[nup == 3][:, :, [0, 2]])
        for k in (1, 2):                                       # triangles cut by the water plane
            sel = T[nup == k]
            if not len(sel): continue
            u = up[nup == k]
            # order the vertices so that the "odd" vertex (the only one above / below) comes first
            odd = np.argmax(u if k == 1 else ~u, axis=1)
            idx = np.arange(len(sel))
            a = sel[idx, odd]; b = sel[idx, (odd + 1) % 3]; c = sel[idx, (odd + 2) % 3]
            def cut(p, q):                                     # point of pq on the water plane
                t = (WATER_Y + 0.05 - p[:, 1]) / (q[:, 1] - p[:, 1]); return p + (q - p) * t[:, None]
            ab, ac = cut(a, b), cut(a, c)
            if k == 1: out.append(np.stack([a, ab, ac], 1)[:, :, [0, 2]])                       # one vertex above
            else:                                                                             # two above: a quad b, c, ac, ab
                out.append(np.stack([b, c, ac], 1)[:, :, [0, 2]]); out.append(np.stack([b, ac, ab], 1)[:, :, [0, 2]])
    return np.concatenate(out).astype(np.float32) if out else np.zeros((0, 3, 2), np.float32)


def raster_masks(d):
    """1 = above the water. Fine mask (0.5 m/px) over CONTACT_BOX: layout polygons + coast triangles. Coarse mask (8 m/px) over SHORE_BOX:
    layout polygons, with the fine mask pasted in over its region."""
    import numpy as np, cv2
    tris = coast_triangles()
    log('coast footprints: %d triangles' % len(tris))
    polys = [d['land']] + [f['pts'] for f in d['far']]
    cl = lambda v: max(-1e5, min(1e5, v))
    def draw(box, px, mask, tri):
        X0, Z0 = box[0], box[1]
        S = 16                                                  # cv2 sub-pixel bits (1/16 px)
        for pts in polys:
            a = np.array([[(cl(x) - X0) / px * S, (cl(z) - Z0) / px * S] for x, z in pts], np.int64)
            cv2.fillPoly(mask, [a.astype(np.int32)], 255, shift=4) if np.abs(a).max() < 2 ** 31 else None
        if tri is not None and len(tri):
            for i in range(0, len(tri), 200000):
                t = tri[i:i + 200000]
                q = np.rint((t - np.array([X0, Z0], np.float32)) / px * S).astype(np.int32)
                cv2.fillPoly(mask, list(q), 255, shift=4)
    X0, Z0, Wm, Hm = CONTACT_BOX; PXF = 0.5
    fine = np.zeros((int(Hm / PXF), int(Wm / PXF)), np.uint8)
    draw(CONTACT_BOX, PXF, fine, tris)
    X0s, Z0s, Ws, Hs = SHORE_BOX
    coarse = np.zeros((int(Hs / 8.0), int(Ws / 8.0)), np.uint8)
    draw(SHORE_BOX, 8.0, coarse, None)
    # paste the fine mask (block max) into the coarse one
    f = fine.reshape(fine.shape[0] // 16, 16, fine.shape[1] // 16, 16).max((1, 3))
    i0, j0 = int((X0 - X0s) / 8.0), int((Z0 - Z0s) / 8.0)
    coarse[j0:j0 + f.shape[0], i0:i0 + f.shape[1]] = np.maximum(coarse[j0:j0 + f.shape[0], i0:i0 + f.shape[1]], f)
    return fine, coarse


def signed_distance(mask, px, cap_m, strip=2048):
    """signed distance (m; negative inside = above the water) from a 0/255 mask, cv2 5x5 chamfer in row strips (half-pixel corrected)"""
    import numpy as np, cv2
    H, W = mask.shape; out = np.empty((H, W), np.float32)
    m = int(cap_m / px) + 8
    for r0 in range(0, H, strip):
        a, b = max(0, r0 - m), min(H, r0 + strip + m)
        s = mask[a:b]
        d_out = cv2.distanceTransform(np.where(s > 0, 0, 255).astype(np.uint8), cv2.DIST_L2, 5)     # water px -> nearest land px
        d_in = cv2.distanceTransform((s > 0).astype(np.uint8) * 255, cv2.DIST_L2, 5)                   # land px -> nearest water px
        sd = np.where(s > 0, -(d_in - 0.5), d_out - 0.5) * px
        out[r0:min(H, r0 + strip)] = sd[r0 - a:r0 - a + min(strip, H - r0)]
    return out


def make_shore_maps(d):
    import numpy as np
    from PIL import Image
    out = os.path.join(WSCR, 'tex')
    fine, coarse = raster_masks(d)
    # far map: 8 m/px, metres / 400 (browser encoding)
    D = signed_distance(coarse, 8.0, 400.0)
    g = (np.clip(D, 0, 400) / 400.0 * 255 + 0.5).astype(np.uint8)
    Image.fromarray(np.stack([g, g, g], -1), 'RGB').save(os.path.join(out, 'T_WaterShore.png'))
    log('shore map %dx%d' % (g.shape[1], g.shape[0]))
    # contact map: signed distance at 0.5 m/px -> 2 m/px block means (a linear field's block mean is its centre value), edge = 0.5, +-16 m
    Df = signed_distance(fine, 0.5, CONTACT_CAP)
    Hh, Ww = Df.shape[0] // 4, Df.shape[1] // 4
    D2 = Df[:Hh * 4, :Ww * 4].reshape(Hh, 4, Ww, 4).mean((1, 3))
    g = (np.clip(0.5 + D2 / (2 * CONTACT_CAP), 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(np.stack([g, g, g], -1), 'RGB').save(os.path.join(out, 'T_WaterContact.png'))
    # the true waterline of the Hudson esplanade around the latitude of the Midtown block centre (probe for views.json): the west-most edge
    # (first pixel above the water, scanning from the west) in the rows z = zc +- 25 m, in a 250 m window around the LAND_POLY shoreline
    zc = -128.0; xs_poly = d['shoreX'][str(int(zc))][0]
    j0, j1 = int((zc - 25 + 4300) / 0.5), int((zc + 25 + 4300) / 0.5); i0, i1 = int((xs_poly - 125 + 1800) / 0.5), int((xs_poly + 125 + 1800) / 0.5)
    edges = []
    for j in range(j0, j1):
        land = np.where(Df[j, i0:i1] < 0)[0]
        if len(land): edges.append(-1800 + (i0 + land[0]) * 0.5)
    json.dump({'zc': zc, 'land_poly_x': xs_poly, 'edge_x_west_most': min(edges), 'edge_x_median': float(np.median(edges)), 'rows': len(edges)}, open(os.path.join(WSCR, 'waterline_probe.json'), 'w'))
    log('contact map %dx%d' % (Ww, Hh))


def make_textures():
    import numpy as np
    from PIL import Image
    out = os.path.join(WSCR, 'tex'); os.makedirs(out, exist_ok=True)
    N = 512

    def spectrum_noise(seed, beta, kmin, kmax):
        rng = np.random.default_rng(seed)
        f = np.fft.fftfreq(N) * N
        kx, ky = np.meshgrid(f, f); k = np.hypot(kx, ky)
        amp = np.where((k >= kmin) & (k <= kmax), np.maximum(k, 1e-6) ** (-beta / 2.0), 0.0)
        spec = amp * np.exp(2j * np.pi * rng.random((N, N)))
        h = np.real(np.fft.ifft2(spec)); return h

    def equalise(h):   # rank transform -> uniform [0, 1]
        r = np.argsort(np.argsort(h.ravel())).astype(np.float64) / (h.size - 1)
        return r.reshape(h.shape)

    # T_WaterNoise: R large soft blobs (gust field), G mid, B fine, A billowy (foam cells)
    R = equalise(spectrum_noise(11, 3.2, 1, 24)); G = equalise(spectrum_noise(12, 2.4, 1, 64)); B = equalise(spectrum_noise(13, 1.7, 2, 200))
    A = equalise(np.abs(spectrum_noise(14, 2.0, 2, 120)))
    rgba = (np.stack([R, G, B, A], -1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(out, 'T_WaterNoise.png'))
    # T_WaterRipple: tileable ripple normal map (RG = slope x / y encoded 0.5 + s), height spectrum k^-3 over 2..24 cycles per tile
    h = spectrum_noise(21, 3.0, 2, 24)
    f = np.fft.fftfreq(N) * N; kx, ky = np.meshgrid(f, f)
    H = np.fft.fft2(h)
    sx = np.real(np.fft.ifft2(1j * kx * H)); sy = np.real(np.fft.ifft2(1j * ky * H))
    sc = 0.5 / max(np.std(sx), np.std(sy))     # unit slope std -> 0.5 (the shader scales it)
    sx, sy = np.clip(sx * sc * 0.5 + 0.5, 0, 1), np.clip(sy * sc * 0.5 + 0.5, 0, 1)
    hh = equalise(h)
    rgba = (np.stack([sx, sy, hh, np.ones_like(hh)], -1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(out, 'T_WaterRipple.png'))
    return out


def ring_plan():
    """radii (m) of the polar grid rings + segment count of every ring. Radial step max(0.5 m, 2 % of r) out to ~1.5 km, growing to
    ~12 % of r toward 70 km (all waves are faded by then: the far rings are flat)."""
    r = [0.0]
    while r[-1] < 70000.0:
        x = r[-1]
        s = min(1.0, max(0.0, (x - 800.0) / 2200.0)); s = s * s * (3 - 2 * s)
        r.append(x + max(0.5, 0.02 * x * (1 + 5.0 * s)))
    n = [64 if x < 6.0 else 128 if x < 14.0 else 256 if x < 40.0 else 512 for x in r]
    n[0] = 1
    return r, n


def make_mesh():
    """polar water grid -> GLB (browser frame: x east, y up, z south, metres). UV0.x = the vertex's local grid spacing (m), which the
    material uses to fade waves the mesh cannot resolve. 2:1 angular refinement between rings is stitched without T-junctions."""
    import numpy as np
    sys.path.insert(0, os.path.join(WT, 'tools', 'export'))
    from glbio import write_glb
    r, n = ring_plan()
    P, UV, I = [], [], []
    first = []
    for j, (rj, nj) in enumerate(zip(r, n)):
        first.append(len(P))
        dr = (r[j + 1] - rj) if j + 1 < len(r) else (rj - r[j - 1])
        for i in range(nj):
            a = 2 * math.pi * i / nj
            P.append((rj * math.cos(a), 0.0, rj * math.sin(a)))
            sp = max(dr, 2 * math.pi * rj / nj) if j else dr
            UV.append((sp, 0.0))
    for j in range(len(r) - 1):
        a0, na, b0, nb = first[j], n[j], first[j + 1], n[j + 1]
        if na == 1:   # centre fan
            for i in range(nb): I += [a0, b0 + i, b0 + (i + 1) % nb]
        elif nb == na:
            for i in range(na):
                a, a1, b, b1 = a0 + i, a0 + (i + 1) % na, b0 + i, b0 + (i + 1) % nb
                I += [a, b, b1, a, b1, a1]
        elif nb == 2 * na:
            for i in range(na):
                a, a1 = a0 + i, a0 + (i + 1) % na
                b, bm, b2 = b0 + 2 * i, b0 + 2 * i + 1, b0 + (2 * i + 2) % nb
                I += [a, b, bm, a, bm, a1, a1, bm, b2]
        else: raise SystemExit('ring plan: unsupported segment ratio %d -> %d' % (na, nb))
    P = np.array(P, np.float32); UV = np.array(UV, np.float32)
    N = np.tile(np.array([[0, 1, 0]], np.float32), (len(P), 1))
    # counter-clockwise seen from +y (three.js convention: the front face looks up)
    I = np.array(I, np.uint32).reshape(-1, 3)[:, ::-1].reshape(-1)
    path = os.path.join(WSCR, 'WaterGrid.glb')
    write_glb(path, {'POSITION': P, 'NORMAL': N, 'TEXCOORD_0': UV}, I, name='WaterGrid')
    log('mesh: %d rings, %d vertices, %d triangles, r_max %.0f m -> %s' % (len(r), len(P), len(I) // 3, r[-1], path))
    return path


def step_assets():
    wave_dispersion_check()
    d = dump_layout()
    make_textures(); make_shore_maps(d); make_mesh()
    json.dump({'shoreX': d['shoreX']}, open(os.path.join(WSCR, 'shore_probe.json'), 'w'))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--steps', default='base,assets,water,views')
    a = ap.parse_args()
    for s in a.steps.split(','):
        f = globals().get('step_' + s)
        if not f: raise SystemExit('unknown step ' + s)
        log('=== step', s); t = time.time(); f(); log('=== step %s done in %.0f s' % (s, time.time() - t))



# ---------------------------------------------------------------------------------------------------------------- views.json
def step_views():
    """docs/night1/water/views.json: the capture views, defined from the browser layout (frame: x east, y up, z south, metres)."""
    dump = json.load(open(os.path.join(WSCR, 'layout_dump.json')))
    lay = json.load(open(os.path.join(SCR, 'export', 'midtown3x3', 'layout.json')))
    reg = lay['region']
    zc = (reg['z0'] + reg['z1']) / 2.0                      # latitude of the centre of the detailed Midtown block
    xc = (reg['x0'] + reg['x1']) / 2.0
    # west shoreline x at zc: layout.js shoreX(z) (the function the land polygon / coast meshes are built from)
    xs = None
    for k, v in dump['shoreX'].items():
        if abs(float(k) - zc) < 1e-6: xs = v[0]
    if xs is None: raise SystemExit('no shoreX probe for z=%s' % zc)
    wl = json.load(open(os.path.join(WSCR, 'waterline_probe.json')))
    x_low = round(wl['edge_x_west_most'] - 4.0, 3)          # 4 m beyond the west-most point of the built esplanade edge
    shots = {sh['id']: sh for sh in json.load(open(os.path.join(HERE, 'city_shots.json')))}
    s4 = shots['S4_perch_skyline']
    y = round(WATER_Y + 6.0, 3)
    low = {'pos': [x_low, y, zc], 'yaw_compass_deg': 0.0, 'pitch_deg': -3.0, 'fov_h_deg': 90.0}
    dolly = {'from': low['pos'], 'to': [x_low, y, zc - 10.0], 'duration_s': 10.0, 'speed_m_s': 1.0, 'hold_before_s': 3.0, 'hold_after_s': 0.5}
    views = {
        '_comment': 'Homage fan game, not an official Marvel/Sony/Insomniac game. Capture views of the water A/B. Browser frame: x east, y up, '
                    'z south (north = -z), metres; UE cm = (x, z, y) * 100; UE yaw = compass yaw - 90 (compass: 0 = north, 90 = east, 270 = west).',
        'frame': 'browser metres (x east, y up, z south)',
        'water_y_m': WATER_Y,
        'midtown_block_centre_xz': [xc, zc],
        'waterline_probe': wl,
        'views': {
            'S4_golden': {'source': 'unreal/WebHomage/Scripts/city_shots.json S4_perch_skyline', 'pos': s4['pos'], 'target': s4['target'],
                          'fov_h_deg': s4['fov'], 'map': '/Game/Maps/Manhattan_View_S4', 'look': 'golden',
                          'files': ['S4_golden_4k.jpg (3840x2160)', 'S4_golden_1080.jpg (1920x1080)']},
            'river_low': {'desc': 'Hudson waterfront at the latitude of the centre of the detailed Midtown block (region z -512..256 -> z = -128), 6 m '
                                  'above the mean water level, looking north ALONG the river (Jersey shore at the left edge, the esplanade edge on the right), '
                                  'pitch -3 deg, horizontal FOV 90 deg. Position: the built waterfront, NOT layout.js LAND_POLY: waterfront.js builds the '
                                  'esplanade fill / bump-outs outward of LAND_POLY (by up to ~25 m here), so x = west-most esplanade edge in z -128 +- 25 m '
                                  '(%.1f) minus 4 m = %.1f. The literal LAND_POLY x (%.1f) hangs over the promenade: see river_low_polygon.' % (wl['edge_x_west_most'], x_low, xs),
                          'pos': low['pos'], 'yaw_compass_deg': 0.0, 'pitch_deg': -3.0, 'fov_h_deg': 90.0,
                          'map': '/Game/Water/Maps/Water_View_Low', 'look': 'golden',
                          'files': ['river_low_4k.jpg (3840x2160)', 'river_low_1080.jpg (1920x1080)']},
            'river_low_dolly': dict({'desc': 'the river_low view moving slowly forward (north, along the look direction), 10 s, 1920x1080, 60 fps; '
                                             'the camera holds still for hold_before_s first (Lumen / exposure settle, trimmed from the clip)'},
                                    **dict({k: dolly[k] for k in ('from', 'to', 'duration_s', 'speed_m_s', 'hold_before_s', 'hold_after_s')},
                                           yaw_compass_deg=0.0, pitch_deg=-3.0, fov_h_deg=90.0, map='/Game/Water/Maps/Water_View_Dolly', look='golden',
                                           files=['river_low_dolly.mp4'])),
            'river_low_west': {'desc': 'SUPPLEMENT: the river_low position looking west, across the river toward the Jersey shore and the low sun (sun '
                                       'glitter, sheen, pier reflections)', 'pos': low['pos'], 'yaw_compass_deg': 270.0, 'pitch_deg': -3.0, 'fov_h_deg': 90.0,
                               'map': '/Game/Water/Maps/Water_View_LowWest', 'look': 'golden', 'files': ['river_low_west_4k.jpg', 'river_low_west_1080.jpg']},
            'river_low_polygon': {'desc': 'SUPPLEMENT: the literal reading of the brief, x = layout.js shoreX(z).west (the LAND_POLY west shoreline) at the '
                                          'block-centre latitude, 6 m above the water, looking north. Camera hangs over the esplanade: little water in frame.',
                                  'pos': [round(xs, 3), y, zc], 'yaw_compass_deg': 0.0, 'pitch_deg': -3.0, 'fov_h_deg': 90.0,
                                  'map': '/Game/Water/Maps/Water_View_LowPoly', 'look': 'golden', 'files': ['river_low_polygon_4k.jpg', 'river_low_polygon_1080.jpg']}},
    }
    os.makedirs(DOCS, exist_ok=True)
    json.dump(views, open(os.path.join(DOCS, 'views.json'), 'w'), indent=1)
    log('views.json: river_low at', low['pos'], '(west shoreline x at z=%s)' % zc)


# ---------------------------------------------------------------------------------------------------------------- inside Unreal
TUNE = {'body': [0.068, 0.086, 0.070],      # linear albedo of the turbid river body (green-grey), lit by the engine's sun + sky light
        'bottom': [0.11, 0.095, 0.065],      # silty river bed showing through near the walls
        'foam': [0.62, 0.64, 0.62],
        'spec': 0.25,                        # UE Specular: F0 = 0.08 * 0.25 = 0.02 (water, n = 1.333)
        'slope_k': 0.7,                      # scale of the resolved Gerstner slopes in the shading normal
        'dn_k': 0.6,                         # scale of the ripple normal layers
        'sw_k': 0.5,                         # extra slope gain of the waves shorter than 5 m (the browser's saturated spectrum reads as marbling at 4K)
        'foam_k': 0.5, 'rough_lo': 0.8, 'rough_hi': 1.2,
        'a2_base': 0.022, 'mss0': 0.0015, 'mss1': 0.003, 'var_k': 0.7}   # GGX alpha^2 = a2_base^2 + 2 mss unres + 2 var_k varU
if os.environ.get('SM2_WATER_TUNE'): TUNE.update(json.loads(os.environ['SM2_WATER_TUNE']))


def hlsl_vertex():
    """WPO: move the polar grid under the camera and displace it with the browser's 12 Gerstner waves (waves.js waveDisp: Lagrangian
    point, horizontal displacement Q A cos, height A sin; waves shorter than ~4 vertex spacings are faded out)."""
    L = ['float2 xz = (cam.xy + wp.xy) * 0.01;   // lattice (Lagrangian) point, browser x / z, metres',
         'float sp = uv.x;                        // local grid spacing of this vertex (m)',
         'float3 o = float3(0.0, 0.0, 0.0); float th, s, c, fd;']
    for w in WAVES:
        L.append('th = %.7f * (%.7f * xz.x + %.7f * xz.y) - %.7f * tt + %.5f; sincos(th, s, c); fd = 1.0 - smoothstep(0.18, 0.3, sp * %.7f);'
                 % (w['k'], w['dx'], w['dz'], w['w'], w['ph'], 1.0 / w['L']))
        L.append('o.xz += %.7f * fd * float2(%.7f, %.7f) * c; o.y += %.5f * fd * s;' % (w['Q'] * w['A'], w['dx'], w['dz'], w['A']))
    L.append('// UE: X = browser x, Y = browser z, Z = browser y (cm); the vertex sits at its origin-relative lattice position, the actor at z = WATER_Y')
    L.append('return float3(cam.x + o.x * 100.0, cam.y + o.z * 100.0, o.y * 100.0 + off * 1.0e9);')
    return '\n'.join(L)


PIXEL_HEAD = r'''
#define NZ(uv) Texture2DSample(tNoise, tNoiseSampler, uv)
#define WN(uv) (Texture2DSample(tRip, tRipSampler, uv).rg * 2.0 - 1.0)
float2 p = wpos.xy * 0.01;                                   // browser x / z, metres
float3 dv = cam - wpos; float dcm = max(length(dv), 1.0); float dist = dcm * 0.01;
float t = tt;
float2 dpx = ddx(p), dpy = ddy(p);
float foot = max(length(abs(dpx) + abs(dpy)), 1e-4);         // pixel footprint on the water (m)
// ---- sea detail: wind-aligned gusts, slicks and streaks (water.js river())
float2 wdir = float2(0.642788, -0.766044);
float g1 = NZ(p / 620.0).r;
float g2 = NZ(p / 230.0 + float2(t * 0.0009, 0.37)).g;
float gust = saturate((g1 * 0.62 + g2 * 0.38 - 0.5) * 1.8 + 0.42);
float along = dot(p, wdir), across = dot(p, float2(-wdir.y, wdir.x)) + (g2 - 0.5) * 26.0;
float slk = NZ(float2(along / 900.0, across / 140.0)).g;
float slick = smoothstep(0.5, 0.78, slk) * (1.0 - gust * 0.8) * 0.9;
float stk = NZ(float2(along / 380.0, across / 22.0) + float2(0.13, 0.71)).g;
float brk = NZ(float2(along / 140.0, across / 60.0) + float2(0.51, 0.29)).r;
float streak = smoothstep(0.6, 0.85, stk) * smoothstep(0.35, 0.65, brk) * 0.7;
float s1 = NZ(float2(p.x / 34.0, p.y / 520.0) + float2(t * 0.0008, t * 0.003)).g;
streak = max(streak, smoothstep(0.6, 0.82, s1) * 0.45);
// ---- distance to the shore (8 m/px map, m / 400)
float wShore = 400.0;
{ float2 su = (p - float2(-6400.0, -8000.0)) / float2(12800.0, 17600.0);
  if (su.x > 0.0 && su.y > 0.0 && su.x < 1.0 && su.y < 1.0) wShore = Texture2DSampleLevel(tShore, tShoreSampler, su, 0.0).r * 400.0; }
float nearS = 1.0 - smoothstep(6.0, 70.0, wShore);
slick = saturate(slick + nearS * 0.3);
float rough = lerp(@RLO@, @RHI@, gust) * (1.0 - slick * 0.7) * (1.0 - streak * 0.3);
// ---- the 12 Gerstner waves (analytic slope of the Lagrangian surface, waves smaller than the pixel move into roughness)
float2 sl = float2(0.0, 0.0); float vu = 0.0, hh = 0.0; float th, s, c, kA, fd, den;
// domain warp for the shorter waves: breaks the regular interference contours (wave phase is not tied to the mesh below ~9 m wavelength)
float2 pw = p + (NZ(p / 41.0).rg - 0.5) * 7.0 + (NZ(p / 13.0 + 0.37).gb - 0.5) * 1.6;
'''

PIXEL_TAIL = r'''
float wk = @SLOPEK@ * lerp(0.8, 1.15, gust) * (1.0 - 0.3 * slick);
float2 sl2 = sl * wk; float varU = vu * wk * wk; float wCrest = hh / @HALFMAX@;
// ---- capillary chop: three normal layers, faded by the pixel footprint
float2 pr1 = float2(0.829 * p.x + 0.559 * p.y, -0.559 * p.x + 0.829 * p.y);
float fd1 = 1.0 - smoothstep(0.04, 0.35, foot), fd2 = 1.0 - smoothstep(0.15, 1.2, foot);
float across0 = dot(p, float2(-wdir.y, wdir.x));                      // un-warped across-wind coordinate for the ripple textures
float2 dn = WN(float2(along - t * 0.55, across0) / float2(2.6, 7.5)) * 0.13 * fd1                      // wind ripples: crests across the wind, drifting downwind
          + WN(float2(along - t * 0.35 + 3.7, across0 + 11.0) / float2(4.4, 12.0)) * 0.11 * fd1
          + WN(pr1 / 9.0 + float2(t * 0.012, -t * 0.009)) * 0.12 * fd2
          + WN(float2(p.y, -p.x) / 21.0 + float2(t * 0.006, t * 0.008)) * 0.09;
dn *= rough * @DNK@;
varU += (0.009 * (1.0 - fd1) + 0.004 * (1.0 - fd2)) * rough * rough * @DNK@ * @DNK@;
float2 slope = sl2 + dn;
// ---- foam: contact with the walls (2 m/px signed distance map, +-16 m), streaks, whitecaps
float foam = 0.0;
float cd = 1000.0;
{ float2 cu = (p - float2(-1800.0, -4300.0)) / float2(3800.0, 8800.0);
  if (cu.x > 0.0 && cu.y > 0.0 && cu.x < 1.0 && cu.y < 1.0)
    cd = (Texture2DSampleLevel(tContact, tContactSampler, cu, max(log2(foot * 0.5), 0.0)).r - 0.5) * 32.0; }
if (cd < 15.0) {
  float dd = max(cd, 0.0);
  float fn = NZ(p / 7.0 + float2(t * 0.01, -t * 0.007)).b;
  float lap = 0.55 + 0.225 * sin(dot(p, float2(0.11, -0.17)) + t * 1.1) + 0.35 * wCrest;   // water sloshing against the wall
  float cf = 1.0 - smoothstep(0.1, 0.5 + 1.7 * fn + 0.9 * lap, dd);
  foam = max(foam, cf * (0.3 + 0.45 * lap) * smoothstep(0.25, 0.6, NZ(p / 3.1 + float2(-t * 0.02, t * 0.013)).r + 0.25 * lap) * (1.0 - smoothstep(400.0, 1800.0, dist)));
  wShore = min(wShore, dd);
}
foam = max(foam, (streak * 0.12 * smoothstep(0.4, 1.0, gust + 0.3) + smoothstep(0.62, 0.95, wCrest) * gust * 0.35) * @FOAMK@);
float fcov = saturate(foam);
float fa = NZ(p / 1.9 + float2(t * 0.004, 0.0)).r, fb = NZ(p / 0.63 + float2(0.0, t * 0.006)).g;
float fpat = smoothstep(1.05 - fcov, 1.3 - fcov, fa * 0.62 + fb * 0.5) * smoothstep(0.0, 0.25, fcov);
float wFoam = fpat * (1.0 - smoothstep(600.0, 2500.0, dist)) + fcov * 0.35 * smoothstep(300.0, 2500.0, dist);
// ---- normal + GGX roughness (Cox-Munk unresolved capillaries + variance of the filtered waves)
float3 Nw = normalize(float3(-slope.x, -slope.y, 1.0));
// masking / shadowing + multiple scattering: a facet that would reflect the view ray back into the water reflects the sky instead
// (Lumen would trace that ray downward into nothing = a dark, noisy river at grazing angles): bend the normal until R points above the horizon
{ float3 Vv = dv / dcm; float3 Rr = reflect(-Vv, Nw); float wl = saturate((0.05 - Rr.z) * 8.0);
  Nw = normalize(lerp(Nw, float3(0.0, 0.0, 1.0), wl));
  Rr = reflect(-Vv, Nw); wl = saturate((0.03 - Rr.z) * 12.0); Nw = normalize(lerp(Nw, float3(0.0, 0.0, 1.0), wl)); }
float mss = @MSS0@ + @MSS1@ * rough;
float unres = saturate(log2(max(foot, 1e-4) * 110.0 / 3.14159) / 9.0);
float a2 = @A2B@ * @A2B@ + mss * 2.0 * unres + 2.0 * @VARK@ * varU + wFoam * 0.2;
float wR = clamp(pow(a2, 0.25), 0.04, 0.7);
// ---- body colour: turbid Hudson (silty olive-green), browner near the walls where the bed shows through, bluer mid-channel
float3 c0 = float3(@BODY@);
float3 m1 = NZ(p / 900.0 + float2(0.0, t * 0.0015)).rgb;
float3 m2 = NZ(float2(p.x / 260.0, p.y / 1400.0) + float2(0.31, t * 0.004)).rgb;
c0 *= 0.85 + 0.3 * m1.r;
c0 = lerp(c0, c0 * float3(1.12, 1.02, 0.80), smoothstep(0.4, 0.8, m2.b) * 0.5);
c0 = lerp(c0, c0 * float3(1.10, 1.05, 0.85), nearS * 0.55);
c0 *= lerp(float3(1.0, 1.0, 1.0), float3(0.85, 0.95, 1.08), smoothstep(150.0, 400.0, wShore));
c0 *= 1.0 + 0.25 * streak;
float depthM = lerp(1.2, 12.0, smoothstep(0.0, 90.0, wShore));            // Beer-Lambert: sigma_t ~ 0.5 / m, two-way path
c0 = lerp(c0, float3(@BOTTOM@), exp(-depthM) * 0.75);
c0 *= 1.0 - 0.35 * (1.0 - smoothstep(0.05, 0.5, wShore));                    // wet contact line darkens the last decimetres
float fo = saturate(wFoam);
c0 = lerp(c0, float3(@FOAM@), fo);
Rough = lerp(wR, 0.85, fo);
Spec = lerp(@SPEC@, 0.45, fo);
NormalW = normalize(lerp(Nw, float3(0.0, 0.0, 1.0), fo * 0.6));
@DEBUG@
return c0;'''


DEBUG_CODE = {1: 'c0 = float3(0.0, 0.0, 0.0);',                                                         # specular only (sun + Lumen reflections)
              2: 'c0 = float3(0.0, 0.0, 0.0); Rough = 0.08; NormalW = float3(0.0, 0.0, 1.0);',           # flat glossy mirror
              3: 'c0 = float3(0.5, 0.5, 0.5); Rough = 0.5; NormalW = float3(0.0, 0.0, 1.0); Spec = 0.0;',  # flat grey diffuse: lighting probe
              4: 'NormalW = float3(0.0, 0.0, 1.0); Rough = 0.16;',                                       # body-colour fields only (flat normal)
              5: 'c0 = float3(0.048, 0.064, 0.056);',
              6: 'c0 = float3(wR, wR, wR) * 0.5; Spec = 0.0; Rough = 1.0; NormalW = float3(0.0, 0.0, 1.0);',                # roughness map
              7: 'c0 = float3(Nw.x * 0.5 + 0.5, Nw.y * 0.5 + 0.5, 0.0) * 0.3; Spec = 0.0; Rough = 1.0; NormalW = float3(0.0, 0.0, 1.0);'}  # normal xy map                                                   # normals / roughness only (constant body)


def hlsl_pixel():
    """per-pixel water: analytic Gerstner slopes (waves.js waveSlope, footprint filtered, unresolved variance -> roughness) + capillary
    normal layers + sea-detail fields + shore / contact foam (water.js river()), body colour from a turbid medium with silt near the walls"""
    W = []
    for i, w in enumerate(WAVES):
        q = 'p' if w['L'] > 9.0 else 'pw'     # the 3 swells (31 / 16.5 / 11.2 m) keep the true lattice, shorter waves ride a low-frequency domain warp
        W.append('th = %.7f * (%.7f * %s.x + %.7f * %s.y) - %.7f * t + %.5f; sincos(th, s, c);' % (w['k'], w['dx'], q, w['dz'], q, w['w'], w['ph']))
        W.append('kA = %.7f; fd = 1.0 - smoothstep(0.12, 0.35, foot * %.7f); den = max(1.0 - %.7f * kA * s, 0.35);' % (w['k'] * w['A'], w['k'] / math.pi, w['Q']))
        g = '@SWK@' if w['L'] < 5.0 else '1.0'     # the browser's saturated (equal slope per octave) spectrum reads as marbling at 4K: short waves get less slope in the shading
        W.append('sl += float2(%.7f, %.7f) * (kA * c / den) * fd * %s; vu += 0.5 * kA * kA * (1.0 - fd) + 0.5 * kA * kA * fd * (1.0 - %s * %s); hh += %.5f * s;' % (w['dx'], w['dz'], g, g, g, w['A']))
    code = PIXEL_HEAD + '\n'.join(W) + PIXEL_TAIL
    rep = {'@HALFMAX@': '%.5f' % (WAVE_MAX * 0.5), '@BODY@': ', '.join('%.5f' % v for v in TUNE['body']), '@BOTTOM@': ', '.join('%.5f' % v for v in TUNE['bottom']),
           '@FOAM@': ', '.join('%.5f' % v for v in TUNE['foam']), '@SPEC@': '%.4f' % TUNE['spec'], '@SLOPEK@': '%.4f' % TUNE['slope_k'], '@DNK@': '%.4f' % TUNE['dn_k'],
           '@FOAMK@': '%.4f' % TUNE['foam_k'], '@SWK@': '%.4f' % TUNE['sw_k'], '@RLO@': '%.4f' % TUNE['rough_lo'], '@RHI@': '%.4f' % TUNE['rough_hi'], '@MSS0@': '%.5f' % TUNE['mss0'],
           '@MSS1@': '%.5f' % TUNE['mss1'], '@A2B@': '%.5f' % TUNE['a2_base'], '@VARK@': '%.4f' % TUNE['var_k'], '@DEBUG@': DEBUG_CODE.get(int(TUNE.get('debug', 0)), '')}
    for k, v in rep.items(): code = code.replace(k, v)
    left = [w for w in ('@' + x + '@' for x in ('SWK', 'HALFMAX', 'BODY', 'BOTTOM', 'FOAM', 'SPEC', 'SLOPEK', 'DNK', 'FOAMK', 'RLO', 'RHI', 'MSS0', 'MSS1', 'A2B', 'VARK', 'DEBUG')) if w in code]
    if left: raise SystemExit('unreplaced shader placeholders: %s' % left)
    return code


def build_water():
    """the 'water' step, inside Unreal (headless commandlet)"""
    import unreal
    EAL = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary
    at = unreal.AssetToolsHelpers.get_asset_tools()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    T0 = time.time()
    def wlog(*a): print('[build_water %5.0fs]' % (time.time() - T0), *a)
    ROOT = '/Game/Water'; TEX, MAT, MESH, MAPS = ROOT + '/Textures', ROOT + '/Materials', ROOT + '/Meshes', ROOT + '/Maps'
    CITY_GEO = '/Game/Tests/City/City_Midtown_Geo'
    RIG = '/Game/Look/Rigs/Look_Rig_golden'
    RIG_MIDDAY = '/Game/Look/Rigs/Look_Rig_midday'
    load = unreal.load_asset
    for d in (TEX, MAT, MESH, MAPS): EAL.make_directory(d)
    views = json.load(open(os.path.join(DOCS, 'views.json')))['views']
    shots = {sh['id']: sh for sh in json.load(open(os.path.join(HERE, 'city_shots.json')))}
    MISS = []
    unreal.SystemLibrary.execute_console_command(None, 'Module Load StaticMeshEditor')   # StaticMeshEditorSubsystem is None in a commandlet until loaded
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

    # ------------------------------------------------------------------------------------------ textures
    def import_files(files, dest, pipeline=None):
        tasks = []
        for f in files:
            t = unreal.AssetImportTask(); t.filename = f; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = False
            if pipeline: t.options = pipeline
            tasks.append(t)
        at.import_asset_tasks(tasks)
    tdir = os.path.join(WSCR, 'tex')
    names = ['T_WaterNoise', 'T_WaterRipple', 'T_WaterShore', 'T_WaterContact']
    import_files([os.path.join(tdir, n + '.png') for n in names], TEX)
    for n in names:
        t = load('%s/%s' % (TEX, n))
        if not t: MISS.append('texture %s not imported' % n); continue
        t.set_editor_property('srgb', False)
        if n in ('T_WaterNoise', 'T_WaterRipple'):
            t.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)   # uncompressed RGBA8
        else:
            t.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_BC7)
            t.set_editor_property('address_x', unreal.TextureAddress.TA_CLAMP); t.set_editor_property('address_y', unreal.TextureAddress.TA_CLAMP)
        EAL.save_asset('%s/%s' % (TEX, n))
    wlog('textures imported')

    # ------------------------------------------------------------------------------------------ mesh
    p = unreal.InterchangeGenericAssetsPipeline()
    p.common_meshes_properties.set_editor_properties({'recompute_normals': False, 'recompute_tangents': False, 'use_full_precision_u_vs': True,
                                                      'remove_degenerates': False})
    p.mesh_pipeline.set_editor_properties({'generate_lightmap_u_vs': False, 'build_nanite': False})
    p.material_pipeline.set_editor_property('import_materials', False)
    p.material_pipeline.texture_pipeline.set_editor_property('import_textures', False)
    import_files([os.path.join(WSCR, 'WaterGrid.glb')], MESH + '/_in', p)
    dst = MESH + '/SM_WaterGrid'
    src = MESH + '/_in/WaterGrid/StaticMeshes/WaterGrid'
    if EAL.does_asset_exist(src):
        if EAL.does_asset_exist(dst): EAL.delete_asset(dst)
        EAL.rename_asset(src, dst); EAL.delete_directory(MESH + '/_in')
    sm = load(dst)
    if not sm: raise RuntimeError('water grid mesh import failed')
    ns = sm.get_editor_property('nanite_settings')
    if ns.enabled: ns.enabled = False; sm.set_editor_property('nanite_settings', ns)
    bs = sms.get_lod_build_settings(sm, 0)
    bs.set_editor_property('use_full_precision_u_vs', True); bs.set_editor_property('generate_lightmap_u_vs', False)
    bs.set_editor_property('recompute_normals', False); bs.set_editor_property('recompute_tangents', False)
    sms.set_lod_build_settings(sm, 0, bs)
    for prop in ('generate_mesh_distance_field', 'support_ray_tracing'):
        try: sm.set_editor_property(prop, False)
        except Exception as e: wlog('mesh property', prop, 'not settable:', str(e).split('\n')[0][:80])
    try: sms.remove_collisions(sm)
    except Exception as e: MISS.append('remove_collisions: ' + str(e)[:80])
    b = sm.get_bounds()
    wlog('mesh bounds origin', b.origin, 'extent', b.box_extent, 'vertices', sms.get_number_verts(sm, 0))
    EAL.save_asset(dst)

    # ------------------------------------------------------------------------------------------ MPC + material
    if not EAL.does_asset_exist(ROOT + '/MPC_Water'):
        mpc = at.create_asset('MPC_Water', ROOT, unreal.MaterialParameterCollection, unreal.MaterialParameterCollectionFactoryNew())
        sp = unreal.CollectionScalarParameter(); sp.set_editor_property('parameter_name', 'Off'); sp.set_editor_property('default_value', 0.0)
        mpc.set_editor_property('scalar_parameters', [sp]); EAL.save_asset(ROOT + '/MPC_Water')
    MP = unreal.MaterialProperty
    mpath = MAT + '/M_WaterRiver'
    if EAL.does_asset_exist(mpath):
        m = load(mpath); mel.delete_all_material_expressions(m)
    else:
        m = at.create_asset('M_WaterRiver', MAT, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property('tangent_space_normal', False)      # the shader outputs a world-space normal
    m.set_editor_property('two_sided', True)
    m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
    m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_OPAQUE)

    def sampler_for(t): return unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if t.get_editor_property('srgb') else unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR

    def custom(name, code, inputs, outputs, x, y0):
        c = mel.create_material_expression(m, unreal.MaterialExpressionCustom, x, y0)
        c.set_editor_property('code', code); c.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
        c.set_editor_property('description', name)
        ins = []
        for n, kind, arg in inputs:
            ci = unreal.CustomInput(); ci.set_editor_property('input_name', n); ins.append(ci)
        c.set_editor_property('inputs', ins)
        outs = []
        for n, k, _ in outputs[1:]:
            co = unreal.CustomOutput(); co.set_editor_property('output_name', n)
            co.set_editor_property('output_type', [None, unreal.CustomMaterialOutputType.CMOT_FLOAT1, unreal.CustomMaterialOutputType.CMOT_FLOAT2, unreal.CustomMaterialOutputType.CMOT_FLOAT3][k])
            outs.append(co)
        c.set_editor_property('additional_outputs', outs)
        y = y0 - 600
        for n, kind, arg in inputs:
            y += 90
            if kind == 'tex':
                e = mel.create_material_expression(m, unreal.MaterialExpressionTextureObject, x - 500, y)
                t = load(arg); e.set_editor_property('texture', t); e.set_editor_property('sampler_type', sampler_for(t))
            elif kind == 'uv':
                e = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, x - 500, y); e.set_editor_property('coordinate_index', arg)
            elif kind == 'wpos': e = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, x - 500, y)
            elif kind == 'cam': e = mel.create_material_expression(m, unreal.MaterialExpressionCameraPositionWS, x - 500, y)
            elif kind == 'time': e = mel.create_material_expression(m, unreal.MaterialExpressionTime, x - 500, y)
            elif kind == 'mpc':
                e = mel.create_material_expression(m, unreal.MaterialExpressionCollectionParameter, x - 500, y)
                e.set_editor_property('collection', load(ROOT + '/MPC_Water')); e.set_editor_property('parameter_name', arg)
            mel.connect_material_expressions(e, '', c, n)
        for i, (n, k, prop) in enumerate(outputs):
            if prop is not None: mel.connect_material_property(c, '' if i == 0 else n, prop)
        return c
    custom('WaterWPO', hlsl_vertex(), [('wp', 'wpos', None), ('cam', 'cam', None), ('tt', 'time', None), ('uv', 'uv', 0), ('off', 'mpc', 'Off')],
           [('', 3, MP.MP_WORLD_POSITION_OFFSET)], 0, -1400)
    custom('WaterShade', hlsl_pixel(),
           [('wpos', 'wpos', None), ('cam', 'cam', None), ('tt', 'time', None), ('tNoise', 'tex', TEX + '/T_WaterNoise'), ('tRip', 'tex', TEX + '/T_WaterRipple'),
            ('tShore', 'tex', TEX + '/T_WaterShore'), ('tContact', 'tex', TEX + '/T_WaterContact')],
           [('', 3, MP.MP_BASE_COLOR), ('Rough', 1, MP.MP_ROUGHNESS), ('NormalW', 3, MP.MP_NORMAL), ('Spec', 1, MP.MP_SPECULAR)], 0, 0)
    mel.recompile_material(m)
    EAL.save_asset(mpath)
    wlog('material M_WaterRiver built')

    # ------------------------------------------------------------------------------------------ the surface in the city geometry level
    KEEP = ('WorldSettings', 'Brush', 'DefaultPhysicsVolume', 'GameplayDebuggerCategoryReplicator', 'WorldDataLayers', 'WorldPartitionMiniMap')
    unreal.EditorLoadingAndSavingUtils.load_map(CITY_GEO)
    n_old = 0
    for a in eas.get_all_level_actors():
        lab = a.get_actor_label()
        if lab == 'WaterSurface': eas.destroy_actor(a)
        elif lab == 'WaterPlane':      # P1's flat plane stays as the collision floor (tagged WHGround by P4) but stops rendering
            a.set_actor_hidden_in_game(True)
            for c in a.get_components_by_class(unreal.PrimitiveComponent):
                c.set_editor_property('visible', False); c.set_cast_shadow(False)
            n_old += 1
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, WATER_Y * 100.0))
    a.set_actor_label('WaterSurface'); a.set_folder_path('Water')
    c = a.static_mesh_component
    c.set_static_mesh(load(dst)); c.set_material(0, load(mpath))
    c.set_cast_shadow(False)
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    for prop, val in (('affect_distance_field_lighting', False), ('affect_dynamic_indirect_lighting', False), ('cast_dynamic_shadow', False),
                      ('visible_in_ray_tracing', False), ('receives_decals', False), ('cast_contact_shadow', False)):
        try: c.set_editor_property(prop, val)
        except Exception as e: MISS.append('WaterSurface.%s: %s' % (prop, str(e).split('\n')[0][:80]))
    unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), CITY_GEO)
    wlog('City_Midtown_Geo: WaterSurface placed, %d old WaterPlane hidden (kept for collision)' % n_old)

    # ------------------------------------------------------------------------------------------ view maps
    def U(x, y, z): return unreal.Vector(x * 100.0, z * 100.0, y * 100.0)    # browser metres -> UE cm

    def open_level(path):
        if EAL.does_asset_exist(path):
            unreal.EditorLoadingAndSavingUtils.load_map(path)
            for x in eas.get_all_level_actors():
                if x.get_class().get_name() not in KEEP and x.get_path_name().startswith(path + '.'): eas.destroy_actor(x)
        else:
            les.new_level(path)
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

    def add_sublevels(world, rig=None):
        have = [l.get_path_name() for l in unreal.EditorLevelUtils.get_levels(world)]
        for lp in (CITY_GEO, rig or RIG):
            if not any(lp.split('/')[-1] in h for h in have): unreal.EditorLevelUtils.add_level_to_world(world, lp, unreal.LevelStreamingAlwaysLoaded)
        les.set_current_level_by_name(str(world.get_name()))

    def look_rot_pos(p, t):
        d = unreal.Vector(t.x - p.x, t.y - p.y, t.z - p.z)
        return unreal.Rotator(roll=0.0, pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x)))

    def camera(pos, rot, fov, label):
        ca = eas.spawn_actor_from_class(unreal.CameraActor, pos, rot)
        ca.set_actor_label(label)
        ca.camera_component.set_editor_property('field_of_view', fov)
        ca.camera_component.set_editor_property('constrain_aspect_ratio', False)
        ca.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.PLAYER0)
        return ca

    def off_sequence(name, world):
        """MPC_Water.Off = 1 (the wave surface moves away: perf baseline 'no water') through a Level Sequence with an MPC track, like P4's rigs"""
        mpc = load(ROOT + '/MPC_Water')
        seq_path = '%s/LS_%s' % (MAPS, name)
        if EAL.does_asset_exist(seq_path): EAL.delete_asset(seq_path)
        seq = at.create_asset('LS_' + name, MAPS, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
        seq.set_display_rate(unreal.FrameRate(30, 1)); seq.set_playback_start(0); seq.set_playback_end(30 * 600)
        tr = seq.add_track(unreal.MovieSceneMaterialParameterCollectionTrack); tr.set_editor_property('mpc', mpc)
        sec = tr.add_section(); sec.set_range(0, 30 * 600); sec.add_scalar_parameter_key('Off', unreal.FrameNumber(0), 1.0)
        EAL.save_asset(seq_path)
        act = eas.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0, 0, 0)); act.set_actor_label('WaterOff_' + name)
        act.set_editor_property('level_sequence_asset', seq)
        ps = act.get_editor_property('playback_settings'); ps.set_editor_property('auto_play', True)
        ps.set_editor_property('loop_count', unreal.MovieSceneSequenceLoopCount(value=-1)); act.set_editor_property('playback_settings', ps)

    def dolly_sequence(name, cam, v):
        seq_path = '%s/LS_%s' % (MAPS, name)
        if EAL.does_asset_exist(seq_path): EAL.delete_asset(seq_path)
        seq = at.create_asset('LS_' + name, MAPS, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
        fps = 60
        seq.set_display_rate(unreal.FrameRate(fps, 1))
        t0, t1, t2 = v['hold_before_s'], v['hold_before_s'] + v['duration_s'], v['hold_before_s'] + v['duration_s'] + v['hold_after_s']
        seq.set_playback_start(0); seq.set_playback_end(int(t2 * fps) + 60)
        bind = seq.add_possessable(cam)
        tr = bind.add_track(unreal.MovieScene3DTransformTrack)
        sec = tr.add_section(); sec.set_range(0, int(t2 * fps) + 60)
        chans = sec.get_all_channels()
        p0, p1 = U(*v['from']), U(*v['to'])
        rot = cam.get_actor_rotation()
        vals = {0: (p0.x, p1.x), 1: (p0.y, p1.y), 2: (p0.z, p1.z), 3: (rot.roll, rot.roll), 4: (rot.pitch, rot.pitch), 5: (rot.yaw, rot.yaw), 6: (1, 1), 7: (1, 1), 8: (1, 1)}
        for i, ch in enumerate(chans):
            a0, a1 = vals[i]
            for fr, val in ((0, a0), (int(t0 * fps), a0), (int(t1 * fps), a1), (int(t2 * fps) + 60, a1)):
                ch.add_key(unreal.FrameNumber(fr), float(val), 0.0, unreal.MovieSceneTimeUnit.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.LINEAR)
        EAL.save_asset(seq_path)
        act = eas.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0, 0, 0)); act.set_actor_label('Dolly_' + name)
        act.set_editor_property('level_sequence_asset', seq)
        ps = act.get_editor_property('playback_settings'); ps.set_editor_property('auto_play', True); act.set_editor_property('playback_settings', ps)

    def make_map(name, cam_kind, off=False, dolly=False, rig=None):
        path = MAPS + '/' + name
        world = open_level(path)
        add_sublevels(world, rig)
        if cam_kind == 'S4':
            s = shots['S4_perch_skyline']; pp, tt = U(*s['pos']), U(*s['target']); cam = camera(pp, look_rot_pos(pp, tt), s['fov'], 'ShotCam_S4')
        else:
            v = views[cam_kind]
            pp = U(*v['pos']); rot = unreal.Rotator(roll=0.0, pitch=v['pitch_deg'], yaw=v['yaw_compass_deg'] - 90.0)
            cam = camera(pp, rot, v['fov_h_deg'], 'ShotCam_' + cam_kind)
        spawn_ps = eas.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 200.0)); spawn_ps.set_actor_label('PlayerStart')
        if off: off_sequence(name, world)
        if dolly: dolly_sequence(name, cam, views['river_low_dolly'])
        ok = unreal.EditorLoadingAndSavingUtils.save_map(world, path)
        wlog('map', path, 'saved' if ok else 'SAVE FAILED', 'off' if off else '', 'dolly' if dolly else '')
    make_map('Water_View_Low', 'river_low')
    make_map('Water_View_Dolly', 'river_low', dolly=True)
    make_map('Water_View_LowWest', 'river_low_west')
    make_map('Water_View_LowPoly', 'river_low_polygon')
    make_map('Water_View_Low_Midday', 'river_low', rig=RIG_MIDDAY)
    make_map('Water_View_LowWest_Midday', 'river_low_west', rig=RIG_MIDDAY)
    make_map('Water_View_S4', 'S4')
    make_map('Water_View_S4_Off', 'S4', off=True)
    make_map('Water_View_Low_Off', 'river_low', off=True)
    if MISS:
        wlog('WARNINGS (%d):' % len(MISS))
        for x in MISS: print('    ', x)
    wlog('DONE')


def step_water():
    bm = load_manhattan()
    os.makedirs(os.path.join(SCR, 'logs'), exist_ok=True)
    txt = bm.ue_python('water', bm.exec_wrapper(os.path.abspath(__file__), ''))
    for l in txt.splitlines():
        if '[build_water' in l: print(l.split('LogPython: ')[-1])


if IN_UE:
    build_water()
elif __name__ == '__main__':
    main()
