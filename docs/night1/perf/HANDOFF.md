# F 4K/60 perf: handoff after round 01

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/perf`, worktree `~/sm2-n1/perf`. All numbers below were measured on the build of integration `Opus-5.5-Loop-Night-1` at 1bbd260 (Manhattan content built 2026-09-29 22:25, binaries built 21:49 with the capture gate). The branch now also merges integration e0ada6c
(look R2, water, combat, life) at the source level only: NOT rebuilt, NOT re-measured; the only difference to integration's `unreal/` tree is the 5-line capture gate.
UE MCP port 8778 (unused: everything is `-game` runs plus headless commandlets). Owns `tools/perf_ue2/` (successor of P4's `tools/perf_ue/`, which it imports) and `docs/night1/perf/`.
Scratch `/Users/midir/sm2-n1/_scratch/perf/` (built export, textures, staged P2 inputs; NOT committed). Content (`unreal/WebHomage/Content`, 885 MB, script-built, never committed) is the untouched
Manhattan build of 2026-09-29 22:25 (restored from `_scratch/perf/content_backup` after the content experiments; `perf_content.sh restore` re-does it).
Spec `SPEC.md`, shot list `SHOTLIST.md`, evidence `round-01/` (`NOTES.md` = facts and every probe, `TABLE_probes.md` = every run, `perf/` = the official runs, `stills/`, `cmp/`, `route_30s.mp4`). No critic has scored it yet.

## Result (all runs `gpu_slot.sh perf`, exclusive, `perf_valid: true`, 3840x2160 OUTPUT, 30 s Manhattan route, fixed step, control and presets in the same sessions)
| config | internal | p50 ms (fps) | p95 ms (fps) | SPEC |
|---|---|---|---|---|
| defaults (as found), TSR 50 % | 1920x1080 | 26.45 (37.8) | 32.09 (31.2) | - |
| defaults, TSR 67 % | 2573x1447 | 31.20 (32.1) | 37.43 (26.7) | - |
| defaults, native | 3840x2160 | 42.52 (23.5) | 50.13 (19.9) | - |
| **perf60**, TSR 50 % | 1920x1080 | **16.44 (60.8)** | 19.86 (50.3) | P1 pass (16.67), P2 short (18.2) |
| perf60_mpe6, TSR 50 % | 1920x1080 | 15.79 (63.3) | 19.00 (52.6) | reserve preset; stills vs perf60 SSIM 0.993-0.996 |
| perf60, TSR 58 % | 2227x1253 | 17.76 (56.3) | 20.83 (48.0) | - |
| perf60, TSR 67 % | 2573x1447 | 19.61 (51.0) | 22.54 (44.4) | - |
| perf60, native | 3840x2160 | 28.65 (34.9) | 32.25 (31.0) | - |
| defaults, S2 static view (42 m over the avenue), TSR 50 % | 1920x1080 | 21.39 (46.8) | 26.96 (37.1) | - |
| **perf60**, S2 static view, TSR 50 % | 1920x1080 | **13.39 (74.7)** | 17.32 (57.7) | P3 pass (18.2) |
| perf60_mpe6, TSR 46 % | 1766x994 | 15.39 (65.0) | 18.53 (54.0) | reserve: p95 0.3 ms short |
| perf60_mpe6, TSR 42 % | 1613x907 | 14.45 (69.2) | 17.47 (57.2) | reserve: P1 and P2 pass |
(The three reserve rows are one session without a same-session control; `f_perf60_sp46` = perf60 with mpe4 at TSR 46 %: 16.03 / 22.72, its p95 is a cold run (50 hitch frames). Going from 50 to 46 % buys only ~0.4 ms of p50: the fixed 4K-output floor, not the internal resolution, is what is left.)
351 of the route's 1800 frames (256 of the last 600) exceed 18.2 ms; see "What is left". Earlier project numbers (contaminated, capture gate on) were 52 ms at TSR 67 %.

## The perf60 preset (this is what to adopt) = `tools/perf_ue2/overrides/perf60.cvars`
```
r.Nanite.MaxPixelsPerEdge=4                          # -5.4 ms. Nanite measures the error against the OUTPUT resolution: 4 px at 4K = 2 px of the 1080p internal. Trees / street furniture only.
r.Lumen.HardwareRayTracing=0                         # -4.6 ms. Software Lumen (surface cache + mesh SDF); Lumen GI and reflections stay on. THE QUALITY TRADE: bounce colour and glass reflections change (cmp/)
r.Shadow.Virtual.ResolutionLodBiasDirectional=1      # -0.7  (cheap)
r.SkyLight.RealTimeReflectionCapture.ResolutionOverride=64   # -0.4
r.VolumetricFog.GridPixelSize=16                     # -0.3
r.VolumetricCloud.ViewRaySampleMaxCount=256          # ~-0.1 (512 was -0.2)
r.Shadow.Virtual.SMRT.RayCountDirectional=4          # -0.3
r.SkyLight.RealTimeReflectionCapture.TimeSlice=1     # -0.1
r.Shadow.Virtual.ResolutionLodBiasDirectionalMoving=1  # -0.1
```
Apply at startup (`-dpcvars=` + `-ExecCmds`, or a Mac device profile), never in `DefaultEngine.ini` (integrator-owned). Everything else the round probed gave nothing (NOTES.md section 3).
Pending decision for the owner / director: (1) TSR 50 % (1080p internal) is the honest 4K/60 budget; TSR 58 % = 56 fps p50, 67 % = 51 fps. (2) Software Lumen (-4.6 ms) is required to be at 60 at TSR 50 %;
hardware RT kept (Nanite error 4 + the cheap set) measured 22.4 ms p50 at TSR 50 % in a slower session. (3) mpe6 (-0.65 ms p50, -0.86 ms p95) is visually indistinguishable from mpe4 in the four stills (SSIM 0.993-0.996, `cmp/perf60mpe6_vs_perf60`); adopt it if the look critic agrees.

## What other pieces must adopt (nothing outside `tools/perf_ue2`, `docs/night1/perf` and the C++ gate below was edited)
1. **P3 traversal / C manhattan (REQUIRED, -11.6 ms):** `Source/WebHomage/Traversal/WebTravCharacter.cpp` `BeginPlay`: the hero-mask + full-scene-depth `SceneCaptureComponent2D` pair is created only when
   `-WHTravMask` is on the command line (diff: `round-01/p3_capture_gate.diff`, already in this branch). Route / anim / hero-mask telemetry checks must pass `-WHTravMask`; perf and movie runs must not.
2. **P4 look:** add the perf60 cvars to a Mac device profile / preset step; look-critic pass on `round-01/cmp/` (software Lumen, mpe4). Untested lever that is yours: `clouds.tracing_max_distance` 50 km -> ~25 km (the cloud pass is 2.4 ms in the far
   third of the route and ignores every cvar).
3. **P1 city (optional):** nothing measurable is left in the kit / hinterland / mobility (section 4 of NOTES.md); do not spend a round on them for perf.
4. **A gpu lock:** trace and `perf_route` sessions hold the lock ~10 min; with 5 capture holders the exclusive wait was 5-10 minutes per session.

## Commands (repo root; editor closed; every game launch goes through the lock)
```
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
python3 tools/perf_ue2/perf_queue.py --out <dir> --configs "base50@50,perf60_50@50+set:perf60,x@50+set:perf60+r.Some.Cvar=1+flag:-WHTravMask" [--tag s] [-- --res 1920x1080 | --script none --map /Game/Maps/Manhattan_View_S2 | --trace cpu,gpu,frame]
     # = gpu_slot.sh perf sessions (<= 15 min hold, exit 75 retried); name@SP+set:<overrides/stem>+cvar=value+flag:-Flag; result.json per config
