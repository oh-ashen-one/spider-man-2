# F perf, round 06: notes (neutral facts, no self-assessment)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Numbers are from the RUNNING game (`-game`, offscreen, 3840x2160 back buffer, **internal 1920x1080 = TSR 50 %**, read back from `wh_perf.internal_w/h`)
> on the rebuilt integrated `/Game/Maps/Manhattan` (golden rig), the 30 s swing route `route_30s_warmup15.json`, window = game s 15..45, fixed step (`-benchmark -fps=60`), CSV profiler (1800 frames per run).
> Every perf run inside `gpu_slot.sh perf` (exclusive, `perf_valid`, util before 0 %, one Unreal instance, `-notraceserver`; no Unreal Insights / trace server / ProfileGPU was used).
> Official session: **`perf/f1`** (`exclusive=true perf_valid=true contaminated=false util_before=0 util_after=0 util_during_avg=71.4 instances_before=0 wait_s=124.5 hold_s=705.8`).
> Exploration sessions (all valid exclusive): `perf/x1`, `perf/y1`, `perf/z1`, `perf/w1`. Per-session tables `perf/<s>/TABLE.md` (perf_route) and `perf/<s>/PASS_DIFF.md` (`tools/perf_ue2/pass_diff.py`: CSV p50/p95, in-game p95, thread times, mean GPU passes, deltas vs a same-session control).

## 0. Build
Same build as round 05 (integration 3aa92ba, P2 inputs from 8ab861a). Traversal r15/r16 and characters r7 were NOT merged this round, so the round-05 numbers stay like-for-like. Content changes: `perf_apply` step `rt_occluders` (below). Preset: `perf60_hwl3` (below) baked into `Config/Mac/MacEngine.ini` by `build_map.py --steps perf_preset`.

## 1. Round target and result (official session `perf/f1`, spec `@ini` = shipped path, no per-run cvars)
| line (task brief / r05 critic) | target | result | pass |
|---|---|---|---|
| life ON (`/Game/PerfF/Life/Manhattan`, P6 traffic + crowd) CSV p50 | <= 16.67 ms | **16.21 / 16.27 / 16.19** (lwarm 16.16) | **yes** |
| life ON CSV p95 | <= 18.0 ms | **18.38 / 18.84 / 18.36** (lwarm 18.28) | **NO** (+0.36 / +0.84 / +0.36) |
| life ON in-game `wh_perf` p95 | reported | 18.93 / 19.58 / 18.94 | (P2 line 18.2: no) |
| life ON hitches (> 25 ms and > 2x median) | 0 | 0 / **14** / 0 | **no in life_b** |
| `LumenScreenProbeGather` saving | >= 1.3 ms | **0** in the shipped preset (2.94-3.00 ms; see 2) | **NO** |
| +1.24 ms life `GPU/Unaccounted` attributed and cut | | = the GPU skin cache; cut by `r.SkinCache.Mode=0`: life Unaccounted 2.31 -> 1.24 ms (= ship level) | yes |
| S1 crop (485,0,710,490) SSIM vs as found | >= 0.97 | **0.9294** (round 05 0.9292) | **NO** |
| S1 recess (1920 space x1700-1850 y540-650) luma | 17.5 +-10 % | **18.0** (as found measured 17.3 here; 1.04x); round 05 29.6 | **yes** |

life_b: a burst of slow frames at window frames 1209-1288 (FT 25-55 ms) in which the game, render, RHI threads AND the GPU are all slow at once (`perf/f1/life_b/csv.csv.gz`); no PSO misses. The two other life runs of the same config have 0 hitches. Cause not identified (a machine-level stall; the GPU lock only knows about Unreal processes, and a local MLX model of another session runs on this machine). Not removed from the result.

