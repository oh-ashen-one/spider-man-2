# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# River water (Hudson / East River around the island): idempotent, headless rebuild of /Game/Water on top of the integrated Manhattan build
# (Scripts/build_manhattan.py). Nothing here is committed as .uasset / .umap (unreal/WebHomage/CONTENT.md).
#
# Two modes in one file (same pattern as build_manhattan.py):
#   * plain python3 (YOUR editor closed; needs numpy + opencv, node):
#         python3 unreal/WebHomage/Scripts/build_water.py [--steps inputs,ue]
#       inputs   generated sources into $SM2_WATER_SCR (default /Users/midir/sm2-n1/_scratch/water):
#                  water_grid.glb   camera-centred polar grid, 384 segments x ~540 rings (0.1 m at the centre, +2 % per ring, 80 km radius)
#                  water_noise.png  4 tileable band-limited noise channels (gusts / slicks / streaks / foam cells / glitter facets)
#                  shore_dist.png   distance (m, 0..400 -> 0..255) from every water point to the nearest land, 8 m/px, from the browser's
#                                   own land polygons (tools/water/dump_shores.mjs: layout.js LAND_POLY + farshore.js FAR_LANDS)
#                  water_slope.png  (r02) tileable random-phase wind-sea slope spectrum, 2 realizations (tools/water/water_inputs.py)
#                  water_contact.png + .json  (r02) distance to the nearest place where the city export's geometry crosses the water plane
#                                   (seawalls, bulkheads, pier piles, bridge piers), island shore box, ~0.9 m/px; export = $SM2_WATER_EXPORT
#                                   (else $SM2_CITY_EXPORT / the Manhattan build's export)
#       ue       headless commandlet (-nullrhi) running this file inside Unreal
#   * inside Unreal (-run=pythonscript -script=<this file>):
#       /Game/Water/Textures/T_WaterNoise, T_ShoreDist, /Game/Water/Meshes/SM_WaterGrid
#       /Game/Water/Materials/M_RiverWater   Single Layer Water material:
#           vertex: the browser's 12 Gerstner waves (src/world/waves.js, same constants), evaluated at the camera-centred grid vertex
#                   (grid follows the camera through WPO; waves shorter than ~4 grid spacings fade out exactly like waves.js waveDisp)
#           pixel:  (r02) analytic slopes of the 5 longest waves + 4 layers of the baked wind-sea slope spectrum (rotated, scrolled at
#                   their phase speed; mip bias +1), filtered by the pixel footprint (resolved -> normal, unresolved slope variance ->
#                   roughness, Cox-Munk), facets whose reflection would point below the horizon bent up, wind gust / slick / streak fields,
#                   contact foam where the surface meets geometry crossing the water line (baked contact map + SceneDepthWithoutWater), sparse whitecaps,
#                   sun glitter facets (emissive, sun = SkyAtmosphere light 0), turbid-river optics as SLW scattering / absorption
#                   coefficients (olive-grey Hudson, siltier within ~100 m of the shore)
#       /Game/Water/Maps/Water_River        sublevel with the water actor (no shadows, not in Lumen scene / ray tracing, no collision)
#       P1's flat WaterPlane in /Game/Tests/City/City_Midtown_Geo is hidden (collision kept: it is still the traversal floor)
#       Water_River is added (always loaded) to /Game/Maps/Manhattan, _Midday, _Night, _View_S1|S2|S4
#       /Game/Water/Maps/Water_View_RiverLow[_Midday]   golden / midday + the low river camera (docs/night1/water/views.json)
#       /Game/Water/Maps/Water_View_RiverLow_Dolly      same camera on an InterpToMovement dolly (16 s, 2 m/s, at the view point at t = 6 s)
#       /Game/Water/Maps/Water_Perf_<RiverLow|S4|RiverSun>_Base  perf baseline: same view, P1's old flat water instead of this water
#       (r02) /Game/Water/Maps/Water_View_RiverSun[_Dolly], Water_View_HarbourHigh, (r04) Water_View_HarbourSunHigh; /Game/Maps/Manhattan_WP (island piece) gets the water
#       actor directly (not spatially loaded); tuning variants: SM2_WATER_VARIANTS='{"A": {"ChopK": 1.4, "_views": ["river_sun"]}}' ->
#       /Game/Water/Variants/MI_Water_A + Water_Var_A_<view>. Material scalar parameters: PARAMS below (+ GlitterK, Dbg).
import os, sys, json, math, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/Users/midir/sm2-n1/water-ab-opus/unreal/WebHomage/Scripts'
PROJ = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(PROJ))
UPROJECT = os.path.join(PROJ, 'WebHomage.uproject')
UE = '/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
SCR = os.environ.get('SM2_WATER_SCR', '/Users/midir/sm2-n1/_scratch/water')
VIEWS_JSON = os.path.join(WT, 'docs', 'night1', 'water', 'views.json')
STEPS_ALL = ['inputs', 'contactb', 'ue']
GPU_SLOT = '/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh'   # every Unreal launch goes through the GPU lock (RULES.md)

WATER_Y = -1.6                                  # browser G.WATER_Y (m)
SHORE_BOX = (-6400.0, -8000.0, 12800.0, 17600.0)  # x0, z0, w, h (browser metres; UE X = x, Y = z)
SHORE_PX = 8.0
GRID_SEG, GRID_R0, GRID_DR0, GRID_G, GRID_R1 = 384, 4.0, 0.1, 1.02, 80000.0

# ---------------------------------------------------------------------------------------------------- waves (src/world/waves.js)
GRAV = 9.81
# [wavelength m, amplitude m, direction deg (0 = +x, 90 = +z), steepness q, phase]   (wind toward the north-east: -50 deg)
SPEC = [
    [31.0, 0.06, -38, 0.2, 0.0], [16.5, 0.055, -62, 0.35, 5.1], [11.2, 0.065, -24, 0.45, 1.7], [7.9, 0.05, -83, 0.5, 4.1],
    [5.6, 0.042, -47, 0.55, 2.3], [4.3, 0.03, -2, 0.5, 3.9], [3.3, 0.026, -71, 0.55, 5.6], [2.45, 0.019, -28, 0.5, 0.9],
    [1.8, 0.014, -104, 0.45, 3.3], [1.33, 0.01, -52, 0.4, 6.0], [0.97, 0.0072, 8, 0.35, 2.0], [0.71, 0.005, -66, 0.3, 4.6],
]
def waves():
    out = []
    for L, A, dd, q, ph in SPEC:
        k = 2 * math.pi / L; d = math.radians(dd)
        out.append(dict(L=L, A=A, k=k, w=math.sqrt(GRAV * k), dx=math.cos(d), dy=math.sin(d), Q=q / (k * A * len(SPEC)), ph=ph))
    return out
WAVE_MAX = sum(w[1] for w in SPEC)
VAR_K = 1.2   # filtered slope variance -> GGX alpha^2 (Cox-Munk: alpha^2 ~ 2 sigma^2 per axis; 1.2 keeps the far river glossy)
# round 02: wind-sea slope spectrum layers (T_WaterSlope, tools/water/water_inputs.py) replace the 12 capillary sinusoids:
#   [tile size m, angle of realization A / B to the wind (deg), RMS slope per axis]   bands: tile/24 .. tile/3
# r03: the 0.73 m layer is replaced by the resolved wind-chop layer (CHOP); per-axis RMS slopes before ChopK
LAYERS = [(21.0, 8.0, -47.0, 0.040), (6.7, -19.0, 38.0, 0.045), (2.2, 27.0, -33.0, 0.050)]
# r04 far-field long-wave layer: 64 m tile (bands 2.7 to 21 m), one realization, sampled with true gradients at every distance (resolved
# from swing height out past 3 km: not folded into roughness). [tile m, angle to the wind deg, per-axis RMS slope before ChopK]
LONG = (64.0, -12.0, 0.035)
LONG_FAR = (100.0, 300.0)   # LongK (far long-wave gain on the 64 m and 21 m layers) ramps in over this distance range (m)
# r03 wind chop (T_WaterChop, 3..10 cycles per tile): [tile m, angle to the wind deg, scroll speed factor] for the two realizations
# (two scroll directions); per-axis RMS slope CHOP_RMS * ChopK * MicroK, resolved (no roughness) within NEAR_M of the camera
CHOP = [(1.5, 28.0, 1.0), (1.17, -36.0, 1.13)]
CHOP_RMS = 0.065
NEAR_M = 150.0        # r03: near field (two realizations, chop layer, foam, contact map); beyond: one realization, no foam
PS_WAVE_MIN_L = 5.5   # analytic Gerstner slopes in the pixel shader: only the waves >= 5.5 m (the vertex geometry); shorter = spectrum layers
WIND_DEG = -50.0
SLOPE_ENC = 6.0       # water_inputs.SLOPE_ENC
CONTACT_MAX = 32.0    # water_inputs.CONTACT_MAX
WIND = (math.cos(math.radians(WIND_DEG)), math.sin(math.radians(WIND_DEG)))


# ================================================================================================ orchestrator (plain python3)
def log(*a):
    print('[build_water %s]' % time.strftime('%H:%M:%S'), *a, flush=True)


