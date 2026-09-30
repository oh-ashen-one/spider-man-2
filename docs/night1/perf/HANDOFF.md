# F 4K/60 perf: handoff after round 04

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/perf`, worktree `~/sm2-n1/perf`, pushed to `origin/night1/perf`. Owns `tools/perf_ue2/` (imports P4's `tools/perf_ue/run_perf.py`) and `docs/night1/perf/`. Scratch `/Users/midir/sm2-n1/_scratch/perf/` (NOT committed: export / tex staging, logs,
raw 4K stills `r03/before` (the as-found reference of this build), `r03/final`, `r04/final`, `r04/L3op`, `r04/L1op`, the round-04 clip frames were deleted).
Spec `SPEC.md` (P1-P11), shot list `SHOTLIST.md`, evidence `round-01` .. `round-04/` (`NOTES.md` = every fact of the round; `TABLE.md` = every run with its lock verdict; `LOOK_GATE.md`; `perf/<session>/`; `stills/`; `cmp/`; `route_30s.mp4`; `content_audit.json`).
Critics: round 01 FAILS, round 02 APPROACHES, round 03 FAILS (look regression, VSM p95; `critic/`). Round-04 blind pack: `/Users/midir/sm2-n1/_scratch/critic-F-r04/pack` (key `pack.key.json` next to it, `pairs.json`), not scored yet.

## ROUND 05 IN PROGRESS (interim note, rewritten at the end of the round)
- Merged `origin/Opus-5.5-Loop-Night-1` (fast-forward to 3aa92ba: traversal r14, characters r6). Rebuilt with `build_map.py --steps cpp,characters,map` (city / look inputs unchanged; P2 inputs staged from P2's worktree head 8ab861a = r07 WIP, C's staging rule).
- Round target (round-04 critic): tree leaves / crowns / bark in the ray-tracing scene as <= 1 k merged proxies. New: `tools/perf_ue2/tree_proxy_dump.py` + `tree_proxy_build.py` (build_map step `tree_proxy`), `perf_apply.py` step `rt_proxy_trees` (402 tile meshes in `/Game/PerfF/RTProxy`, actors in `City/RTProxy`, hidden in game + affect-indirect-while-hidden = ray-tracing only; originals out of RT).
- Gotcha found: `render_in_main_pass = False` removes a primitive from ray tracing and from Lumen card capture (engine `RayTracingMaterialHitShaders.cpp` 512, `LumenSceneRendering.cpp` 400). Use `hidden_in_game + affect_indirect_lighting_while_hidden` (`RayTracing.cpp` 1368).
- Life: `tools/perf_ue2/build_life_variant.sh` -> `/Game/PerfF/Life/Manhattan` (perf spec `name@ini+variant:Life`).

## State at the end of round 04 (all numbers `round-04/NOTES.md`; exclusive `gpu_slot.sh perf`, `perf_valid`, 3840x2160 output, internal 1920x1080, 30 s route, fixed step)
Shipped path on the rebuilt integrated map (build = integration c4fffda, same as round 03), no per-run cvars (`@ini`):
preset `tools/perf_ue2/overrides/perf60_hwl2.cvars` (= `perf60_hwl` + far-shadow culling off + conservative clipmap culling + cloud samples spread over 50 km + RT culling angle 3) + `r.ScreenPercentage 50`,
content = rebuilt + `perf_apply rt_lite_trees,tree_rt_opaque,cloud` (tree leaves back in the RT scene and opaque there, bark / props / hinterland / far ground out, cloud 20 km).
| line | result | pass |
|---|---|---|
| P1 p50 <= 16.67 | 16.08 / 16.03 / 16.11 (`f1/ship_a/b/c`) | yes |
| P2 p95 <= 18.18, 0 hitches | 18.03 / 18.03 / 18.05, 0 hitches | yes, **margin 0.13-0.15 ms** |
| P10 ShadowDepths p95 <= 2.5 | 2.44 (round 03 4.22) | yes |
| P3 static S2 | 14.66 | yes |
| P11 canopy +-10 %, route saturation 5 %, clouds 20 km | S1 0.912 .. t42 1.042; sat -1.7 .. +2.0 %; t42 sky detail 1.013 | yes |
| P11 round-02 S1 crop >= 0.97 | **0.9508** (round 03 0.4998) | **no** |
| P6 cloud last 600 <= 0.7 | 1.05 (superseded by 20 km) | no |
| P8 frame - GPU <= 1.0 | 1.40 (leaf instances in the RT scene) | no |
The VSM cause was REVEALED non-Nanite primitives (far-shadow culling + frustum-clipped caster volume re-reveal primitives every frame of a swinging camera; each reveal invalidates all pages of the primitive). Details and every A/B: `round-04/NOTES.md` sections 2-4.

## How to reproduce / rebuild (editor and game closed; every game launch through the lock; never run a commandlet while your own perf session runs: it contaminates it, see NOTES 7)
```
python3 tools/perf_ue2/build_map.py                                   # ALL steps (~11 min, no GPU): cpp .. map, then perf_apply (rt_lite_trees,tree_rt_opaque,cloud 20 km), perf_preset (perf60_hwl2), perf_audit (-> round-04/content_audit.json)
python3 tools/perf_ue2/build_map.py --steps perf_apply,perf_preset,perf_audit      # only the perf state on built content
python3 tools/perf_ue2/build_map.py --preset-off                      # remove the preset block from Config/Mac/MacEngine.ini (as-found runs; content changes stay: rebuild content for a true as-found)
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
python3 tools/perf_ue2/perf_queue.py --out <dir> --tag x --configs "warm@ini,a@ini,b@ini,s2@ini+view:S2" -- --budget-s 870
$G capture --label perf -- tools/perf_ue2/stills2.sh <out> "ship@ini" "S1 S2 S7 route"     # env SM2_PERF_ROUTE_SHOTS=20,28,38,42
$G capture --label perf -- tools/perf_ue2/route_movie.sh <out> "movie@100+set:perf60_hwl2"
python3 tools/perf_ue2/look_gate.py /Users/midir/sm2-n1/_scratch/perf/r03/before <stills dir>      # the P11 gate (round-02 crops, canopy, saturation, sky)
VSM stats in a perf CSV: add +flag:-csvCategories=VSM to a config (costs ~0.3 ms; diagnostic only)
Local A/B maps: make_variants.py (Cl<km>), make_rtvars.py (RTvA-F, RTvL = leaves only; env SM2_PERF_RTVAR_CLOUD_KM=20 -> RTv<tag>k20); /Game/PerfF/* is local, never committed
```
- `unreal/WebHomage/Config/Mac/MacEngine.ini` is GENERATED and UNTRACKED: never `git add -A` / `git add unreal`. Content (`Content/`, DDC, Intermediate) is local and was kept (a fresh builder needs it; rebuild = 11 min).
- Every F launch passes `-notraceserver`. Stop an engine only with `_scratch/gpu/bin/stop_ue.sh "<pattern of your own path>"`. One Unreal process of F at a time. Start every perf session with a throw-away `warm@ini`; deltas need a control in the same session.
- Csv files are committed gzipped and logs pruned (keep `csv.csv.gz`, `*_perf.json`, `result.json`, `run.txt` per config).

## Decisions and open items (facts, ranked)
1. **P2 margin is 0.13-0.15 ms.** Cheapest measured lever: every RT instance opaque (`r.RayTracing.DebugForceOpaque 1`, debug cvar: `z1/ship_op` 15.82 / 17.73, +0.3 ms margin; the remaining masked RT geometry is the street kit / detail tiles). A per-asset form = `enable_section_force_opaque` on those tile meshes (not tried: masked railings / fire escapes would become solid in reflections).
2. **Round-02 S1 crop 0.9508 < 0.97**: the crop is street-tree canopy; opaque leaf cards over-darken the crown interior (canopy -8.8 %). Keeping the LOD0 street-tree leaves masked (`SM2_PERF_OPAQUE_SKIP=_l0_`) is closer but costs +0.6 / +0.9 ms (fails P2). Needs ~0.9 ms p95 found elsewhere (P1's shade-fill march, Lumen budgets, TSR 48).
3. P8 regressed to 1.40 ms: the 42 k leaf instances in the RT scene add CPU work per frame (per-instance RT culling). Fewer tree instances (merge leaves + crown per tree, or a coarser tree set for RT) would cut it.
4. **Integrator:** adopt `perf60_hwl2` + `r.ScreenPercentage 50` as a `[Mac DeviceProfile]` block, and the content policy (tree leaves in the RT scene + force-opaque sections, hinterland / props / far ground / bark out, cloud 20 km) in `build_city.py` / `look_presets.json` (P1 / P4 files) or run `perf_apply` after the build.
5. Not merged this round: `origin/Opus-5.5-Loop-Night-1` (traversal camera r13, characters r5-r6). Merge + rebuild + re-measure next round (the camera change moves the route frames). The map still has no life / water / combat content.
6. Hero and street people remain out of the RT scene (1.5 ms to put the hero back, round 03).
