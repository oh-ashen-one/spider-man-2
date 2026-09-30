# F 4K/60 perf: handoff after round 03

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/perf`, worktree `~/sm2-n1/perf`, pushed to `origin/night1/perf`. Owns `tools/perf_ue2/` (imports P4's `tools/perf_ue/run_perf.py`) and `docs/night1/perf/`. Scratch `/Users/midir/sm2-n1/_scratch/perf/` (NOT committed: export / tex / chars staging, logs, `r03/` raw 4K stills, movie frames were deleted).
Spec `SPEC.md` (P1-P9), shot list `SHOTLIST.md`, evidence `round-01/`, `round-02/`, `round-03/` (`NOTES.md` = every fact of the round; `TABLE.md`, `SERIAL.md`, `perf/<session>/`, `stills/`, `cmp/`, `lookprobe/`, `route_30s.mp4`, `content_audit*.json`).
Critics so far: round 01 FAILS TARGET, round 02 APPROACHES TARGET (`critic/`). Round 03 blind pack: `/Users/midir/sm2-n1/_scratch/critic-F-r03/pack` (key `pack.key.json` outside it, `pairs.json`), no critic has scored it yet.

## ROUND 04 IN PROGRESS (WIP note, 2026-09-30 ~13:40; the full rewrite comes at the end of the round)
- Target (round-03 critic): VSM ShadowDepths p95 <= 2.5 ms, trees within 100 m back in the RT scene, cloud TracingMaxDistance >= 20 km, look re-gated on the ROUND-02 S1 crop + canopy luma +-10 % + route saturation +-5 % vs `_scratch/perf/r03/before`; p95 <= 18.18, p50 <= 16.67 on the shipped path.
- Found (session `round-04/perf/v1`, VSM CSV stats `-csvCategories=VSM`): the ShadowDepths spikes are REVEALED non-Nanite primitives (CPU-culled -> unculled for the clipmap, `r.Shadow.Virtual.Cache.DebugSkipRevealedPrimitivesInvalidation 1`: ShadowDepths p95 4.19 -> 2.39 ms; skip all dynamic invalidation 2.25). ~54 dynamic pages invalidated per frame.
- Tools: `tools/perf_ue2/look_gate.py` (the gate), `make_rtvars.py` env `SM2_PERF_RTVAR_CLOUD_KM` (variant RTvCk20 = trees in + cloud 20 km); local variants Cl20, RTvCk20 exist.

## State at the end of round 03 (numbers: `round-03/NOTES.md`; all exclusive `gpu_slot.sh perf`, `perf_valid: true`, 3840x2160 output, 30 s route, fixed step)
**Shipped path, on the REBUILT integrated map (integration c4fffda merged + rebuilt by scripts), no per-run cvars:** internal 1920x1080 (TSR 50 %), preset `overrides/perf60_hwl.cvars` = full hardware-RT Lumen (GI + reflections), RT-lite scene (518 of 117 506 instances), cloud 4 km, Nanite error 8, skeletal meshes out of the RT scene.
| line | result | pass |
|---|---|---|
| P1 p50 <= 16.67 | 15.46 / 15.34 ms (`f1/hwl_a`, `hwl_b`) | yes |
| P2 p95 <= 18.18, 0 hitches | 17.88 / 17.91 ms, 0 hitches (margin 0.27-0.30 ms) | yes |
| P3 static S2 p50 <= 18.2 | 14.49 (p95 15.45) | yes |
| P6 cloud pass last 600 frames <= 0.7 ms | 0.49 | yes |
| P7 crop SSIM >= 0.97 (S1 glass / S2 windows / S2 gold, vs the as-found still of the same map at TSR 50) | 0.9733 / 0.9921 / 0.9773 | yes |
| P8 mean frame - GPUTime <= 1.0 ms | 0.82 / 0.83 (instrument caveat: it reads 1.2 / 2.7 ms for other processes with identical work; A/B evidence in NOTES section 3) | yes, weak |
| P9 shipped path (no per-run cvars, internal disclosed) | `@ini` runs report 1920x1080 | yes |
| P4 look lines | **S1 mean Y 92.1 -> 103.6 (line <= 100), route t20 89.5 -> 101.7, t42 98.7 -> 114.1: canopy / skyline brighter than as-found** (trees are not in the RT scene, hardware GI rays leave through them) | **no (disclosed)** |
What the serialisation was: the hero (animated skeletal mesh) in the ray-tracing scene = 1.5 ms of `GPU/RayTracingScene` every frame and 1.6 ms of frame time; people 0.1 ms; occlusion-query buffering, an update budget and Metal fast-build change nothing. Out of the RT scene (cvar line in the preset), hardware GI costs nothing measurable.

## How to reproduce / rebuild (editor and game closed; every game launch through the lock)
```
python3 tools/perf_ue2/build_map.py                              # ALL steps: cpp, city_export, city_prep, city_extra, city, traversal, characters, look, map, perf_apply, perf_preset, perf_audit (~11 min, no GPU)
python3 tools/perf_ue2/build_map.py --steps perf_apply,perf_preset,perf_audit   # only the perf state on already built content (idempotent)
python3 tools/perf_ue2/build_map.py --preset-off                 # remove the preset block from Config/Mac/MacEngine.ini (as-found comparison runs)
SM2_PERF_PRESET=perf60_hwrefl_sk0 SM2_PERF_PRESET_SP=48 python3 tools/perf_ue2/build_map.py --steps perf_preset   # the software-GI fallback preset (see below)
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
python3 tools/perf_ue2/perf_queue.py --out <dir> --tag x --configs "warm@ini,a@ini,b@ini,s2@ini+view:S2" -- --budget-s 870     # spec name@ini = shipped path (no cvar, no r.ScreenPercentage on the command line); name@SP+cvar=value = probes
$G capture --label perf -- tools/perf_ue2/stills2.sh <out> "ship@ini" "S1 S2 S7 route"     # env SM2_PERF_ROUTE_SHOTS=20,28,38,42
$G capture --label perf -- tools/perf_ue2/route_movie.sh <out> "movie@100+set:perf60_hwl"  # 1080p60 clip, watchdog = stop_ue.sh
python3 tools/perf_ue2/crop_ssim.py <ref_dir> <test_dir> [--sbs dir] [--set r03]             # P7 crops; compare_stills.py for whole stills (P4 luma lines); serial.py <run dir> (P8 chain fit)
python3 tools/perf_ue2/make_variants.py / make_rtvars.py         # local A/B map copies under /Game/PerfF (commandlets; env SM2_PERF_CLOUD_KM=4P, SM2_PERF_RTVARS=A,B,C,D,E,F)
```
- `unreal/WebHomage/Config/Mac/MacEngine.ini` is GENERATED and UNTRACKED: never `git add -A` / `git add unreal`; add explicit paths. Saved/Config ini files do not work for the preset (the engine deletes them at exit).
- Every launch of F passes `-notraceserver` (the engine otherwise auto-starts `UnrealTraceServer`, a listening process). Stop an engine only with `_scratch/gpu/bin/stop_ue.sh "<pattern matching only your own path>"`. One Unreal process of F at a time.
- The first config of a session is cold (p95 wrong): start every session with a throw-away `warm@ini`. Every delta needs a control in the SAME session (identical configs differ by +-0.1 ms p50 inside a session, up to 0.3 between sessions).
- Raw 4K PNG stills of the round are in `_scratch/perf/r03/{before,final}` (the pack holds re-encoded JPEGs). Local content (`Content/`, `Intermediate`, `DerivedDataCache`) was NOT deleted: a fresh builder needs it (rebuild = 11 min).

## Decisions and open items (facts, ranked)
1. **Owner / director decision: brighter canopy (shipped) vs darker software-GI look.** `perf60_hwl` passes every numeric line but the S1 / t20 / t42 luma lines; the fallback `perf60_hwrefl_sk0` at TSR 48 (software GI, hardware reflections) keeps luma within -2 .. -6 of as-found (p50 15.27 / 15.25, p95 17.61 / 17.86, `d1`) but fails the crop gate (0.943 / 0.980 / 0.943) and is 6 % darker on the route (round-02 critic).
2. **Fix the canopy brightness without the 2.2 ms of trees in the RT scene** (trees in: p50 17.67, p95 20.32; within 100 m 16.77 / 19.40; within 50 m 16.14 / 18.78 but it also culls facades beyond 50 m out of the reflections). Ideas, none tried: a decimated RT-only occluder set for the trees (extra HISM component, `render_in_main_pass False`, `visible_in_ray_tracing True`, every 2nd-3rd tree; expect ~0.5 ms, p95 margin is 0.27 ms) - needs a saving of the same size elsewhere;
   P1's shade fill march (`ShadeFill.ush` 28 steps, their to-do 2) is part of the 1.2 ms base pass; Lumen surface-cache update budgets; VSM 2.2 ms. Not F-owned files: ask the owner pieces.
3. **The hero is not in ray-traced reflections.** A cheaper hero instance needs code (a static / low-rate proxy in the RT scene); no cvar reduces it (`MaxUpdatePrimitivesPerFrame 1`, Metal fast build: no change). If the critic wants the hero mirrored, the price is 1.5 ms.
4. **Integrator:** adopt `overrides/perf60_hwl.cvars` + `r.ScreenPercentage 50` as a `[Mac DeviceProfile]` block (`DefaultDeviceProfiles.ini`, integrator-owned) and run `perf_apply rt_lite,cloud` (or move `visible_in_ray_tracing = False` for `City/Far`, `City/Props`, `City/far` and `tracing_max_distance 4` into `build_city.py` / `look_presets.json` of P1 / P4).
   `build_manhattan.py` (C) still lacks P1's `city_extra` tools (they are in `build_map.py` here) and does not build life / water / combat content: the map measured here has no moving traffic / crowd.
5. Re-measure when life / water / combat content is in the map (more lights, actors, skeletal meshes: the `SkeletalMeshes 0` line covers skeletal RT cost, but VSM / Lumen / Nanite will grow) and when P1 lowers the shade march cost.
6. The route leaves the detailed block at ~22.6 s (C's issue 4); a second route inside the block would separate far-LOD cost from street cost. The horizon cloud wisps are gone at 4 km (round 02); no cheaper horizon cloud found.
7. Not measured this round: native 2160p internal, TSR 58 / 67 with the new preset (TSR 58 measured with software GI: 19.0 p50), midday / night rigs (only the golden rig was timed; the cloud step covers all three).