def step_inputs():
    import numpy as np, cv2
    sys.path.insert(0, os.path.join(WT, 'tools', 'export'))
    import glbio
    os.makedirs(SCR, exist_ok=True)
    # ---- polar grid (glTF: y up; x east, z south). Rings: uniform 0.1 m to 4 m, then +2 % per ring to 80 km.
    radii = [GRID_DR0 * j for j in range(1, int(round(GRID_R0 / GRID_DR0)) + 1)]
    while radii[-1] < GRID_R1: radii.append(radii[-1] * GRID_G)
    R = np.array(radii); th = np.arange(GRID_SEG) * 2 * math.pi / GRID_SEG
    P = np.zeros((1 + len(R) * GRID_SEG, 3))
    P[1:, 0] = (R[:, None] * np.cos(th)[None, :]).reshape(-1)
    P[1:, 2] = (R[:, None] * np.sin(th)[None, :]).reshape(-1)
    vid = lambda j, a: 1 + j * GRID_SEG + (a % GRID_SEG)
    tris = []
    a = np.arange(GRID_SEG)
    tris.append(np.stack([np.zeros(GRID_SEG, int), vid(0, a + 1), vid(0, a)], 1))  # centre fan
    for j in range(len(R) - 1):
        A_, B_, C_, D_ = vid(j, a), vid(j + 1, a), vid(j + 1, a + 1), vid(j, a + 1)
        tris.append(np.stack([A_, D_, B_], 1)); tris.append(np.stack([D_, C_, B_], 1))
    I = np.concatenate(tris)
    e1, e2 = P[I[:, 1]] - P[I[:, 0]], P[I[:, 2]] - P[I[:, 0]]
    ny = np.cross(e1, e2)[:, 1]
    assert (ny > 0).all(), 'grid winding: %d faces point down' % int((ny <= 0).sum())
    N = np.zeros_like(P); N[:, 1] = 1.0
    UV = np.zeros((len(P), 2))
    glbio.write_glb(os.path.join(SCR, 'water_grid.glb'), {'POSITION': P, 'NORMAL': N, 'TEXCOORD_0': UV}, I.reshape(-1), name='SM_WaterGrid')
    log('grid: %d rings (r %.1f m .. %.0f m), %d verts, %d tris' % (len(R), R[0], R[-1], len(P), len(I)))
    # ---- tileable band-limited noise, 4 channels, ~N(0.5, 0.17) clipped to [0, 1]
    rng = np.random.default_rng(1729); S = 512
    fy, fx = np.meshgrid(np.fft.fftfreq(S) * S, np.fft.fftfreq(S) * S, indexing='ij'); f = np.hypot(fx, fy)
    chans = []
    for lo, hi in ((2, 16), (4, 32), (8, 64), (16, 128)):
        w = rng.standard_normal((S, S))
        band = ((f >= lo) & (f <= hi)) / np.maximum(f, 1)
        n = np.real(np.fft.ifft2(np.fft.fft2(w) * band)); n = (n - n.mean()) / n.std()
        chans.append(np.clip(0.5 + 0.17 * n, 0, 1))
    rgba = (np.stack(chans, -1) * 255 + 0.5).astype(np.uint8)
    cv2.imwrite(os.path.join(SCR, 'water_noise.png'), rgba[..., [2, 1, 0, 3]])  # cv2 writes BGRA
    # ---- shore distance map
    shores = os.path.join(SCR, 'shores.json')
    r = subprocess.run(['node', os.path.join(WT, 'tools', 'water', 'dump_shores.mjs'), shores], cwd=WT, capture_output=True, text=True)
    if r.returncode: raise SystemExit('dump_shores failed: ' + r.stderr[-800:])
    lands = json.load(open(shores))['lands']
    x0, z0, W, H = SHORE_BOX; nw, nh = int(W / SHORE_PX), int(H / SHORE_PX)
    land = np.zeros((nh, nw), np.uint8)
    for L in lands:
        pts = np.array([[(max(-1e5, min(1e5, x)) - x0) / SHORE_PX, (max(-1e5, min(1e5, z)) - z0) / SHORE_PX] for x, z in L['pts']])
        cv2.fillPoly(land, [np.round(pts * 16).astype(np.int32)], 255, lineType=cv2.LINE_8, shift=4)
    dist = cv2.distanceTransform((land == 0).astype(np.uint8), cv2.DIST_L2, 5) * SHORE_PX
    # r03: resampled to 2048^2 (power of two -> the texture gets mips; r02 sampled the NPOT map at level 0 = cache thrash at distance)
    sd = cv2.resize(np.clip(dist / 400.0 * 255 + 0.5, 0, 255).astype(np.float32), (2048, 2048), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(SCR, 'shore_dist.png'), np.clip(sd + 0.5, 0, 255).astype(np.uint8))
    log('shore map %dx%d (%.0f %% water), noise %dx%d' % (nw, nh, (land == 0).mean() * 100, S, S))
    # ---- round 02: wind-sea slope spectrum + contact-distance map (tools/water/water_inputs.py)
    sys.path.insert(0, os.path.join(WT, 'tools', 'water'))
    import water_inputs
    st = water_inputs.slope_texture(os.path.join(SCR, 'water_slope.png'))
    log('slope spectrum texture', st)
    log('wind-chop texture (r03)', water_inputs.chop_texture(os.path.join(SCR, 'water_chop.png')))
    exp = export_dir()
    cm = water_inputs.contact_map(exp, os.path.join(SCR, 'water_contact.png'))
    json.dump(dict(cm, export=exp), open(os.path.join(SCR, 'water_contact.json'), 'w'), indent=1)
    log('contact map from %s: box %s, %.2f m/px, %d segments, %d files' % (exp, [round(v, 1) for v in cm['box']], cm['px'], cm['segments'], len(cm['files'])))