Ship (no life) in the same session: CSV p50 15.58 / 15.49 / 15.44, CSV p95 17.72 / 17.62 / 17.61, in-game p95 17.70 / 17.68 / 17.63, 0 hitches (round 05: 15.65-15.72 / 17.75-17.79 / in-game 17.81-17.87). P3 static S2: p50 14.52, p95 15.76.
Other spec lines, same session: P8 mean FrameTime - GPUTime ship 1.72 / 1.15 / 1.34, life 0.95 / 0.78 / 1.01 (`perf/f1/serial.json`; Metal per-process GPUTime offset, SPEC P8 caveat) - **fails the 1.0 line in the ship runs**. P10 `GPU/ShadowDepths` p95 2.65 / 2.65 / 2.65 ship, 2.72 life - **fails 2.5** (no VSM change this round; round-05 value not re-derived). P6 cloud last-600-frame mean 0.55-0.58 ms (20 km, superseded by P11).
Same-session controls with the round-05 preset (`r5ship`, `r5life` = `@ini` + `r.SkinCache.Mode=1` at startup): r5ship 15.74 / 17.99; r5life 17.25 / 22.11 with 4 hitches and RHI 6.7 ms. r5life is worse than the round-05 life runs (17.1 / 19.4-19.6) and than x1 `life` (17.12 / 19.47, skin cache on from the ini): switching the cache back on per run is not a faithful round-05 control; the clean skin-cache attribution is x1 (`life` vs `lsk0`) and the 7 life runs of z1.

## 2. What was found and done
### 2a. Life cost (P6 traffic + crowd): GPU skin cache
- x1: crowd off (`-WHCrowdOff`) -1.21 ms FT / Unaccounted -0.77; traffic off -0.08; crowd shadows off -0.11; **`r.SkinCache.Mode=0` -1.04 ms FT p50 (17.12 -> 16.08), p95 19.47 -> 18.23, `GPU/Unaccounted` -1.05 ms, RHI thread 5.09 -> 2.90 ms, LumenSceneUpdate -0.21.** ~600 live skinned citizens = ~600 skin-cache compute dispatches per frame that sit outside every GPU stat scope on Metal.
- z1 (7 life runs with skin cache off): p50 16.11-16.26, p95 18.22-18.52. Crowd density 75 % (`-WHLifePerKm=1200:825`): no change (the live set is capped by the 600-component pool). y1: crowd shadow radius 30 m, view margin 15 deg: no change. w1: crowd fill light off (`-WHLifeFill=0`) -0.10 ms.
- Remaining life cost vs ship with skin cache off (z1 means): FT +0.62 ms; GPU passes Basepass +0.17, NaniteVisBuffer +0.13 (moving traffic), RenderVelocities +0.10, ShadowDepths +0.09, LumenScreenProbeGather +0.08, Lights + DeferredLighting +0.10 (fill light); game thread 1.9 -> 4.4 ms (not the bound: frames are GPU-bound, see 3).
- Look: skin cache off is neutral: S1 / S2 / S7 full-frame SSIM vs the round-05 preset 0.990 / 0.991 / 0.996, S2 crops 0.992 / 0.974; the hero and citizens render normally in the route stills (`stills/life_route_t20.jpg`). Nothing in the project uses recompute-tangents, morph targets or skinned meshes in ray tracing.
- Shipped: preset `overrides/perf60_hwl3.cvars` = `perf60_hwl2` + `sk0` (`r.SkinCache.Mode=0`).

### 2b. LumenScreenProbeGather (2.96 ms): the probe-density lever does not exist in this game
- **The running game already applies the engine "High" GI scalability**: every run log has `Applying CVar settings from Section [GlobalIlluminationQuality@2]` (and AA / Shadow / PostProcess @2) after the Epic @3 sections. Screen probes are therefore already one per 32 px tile with 16 adaptive probes, radiance cache 16 / 100, surface-cache relight 64 / 128. This explains why `spg_a` (DownsampleFactor 32), `rch` (radiance cache High), `lsu` (relight rate High) measured 0 and `spg_c` (24 px, i.e. denser) +0.26 ms.
- Measured knobs (pass mean delta / frame-time delta vs a same-session control):
| knob | ScreenProbeGather | FT p50 / p95 | look (S1 crop / recess / full frame vs hwl2) | verdict |
|---|---|---|---|---|
| tiles 24 px (`spg_c`) | +0.26 | +0.30 / +0.24 | 0.894 | denser than the game's 32 |
| tiles 48 px (`ds48`) | -0.19 | -0.16 / -0.15 (ship), life -0.13 / -0.10 (vs mean of lk_a, lk_b) | crop **0.870**, full 0.959, blotchy canopy GI | rejected |
| tiles 64 px (`ds64`) | -0.28 | -0.27 / -0.29 (ship), life p95 18.14-18.23 (still > 18.0) | crop **0.852**, recess 1.10x, full 0.950 | rejected |
| tracing octahedron 4 (16 rays / probe) | -0.26 | -0.27 / -0.22 | crop **0.880**, recess 1.11x, full 0.965 | rejected |
| short-range AO off | -0.06 | -0.14 / -0.15 | not shipped (diagnostic) | - |
| translucency GI volume off (`tv0`) | +0.07 (LumenReflections -0.23) | -0.17 / -0.19 | recess **1.26x**, S7 +5 % luma | rejected |
| radiance cache High (`rch`), relight rate High (`lsu`), irradiance format / stochastic interpolation (`spg_b`, `spg_d`) | 0 | 0 | - | already the game's setting / no effect |
- Even the strongest density cut (64 px) leaves life p95 at 18.14-18.23 ms.

