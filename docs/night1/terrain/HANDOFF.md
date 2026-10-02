# Terrain (piece E) — HANDOFF (round 02: pass 2 rendered, measured and packed; pass 3 partly rendered, 3b queued in the GPU lock)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/terrain` (pushed), worktree `/Users/midir/sm2-n1/terrain`, scratch `/Users/midir/sm2-n1/_scratch/terrain`, dev port 5209 (Vite, exports only).
Owns `/Game/Terrain`, `tools/export/{export_terrain.mjs,collect_terrain.js,gen_terrain_shaders.mjs}`, `tools/terrain/`, `unreal/WebHomage/Scripts/{build_terrain.py,terrain_materials.py}`,
`unreal/WebHomage/Shaders/Terrain/`, `docs/night1/terrain/`. Spec / shot list / cameras: `SPEC.md` (E8 added), `SHOTLIST.md`, `shots.json`.

## Round 02 target and what was done
Target (round-01 critic's biggest gap): trees / canopy at swing height. The flat hull crowns were the browser's `crownfar` pool drawn at every distance (HISM / Nanite ignore per-instance cull distances); the browser's `trees-*-near` (leaf cards 44-165 m) and
`trees-*-crown` (lumpy clump crowns 165-520 m) pools were never exported. Now (all committed; Content is generated, never committed):
- `collect_terrain.js` exports the whole park-tree chain (`trees-{park,elm,conifer}-{near,crown,crownfar}`, `trunks-*`) with each pool's `near / far / fadeIn / fadeOut`.
- Every band is a dithered material clip by camera distance (`unreal/WebHomage/Shaders/Terrain/Foliage.ush`: `tfBand`, `TerrainClumpCrown` = port of trees.js `crownMaterial`, `TerrainLeafCards` = port of `leafMaterial`) on 46 HISM pools / 47,710 instances
  (`build_terrain.py`, one material instance per pool, band = (near, far, 0): UE hands a VectorParameter to a Custom node as **float3**). ez L0 < 20 m, ez L1 to 44 m, leaf cards 44-165 m, clump crowns 165-520 m, `M_TerrainCrown` (crownfar) only >= 520 m.
  The clip is skipped in shadow-depth and Lumen-card-capture passes (`SHADOW_DEPTH_SHADER`, `LUMEN_CARD_CAPTURE`; Nanite depth-only raster defines `SHADOW_DEPTH_SHADER` too), so trees still cast shadows / bounce light at every distance.
  Derivatives are not used in ray tracing hit shaders (`RAYTRACINGSHADER`). The ez materials carry the Nanite usage flag (the round-01 game log said "missing usage flag Nanite ... Default Material will be used in game").
- Secondary: lawn albedo grade `LAWN_GRADE` (`terrain_materials.py`), picnic blankets brightened (their exported colours are linearised twice: near-black slabs), shots `p3` (raised), `p6`, `p7` (cameras moved: p6 sat above a pier-shed roof, p7 inside the far-bank masses).
- Merge preconditions: the two round-01 movies (and their contact frames) with the dev suit emblem are `git rm`ed; round-02 movies hide the hero (`ShowFlag.SkeletalMeshes 0`, verified on the frames); the park-reservoir pair uses a park-water-basin aerial frame cut from the library's pond clip
  (no frame of the Reservoir itself exists in the private refs: all street / traversal stills were scanned).

## Pass 1 (rendered 2026-10-02 01:33-01:49, hold 955 s; stills / movies kept local in `round-02/pass1/`, numbers committed there)
First run of the new materials: the **warm-up check caught a real compile failure** (float4 vs float3 `band`; hold aborted after 41 s, fixed, re-queued). Pass 1 numbers (`round-02/pass1/crown_stats.txt`, 24 hand-picked 150 px crown crops of p1_south):
far / mid crowns 6.6-10.5, near-right 6.9-10.0, foreground crowns (dark: luma 21-66) 2.2-5.9 -> **E8 FAIL** (min 2.23, median 6.66; round-01 on the same boxes: median 6.0). Flat hull faces: p10_lawn_eye max 20 px (PASS), p1_south max 72 px
(dark crushed foreground patches, not lit hull faces). Lawn: vivid green now (p10 crop G/R 1.20, sat 0.51; aerial crops G/R 0.78-0.96), E1 guard boxes 6.47 / 3.66 / 4.79 / 11.76 vs round 1 4.92 / 4.65 / 6.93 / 15.09 (the p9 / p4 boxes of round 1 contain tree parts).
Visuals: p2 Reservoir, p4 Great Lawn, p9 panorama, p8 pier read well; foreground canopy too dark; far crowns read as yellow lumpy "potatoes"; p6 / p7 cameras were against buildings (fixed for pass 2).

## Pass 2 (rendered 2026-10-02 03:44-04:08, committed in `round-02/`; critic pack built from it)
Changes since pass 1: crown contrast up (`Foliage.ush`: extra ~1 m octave, bump weights 3 / 0.5 -> 7.5 / 0.2, deeper gaps, clump contrast 0.42-1.35, tilt 0.0026 x distance), lawn grade (0.54, 1.20, 0.46), cameras p3 / p6 / p7, ambient-fill `Emis` on the leaf materials.
Result (`round-02/README.md`, `crown_stats.txt`): far / mid crowns 8.2-13.8 (most >= 9), dark foreground crowns still 2.2-5.7 (luma 21-66), 9 / 24 crops >= 9 -> **E8 not met**; p10 has no flat hull face > 40 px, p1 has 3 dark crushed patches (max 82 px).
**Diagnosis of the unchanged foreground**: `Emis` was wired (probed with a nullrhi commandlet) but 0.65 x albedo is ~1000x too small: the golden rig is physical (sun 44000 lux, EV 8.2-13, sunlit albedo A radiates ~10000 A cd/m2) -> pass 3 uses `Emis = c * 1800 * (0.4 + 0.6 expo)` (about a 15 % fill).
The pass-2 p7 camera sat inside a far-city mass (the browser export's `farCity*` boxes overhang the water up to 35 m along z -1080..-320 on both shores): p7 moved to z -1270 (no mass within 250 m of the shore). p6 (z -820) rendered fine.
A pass-1 -> pass-2 health event is documented in the README (monitor stopped the first 4K still launch with `WS-STARVED`, auto-pause, auto-lift after 10 calm min).

## Pass 3 (partly rendered 2026-10-02 05:19-05:22 into `docs/night1/terrain/round-02b/`; 3b queued)
Pass 3 = pass 2 + the physical emissive fill (`Emis = c * 1800 * (0.4 + 0.6 expo)`) + p7 camera at z -1270. It rendered `p1_south`, `p10_lawn_eye`, `p2_reservoir`, `p6_west_shore`, `p3_lake` and was then **stopped by the health monitor** (05:22:39 `WS-STARVED`, gpu 100 %, ws_cpu 2 %,
auto-pause, slots demoted to 1; a `look` perf engine was rendering at the same time = two heavy renders). I killed my own hold scripts by PID so nothing relaunches after the auto-lift. The effect of the fill is large: foreground canopy luma 40 -> 90, crown-crop min SD 2.25 -> 5.41, median 8.34 (same), 10 / 24 crops >= 9,
foreground crops 5.4-7.5 (round-02b `crown_stats`); p1_south now shows bright, leafy, autumn-tinted foreground trees. A flat patch > 40 px remains in p1_south (108 px max: the fill flattens deep shade).
**3b (queued)**: the missing stills `p4_greatlawn p7_east_shore p8_pier p9_park_panorama` + both movies into the same `round-02b/`: `ROUND_NAME=round-02b ONLY_IDS="p4_greatlawn p7_east_shore p8_pier p9_park_panorama" PRIO_IDS="" gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round2.sh`
(waiter pid in `_scratch/terrain/round2_hold.pid`, log `_scratch/terrain/logs/round2_hold_e.log`). If a pause is active the lock waits; do not lift it yourself (auto-lift after 10 calm minutes); if it is stopped again, stop and report (2 stops already).
When round-02b is complete: `crops.json` (copy of round-02's), `tools/terrain/measure_round.sh docs/night1/terrain/round-02b`, then `make_pairs.py docs/night1/terrain/round-02b ... docs/night1/terrain/round-01` + `abpack.py` (the pass-2 pack is the fallback); say in `round-02/README.md` which pass the pack uses.

## Offline shader verification (new, saves GPU-lock turns)
- `python3 tools/terrain/check_hlsl.py`: every material body through DXC with UE's parameter types (VectorParameter = float3). 12 / 12.
- `python3 tools/terrain/scw_check.py`: UE's own `ShaderCompileWorker` (CPU only) recompiles every dumped permutation under `unreal/WebHomage/Saved/ShaderDebugInfo/METAL_SM6/M_Terrain*` with the CURRENT `Foliage.ush` and the CURRENT Custom-node bodies of
  `terrain_materials.py` regenerated into the dumped wrapper (27 permutations: base pass, depth, shadow depth, Nanite raster HW / micropoly, Nanite base pass + Lumen card, ray tracing any-hit). Dumps exist only for permutations that failed once.
- The hold driver's warm-up stops the hold (exit 4) when the game log shows `Failed to compile Material` / shader errors.

## Not built / known
Pickets, wet bands, pond shallows, ballfield fences, Met-like museum (skipped on purpose), lamp night look, collision on rocks / esplanades; street trees island-wide belong to the island piece; lawn micro-detail (E1) is still the round-01 shader;
the t5 "flat grey perimeter ground" (critic secondary 2) is city ground, not touched; crown hulls still read as lumpy blobs at 165-520 m (4-lobe crown LOD of the browser).

## Rebuild recipe (CPU steps need no slot)
1. `npx vite --port 5209 --host 127.0.0.1 --strictPort` (needs `npm ci`), `node tools/export/export_terrain.mjs`, `python3 tools/terrain/prep_terrain.py`, `node tools/export/gen_terrain_shaders.mjs`, `python3 tools/terrain/check_hlsl.py`.
2. Base Manhattan content exists in this worktree's `unreal/WebHomage/Content` (round-01 recipe: `git show 77d0946:docs/night1/terrain/HANDOFF.md`).
3. `build_terrain.py` through the nullrhi commandlet (about 2 min, no GPU): wrapper `_scratch/terrain/jobs_terrain_r02.py` (`JOB_ARGS steps clean,tex,mat,mesh,foliage,trees,map,views`); touch `_scratch/terrain/BUILDING` while it runs (the hold driver waits for it, max 15 min).
4. Captures only through the lock, always `--timeout 28800`. Never `pgrep -f` a pattern that appears in your own command line (it matched my wait loops).
