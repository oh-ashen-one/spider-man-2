# Terrain (piece E) — HANDOFF (round 01: build + checkers done, NO GPU capture yet — blocked by the health pause)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/terrain` (pushed), worktree `/Users/midir/sm2-n1/terrain`, scratch `/Users/midir/sm2-n1/_scratch/terrain`, dev port 5209 (Vite, exports only; stopped at the end of the round).
Owns `/Game/Terrain`, `tools/export/{export_terrain.mjs,collect_terrain.js,gen_terrain_shaders.mjs}`, `tools/terrain/`, `unreal/WebHomage/Scripts/{build_terrain.py,terrain_materials.py}`,
`unreal/WebHomage/Shaders/Terrain/`, `docs/night1/terrain/`. Spec / shot list / cameras: `SPEC.md`, `SHOTLIST.md`, `shots.json`.

## READ THIS FIRST: the incident that stopped the captures
- 2026-10-01 20:43: the FIRST game run of this piece (warm-up on `/Game/Terrain/Maps/V_p1_south`, 960x540 offscreen, one engine) ran GPU 100 % with WindowServer starved (`health.log` 20:43:31-46: `probe=FAIL`, `WS-STARVED`);
  the health monitor stopped the game (SIGTERM, clean exit) and created `_scratch/gpu/PAUSED` ("20:43 auto-pause by health_monitor: WindowServer starved"). It was still in place when this round ended (22:30, 107 min later), so no capture of any
  kind was produced. I did not lift it (owner / orchestrator decision) and never rendered around it.
- Suspected cause (not yet proven): every instance of the 181 k grass tufts + 19 k tree instances became a distance-field object (the log shows `FDistanceFieldSceneData::UpdateDistanceFieldObjectBuffers` precision ensure at map load). Fix is already in
  `build_terrain.py` (`lite()`: `affect_distance_field_lighting=False` + `affect_dynamic_indirect_lighting=False` on every HISM and every world-space mesh; trees L1 keep Lumen indirect) but has NOT been run on the GPU yet.
  `capture_round.sh` now also throttles every run (`WH_CAPTURE_MAXFPS=12`, warm-up 12 s). If a run is starved again: stop, do not retry; reduce `SM2_TUFT_PER_M2` (prep, default 0.55) and the tree HISMs first.