### 2c. S1 recess (round-05 critic): sidewalk sheds back in ray tracing
- Cause: `rt_lite` / `rt_lite_trees` took every `City/Props` component out of the ray-tracing scene, including the sidewalk-shed roofs (`ISM_shed` / `ISM_shedtop`); hardware-RT Lumen GI rays passed through them (recess: as found 17.3, round 03 38.4, rounds 04 / 05 ~29).
- New `perf_apply` step `rt_occluders` (default in `build_map.py` now): `ISM_shed, ISM_shedtop, ISM_shelter, ISM_busstop, ISM_kiosk, ISM_subway, ISM_dumpster, ISM_rolloff` back IN ray tracing (8 components, ~560 instances, <= 132 triangles each). Recess 18.0 (1.04x). Cost not separately measured (applied before every round-06 session; ship p50 15.44-15.58 vs round 05 15.65-15.72).

### 2d. S1 crop (round-02 crop, gate 0.97, not moved)
- Repeat noise of THIS crop for the same content and settings: 0.969 (`st/base` vs `st/base2`), 0.964 / 0.966 (`spgb` / `spgd` vs `base`); round 05 0.986 / 0.964. Single captures of the shipped content against the as-found still: 0.905, 0.917, 0.913, 0.927, **0.929 (final)**.
- With the as-found render settings on today's content (`asfl`: Epic VSM -1.5 bias + 8 SMRT rays, TSR history 200 %, Nanite error 1): 0.940. The remaining gap is the ray-tracing representation of the canopy (merged opaque proxies vs the as-found alpha-masked leaves); the round-04 content (masked leaves) read 0.945-0.951.

## 3. Where the life frame goes (z1 / f1)
GPU-bound: in the p95 frames (`lk0`) GPUTime 17.0 vs 14.9 in the p50 frames, game thread 4.4 either way, RHI 2.9. p95 per 2.5 s block of the window (y1 `lk0`): 16.5 17.9 18.2 18.7 18.9 18.4 18.9 18.0 18.0 17.1 16.4 16.1, i.e. window s 5-22.5 carry the p95; ship (`warm`) 15.6 17.0 16.9 17.6 18.1 17.5 18.2 17.9 17.7 17.0 15.9 15.8.

## 4. Look (`LOOK_GATE_raw.md`, `s1_gate.json`, `crops_r02.json`; stills `stills/final_*.jpg` = 1920x1080 JPEG of the 3840x2160 PNGs, internal 1920x1080; `stills/life_route_*.jpg` = the same with traffic + crowd)
- S1: crop 0.929 (fails 0.97), recess 18.0 (passes), canopy luma 0.996, saturation 1.004, full-frame SSIM 0.977. S2 crops: windows 0.994, gold 0.984. S7 saturation 1.005.
- Route stills are on P3's r14 camera (since round 05), the as-found route stills are on the old camera: the route rows of the look gate (t28 / t38 saturation "FAIL", sky ratios) compare different frames and are not evidence either way.
- `cmp/S1_recess_asfound_r05_r06.jpg`, `cmp/S1_crop_r02_asfound_r05_r06.jpg`, `cmp/S1_asfound_r05_r06.jpg`, `cmp/S1_crop_rejected_cuts.jpg` (shipped vs translucency-volume-off vs octahedron-4 vs 48 px).
- Disclosed visual differences vs as found (unchanged from round 05 unless said): leaf-level canopy GI pattern (proxies); far trees as every 16th card enlarged in ray tracing; proxies not in reflection captures; characters out of ray tracing; far shadows from VSM; cloud 20 km; **new: skinning in the vertex shader (no visible difference measured)**.

## 5. Clips
See `CLIPS.md`.

## 6. Critic pack
`/Users/midir/sm2-n1/_scratch/critic-F-r06/pack` (key `pack.key.json` next to it, `pairs.json`).