python3 tools/perf_ue2/make_table.py <dir> [<dir> ...] --md TABLE.md     # p50 / p95 / p95 of the 2-frame mean / GPU p95 / lock verdict; python3 tools/perf_ue2/attribute.py <session dirs> = deltas + GPU passes
python3 tools/perf_ue2/insights_frame.py <trace.utrace> --t0 60 --out <dir>   # headless Unreal Insights: GPU queue holes, what the render thread waits on (no window)
$G capture --label perf -- tools/perf_ue2/stills.sh <out> 50 "set:perf60"     # 4K stills S1 / S2 / S7 + route t20 / t28;  route_movie.sh <out> = 1080p60 clip
python3 tools/perf_ue2/compare_stills.py <before_dir> <after_dir> <out_dir>   # PSNR / SSIM / luma / near-black / clipped + side-by-side + 4x diff
tools/perf_ue2/perf_content.sh apply static,far_plain,kit_plain,tree_lumen,... | restore    # local content experiments (perf_apply.py); backs up first
tools/perf_ue2/perf_matrix.sh <out> "<configs>" step1 step2 ...                # cumulative content variants, one perf session each
```
`/Game/PerfF/View_S7` (sunset cross street) is made by `tools/perf_ue2/make_views.py` after C's `map` step (local content). Rebuild of the whole map: `python3 tools/perf_ue2/build_map.py` (C's build_manhattan with a slot-wait fix, ~12 min).

## Method rules learned (each cost a wrong conclusion once)
- **Every delta needs a control in the same session** (sessions drift up to 1.6 ms). Warm every new cvar set once before measuring (new shader permutations hitch the first run: p50 fine, p95 / avg garbage).
- **The frame p50 is the truth, not `GPUTime`, not the per-pass table.** A pass can vanish from the table (`RayTracingScene` 1.5 -> 0.05) without the frame moving.
- Nanite / TSR costs depend on the OUTPUT resolution: a 1080p-output run is not a 4K run at 50 %. Always run 3840x2160 output.
- p95 of the raw frame time is the SPEC line; `make_table.py` also prints p95 of the 2-frame mean (the fixed-step loop alternates long / short frame pairs; it changes p95 by ~0.5-1 ms).
- Perf runs take the exclusive lock and wait for every capture; other agents' captures make that 5-10 minutes per session. Batch configs into as few sessions as the 15 min hold allows (perf_queue does).
- Content changes made by `perf_apply.py` are LOCAL and reversible; nothing under `Content/` is ever committed. Never run `perf_content.sh apply` while a queue of yours is waiting for the lock.

## What is left (facts, ranked by ms in the failing part of the route)
1. **p95 19.9 ms vs 18.2:** the last third of the route (hero over the far LOD): VolumetricCloud 2.4 ms + NaniteVisBuffer 3.0 ms above the first third. Levers not yet measured: cloud `tracing_max_distance`, tree `ld_max_draw_distance`
   (`perf_apply.py props_far_cull`, written, not run), Nanite error 6 (-0.65, in the reserve rows), TSR below 50 %.
2. HWRT Lumen is a 4.6 ms feature here; a cheaper hybrid (HW reflections on glass only, software GI) measured -0.4 / -0.7 separately, the TLAS build is the fixed part. Not worth more time unless the look critic rejects software Lumen.
3. Fixed 4K-output floor: TSR 25 % still costs 14.1 ms (Nanite error against 4K output, VSM 2 ms, probe gather 1.6, clouds 1, TSR + post ~2-3).
4. Re-measure after merging look R2 / water / combat / life (they add lights, water, actors): the numbers above are for the 22:25 Manhattan build only.
5. The route leaves the detailed block at 22.6 s (C's issue 4): the last third is not representative street gameplay; a second route that stays in the block would separate "far LOD cost" from "street cost".