## What exists (all committed; Content is generated, never committed)
- `tools/export/export_terrain.mjs` + `collect_terrain.js`: headless-Chrome export of the TERRAIN kinds island-wide (park ground, lawns, ponds / Reservoir, furniture, rock outcrops, ez-tree prototypes + instances with per-tree autumn tints, pools) -> `<scratch>/export` (23 s).
- `tools/terrain/prep_terrain.py`: path / drive mask (0.5 m), grass tuft prototype + 181 k scattered tufts (grass.js mask), rock outcrops (the Met-like museum triangles are dropped on purpose), `ParkData.ush`, leaf textures, stats (E2).
- `tools/export/gen_terrain_shaders.mjs` -> `Shaders/Terrain/Park.ush`: the browser park / lawn GLSL (ground.js createGrassMaterial) translated to HLSL by the city's glsl2hlsl.
- `tools/terrain/shore_audit.py`: E3. The browser coast has 12 gaps > 5 m (max 12 m, all at the Inwood tip); a granite bulkhead patch (`shore_patch.glb`, 195 blocks) closes them: after patch 0 gaps > 5 m (piers excluded, 1 m grid, 1.5 m tolerance).
- `tools/terrain/check_hlsl.py`: offline DXC compile of every material body (UE's libdxcompiler via ctypes) — run it after any shader edit (8/8 materials compile, `round-01/hlsl_check.txt`).
- `unreal/WebHomage/Scripts/build_terrain.py` (steps clean, tex, mat, mesh, foliage, trees, map, views; every step and land section fail-soft): materials from `terrain_materials.py`; `/Game/Terrain/Terrain_Land` sublevel (park ground tagged WHGround
  3 cm above the city's flat ribbons, lawns, ponds, furniture, tufts HISM x3 wind classes (cull 45 m), reeds / blankets / lamps, tinted ez-tree HISMs L0 < 22 m / L1 < 520 m, schist rocks, shore patch); `City_Geo_T` = private copy of the city geometry
  level with the city's flat park ribbons / lawns / ez park trees hidden in game (the original level and the baseline maps stay untouched); `/Game/Terrain/Maps/Manhattan_Terrain` (golden Manhattan + terrain); still maps `V_<id>` / baseline `VB_<id>` from `shots.json`.
  First real run (2026-10-01 20:41, base content built the same evening): the whole build ran clean in 102 s (`_scratch/terrain/manhattan/logs/terrain_turn2.log`): 23 meshes, 181,328 tufts, 589 lamps, 19,084 tree instances, 9 view maps.
- `docs/night1/terrain/capture_round.sh` (+ `turn2.sh`): ONE slot hold per run; stills 3840x2160 (internal 1920x1080 = auto 50 % TSR), movies 1920x1080 (internal 1920x1080, `r.ScreenPercentage 100`), 35 min hold budget, priority order. `scripts/t4_lawn_sprint.json`, `t5_avenue_to_park.json`.
- `tools/terrain/measure_round.sh <round>` (SPEC numbers), `tools/terrain/crop_stats.py`, `tools/terrain/make_pairs.py <round> <pairs.json>` + `tools/night1/abpack.py` (blind critic pack).

## Measured so far (CPU only; `round-01/`)
| SPEC | number | note |
|---|---|---|
| E2 grass cover | **89.9 %** of open park land (503,384 of 559,936 m2); 94.5 % excluding the schist-outcrop cut-outs; 76.5 % of ALL park land | 12.5 % of the park rectangle is path / drive by the browser design, so a literal "of all park land" reading cannot exceed ~87.5 %. Short of 90 % by 0.1 point: the remainder is rock outcrops (27 k m2) and mud banks by design |
| E3 shoreline | before patch: 12 gaps > 5 m (max 12 m); after patch **0 gaps > 5 m** (max 0) | geometry audit of the exported coast; an in-engine shore-walk capture is still to do |
| E1 park crop hp-sd >= 8 | not measured (no render) | `crop_stats.py` ready; reference meadow crops measure 10.5-13.6 (1080p) with the same filter |
| E5 axes | not judged | no captures, no critic pack |

## Re-launch recipe (when `_scratch/gpu/PAUSED` is gone; the owner / orchestrator decides that)
1. State to verify: `ls _scratch/gpu/PAUSED` absent, `gpu_status.sh` shows no engine, `health_monitor.sh` running. Base Manhattan content (city + traversal + look + map) already exists in this worktree's `unreal/WebHomage/Content` (built 2026-10-01 ~20:35, `jobs_base_all.py`); the terrain content was last built BEFORE the `lite()` fix, so rebuild first.
2. CPU steps (no slot): `npx vite --port 5209 --host 127.0.0.1 --strictPort` (needs `npm ci`), `node tools/export/export_terrain.mjs`, `python3 tools/terrain/prep_terrain.py`, `node tools/export/gen_terrain_shaders.mjs`, `python3 tools/terrain/check_hlsl.py`.
3. One slot hold (use `--timeout 28800`; the default wait timeout is 60 min): `gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/turn2.sh` with `_scratch/terrain/turn2_rebuild_steps` = `clean,tex,mat,mesh,foliage,trees,map,views` (rebuilds, then warm-up + stills),
   then `gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/capture_round.sh docs/night1/terrain/round-01 moves`. Watch `_scratch/gpu/health.log` during the first minutes.
4. `tools/terrain/measure_round.sh docs/night1/terrain/round-01`, `python3 tools/terrain/make_pairs.py docs/night1/terrain/round-01 _scratch/critic-E-r01/pairs.json`, `python3 tools/night1/abpack.py _scratch/critic-E-r01/pack _scratch/critic-E-r01/pairs.json` (from the integrator's tools dir).

## Known gaps / next (after the first render, in this order)
1. Look at the V_* stills against `round-01/browser/parkHigh|parkLow|parkClose.jpg` (the browser target: olive-gold woods, pale paths, tannin pond): tune `gain` params of the MIs / luma knee, tuft density, tree tints.
2. Trees: LOD between 44 m and 520 m is the ez L1 only (the browser has near / crown LODs there); street trees island-wide are the island piece's.
3. Not built yet (exported or skipped on purpose): pickets, wet bands, pier sheds (in the city coast meshes), ballfield fences (translucent panels would render solid), the Met-like museum (real-building copy: skipped), pond shallows, night look of lamps / globes, collision on rocks / coast esplanades (the hero cannot walk the shore: only the park, lawns and ponds carry `WHGround`).
4. Note: `unreal/WebHomage/Scripts/run_game.sh` in this worktree carries the orchestrator's uncommitted capture frame-cap edit; this piece does not commit it.
