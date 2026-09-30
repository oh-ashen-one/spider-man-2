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
#       ue       headless commandlet (-nullrhi) running this file inside Unreal
#   * inside Unreal (-run=pythonscript -script=<this file>):
#       /Game/Water/Textures/T_WaterNoise, T_ShoreDist, /Game/Water/Meshes/SM_WaterGrid
#       /Game/Water/Materials/M_RiverWater   Single Layer Water material:
#           vertex: the browser's 12 Gerstner waves (src/world/waves.js, same constants), evaluated at the camera-centred grid vertex
#                   (grid follows the camera through WPO; waves shorter than ~4 grid spacings fade out exactly like waves.js waveDisp)
#           pixel:  analytic slopes of the same 12 waves + 12 short capillary waves, filtered by the pixel footprint (resolved -> normal,
#                   unresolved slope variance -> roughness, Cox-Munk), wind gust / slick / streak fields, contact foam where the surface
#                   meets anything below the water line (SceneDepthWithoutWater: seawalls, bulkheads, piles, piers), sparse whitecaps,
#                   sun glitter facets (emissive, sun = SkyAtmosphere light 0), turbid-river optics as SLW scattering / absorption
#                   coefficients (olive-grey Hudson, siltier within ~100 m of the shore)
#       /Game/Water/Maps/Water_River        sublevel with the water actor (no shadows, not in Lumen scene / ray tracing, no collision)
#       P1's flat WaterPlane in /Game/Tests/City/City_Midtown_Geo is hidden (collision kept: it is still the traversal floor)
#       Water_River is added (always loaded) to /Game/Maps/Manhattan, _Midday, _Night, _View_S1|S2|S4
#       /Game/Water/Maps/Water_View_RiverLow[_Midday]   golden / midday + the low river camera (docs/night1/water/views.json)
#       /Game/Water/Maps/Water_View_RiverLow_Dolly      same camera on an InterpToMovement dolly (16 s, 2 m/s, at the view point at t = 6 s)
#       /Game/Water/Maps/Water_Perf_<RiverLow|S4>_Base  perf baseline: same view, P1's old flat water instead of this water
import os, sys, json, math, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/Users/midir/sm2-n1/water-ab-opus/unreal/WebHomage/Scripts'
PROJ = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(PROJ))
UPROJECT = os.path.join(PROJ, 'WebHomage.uproject')
UE = '/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
SCR = os.environ.get('SM2_WATER_SCR', '/Users/midir/sm2-n1/_scratch/water')
VIEWS_JSON = os.path.join(WT, 'docs', 'night1', 'water', 'views.json')
STEPS_ALL = ['inputs', 'ue']

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
# capillary / short chop (pixel shader only; replaces the browser's tiled normal-map layers): [wavelength m, steepness kA, direction deg, phase]
CAPS = [
    [0.52, 0.050, -44, 0.7], [0.41, 0.048, -69, 2.9], [0.33, 0.046, -25, 5.2], [0.27, 0.045, -58, 1.4], [0.22, 0.043, -8, 3.8],
    [0.18, 0.042, -83, 0.2], [0.15, 0.040, -37, 4.4], [0.125, 0.038, -95, 2.1], [0.105, 0.036, -15, 5.9], [0.088, 0.034, -62, 1.0],
    [0.074, 0.032, -30, 3.3], [0.062, 0.030, -77, 4.8],
]
def waves():
    out = []
    for L, A, dd, q, ph in SPEC:
        k = 2 * math.pi / L; d = math.radians(dd)
        out.append(dict(L=L, A=A, k=k, w=math.sqrt(GRAV * k), dx=math.cos(d), dy=math.sin(d), Q=q / (k * A * len(SPEC)), ph=ph))
    return out
def caps():
    out = []
    for L, kA, dd, ph in CAPS:
        k = 2 * math.pi / L; d = math.radians(dd)
        w = math.sqrt(GRAV * k + 7.28e-5 * k ** 3)  # capillary-gravity dispersion
        out.append(dict(L=L, A=CAP_K * kA / k, k=k, w=w, dx=math.cos(d), dy=math.sin(d), ph=ph))
    return out