def step_contactb():
    """r05: a half-resolution copy of the contact map (2048 x 4096, ~1.1 x 1.8 m/px) for the import-path diagnosis (Dbg 9): T_WaterContactB
    (Interchange, NeverStream) and T_WaterContactC (legacy TextureFactory) are imported from it; the material picks one with CSel"""
    import numpy as np, cv2
    im = cv2.imread(os.path.join(SCR, 'water_contact.png'), cv2.IMREAD_UNCHANGED)
    h, w = im.shape
    b = cv2.resize(im.astype(np.float32), (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(SCR, 'water_contact_b.png'), np.clip(b + 0.5, 0, 255).astype(np.uint8))
    log('contact map B %dx%d from %dx%d' % (w // 2, h // 2, w, h))


def export_dir():
    """the city export whose geometry defines the contact (water line) map: $SM2_WATER_EXPORT, else the export the Manhattan build used"""
    for c in (os.environ.get('SM2_WATER_EXPORT'), os.environ.get('SM2_CITY_EXPORT'),
              os.path.join(os.environ.get('SM2_MANHATTAN_SCR', ''), 'export', 'midtown3x3') if os.environ.get('SM2_MANHATTAN_SCR') else None,
              os.path.join(SCR, 'manhattan', 'export', 'midtown3x3')):
        if c and os.path.exists(os.path.join(c, 'manifest.json')): return c
    raise SystemExit('no city export found for the contact map: set SM2_WATER_EXPORT=<export dir with manifest.json>')


def step_ue():
    if subprocess.run(['pgrep', '-f', UPROJECT], capture_output=True).returncode == 0:
        raise SystemExit('an Unreal process of this worktree is running; stop it first')
    n = 0
    while int(subprocess.run("pgrep -f '^%s( |$)' | wc -l" % UE, shell=True, capture_output=True, text=True).stdout.strip() or 0) >= 3:
        if n % 12 == 0: log('3+ Unreal instances running, waiting')
        n += 1; time.sleep(5)
    os.makedirs(os.path.join(SCR, 'logs'), exist_ok=True)
    # r02: start from an empty /Game/Water on disk. Rebuilding M_RiverWater in place (delete_all_material_expressions + new graph) compiled
    # in a fresh project but left a material that failed to compile for SF_METAL_SM6 on every later rebuild (default material in game).
    cw = os.path.realpath(os.path.join(PROJ, 'Content', 'Water'))
    if not cw.startswith(os.path.realpath(WT) + '/'): raise SystemExit('refusing to delete ' + cw)
    if os.path.isdir(cw):
        import shutil; shutil.rmtree(cw); log('removed', cw)
    lg = os.path.join(SCR, 'logs', 'water_ue.log')
    t0 = time.time()
    with open(lg + '.stdout', 'w') as so:
        r = subprocess.run([GPU_SLOT, 'capture', '--label', 'water', '--', UE, UPROJECT, '-run=pythonscript', '-script=' + os.path.abspath(__file__), '-unattended', '-nullrhi', '-nosplash',
                            '-RenderOffScreen', '-NoSound', '-NoCrashReports', '-abslog=' + lg], env={**os.environ, 'SM2_WATER_SCR': SCR},
                           stdout=so, stderr=subprocess.STDOUT, timeout=5400)
    txt = open(lg, errors='replace').read() if os.path.exists(lg) else ''
    bad = [l for l in txt.splitlines() if 'LogPython: Error' in l or 'Traceback' in l]
    for l in txt.splitlines():
        if '[water' in l: print(l.split('LogPython: ')[-1])
    log('UE commandlet: rc %d, %.0f s, %d python error lines (log %s)' % (r.returncode, time.time() - t0, len(bad), lg))
    if bad:
        print('\n'.join(bad[:40])); raise SystemExit('python error in the water build')


def main():
    import argparse
    ap = argparse.ArgumentParser(description='River water: /Game/Water on top of the Manhattan build (headless)')
    ap.add_argument('--steps', default=','.join(STEPS_ALL))
    a = ap.parse_args()
    for s in STEPS_ALL:
        if s in a.steps.split(','):
            log('=== step', s); globals()['step_' + s]()


# ================================================================================================ inside Unreal
def hlsl_vs():
    """WPO of the camera-centred grid: grid translation + Gerstner displacement (waves.js waveDisp); extra output Lag (m) -> vertex interpolator -> pixel shader"""
    c = ['float2 cam = Cam.xy * 0.01;', 'float2 rel = WPos.xy * 0.01;', 'float2 lag = rel + cam;',
         'float sp = max(%.3f, %.4f * length(rel));' % (GRID_DR0 * 0.8, GRID_G - 1.0), 'float3 o = 0; float s, c, a;']
    for w in waves():
        c.append('sincos(%.6f * dot(float2(%.6f, %.6f), lag) - %.6f * T + %.4f, s, c); a = %.6f * (1.0 - smoothstep(0.18, 0.3, sp / %.4f)); '
                 'o.xy += %.6f * a * float2(%.6f, %.6f) * c; o.z += a * s;' % (w['k'], w['dx'], w['dy'], w['w'], w['ph'], w['A'], w['L'], w['Q'], w['dx'], w['dy']))
    c += ['float3 h3 = frac(float3(rel.xyx) * 0.1031 * 7.31); h3 += dot(h3, h3.yzx + 33.33);', 'Lag = float3(lag, frac((h3.x + h3.y) * h3.z));', 'return float3((cam + o.xy) * 100.0, o.z * 100.0);']
    return '\n'.join(c)


def hlsl_ps():
    """round 03: the 5 longest Gerstner waves analytically (they match the vertex geometry) + 3 layers of the baked random-phase wind-sea slope
    spectrum (T_WaterSlope, 21 / 6.7 / 2.2 m tiles) + the resolved 0.15-0.5 m wind-chop layer (T_WaterChop, two realizations scrolling in two
    directions). Near field (<= NEAR_M): both realizations, the chop, contact / whitecap foam; textures sampled with their true gradients (no
    mip bias) and the BRDF roughness stays <= 0.08 (r02 turned mip-biased variance into roughness ~0.4 here: the flat look). Beyond NEAR_M:
    one realization per layer, no chop sample (its variance -> GGX roughness x FarVarK), no foam, no contact-map lookup (perf)."""
    CONTACT = json.load(open(os.path.join(SCR, 'water_contact.json')))
    W = [w for w in waves() if w['L'] >= PS_WAVE_MIN_L]
    big = '\n'.join('sincos(%.6f * dot(float2(%.6f, %.6f), p) - %.6f * t + %.4f, s, c); f = 1.0 - smoothstep(0.12, 0.35, foot * %.6f); '
                    'sl2 += float2(%.6f, %.6f) * (%.6f * c / max(1.0 - %.6f * s, 0.35)) * f; varU += %.8f * (1.0 - f); h += %.6f * s;'
                    % (w['k'], w['dx'], w['dy'], w['w'], w['ph'], w['k'] / math.pi, w['dx'], w['dy'], w['k'] * w['A'], w['Q'] * w['k'] * w['A'],
                       0.5 * (w['k'] * w['A']) ** 2, w['A']) for w in W)
    def rot(c, s_): return 'float2(%.6f, %.6f)' % (c, s_), 'float2(%.6f, %.6f)' % (-s_, c)
    lay = []
    for i, (sc, aA, aB, amp) in enumerate(LAYERS):
        lc = sc / 8.5
        kc = 2 * math.pi / lc
        spd = math.sqrt(GRAV / kc + 7.28e-5 * kc)
        tA, tB = math.radians(WIND_DEG + aA), math.radians(WIND_DEG + aB)
        cA, sA, cB, sB = math.cos(tA), math.sin(tA), math.cos(tB), math.sin(tB)
        sc2 = sc * 0.87
        uA, vA = rot(cA, sA); uB, vB = rot(cB, sB)
        lay.append(('{ float2 qa = float2(dot(p, %(uA)s), dot(p, %(vA)s)) / %(sc).4f - float2(%(va).6f * t, 0.0);\n'
                    '  float2 ga = (Texture2DSampleGrad(tW, tWSampler, qa, float2(dot(dpx, %(uA)s), dot(dpx, %(vA)s)) / %(sc).4f, float2(dot(dpy, %(uA)s), dot(dpy, %(vA)s)) / %(sc).4f).rg - 0.5) * %(enc).2f;\n'
                    '  ga = float2(ga.x * %(cA).6f - ga.y * %(sA).6f, ga.x * %(sA).6f + ga.y * %(cA).6f);\n'
                    '  float2 g = ga * waR;\n'
                    '  [branch] if (nearW > 0.0) {\n'
                    '    float2 qb = float2(dot(p, %(uB)s), dot(p, %(vB)s)) / %(sc2).4f - float2(%(vb).6f * t, 0.0) + float2(0.37, %(off).3f);\n'
                    '    float2 gb = (Texture2DSampleGrad(tW, tWSampler, qb, float2(dot(dpx, %(uB)s), dot(dpx, %(vB)s)) / %(sc2).4f, float2(dot(dpy, %(uB)s), dot(dpy, %(vB)s)) / %(sc2).4f).ba - 0.5) * %(enc).2f;\n'
                    '    g += float2(gb.x * %(cB).6f - gb.y * %(sB).6f, gb.x * %(sB).6f + gb.y * %(cB).6f) * wbR; }\n'
                    '  slT += g * %(amp).5f%(lk)s; varL += %(amp2).7f * saturate(log2(2.0 * foot / %(lmin).5f) / 3.0); }')
                   % dict(uA=uA, vA=vA, uB=uB, vB=vB, cA=cA, sA=sA, cB=cB, sB=sB, sc=sc, sc2=sc2, va=spd / sc, vb=spd * 1.07 / sc2, off=0.61 * (i + 1),
                          enc=SLOPE_ENC, amp=amp, amp2=amp * amp, lmin=sc2 / 24.0, lk=' * lk' if sc >= 20.0 else (' * lm' if sc >= 5.0 else '')))
    sc, ang, amp = LONG
    lc = sc / 8.5; kc = 2 * math.pi / lc; spd = math.sqrt(GRAV / kc + 7.28e-5 * kc)
    th = math.radians(WIND_DEG + ang); cL, sL = math.cos(th), math.sin(th); uL, vL = rot(cL, sL)
    longc = ('{ float2 q = float2(dot(p, %(u)s), dot(p, %(v)s)) / %(sc).4f - float2(%(vv).6f * t, 0.53);\n'
             '  float2 g = (Texture2DSampleGrad(tW, tWSampler, q, float2(dot(dpx, %(u)s), dot(dpx, %(v)s)) / %(sc).4f, float2(dot(dpy, %(u)s), dot(dpy, %(v)s)) / %(sc).4f).ba - 0.5) * %(enc).2f;\n'
             '  slL = float2(g.x * %(c).6f - g.y * %(s).6f, g.x * %(s).6f + g.y * %(c).6f) * %(amp).5f; }'
             % dict(u=uL, v=vL, sc=sc, vv=spd / sc, enc=SLOPE_ENC, c=cL, s=sL, amp=amp))
    chop = []
    for j, (sc, ang, vf) in enumerate(CHOP):
        lc = sc / 5.5; kc = 2 * math.pi / lc
        spd = math.sqrt(GRAV / kc + 7.28e-5 * kc) * vf
        th = math.radians(WIND_DEG + ang); c_, s_ = math.cos(th), math.sin(th); u, v = rot(c_, s_)
        ch = 'rg' if j == 0 else 'ba'
        chop.append(('{ float2 q = float2(dot(p, %(u)s), dot(p, %(v)s)) / %(sc).4f - float2(%(vv).6f * t, %(off).3f);\n'
                     '    float2 g = (Texture2DSampleGrad(tK, tKSampler, q, float2(dot(dpx, %(u)s), dot(dpx, %(v)s)) / %(sc).4f, float2(dot(dpy, %(u)s), dot(dpy, %(v)s)) / %(sc).4f).%(ch)s - 0.5) * %(enc).2f;\n'
                     '    slC += float2(g.x * %(c).6f - g.y * %(s).6f, g.x * %(s).6f + g.y * %(c).6f); lostC += 0.5 * saturate(log2(2.0 * foot / %(lmin).5f) / 1.74); }')
                    % dict(u=u, v=v, sc=sc, vv=spd / sc, off=0.29 * (j + 1), ch=ch, enc=SLOPE_ENC, c=c_, s=s_, lmin=sc / 10.0))
    return PS_TEMPLATE % dict(wx=WIND[0], wy=WIND[1], sx=SHORE_BOX[0], sz=SHORE_BOX[1], sw=SHORE_BOX[2], sh=SHORE_BOX[3], big=big, lay='\n'.join(lay),
                              chop='\n    '.join(chop), crms=CHOP_RMS, near=NEAR_M, longc=longc, lf0=LONG_FAR[0], lf1=LONG_FAR[1],
                              hmax=WAVE_MAX * 0.5, ss='%(SCAT)s', sa='%(ABS)s', cx=CONTACT['box'][0], cz=CONTACT['box'][1], cw=CONTACT['box'][2],
                              ch=CONTACT['box'][3], cmax=CONTACT_MAX)


PS_TEMPLATE = r'''
#define NZG(uv, s) Texture2DSampleGrad(tN, tNSampler, (uv), dpx * (s), dpy * (s))
float2 p = Lag.xy; float t = T;
float3 wp = WPos * 0.01, cm = Cam * 0.01;
float3 Vv = cm - wp; float dist = length(Vv); float3 V = Vv / max(dist, 1e-3);
float2 dpx = ddx(p), dpy = ddy(p);
float foot = max(length(abs(dpx) + abs(dpy)), 1e-4);
// r03: near field (<= %(near).0f m): two realizations per layer, the resolved wind chop, foam, contact map; beyond: one realization
float nearW = 1.0 - smoothstep(%(near).1f * 0.73, %(near).1f, dist);
float wbR = 0.70711 * nearW, waR = sqrt(1.0 - wbR * wbR);
// ---- wind gusts (broad, wind-aligned patches of rougher water). r03: wind-streak and slick terms deleted (pale comet streaks)
float2 wdir = float2(%(wx).6f, %(wy).6f);
float4 nA = NZG(p / 620.0, 1.0 / 620.0), nB = NZG(p / 230.0 + float2(t * 0.0009, 0.37), 1.0 / 230.0);
float gust = saturate((nA.r * 0.62 + nB.g * 0.38 - 0.5) * 2.4 + 0.5);
// r04: far-field long-wave gain (LongK on the 64 m and 21 m layers beyond ~%(lf0).0f m) and 'looking down' weight (camera above the water:
//      the far field is seen at steep angles, so its resolved long waves and a sharper lobe carry the structure instead of roughness)
float2 su = (p - float2(%(sx).1f, %(sz).1f)) / float2(%(sw).1f, %(sh).1f);
float shore = (all(su > 0.0) && all(su < 1.0)) ? Texture2DSampleGrad(tS, tSSampler, su, dpx / float2(%(sw).1f, %(sh).1f), dpy / float2(%(sw).1f, %(sh).1f)).r * 400.0 : 400.0;
// r05: the far-field gains fade out within ShoreCalm m of land: sheltered water along the island stays calm enough to mirror it (r03's
//      island reflections, lost to LongK 3 in r04)
float down = smoothstep(0.08, 0.25, V.z);
// final hold 1: at river level the calm also flattened the 100-300 m rows of the river_low near crop (hp 10.7, r04 11.7): the calm applies
//      seen from above (down) or beyond 300-500 m (the far shore's reflection), not to river-level water inside 300 m
// r05b: RCalm 0 = no calm at river level at all (LongK 3 everywhere beyond LFa..LFb, as r04); LFa / LFb = the LongK / MidK ramp (r04: 100..300 m)
float calm = ShoreCalm > 0.0 ? lerp(1.0, smoothstep(ShoreCalm * 0.35, ShoreCalm, shore), max(down, RCalm * smoothstep(300.0, 500.0, dist))) : 1.0;
float lk = lerp(1.0, LongK, smoothstep(LFa, LFb, dist) * calm);
float lm = lerp(1.0, MidK, smoothstep(LFa, LFb, dist) * calm);   // r04: the 6.7 m layer (0.3-2.2 m waves: 1-10 px from swing height)
float gk = lerp(0.75, 1.25, gust);
// ---- the long Gerstner waves (waves.js waveSlope: resolved -> slope, unresolved -> slope variance)
float2 sl2 = 0; float varU = 0, h = 0, s, c, f;
%(big)s
float crest = h / %(hmax).5f;
sl2 *= lerp(0.85, 1.1, gust); varU *= 1.2;
// ---- wind-sea spectrum layers (baked random-phase slopes, true texture gradients: what the mips drop is counted in varL)
float2 slT = 0; float varL = 0; float2 slL = 0;
%(longc)s
slT += slL * lk;
%(lay)s
// ---- r03 resolved wind chop 0.15-0.5 m: two realizations, two scroll directions (near field only; beyond, all of it is sub-pixel variance)
float2 slC = 0; float lostC = 1.0;
// r04: seen from above (down -> 1) the resolved chop continues to ChopFar m (0.15-0.5 m waves are 1-3 px there from swing height)
float chopW = max(nearW, down * (1.0 - smoothstep(ChopFar * 0.6, ChopFar, dist)));
[branch] if (chopW > 0.0) {
    lostC = 0.0;
    %(chop)s
    slC *= chopW * 0.70711;
    lostC = lerp(1.0, lostC, chopW);
}
float ck = ChopK * gk, mk = ChopK * MicroK * gk * %(crms).4f;
slT *= ck; varL *= ck * ck;
float2 slope = sl2 + slT + slC * mk;
// r04: under a low sun (9 deg) facets tilted away from it by more than the sun elevation get N.L <= 0 and SLW lights them as black,
//      crisp-edged specks (Dbg 5). Soft-limit only the slope component pointing away from the sun (SunClampK 0 = r03)
float3 LsN = normalize(SunDir);
[branch] if (LsN.z > 0.02 && SunClampK > 0.0) {
    float2 Lh = LsN.xy / max(length(LsN.xy), 1e-3);
    float ss = dot(slope, Lh), sm = 0.85 * LsN.z / max(length(LsN.xy), 1e-3), k0 = 0.5 * sm;
    float sc = ss > k0 ? k0 + (sm - k0) * tanh((ss - k0) / max(sm - k0, 1e-3)) : ss;
    slope += Lh * (sc - ss) * SunClampK;
}
float varF = varL + lostC * mk * mk;      // per-axis slope variance the shading cannot resolve
// ---- foam (near field only, faded to zero by %(near).0f m): contact (the water line against anything below it), rare whitecaps
float cf = 0.0, wf = 0.0, farF = 0.0, dbgC = 32.0, dbgL = 99.0;   // dbgC / dbgL: contact-map distance and under-water ray length (Dbg 7)
[branch] if (nearW > 0.0) {
    float fn = NZG(p / 7.0 + float2(t * 0.01, -t * 0.007), 1.0 / 7.0).b;
    float lap = 0.55 + 0.225 * sin(dot(p, float2(0.11, -0.17)) + t * LapW) + 0.35 * crest + 0.15 * (slT.x - slT.y);
    float dnw = max(DNW - PD, 0.0) * 0.01;
    float lr = dnw / max(dot(-V, View.ViewForward), 0.2); dbgL = lr;
    cf = 1.0 - smoothstep(0.04, 0.25 + 1.1 * fn + 0.6 * lap, lr);
    float2 cu = (p - float2(%(cx).2f, %(cz).2f)) / float2(%(cw).2f, %(ch).2f);
    float craw = 1.0;   // r05: CSel picks the contact texture (0 = T_WaterContact, 1 = B half-res Interchange NeverStream, 2 = C legacy factory)
    [branch] if (all(cu > 0.0) && all(cu < 1.0)) {
        if (CSel < 0.5) craw = Texture2DSampleLevel(tC, tCSampler, cu, 0).r;
        else if (CSel < 1.5) craw = Texture2DSampleLevel(tC2, tC2Sampler, cu, 0).r;
        else craw = Texture2DSampleLevel(tC3, tC3Sampler, cu, 0).r;
    }
    float cdm = craw * %(cmax).1f;
    // r04: Dbg 4 showed no contact coverage at the river_low bulkhead (the depth test finds no geometry under the water there, and the
    //      0.9 m/px map reads 1.7 to 2.6 m at the built wall face: its contact line wanders +-3 m): the map term reaches CBias m further
    float ce0 = 0.12 + CBias; dbgC = cdm;
    cf = max(cf, 1.0 - smoothstep(ce0, max(0.45 + CBias * 0.5 + 1.5 * fn + 0.9 * lap, ce0 + 0.3), cdm));
    float foam = cf * (0.4 + 0.45 * lap) * smoothstep(0.25, 0.6, NZG(p / 3.1 + float2(-t * 0.02, t * 0.013), 1.0 / 3.1).r + 0.25 * lap) * FoamK;
    foam = max(foam, smoothstep(0.8, 1.0, crest) * smoothstep(0.55, 0.9, gust) * 0.2);
    // r05b: CovMax < 1 keeps the foam threshold above the noise floor (lace instead of a solid strip: the r05 band was one flat cream sheet
    //       and its XOR / OR between 4 fps dolly frames fell to 0.2 where the band was widest); FoamTK / LapW: foam drift + swell breathing
    float cov = saturate(foam) * CovMax;
    float pat = NZG(p / 1.9 + float2(t * 0.004 * FoamTK, 0.0), 1.0 / 1.9).r * 0.62 + NZG(p / 0.63 + float2(0.0, t * 0.006 * FoamTK), 1.0 / 0.63).g * 0.5;
    wf = saturate(smoothstep(1.05 - cov, 1.3 - cov, pat) * smoothstep(0.0, 0.25, cov)) * nearW;
}
// r05: far contact line (beyond the near field, out to FoamFar m): the same contact map, no sub-metre pattern (it would alias at 1 km); it
//      breathes with the swell (lap). Branch-free and without a shore-map gate (final hold 1: the gated, branched form rendered nothing; the
//      8 m/px layout shore distance reads 70-100 m at the built tip seawall): away from shores the map itself returns 32 m (no foam)
{
    float2 cuF = (p - float2(%(cx).2f, %(cz).2f)) / float2(%(cw).2f, %(ch).2f);
    float inb = (all(cuF > 0.0) && all(cuF < 1.0)) ? 1.0 : 0.0;
    float cdF = lerp(%(cmax).1f, Texture2DSampleLevel(tC, tCSampler, saturate(cuF), 0).r * %(cmax).1f, inb);
    float lapF = 0.55 + 0.225 * sin(dot(p, float2(0.11, -0.17)) + t * 1.1) + 0.35 * crest;
    float fF = NZG(p / 9.0 + float2(t * 0.012, -t * 0.008), 1.0 / 9.0).b;
    // a 1-2 m band is < 1 px at 1 km from swing height (hold 1: line in 0.3 pct of columns): the band reaches at least FarPx pixel footprints
    // r05b: the band is capped at FarMaxM metres: at river level 400-600 m out one pixel row spans 14-30 m, FarPx footprints made the far
    //       quay's line a 40 px flat white bar across the horizon (river_low r05); from swing height 1.3 km out (3 m / px) 16 m is 5 px.
    //       FarLowK: alpha of the far line at river level (down = 0), 1 from above
    float ce1F = min(max(0.5 + CBias * (0.7 + 0.6 * lapF) + 0.8 * fF, FarPx * foot * (0.8 + 0.4 * lapF)), FarMaxM);
    float cfF = 1.0 - smoothstep(0.4 * ce1F, ce1F, cdF);
    farF = saturate(cfF * FoamFarK * lerp(FarLowK, 1.0, down) * (0.75 + 0.35 * lapF)) * (1.0 - nearW) * (1.0 - smoothstep(FoamFar * 0.7, FoamFar, dist));
    wf = max(wf, farF);
}
// ---- normal / roughness. Near field: GGX alpha from RoughN only (<= 0.08: the resolved facets carry the slope variance);
//      beyond: + the unresolved variance x FarVarK (Cox-Munk alpha^2 = 2 sigma^2 per axis)
float3 N = normalize(float3(-slope.x, -slope.y, 1.0));
{ float3 Rr = reflect(-V, N); float wl = saturate((0.05 - Rr.z) * 8.0); N = normalize(lerp(N, float3(0, 0, 1), wl * BendK));
  Rr = reflect(-V, N); wl = saturate((0.03 - Rr.z) * 12.0); N = normalize(lerp(N, float3(0, 0, 1), wl * BendK)); }
// r05: tried and removed (round-05 NOTES): an F0 scale (x0.25) and a 0.2 normal lean toward the camera on sun-facing swing-height water
//      left harbour_sun_high's mean colour unchanged (R-B 100.0 / 99.7): its brass is the atmosphere's forward in-scatter, not the water.
float farW = smoothstep(%(near).1f * 0.4, %(near).1f, dist);
float r4 = RoughN * RoughN; r4 *= r4;
float a2 = r4 + VARK * FarVarK * lerp(1.0, TopVarK, down) * farW * (varU + 2.0 * varF);
float rcap = lerp(0.08, lerp(0.7, FarRough, down), smoothstep(%(near).1f, %(near).1f * 2.7, dist));
float rr = clamp(pow(a2, 0.25), 0.03, rcap);
// r04 perf: at grazing views (river level) the far field gets a rough lobe beyond ~1.7 x near (Lumen does not trace it; its slope
//      variance is unresolved there anyway); from above (down -> 1) this floor is off
rr = max(rr, GrazeRough * smoothstep(%(near).1f, %(near).1f * 1.7, dist) * (1.0 - down));
Rough = lerp(rr, 0.6, wf);
// r04 foam fix: foam pixels take the long-wave (Gerstner) normal, not the steep resolved chop normal (r03's chop-lit foam rendered as dark
//      specks under the 9 deg sun); FoamNK 0.6 ~ r03 behaviour
float3 Nlong = normalize(float3(-sl2.x, -sl2.y, 1.0));
NormalW = normalize(lerp(N, Nlong, saturate(wf * FoamNK)));
Spec = 0.25 * SpecK;     // F0 = 0.02 (IOR 1.333) x SpecK

Opac = wf * 0.92;
// ---- turbid river optics (per cm): olive-grey Hudson body (ScatK), siltier / browner along the bulkheads
float silt = (1.0 - smoothstep(10.0, 120.0, shore)) * 0.75;
float turb = 0.85 + 0.3 * nA.r;   // r04: turbidity patches from the broad gust noise (r03: its own 900 m sample; one texture fetch less per pixel)
float3 sS = float3(%(ss)s) * ScatK * turb * (1.0 + float3(0.9, 0.6, 0.3) * silt);
float3 sA = float3(%(sa)s) * (1.0 + float3(0.1, 0.2, 0.5) * silt);
Scat = sS * 0.01; Abs = sA * 0.01;
// ---- sun glitter: sparse facets that face the sun get their normal tilted onto the sun half-vector (beyond 25 m; the near field glints
//      off its own resolved facets with the sharp GGX lobe)
float3 Ls = normalize(SunDir);
float3 Hh = normalize(Ls + V);
float gw = 0.0;
// r04: only where the sun can be mirrored at all (the flat-water mirror direction within ~40 deg of the sun: none at the north-facing
//      river_low / harbour_high views), and out to GlitDist (r03: 900 m) with a coarser facet scale beyond 300 m (GlitFar x) so the far
//      facets stay a few pixels wide instead of mip-averaging away
float3 Rm = reflect(-V, float3(0, 0, 1));
[branch] if (dist < GlitDist && dist > 20.0 && Ls.z > 0.0 && dot(Rm, Ls) > 0.76) {
    float gs = lerp(1.0, GlitFar, smoothstep(250.0, 600.0, dist));
    float2 pg = p / gs;
    float2 gn = (NZG(pg / 2.3 + float2(t * 0.05, t * 0.034) / gs, 1.0 / (2.3 * gs)).ga - 0.5) * 2.0 + 0.8 * (NZG(float2(-pg.y, pg.x) / 3.7 + float2(-t * 0.041, t * 0.02) / gs, 1.0 / (3.7 * gs)).ga - 0.5) * 2.0;
    float3 nG = normalize(N + float3(gn * GSpread, 0.0));
    float gl = pow(saturate(dot(nG, Hh)), 700.0);
    float spark = smoothstep(0.62, 0.9, NZG(pg / 5.0 + float2(t * 0.02 / gs, 0.0), 1.0 / (5.0 * gs)).r);
    gw = saturate(gl * spark * (1.0 - smoothstep(GlitDist * 0.7, GlitDist, dist)) * smoothstep(20.0, 40.0, dist) * (1.0 - wf) * saturate(Ls.z * 8.0) * 3.0 * GlitterK);
}
NormalW = normalize(lerp(NormalW, Hh, gw));
Rough = lerp(Rough, 0.06, gw);
Emis = FarEmisK * farF * float3(0.62, 0.6, 0.55);   // r05b candidate (default 0): the far line also as emission, independent of the Opacity path
// r05 Dbg 10: far contact line diagnosis (harbour_high rendered no line). Base colour = a grey value in interleaved 24-px screen columns
//   (column mod 8): 0 contact-map distance / 32 m (recomputed here, same UV as the far line); 1 footprint foot / 8 m; 2 far-line coverage
//   (recomputed with the simple band); 3 the real wf of this material evaluation; 4 nearW; 5 dist / 2000 m; 6 the real near contact
//   cf; 7 the real near contact distance dbgC / 4 m. The bottom 6 pct of the frame is a calibration ramp (value = x / width) in the same
//   shading, so the grey levels can be read back through it.
[branch] if (Dbg > 9.5) {
    float2 cuF = (p - float2(%(cx).2f, %(cz).2f)) / float2(%(cw).2f, %(ch).2f);
    float inb = (all(cuF > 0.0) && all(cuF < 1.0)) ? 1.0 : 0.0;
    float cdF = lerp(%(cmax).1f, Texture2DSampleLevel(tC, tCSampler, saturate(cuF), 0).r * %(cmax).1f, inb);
    float ce1F = max(0.5 + CBias, FarPx * foot);
    float cv = (1.0 - smoothstep(0.4 * ce1F, ce1F, cdF)) * (1.0 - nearW);
    float2 sp10 = Parameters.SvPosition.xy * View.ViewSizeAndInvSize.zw;
    float k = fmod(floor(Parameters.SvPosition.x / 24.0), 8.0);
    float dg = k < 0.5 ? saturate(cdF / 32.0) : (k < 1.5 ? saturate(foot / 8.0) : (k < 2.5 ? saturate(cv) : (k < 3.5 ? saturate(wf) : (k < 4.5 ? saturate(nearW) :
               (k < 5.5 ? saturate(dist / 2000.0) : (k < 6.5 ? saturate(cf) : saturate(dbgC / 4.0)))))));
    if (sp10.y > 0.94) dg = sp10.x;
    Emis = 0; Opac = 1.0; NormalW = float3(0, 0, 1); Rough = 1.0;
    return dg.xxx;
}
// r05 Dbg 9: import-path diagnosis. Screen rows (y 0.54..0.99 of the frame, 14 bands of 0.032) each show one value as a thermometer
//   along x (0 at the left edge, full scale at x = 0.48 of the width: white while value > x / 0.48 * full). Bands:
//   0-2 T_WaterContact width / height (full 8192) and mip count (16); 3 its Load() at the texel the file reads 0 m (8 m full scale);
//   4 SampleLevel at that UV (8 m); 5 SampleLevel at open water 10 m off the wall (file 11.7 m; 32 m); 6-7 B width / height;
//   8-9 B at the 0 m / open UVs; 10 C height; 11-12 C at the 0 m / open UVs; 13 T_ShoreDist at the open UV (400 m full scale)
[branch] if (Dbg > 8.5) {
    float2 sp = Parameters.SvPosition.xy * View.ViewSizeAndInvSize.zw;
    float uu = sp.x / 0.48, yb = (sp.y - 0.54) / 0.032, bb = floor(yb);
    uint w0, h0, l0, w1, h1, l1, w2, h2, l2, w3, h3, l3;
    tC.GetDimensions(0, w0, h0, l0); tC2.GetDimensions(0, w1, h1, l1); tC3.GetDimensions(0, w2, h2, l2); tS.GetDimensions(0, w3, h3, l3);
    float2 cbx = float2(%(cx).3f, %(cz).3f), cbw = float2(%(cw).3f, %(ch).3f);
    float2 cuP = (float2(-766.12, -131.22) - cbx) / cbw, cuO = (float2(-778.0, -128.0) - cbx) / cbw;
    float2 suO = (float2(-778.0, -128.0) - float2(%(sx).1f, %(sz).1f)) / float2(%(sw).1f, %(sh).1f);
    float vv = 0.0, full = 1.0;
    if (bb < 0.5) { vv = w0; full = 8192.0; }
    else if (bb < 1.5) { vv = h0; full = 8192.0; }
    else if (bb < 2.5) { vv = l0; full = 16.0; }
    else if (bb < 3.5) { vv = tC.Load(int3(int2(cuP * float2(w0, h0)), 0)).r * %(cmax).1f; full = 8.0; }
    else if (bb < 4.5) { vv = Texture2DSampleLevel(tC, tCSampler, cuP, 0).r * %(cmax).1f; full = 8.0; }
    else if (bb < 5.5) { vv = Texture2DSampleLevel(tC, tCSampler, cuO, 0).r * %(cmax).1f; full = 32.0; }
    else if (bb < 6.5) { vv = w1; full = 8192.0; }
    else if (bb < 7.5) { vv = h1; full = 8192.0; }
    else if (bb < 8.5) { vv = Texture2DSampleLevel(tC2, tC2Sampler, cuP, 0).r * %(cmax).1f; full = 8.0; }
    else if (bb < 9.5) { vv = Texture2DSampleLevel(tC2, tC2Sampler, cuO, 0).r * %(cmax).1f; full = 32.0; }
    else if (bb < 10.5) { vv = h2; full = 8192.0; }
    else if (bb < 11.5) { vv = Texture2DSampleLevel(tC3, tC3Sampler, cuP, 0).r * %(cmax).1f; full = 8.0; }
    else if (bb < 12.5) { vv = Texture2DSampleLevel(tC3, tC3Sampler, cuO, 0).r * %(cmax).1f; full = 32.0; }
    else { vv = Texture2DSampleLevel(tS, tSSampler, suO, 0).r * 400.0; full = 400.0; }
    float dg = vv > uu * full ? 1.0 : 0.0;
    if (uu < 0.012) dg = 0.5;
    if (uu > 1.0 || bb < 0.0 || bb > 13.5) dg = 0.25;
    if (frac(yb) < 0.15) dg = 0.05;
    Emis = dg.xxx * DbgK * 0.01; Opac = 1.0; NormalW = float3(0, 0, 1); Rough = 1.0;
    return dg.xxx;
}
if (Dbg > 0.5) { float3 dv = Dbg < 1.5 ? float3(frac(p / 10.0), 0.0) : (Dbg < 2.5 ? N * 0.5 + 0.5 : (Dbg < 3.5 ? Rough.xxx : (Dbg < 4.5 ? float3(wf, cf, gust) : (Dbg < 5.5 ? float3(saturate(dot(NormalW, Ls) * 4.0), wf, saturate(dot(N, Ls) * 4.0)) : (Dbg < 6.5 ? Lag.zzz : (Dbg < 7.5 ? float3(saturate(dbgC / 4.0), saturate(dbgL / 4.0), cf) : float3(frac(p.x), frac(p.y * 0.25), 0.0))))))); Emis = 0; Opac = 1.0; return dv; }
return float3(0.62, 0.6, 0.55);   // r03: cream foam albedo (r02 0.74 clipped at the seawall in the golden key)
#undef NZG
'''


# body optics per metre (tuned against CITY-SPEC C14 and the refs; see docs/night1/water/HANDOFF.md)
SCAT = (0.07, 0.09, 0.078)
ABS = (0.50, 0.34, 0.56)
PHASE_G = 0.55
GLITTER = 0.5
# material scalar parameters (round 02 look; variants for tuning: SM2_WATER_VARIANTS, see build_in_unreal)
WP_MAPS = ('/Game/Maps/Manhattan_WP',)   # island piece's World Partition map(s), if built in this project
# r03 start (CPU emulation of the river_low near crop against the round-02 frame, see docs/night1/water/round-03/NOTES.md): dark body
# (ScatK 0.06: the body radiance set the r02 trough floor p1 46), steeper resolved chop, F0 x1.6 (SpecK) for the sky / mist reflections
# round-03 captures: autopick variant V3 (lowest penalty on the 1080p iteration stills, docs/night1/water/round-03/iter/autopick.json)
PARAMS = {'ChopK': 2.6, 'MicroK': 2.0, 'ScatK': 0.04, 'FarVarK': 0.1, 'FoamK': 1.8, 'BendK': 0.3, 'RoughN': 0.06, 'SpecK': 2.0,
          # r04 (far field from swing height, foam normal, perf): see docs/night1/water/round-04/NOTES.md
          'LongK': 3.0, 'FarRough': 0.2, 'TopVarK': 0.1, 'GrazeRough': 0.0, 'FoamNK': 3.0, 'GlitDist': 4000.0, 'GlitFar': 8.0,
          'CBias': 0.55, 'SunClampK': 1.0, 'MidK': 2.0, 'ChopFar': 0.0,
          # r05: GrazeRough 0 (r04's 0.42 grazing floor blurred the far-shore reflection at river level: merge-blocker; perf is not this
          # round's gate). CSel: which contact-map texture (0 = T_WaterContact as r04, 1 = B: half-res Interchange + NeverStream,
          # 2 = C: half-res legacy TextureFactory; Dbg 9 showed all three read correctly in-engine). ShoreCalm: the far-field long-wave
          # gains (LongK / MidK) fade out within ShoreCalm m of land (sheltered water mirrors the island: the r03 reflections).
          # FoamFarK / FoamFar: the far contact line (harbour_high: the island seawall ~1 km away had no foam: foam stopped at NEAR_M)
          # FarPx: the far line spans >= FarPx pixel footprints (a 1-2 m band is < 1 px at 1 km from swing height: hold 1 line 0.3 %)
          'CSel': 0.0, 'ShoreCalm': 380.0, 'FoamFarK': 1.0, 'FoamFar': 2500.0, 'FarPx': 6.0,
          # r05b: FarMaxM / FarLowK cap the far contact line (r05's FarPx footprints painted a 40 px white bar over the far quay at river
          # level); FarEmisK: the far line also as emission (candidate); CovMax / FoamTK / LapW: lacy, drifting near foam (gate 2: XOR / OR
          # fell to 0.2 where the solid band was widest); RCalm / LFa / LFb: river-level calm and the LongK ramp; GSpread: glitter facet spread
          'FarMaxM': 16.0, 'FarLowK': 0.7, 'FarEmisK': 0.0, 'CovMax': 0.62, 'FoamTK': 14.0, 'LapW': 2.4, 'RCalm': 1.0, 'LFa': 100.0, 'LFb': 300.0,
          'GSpread': 0.22}
if os.environ.get('SM2_WATER_PARAMS'): PARAMS.update(json.loads(os.environ['SM2_WATER_PARAMS']))


def build_in_unreal():
    import unreal
    EAL = unreal.EditorAssetLibrary
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mel = unreal.MaterialEditingLibrary
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    T0 = time.time()
    WARN = []
    def wlog(*a): print('[water %5.0fs]' % (time.time() - T0), *a)
    ROOT = '/Game/Water'
    CITY_GEO = '/Game/Tests/City/City_Midtown_Geo'
    BOXES = '/Game/Look/Look_Boxes'
    RIG = '/Game/Look/Rigs/Look_Rig_%s'
    ACTORS = '/Game/Maps/Manhattan_Actors'
    LEVEL = ROOT + '/Maps/Water_River'
    views = json.load(open(VIEWS_JSON))
    for need in (CITY_GEO, BOXES, RIG % 'golden', RIG % 'midday'):
        if not EAL.does_asset_exist(need): raise RuntimeError('missing %s: run build_manhattan.py first' % need)
    KEEP = ('WorldSettings', 'Brush', 'DefaultPhysicsVolume', 'GameplayDebuggerCategoryReplicator', 'WorldDataLayers', 'WorldPartitionMiniMap')
    if sms is None:  # commandlet: the subsystem needs its module
        unreal.SystemLibrary.execute_console_command(None, 'Module Load StaticMeshEditor'); sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

    def load(p): return unreal.load_asset(p)

    def open_level(path):
        if EAL.does_asset_exist(path):
            unreal.EditorLoadingAndSavingUtils.load_map(path)
            for a in eas.get_all_level_actors():
                if a.get_class().get_name() not in KEEP and a.get_path_name().startswith(path + '.'): eas.destroy_actor(a)
        else:
            les.new_level(path)
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

    def import_files(files, dest, options=None):
        tasks = []
        for f in files:
            t = unreal.AssetImportTask(); t.filename = f; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = False
            if options: t.options = options
            tasks.append(t)
        at.import_asset_tasks(tasks)

    # ---------------------------------------------------------------- textures
    # imported in place under their final names (re-import replaces the asset; no rename / delete of referenced assets)
    import shutil
    stage = os.path.join(SCR, 'ue_import'); os.makedirs(stage, exist_ok=True)
    TEXS = (('water_noise.png', 'T_WaterNoise'), ('shore_dist.png', 'T_ShoreDist'), ('water_slope.png', 'T_WaterSlope'), ('water_contact.png', 'T_WaterContact'),
            ('water_chop.png', 'T_WaterChop'), ('water_contact_b.png', 'T_WaterContactB'))
    for src, name in TEXS + (('water_grid.glb', 'SM_WaterGrid'), ('water_contact_b.png', 'T_WaterContactC')):
        shutil.copyfile(os.path.join(SCR, src), os.path.join(stage, name + os.path.splitext(src)[1]))
    import_files([os.path.join(stage, n + '.png') for _, n in TEXS], ROOT + '/Textures')
    # r05 (Dbg 9 import-path diagnosis): T_WaterContactC = the half-res map through the legacy TextureFactory instead of Interchange
    try:
        tk = unreal.AssetImportTask(); tk.filename = os.path.join(stage, 'T_WaterContactC.png'); tk.destination_path = ROOT + '/Textures'
        tk.automated = True; tk.replace_existing = True; tk.save = False; tk.factory = unreal.TextureFactory()
        at.import_asset_tasks([tk])
    except Exception as e: WARN.append('legacy TextureFactory import: %s' % str(e)[:120])
    if not EAL.does_asset_exist(ROOT + '/Textures/T_WaterContactC'):
        WARN.append('T_WaterContactC missing after the legacy import: Interchange fallback'); import_files([os.path.join(stage, 'T_WaterContactC.png')], ROOT + '/Textures')
    for name in [n for _, n in TEXS] + ['T_WaterContactC']:
        tx = load(f'{ROOT}/Textures/{name}')
        tx.set_editor_property('srgb', False)
        vec = name in ('T_WaterNoise', 'T_WaterSlope', 'T_WaterChop')
        tx.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP if vec else unreal.TextureCompressionSettings.TC_GRAYSCALE)
        if not vec:
            tx.set_editor_property('address_x', unreal.TextureAddress.TA_CLAMP); tx.set_editor_property('address_y', unreal.TextureAddress.TA_CLAMP)
        if name.startswith('T_WaterContact'):   # distance map, sampled at level 0 only
            tx.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
        if name in ('T_WaterContactB', 'T_WaterContactC'):   # r05: never streamed, never virtual
            for k, v in (('never_stream', True), ('virtual_texture_streaming', False)):
                try: tx.set_editor_property(k, v)
                except Exception as e: WARN.append('%s.%s: %s' % (name, k, str(e)[:60]))
        try: tx.post_edit_change()
        except Exception: pass
        EAL.save_asset(f'{ROOT}/Textures/{name}')
    # r05: what the engine actually holds (the r04 in-engine contact reading did not match the file)
    for name in ('T_WaterContact', 'T_WaterContactB', 'T_WaterContactC', 'T_ShoreDist'):
        tx = load(f'{ROOT}/Textures/{name}'); info = []
        for k in ('blueprint_get_size_x', 'blueprint_get_size_y'):
            try: info.append('%s=%s' % (k[-6:], getattr(tx, k)()))
            except Exception as e: info.append('%s=? (%s)' % (k, str(e)[:40]))
        for k in ('compression_settings', 'mip_gen_settings', 'lod_group', 'never_stream', 'virtual_texture_streaming', 'srgb', 'power_of_two_mode',
                  'max_texture_size', 'compression_none', 'filter', 'address_x', 'mip_load_options', 'source_color_settings'):
            try: info.append('%s=%s' % (k, tx.get_editor_property(k)))
            except Exception as e: info.append('%s=?' % k)
        try: info.append('class=%s outer=%s' % (tx.get_class().get_name(), tx.get_path_name()))
        except Exception: pass
        wlog('TEXINFO', name, ' '.join(info))
    wlog('textures')

    # ---------------------------------------------------------------- grid mesh
    p = unreal.InterchangeGenericAssetsPipeline()
    p.common_meshes_properties.set_editor_properties({'recompute_normals': False, 'recompute_tangents': False, 'use_full_precision_u_vs': True,
                                                      'remove_degenerates': False})
    p.mesh_pipeline.set_editor_properties({'generate_lightmap_u_vs': False, 'build_nanite': False})
    try: p.mesh_pipeline.set_editor_property('collision', False)
    except Exception as e: WARN.append('pipeline collision flag: %s' % str(e)[:80])
    p.material_pipeline.set_editor_property('import_materials', False)
    p.material_pipeline.texture_pipeline.set_editor_property('import_textures', False)
    import_files([os.path.join(stage, 'SM_WaterGrid.glb')], ROOT + '/Meshes', p)
    dst = ROOT + '/Meshes/SM_WaterGrid/StaticMeshes/SM_WaterGrid'   # Interchange glTF layout <dest>/<file>/StaticMeshes/<mesh>
    if not EAL.does_asset_exist(dst):
        found = [x.split('.')[0] for x in EAL.list_assets(ROOT + '/Meshes', recursive=True) if isinstance(load(x.split('.')[0]), unreal.StaticMesh)]
        raise RuntimeError('grid import: %s missing, found %s' % (dst, found))
    sm = load(dst)
    bs = sms.get_lod_build_settings(sm, 0)
    for k, v in (('use_full_precision_u_vs', True), ('generate_lightmap_u_vs', False), ('recompute_normals', False), ('recompute_tangents', False),
                 ('distance_field_resolution_scale', 0.0)):
        try: bs.set_editor_property(k, v)
        except Exception as e: WARN.append('build setting %s: %s' % (k, str(e)[:60]))
    sms.set_lod_build_settings(sm, 0, bs)
    try: sms.remove_collisions(sm)
    except Exception as e: WARN.append('remove_collisions: %s' % str(e)[:80])
    EAL.save_asset(dst, only_if_is_dirty=False)
    bb = sm.get_bounding_box()
    wlog('grid mesh', dst, 'verts', sm.get_num_vertices(0), 'tris', sm.get_num_triangles(0), 'bounds', bb.min, bb.max)

    # ---------------------------------------------------------------- material
    MATP = ROOT + '/Materials/M_RiverWater'
    if EAL.does_asset_exist(MATP):
        m = load(MATP); mel.delete_all_material_expressions(m)
    else:
        m = at.create_asset('M_RiverWater', ROOT + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_SINGLE_LAYER_WATER)
    m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_OPAQUE)
    m.set_editor_property('tangent_space_normal', False)
    m.set_editor_property('two_sided', False)
    MP = unreal.MaterialProperty
    def expr(cls, x, y, **props):
        e = mel.create_material_expression(m, cls, x, y)
        for k, v in props.items(): e.set_editor_property(k, v)
        return e
    def custom(name, code, inputs, outputs, x, y):
        c = expr(unreal.MaterialExpressionCustom, x, y)
        c.set_editor_property('code', code); c.set_editor_property('description', name)
        c.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
        ins = []
        for n, _ in inputs:
            ci = unreal.CustomInput(); ci.set_editor_property('input_name', n); ins.append(ci)
        c.set_editor_property('inputs', ins)
        T = {1: unreal.CustomMaterialOutputType.CMOT_FLOAT1, 2: unreal.CustomMaterialOutputType.CMOT_FLOAT2, 3: unreal.CustomMaterialOutputType.CMOT_FLOAT3}
        outs = []
        for n, k in outputs:
            co = unreal.CustomOutput(); co.set_editor_property('output_name', n); co.set_editor_property('output_type', T[k]); outs.append(co)
        c.set_editor_property('additional_outputs', outs)
        for n, e in inputs: mel.connect_material_expressions(e, '', c, n)
        return c
    wpos_vs = expr(unreal.MaterialExpressionWorldPosition, -1400, -400)
    cam = expr(unreal.MaterialExpressionCameraPositionWS, -1400, -300)
    tim = expr(unreal.MaterialExpressionTime, -1400, -200)
    vs = custom('WaterVS', hlsl_vs(), [('WPos', wpos_vs), ('Cam', cam), ('T', tim)], [('Lag', 3)], -900, -400)
    mel.connect_material_property(vs, '', MP.MP_WORLD_POSITION_OFFSET)
    # Lag (m) travels vertex -> pixel through a vertex interpolator (the Python API does not expose the CustomizedUV material pins)
    vi = expr(unreal.MaterialExpressionVertexInterpolator, -600, -250)
    if not (mel.connect_material_expressions(vs, 'Lag', vi, 'VS') or mel.connect_material_expressions(vs, 'Lag', vi, '')): raise RuntimeError('interpolator not connected')
    wpos_ps = expr(unreal.MaterialExpressionWorldPosition, -1400, 100)
    try: wpos_ps.set_editor_property('world_position_shader_offset', unreal.WorldPositionIncludedOffsets.WPT_EXCLUDE_ALL_SHADER_OFFSETS)
    except Exception: pass
    cam2 = expr(unreal.MaterialExpressionCameraPositionWS, -1400, 200)
    tim2 = expr(unreal.MaterialExpressionTime, -1400, 300)
    tN = expr(unreal.MaterialExpressionTextureObject, -1400, 400, texture=load(ROOT + '/Textures/T_WaterNoise'), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    tS = expr(unreal.MaterialExpressionTextureObject, -1400, 500, texture=load(ROOT + '/Textures/T_ShoreDist'), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE)
    sund = expr(unreal.MaterialExpressionSkyAtmosphereLightDirection, -1400, 600, light_index=0)
    sune = expr(unreal.MaterialExpressionSkyAtmosphereLightIlluminance, -1400, 700, light_index=0)
    dnw = expr(unreal.MaterialExpressionSceneDepthWithoutWater, -1400, 800)
    try: dnw.set_editor_property('fallback_depth', 1.0e7)
    except Exception as e: WARN.append('fallback_depth: %s' % str(e)[:60])
    pd = expr(unreal.MaterialExpressionPixelDepth, -1400, 900)
    gk = expr(unreal.MaterialExpressionScalarParameter, -1400, 1000, parameter_name='GlitterK', default_value=GLITTER)
    tW = expr(unreal.MaterialExpressionTextureObject, -1600, 400, texture=load(ROOT + '/Textures/T_WaterSlope'), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    tC = expr(unreal.MaterialExpressionTextureObject, -1600, 500, texture=load(ROOT + '/Textures/T_WaterContact'), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE)
    tK = expr(unreal.MaterialExpressionTextureObject, -1600, 300, texture=load(ROOT + '/Textures/T_WaterChop'), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    tC2 = expr(unreal.MaterialExpressionTextureObject, -1800, 500, texture=load(ROOT + '/Textures/T_WaterContactB'), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE)
    tC3 = expr(unreal.MaterialExpressionTextureObject, -1800, 600, texture=load(ROOT + '/Textures/T_WaterContactC'), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE)
    prm = {k: expr(unreal.MaterialExpressionScalarParameter, -1600, 600 + 100 * i, parameter_name=k, default_value=float(v)) for i, (k, v) in enumerate(PARAMS.items())}
    dbg = expr(unreal.MaterialExpressionScalarParameter, -1400, 1100, parameter_name='Dbg', default_value=float(os.environ.get('SM2_WATER_DBG', '0')))
    dbgk = expr(unreal.MaterialExpressionScalarParameter, -1400, 1200, parameter_name='DbgK', default_value=float(os.environ.get('SM2_WATER_DBGK', '3000')))
    code = hlsl_ps().replace('VARK', '%.3f' % VAR_K) % dict(SCAT='%.4f, %.4f, %.4f' % SCAT, ABS='%.4f, %.4f, %.4f' % ABS)
    ps = custom('WaterPS', code, [('Lag', vi), ('WPos', wpos_ps), ('Cam', cam2), ('T', tim2), ('tN', tN), ('tS', tS), ('SunDir', sund), ('SunE', sune),
                                  ('DNW', dnw), ('PD', pd), ('GlitterK', gk), ('Dbg', dbg), ('DbgK', dbgk), ('tW', tW), ('tC', tC), ('tK', tK), ('tC2', tC2), ('tC3', tC3)] + list(prm.items()),
                [('NormalW', 3), ('Rough', 1), ('Opac', 1), ('Emis', 3), ('Spec', 1), ('Scat', 3), ('Abs', 3)], -900, 200)
    for out, prop in (('', MP.MP_BASE_COLOR), ('NormalW', MP.MP_NORMAL), ('Rough', MP.MP_ROUGHNESS), ('Opac', MP.MP_OPACITY), ('Emis', MP.MP_EMISSIVE_COLOR),
                      ('Spec', MP.MP_SPECULAR)):
        mel.connect_material_property(ps, out, prop)
    slw = expr(unreal.MaterialExpressionSingleLayerWaterMaterialOutput, -300, 600)
    phase = expr(unreal.MaterialExpressionConstant, -600, 750, r=PHASE_G)
    ins = [str(n) for n in mel.get_material_expression_input_names(slw)] if hasattr(mel, 'get_material_expression_input_names') else []
    def slw_in(want):
        for n in ins:
            if n.replace(' ', '').lower() == want.replace(' ', '').lower(): return n
        return want
    for src_e, out, want in ((ps, 'Scat', 'Scattering Coefficients'), (ps, 'Abs', 'Absorption Coefficients'), (phase, '', 'Phase G')):
        if not mel.connect_material_expressions(src_e, out, slw, slw_in(want)): WARN.append('SLW input %s not connected (inputs %s)' % (want, ins))
    mel.recompile_material(m)
    EAL.save_asset(MATP)
    wlog('material', MATP, 'SLW inputs', ins)

    # ---------------------------------------------------------------- water sublevel
    def water_actor(label='RiverWater', material=None):
        a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, WATER_Y * 100.0), unreal.Rotator(0, 0, 0))
        a.set_actor_label(label); a.set_folder_path('Water')
        c = a.static_mesh_component
        c.set_editor_property('mobility', unreal.ComponentMobility.STATIC)
        c.set_static_mesh(sm); c.set_material(0, material or m)
        for k, v in (('cast_shadow', False), ('affect_distance_field_lighting', False), ('affect_dynamic_indirect_lighting', False),
                     ('affect_indirect_lighting_while_hidden', False), ('visible_in_ray_tracing', False), ('visible_in_reflection_captures', False),
                     ('visible_in_real_time_sky_captures', False), ('receives_decals', False), ('bounds_scale', 1.5), ('can_ever_affect_navigation', False)):
            try: c.set_editor_property(k, v)
            except Exception as e: WARN.append('%s.%s: %s' % (label, k, str(e)[:60]))
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        return a
    open_level(LEVEL); water_actor()
    unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), LEVEL)
    wlog('level', LEVEL)

    # ---------------------------------------------------------------- P1 flat water plane: hidden (collision kept)
    unreal.EditorLoadingAndSavingUtils.load_map(CITY_GEO)
    n = 0
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == 'WaterPlane':
            a.static_mesh_component.set_visibility(False, False); a.set_actor_hidden_in_game(True); n += 1
    unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), CITY_GEO)
    if n != 1: WARN.append('WaterPlane actors hidden: %d (expected 1)' % n)
    wlog('P1 WaterPlane hidden:', n)

    # ---------------------------------------------------------------- Manhattan maps get the water sublevel
    def add_sublevels(world, levels):
        have = [l.get_path_name() for l in unreal.EditorLevelUtils.get_levels(world)]
        for lp in levels:
            nm = lp.split('/')[-1]
            if not any((nm + '.') in h or h.endswith(nm) or ('/' + nm + ':') in h for h in have):
                unreal.EditorLevelUtils.add_level_to_world(world, lp, unreal.LevelStreamingAlwaysLoaded)
        les.set_current_level_by_name(str(world.get_name()))
    for mp in ('/Game/Maps/Manhattan', '/Game/Maps/Manhattan_Midday', '/Game/Maps/Manhattan_Night', '/Game/Maps/Manhattan_View_S1',
               '/Game/Maps/Manhattan_View_S2', '/Game/Maps/Manhattan_View_S4'):
        if not EAL.does_asset_exist(mp): WARN.append('missing map ' + mp); continue
        unreal.EditorLoadingAndSavingUtils.load_map(mp)
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        add_sublevels(w, [LEVEL])
        unreal.EditorLoadingAndSavingUtils.save_map(w, mp)
        wlog('water added to', mp)

    # ---------------------------------------------------------------- view / perf maps
    def cam_actor(v, label):
        loc = unreal.Vector(*v['ue_cm'])
        ca = eas.spawn_actor_from_class(unreal.CameraActor, loc, unreal.Rotator(roll=0.0, pitch=v['pitch'], yaw=v['yaw']))
        ca.set_actor_label(label)
        ca.camera_component.set_editor_property('field_of_view', v['hfov'])
        ca.camera_component.set_editor_property('constrain_aspect_ratio', False)
        ca.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.PLAYER0)
        return ca
    def view_map(path, rig, v, water=True, dolly=None, mat=None):
        world = open_level(path)
        add_sublevels(world, [CITY_GEO, BOXES, RIG % rig, ACTORS] + ([LEVEL] if water and mat is None else []))
        if mat is not None: water_actor('RiverWater_Variant', mat)   # tuning variant: its own water actor with a material instance
        if not water:  # perf baseline: P1's previous flat water (M_CityWater plane at G.WATER_Y), as the city had it before this piece
            g = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, WATER_Y * 100.0), unreal.Rotator(0, 0, 0))
            g.set_actor_label('BaselineWaterPlane')
            g.static_mesh_component.set_static_mesh(load('/Engine/BasicShapes/Plane')); g.set_actor_scale3d(unreal.Vector(60000, 60000, 1))
            g.static_mesh_component.set_material(0, load('/Game/City/Materials/M_CityWater'))
        if dolly:
            yaw = math.radians(v['yaw']); d = (math.cos(yaw), math.sin(yaw))
            start = [v['ue_cm'][0] - d[0] * dolly['pre_m'] * 100, v['ue_cm'][1] - d[1] * dolly['pre_m'] * 100, v['ue_cm'][2]]
            ca = cam_actor(dict(v, ue_cm=start), 'DollyCam')
            ca.root_component.set_editor_property('mobility', unreal.ComponentMobility.MOVABLE)
            root = sds.k2_gather_subobject_data_for_instance(ca)[0]
            hnd, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.InterpToMovementComponent, blueprint_context=None))
            mv = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(hnd))
            L = (dolly['pre_m'] + dolly['post_m']) * 100
            pts = []
            # InterpToMovement rotates EVERY control point by the actor rotation (UE 5.8 InterpToMovementComponent.cpp:280), relative or not:
            # give it the world offset un-rotated by the camera rotation (yaw + pitch -3 deg), relative to the start -> a level, straight dolly
            P_, Y_ = math.radians(v['pitch']), math.radians(v['yaw'])
            Fw = (math.cos(P_) * math.cos(Y_), math.cos(P_) * math.sin(Y_), math.sin(P_)); Rt = (-math.sin(Y_), math.cos(Y_), 0.0)
            Up = (-math.sin(P_) * math.cos(Y_), -math.sin(P_) * math.sin(Y_), math.cos(P_))
            unrot = lambda w: unreal.Vector(sum(a * b for a, b in zip(w, Fw)), sum(a * b for a, b in zip(w, Rt)), sum(a * b for a, b in zip(w, Up)))
            for s_ in (0.0, 1.0):
                cp = unreal.InterpControlPoint()
                cp.set_editor_property('position_control_point', unrot((d[0] * L * s_, d[1] * L * s_, 0.0)))
                cp.set_editor_property('position_is_relative', True); pts.append(cp)
            mv.set_editor_property('control_points', pts)
            mv.set_editor_property('duration', float(dolly['duration_s']))
            mv.set_editor_property('behaviour_type', unreal.InterpToBehaviourType.ONE_SHOT)
            try: mv.finalise_control_points()
            except Exception as e: WARN.append('finalise_control_points: %s' % str(e)[:60])
        else:
            cam_actor(v, 'ShotCam_' + v['id'])
        ok = unreal.EditorLoadingAndSavingUtils.save_map(world, path)
        wlog('map', path, rig, 'water' if water else 'BASELINE', 'saved' if ok else 'SAVE FAILED')
    rl, s4 = views['river_low'], views['S4_perch_skyline']
    view_map(ROOT + '/Maps/Water_View_RiverLow', 'golden', rl)
    view_map(ROOT + '/Maps/Water_View_RiverLow_Midday', 'midday', rl)
    view_map(ROOT + '/Maps/Water_View_S4_Midday', 'midday', s4)
    view_map(ROOT + '/Maps/Water_View_RiverLow_Dolly', 'golden', rl, dolly=views['river_low_dolly'])
    view_map(ROOT + '/Maps/Water_Perf_RiverLow_Base', 'golden', rl, water=False)
    view_map(ROOT + '/Maps/Water_Perf_S4_Base', 'golden', s4, water=False)
    view_map(ROOT + '/Maps/Water_Perf_S4', 'golden', s4)   # = Manhattan_View_S4 with the same camera construction as the baseline
    rs = views['river_sun']
    view_map(ROOT + '/Maps/Water_View_RiverSun', 'golden', rs)
    view_map(ROOT + '/Maps/Water_View_RiverSun_Dolly', 'golden', rs, dolly=views['river_sun_dolly'])
    view_map(ROOT + '/Maps/Water_View_HarbourHigh', 'golden', views['harbour_high'])
    view_map(ROOT + '/Maps/Water_View_HarbourSunHigh', 'golden', views['harbour_sun_high'])   # r04: same position, yaw toward the sun
    view_map(ROOT + '/Maps/Water_Perf_RiverSun_Base', 'golden', rs, water=False)
    # ---------------------------------------------------------------- tuning variants (SM2_WATER_VARIANTS = {"name": {param: value}, ...})
    var = json.loads(os.environ.get('SM2_WATER_VARIANTS') or '{}')
    if EAL.does_directory_exist(ROOT + '/Variants'): EAL.delete_directory(ROOT + '/Variants')
    for vn, pv in var.items():
        mi = at.create_asset('MI_Water_' + vn, ROOT + '/Variants', unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mi.set_editor_property('parent', m)
        for k, val in pv.items():
            if k.startswith('_'): continue
            unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi, k, float(val))
        EAL.save_asset(mi.get_path_name().split('.')[0])
        for key in pv.get('_views', ['river_low', 'river_sun', 'S4_perch_skyline']):
            view_map(ROOT + '/Variants/Water_Var_%s_%s' % (vn, key), 'golden', views[key], mat=mi)
    # ---------------------------------------------------------------- World Partition Manhattan (island piece): the water actor goes straight
    # into the persistent WP level, not spatially loaded (a classic sublevel cannot be added to a WP map)
    for mp in WP_MAPS:
        if not EAL.does_asset_exist(mp): continue
        try:
            unreal.EditorLoadingAndSavingUtils.load_map(mp)
            for a in eas.get_all_level_actors():
                if a.get_actor_label() in ('RiverWater', 'RiverWater_WP'): eas.destroy_actor(a)
            hid = 0
            for a in eas.get_all_level_actors():
                if a.get_actor_label() == 'WaterPlane':
                    a.static_mesh_component.set_visibility(False, False); a.set_actor_hidden_in_game(True); hid += 1
            wa = water_actor('RiverWater_WP')
            try: wa.set_editor_property('is_spatially_loaded', False)
            except Exception as e: WARN.append('WP is_spatially_loaded: %s' % str(e)[:60])
            unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
            wlog('water added to WP map', mp, '(flat WaterPlane actors hidden: %d)' % hid)
            if hid == 0: WARN.append('%s: no loaded WaterPlane actor hidden (hide or drop the flat plane in the city build when /Game/Water exists)' % mp)
        except Exception as e:
            WARN.append('WP map %s: %s' % (mp, str(e)[:120]))
    if WARN:
        wlog('WARNINGS (%d):' % len(WARN))
        for w in WARN: print('    ', w)
    wlog('DONE')


try:
    import unreal  # noqa: F401
    IN_UE = hasattr(unreal, 'EditorAssetLibrary')
except ImportError:
    IN_UE = False

if IN_UE:
    build_in_unreal()
elif __name__ == '__main__':
    main()
