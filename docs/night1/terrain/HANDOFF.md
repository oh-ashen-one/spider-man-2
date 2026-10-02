# Terrain (piece E) — HANDOFF (round 01 done: captures + measurements + critic pack; v3 fixes committed, not rendered)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/terrain` (pushed), worktree `/Users/midir/sm2-n1/terrain`, scratch `/Users/midir/sm2-n1/_scratch/terrain`, dev port 5209 (Vite, exports only; stopped at the end of the round).
Owns `/Game/Terrain`, `tools/export/{export_terrain.mjs,collect_terrain.js,gen_terrain_shaders.mjs}`, `tools/terrain/`, `unreal/WebHomage/Scripts/{build_terrain.py,terrain_materials.py}`,
`unreal/WebHomage/Shaders/Terrain/`, `docs/night1/terrain/`. Spec / shot list / cameras: `SPEC.md`, `SHOTLIST.md`, `shots.json`.

## Round 01 outcome (2026-10-01 23:25)
Fresh captures exist: `round-01/README.md` lists them with disclosed resolutions (13 terrain stills 3840x2160 internal 1920x1080, 4 baseline stills, 2 movies 1920x1080, browser reference shots) and the measured SPEC numbers.
Blind critic pack: `/Users/midir/sm2-n1/_scratch/critic-E-r01/pack` (key outside: `pack.key.json`; pairs `pairs.json`; 12 pairs = 8 vs references + 4 progress pairs vs the city-alone baseline). Not judged yet.
| SPEC | result |
|---|---|
| E1 crop hp-sd >= 8 | **FAIL**: 4.92 eye-level lawn, 4.65 / 6.93 aerial lawn, 15.09 great lawn with infields (baseline eye-level crop 2.57) |
| E2 grass cover >= 90 % | **89.9 %** of open land (94.5 % excl. schist outcrops) |
| E3 shoreline gaps <= 5 m | **0** after the bulkhead patch (browser coast: 12) |
| E7 collision | hero ran 130 m over the lawn in ground mode |
| E5 axes >= 6 | not judged |

## Incident 2026-10-01 20:43 (resolved 22:30 by the owner / orchestrator)
The first terrain game run (warm-up) pinned the GPU at 100 % with WindowServer starved; the health monitor stopped it (clean exit) and created `PAUSED`; 107 min until it was lifted. Suspected cause: every HISM instance (181 k tufts + 19 k trees) became a
distance-field object. Fix (committed): `lite()` in `build_terrain.py` (no distance-field / dynamic-indirect for instanced props and world-space meshes) + every capture run throttled (`WH_CAPTURE_MAXFPS`, short warm-up). After the fix the 13 stills + 2 movies ran with no further pause
(`health.log` still shows one `probe=FAIL` sample at each engine start, 23:02:41 and 23:10:32, without a pause). Do not lift a pause yourself.

## NEXT (round 2), in this order
1. **v3 is committed but NOT rendered** (`docs/night1/terrain/turn4.sh`: rebuild + warm-up + all terrain stills in one hold; enqueue with `gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/turn4.sh`; its ticket was cancelled at the end of this round because the queue was ~3 h): `M_TerrainCrown`
   (distance-clipped, tinted far crowns: the v2 stills show opaque green polyhedra in the canopy at every distance because instance cull distances do not hide the city's far-crown instances), tufts gain 1.7, shore cameras moved off the buildings. Re-measure E1 / E2 with `tools/terrain/crop_manual.py`.
2. **E1 lawn detail**: the lawn is soft at eye level (hp-sd 4.9): add a tiled grass_nrm micro-normal + high-frequency albedo breakup at < 1 m, bigger / brighter tufts near the camera.
3. Per-instance cull distance on HISM does nothing here (instance_start / end_cull_distance): use material distance clips or LOD meshes for every distance band (tufts end at 45 m by cull property today: check if they are really culled).
4. Trees: only ez L1 between 44 m and 520 m (browser has near / crown LODs); street trees island-wide belong to the island piece.
5. Not built: pickets, wet bands, pond shallows, ballfield fences (translucent panels), Met-like museum (skipped on purpose), lamp night look, collision on rocks / esplanades (the hero can walk only the park, lawns and ponds).
6. Movies show the HeroDev default suit (red / blue, white emblem): this worktree's base build skips the characters step. Not terrain, but the owner may not want it in committed mp4s.

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

## Rebuild recipe (CPU steps need no slot)
1. `npx vite --port 5209 --host 127.0.0.1 --strictPort` (needs `npm ci`; stopped at the end of this round), then `node tools/export/export_terrain.mjs`, `python3 tools/terrain/prep_terrain.py`, `node tools/export/gen_terrain_shaders.mjs`, `python3 tools/terrain/check_hlsl.py`.
2. Base Manhattan content (city + traversal + look + map) exists in this worktree's `unreal/WebHomage/Content` (built 2026-10-01 20:35 by `_scratch/terrain/run_base_all.sh` + `jobs_base_all.py`, one editor session, 7 min; city export in `_scratch/terrain/manhattan/export/midtown3x3`, `_scratch/terrain/run_manhattan.py` shows the `DEV_PORT = 5209` wrapper).
3. One slot hold with rebuild + captures: `turn4.sh` (stills) / `capture_round.sh <round> moves` (movies). Always `--timeout 28800` (the default wait timeout is 60 min and silently drops the ticket). Watch `_scratch/gpu/health.log` for the first minutes.
4. `tools/terrain/measure_round.sh <round>`, `tools/terrain/crop_manual.py`, `tools/terrain/make_pairs.py` + `abpack.py`.
5. Note: `unreal/WebHomage/Scripts/run_game.sh` in this worktree carries the orchestrator's uncommitted capture frame-cap edit; this piece does not commit it.