WAVE_MAX = sum(w[1] for w in SPEC)
VAR_K = 1.2   # filtered slope variance -> GGX alpha^2 (Cox-Munk: alpha^2 ~ 2 sigma^2 per axis; 1.2 keeps the far river glossy)
CAP_K = 0.45   # capillary steepness scale (sheltered river chop; tuned on CITY-SPEC C14 at S4)
WIND = (math.cos(math.radians(-50)), math.sin(math.radians(-50)))


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
    cv2.imwrite(os.path.join(SCR, 'shore_dist.png'), np.clip(dist / 400.0 * 255 + 0.5, 0, 255).astype(np.uint8))
    log('shore map %dx%d (%.0f %% water), noise %dx%d' % (nw, nh, (land == 0).mean() * 100, S, S))


def step_ue():
    if subprocess.run(['pgrep', '-f', UPROJECT], capture_output=True).returncode == 0:
        raise SystemExit('an Unreal process of this worktree is running; stop it first')
    n = 0
    while int(subprocess.run("pgrep -f '^%s( |$)' | wc -l" % UE, shell=True, capture_output=True, text=True).stdout.strip() or 0) >= 3:
        if n % 12 == 0: log('3+ Unreal instances running, waiting')
        n += 1; time.sleep(5)
    os.makedirs(os.path.join(SCR, 'logs'), exist_ok=True)
    lg = os.path.join(SCR, 'logs', 'water_ue.log')
    t0 = time.time()
    with open(lg + '.stdout', 'w') as so:
        r = subprocess.run([UE, UPROJECT, '-run=pythonscript', '-script=' + os.path.abspath(__file__), '-unattended', '-nullrhi', '-nosplash',
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
    W = waves(); C = caps()
    big = '\n'.join('sincos(%.6f * dot(float2(%.6f, %.6f), p) - %.6f * t + %.4f, s, c); f = 1.0 - smoothstep(0.12, 0.35, foot * %.6f); '
                    'sl2 += float2(%.6f, %.6f) * (%.6f * c / max(1.0 - %.6f * s, 0.35)) * f; varU += %.8f * (1.0 - f); h += %.6f * s;'
                    % (w['k'], w['dx'], w['dy'], w['w'], w['ph'], w['k'] / math.pi, w['dx'], w['dy'], w['k'] * w['A'], w['Q'] * w['k'] * w['A'],
                       0.5 * (w['k'] * w['A']) ** 2, w['A']) for w in W)
    cap = '\n'.join('sincos(%.5f * dot(float2(%.6f, %.6f), p) - %.5f * t + %.4f, s, c); f = 1.0 - smoothstep(0.12, 0.35, foot * %.5f); '
                    'sl3 += float2(%.6f, %.6f) * (%.6f * c) * f; var3 += %.8f * (1.0 - f);'
                    % (w['k'], w['dx'], w['dy'], w['w'], w['ph'], w['k'] / math.pi, w['dx'], w['dy'], w['k'] * w['A'], 0.5 * (w['k'] * w['A']) ** 2) for w in C)
    return r'''
#define NZ(uv) Texture2DSample(tN, tNSampler, (uv))
float2 p = Lag.xy; float t = T;
float3 wp = WPos * 0.01, cm = Cam * 0.01;
float3 Vv = cm - wp; float dist = length(Vv); float3 V = Vv / max(dist, 1e-3);
float foot = max(length(fwidth(p)), 1e-4);
// ---- sea detail (tidewater SeaDetail as in water.js): wind-aligned gusts, slicks, streaks; current streaks along the rivers (UE Y)
float2 wdir = float2(%(wx).6f, %(wy).6f);
float4 nA = NZ(p / 620.0), nB = NZ(p / 230.0 + float2(t * 0.0009, 0.37));
float gust = saturate((nA.r * 0.62 + nB.g * 0.38 - 0.5) * 2.4 + 0.5);
float along = dot(p, wdir), across = dot(p, float2(-wdir.y, wdir.x)) + (nB.g - 0.5) * 26.0;
float slick = smoothstep(0.62, 0.76, NZ(float2(along / 1100.0, across / 70.0)).b) * (1.0 - gust * 0.8) * 0.9;
float streak = smoothstep(0.66, 0.82, NZ(float2(along / 380.0, across / 11.0) + float2(0.13, 0.71)).r) * smoothstep(0.4, 0.62, NZ(float2(along / 140.0, across / 40.0) + float2(0.51, 0.29)).g) * 0.7;
streak = max(streak, smoothstep(0.6, 0.82, NZ(float2(p.x / 34.0, p.y / 520.0) + float2(t * 0.0008, t * 0.003)).g) * 0.45);
float2 su = (p - float2(%(sx).1f, %(sz).1f)) / float2(%(sw).1f, %(sh).1f);
float shore = (all(su > 0.0) && all(su < 1.0)) ? Texture2DSampleLevel(tS, tSSampler, su, 0).r * 400.0 : 400.0;
float nearS = 1.0 - smoothstep(6.0, 70.0, shore);
slick = saturate(slick + nearS * 0.3);
float rough = lerp(0.55, 1.45, gust) * (1.0 - slick * 0.7) * (1.0 - streak * 0.3);
// ---- the 12 Gerstner waves (waves.js waveSlope: resolved -> slope, unresolved -> slope variance) + 12 capillary waves
float2 sl2 = 0, sl3 = 0; float varU = 0, var3 = 0, h = 0, s, c, f;
%(big)s
%(cap)s
float crest = h / %(hmax).5f;
float wk = lerp(0.8, 1.15, gust) * (1.0 - 0.3 * slick);
sl2 *= wk; varU *= wk * wk; sl3 *= rough; var3 *= rough * rough;
float2 slope = sl2 + sl3;
// ---- foam: contact (the water line against anything below it), whitecaps in the gusts, wind streaks
float dnw = max(DNW - PD, 0.0) * 0.01;                                 // view-depth of water in front of what lies below it (m)
float lr = dnw / max(dot(-V, View.ViewForward), 0.2);                  // -> distance along the view ray under the surface
float fn = NZ(p / 7.0 + float2(t * 0.01, -t * 0.007)).b;
float lap = 0.55 + 0.225 * sin(dot(p, float2(0.11, -0.17)) + t * 1.1) + 0.35 * crest;
float cf = (1.0 - smoothstep(0.04, 0.25 + 1.1 * fn + 0.6 * lap, lr)) * (1.0 - smoothstep(1500.0, 3000.0, dist));
float foam = cf * (0.35 + 0.45 * lap) * smoothstep(0.25, 0.6, NZ(p / 3.1 + float2(-t * 0.02, t * 0.013)).r + 0.25 * lap);
foam = max(foam, streak * 0.12 * smoothstep(0.4, 1.0, gust + 0.3));
foam = max(foam, smoothstep(0.62, 0.95, crest) * gust * 0.35);
float cov = saturate(foam);
float pat = NZ(p / 1.9 + float2(t * 0.004, 0.0)).r * 0.62 + NZ(p / 0.63 + float2(0.0, t * 0.006)).g * 0.5;
float wf = smoothstep(1.05 - cov, 1.3 - cov, pat) * smoothstep(0.0, 0.25, cov) * (1.0 - smoothstep(600.0, 2500.0, dist)) + cov * 0.35 * smoothstep(300.0, 2500.0, dist);
wf = saturate(wf);
// ---- normal / roughness (GGX alpha^2 = base + filtered wave variance + foam)
float3 N = normalize(float3(-slope.x, -slope.y, 1.0));
float a2 = 0.028 * 0.028 + VARK * (varU + var3) + wf * 0.2;
Rough = clamp(pow(a2, 0.25), 0.04, 0.7);
NormalW = normalize(lerp(N, float3(0, 0, 1), wf * 0.6));
Spec = 0.25 * lerp(0.9, 1.12, slick) * (1.0 + 0.1 * streak);     // F0 = 0.02 (IOR 1.333); slicks mirror a little more, gust patches less
Opac = wf * 0.92;
// ---- turbid river optics (per cm): olive-grey Hudson body, siltier / browner along the bulkheads, turbidity patches, current streaks
float fn2 = NZ(p / 23.0 + float2(t * 0.002, -t * 0.003)).g;
float silt = (1.0 - smoothstep(10.0, 120.0, shore)) * (0.55 + 0.45 * fn2);
float turb = 0.85 + 0.3 * NZ(p / 900.0 + float2(0.0, t * 0.0015)).r;
float3 sS = float3(%(ss)s) * turb * (1.0 + 0.25 * streak) * (1.0 + float3(0.9, 0.6, 0.3) * silt);
float3 sA = float3(%(sa)s) * (1.0 + float3(0.1, 0.2, 0.5) * silt);
Scat = sS * 0.01; Abs = sA * 0.01;
// ---- sun glitter: sparse facets of a finer chop that face the sun get their normal tilted onto the sun half-vector and a smoother
//      micro-roughness, so the engine's own (shadowed) GGX sun specular lights them as glints (emissive does not reach the SLW output)
float3 Ls = normalize(SunDir);
float3 Hh = normalize(Ls + V);
float2 gn = (NZ(p / 2.3 + float2(t * 0.05, t * 0.034)).ga - 0.5) * 2.0 + 0.8 * (NZ(float2(-p.y, p.x) / 3.7 + float2(-t * 0.041, t * 0.02)).ga - 0.5) * 2.0;
float3 nG = normalize(N + float3(gn * 0.22 * (1.0 - 0.6 * slick), 0.0));
float gl = pow(saturate(dot(nG, Hh)), 700.0);
float spark = smoothstep(0.62, 0.9, NZ(p / 5.0 + float2(t * 0.02, 0.0)).r);
float gfade = 1.0 - smoothstep(900.0, 4000.0, dist);
float gw = saturate(gl * spark * gfade * (1.0 - wf) * saturate(Ls.z * 8.0) * 3.0 * GlitterK);
NormalW = normalize(lerp(NormalW, Hh, gw));
Rough = lerp(Rough, 0.06, gw);
Emis = 0;
if (Dbg > 0.5) { float3 dv = Dbg < 1.5 ? float3(frac(p / 10.0), 0.0) : (Dbg < 2.5 ? N * 0.5 + 0.5 : (Dbg < 3.5 ? Rough.xxx : (Dbg < 4.5 ? float3(wf, cf, gust) : Lag.zzz))); Emis = 0; Opac = 1.0; return dv; }
return float3(0.74, 0.76, 0.75);   // foam albedo (SLW: base colour covers the water by Opacity)
#undef NZ
''' % dict(wx=WIND[0], wy=WIND[1], sx=SHORE_BOX[0], sz=SHORE_BOX[1], sw=SHORE_BOX[2], sh=SHORE_BOX[3], big=big, cap=cap, hmax=WAVE_MAX * 0.5,
           ss='%(SCAT)s', sa='%(ABS)s')


# body optics per metre (tuned against CITY-SPEC C14 and the refs; see docs/night1/water/HANDOFF.md)
SCAT = (0.07, 0.09, 0.078)
ABS = (0.50, 0.34, 0.56)
PHASE_G = 0.55
GLITTER = 1.0


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
    for src, name in (('water_noise.png', 'T_WaterNoise.png'), ('shore_dist.png', 'T_ShoreDist.png'), ('water_grid.glb', 'SM_WaterGrid.glb')):
        shutil.copyfile(os.path.join(SCR, src), os.path.join(stage, name))
    import_files([os.path.join(stage, 'T_WaterNoise.png'), os.path.join(stage, 'T_ShoreDist.png')], ROOT + '/Textures')
    for name in ('T_WaterNoise', 'T_ShoreDist'):
        tx = load(f'{ROOT}/Textures/{name}')
        tx.set_editor_property('srgb', False)
        tx.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP if name == 'T_WaterNoise' else unreal.TextureCompressionSettings.TC_GRAYSCALE)
        if name == 'T_ShoreDist':
            tx.set_editor_property('address_x', unreal.TextureAddress.TA_CLAMP); tx.set_editor_property('address_y', unreal.TextureAddress.TA_CLAMP)
        EAL.save_asset(f'{ROOT}/Textures/{name}')
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
    dbg = expr(unreal.MaterialExpressionScalarParameter, -1400, 1100, parameter_name='Dbg', default_value=float(os.environ.get('SM2_WATER_DBG', '0')))
    dbgk = expr(unreal.MaterialExpressionScalarParameter, -1400, 1200, parameter_name='DbgK', default_value=float(os.environ.get('SM2_WATER_DBGK', '3000')))
    code = hlsl_ps().replace('VARK', '%.3f' % VAR_K) % dict(SCAT='%.4f, %.4f, %.4f' % SCAT, ABS='%.4f, %.4f, %.4f' % ABS)
    ps = custom('WaterPS', code, [('Lag', vi), ('WPos', wpos_ps), ('Cam', cam2), ('T', tim2), ('tN', tN), ('tS', tS), ('SunDir', sund), ('SunE', sune),
                                  ('DNW', dnw), ('PD', pd), ('GlitterK', gk), ('Dbg', dbg), ('DbgK', dbgk)],
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
    def view_map(path, rig, v, water=True, dolly=None):
        world = open_level(path)
        add_sublevels(world, [CITY_GEO, BOXES, RIG % rig, ACTORS] + ([LEVEL] if water else []))
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
