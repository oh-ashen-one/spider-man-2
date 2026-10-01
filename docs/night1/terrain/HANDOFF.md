# Terrain (piece E) — HANDOFF (round 01, WIP: captures pending in the GPU lock queue)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/terrain` (pushed), worktree `/Users/midir/sm2-n1/terrain`, scratch `/Users/midir/sm2-n1/_scratch/terrain`, dev port 5209 (Vite, exports only).
Owns `/Game/Terrain`, `tools/export/{export_terrain.mjs,collect_terrain.js,gen_terrain_shaders.mjs}`, `tools/terrain/`, `unreal/WebHomage/Scripts/{build_terrain.py,terrain_materials.py}`,
`unreal/WebHomage/Shaders/Terrain/`, `docs/night1/terrain/`. Spec / shot list: `SPEC.md`, `SHOTLIST.md`, `shots.json`.

## What exists (all committed; Content is generated, never committed)
- `tools/export/export_terrain.mjs` + `collect_terrain.js`: headless Chrome export of the TERRAIN kinds island-wide (park ground, lawns, ponds, furniture, ez-tree prototypes + instances with per-tree autumn tints, rock outcrops, pools) -> `<scratch>/export`.
- `tools/terrain/prep_terrain.py`: path / drive mask (0.5 m), grass tuft prototype + 181 k scattered tufts (grass.js mask), rock outcrops (Met-like museum triangles dropped on purpose), `ParkData.ush`, stats (E2).
- `tools/export/gen_terrain_shaders.mjs` -> `Shaders/Terrain/Park.ush`: the browser park / lawn GLSL (ground.js createGrassMaterial) translated to HLSL by the city's glsl2hlsl.
- `tools/terrain/shore_audit.py`: E3. Browser coast has 12 gaps > 5 m at the Inwood tip; a granite bulkhead patch (`shore_patch.glb`) closes them (after patch: 0 gaps > 5 m).
- `tools/terrain/check_hlsl.py`: offline DXC compile of every material body (UE's libdxcompiler via ctypes) — run it after any shader edit (all 8 materials OK).
- `unreal/WebHomage/Scripts/build_terrain.py` (steps clean, tex, mat, mesh, foliage, trees, map, views; every step fail-soft): materials from `terrain_materials.py`; `/Game/Terrain/Terrain_Land` sublevel
  (park ground tagged WHGround, lawns, ponds, furniture, tufts HISM x3 wind classes, reeds / blankets / lamps, tinted ez-tree HISMs, rocks, shore patch); `City_Geo_T` = private copy of the city geometry level with the
  city's flat park ribbons / lawns / ez park trees hidden in game; `/Game/Terrain/Maps/Manhattan_Terrain` (golden Manhattan + terrain); still maps `V_<id>` (terrain) / `VB_<id>` (city alone) from `shots.json`.
- `docs/night1/terrain/capture_round.sh` (+ `turn2.sh`): one GPU-slot hold per run; stills 3840x2160 (internal 1920x1080, TSR), movies 1920x1080 (internal 1920x1080, r.ScreenPercentage 100).
  `tools/terrain/measure_round.sh <round>` computes the SPEC numbers; `tools/terrain/make_pairs.py <round> <pairs.json>` + `tools/night1/abpack.py` build the blind critic pack.

## Rebuild recipe (CPU steps need no slot)
1. `npx vite --port 5209 --host 127.0.0.1 --strictPort` in the worktree (needs `npm ci`), then `node tools/export/export_terrain.mjs`, `python3 tools/terrain/prep_terrain.py`, `node tools/export/gen_terrain_shaders.mjs`.
2. Base Manhattan content in this worktree (city + traversal + look + map): scratch wrapper `_scratch/terrain/run_base_all.sh` (one editor session, GPU-locked; `jobs_base_all.py`), ~7 min; it needs the city export in `_scratch/terrain/manhattan/export/midtown3x3` (`build_manhattan.py` city_export step with `DEV_PORT = 5209`, see `_scratch/terrain/run_manhattan.py`).
3. `build_terrain.py` as a headless `-run=pythonscript -nullrhi` commandlet through `gpu_slot.sh capture --label terrain` (the base job's last step runs it; `turn2.sh` can re-run any steps via `_scratch/terrain/turn2_rebuild_steps`).

## State at this commit
- First GPU-locked build ran (base OK, 7 min); the terrain step failed on leaf textures (fixed since: prep stages `leaf_*.png`). No terrain render exists yet. Two queue tickets are waiting: turn2 (rebuild all terrain steps + warm-up + stills) and turn3 (2 movies).
- Python logic of build_terrain.py is dry-run against a mocked `unreal` module (`_scratch/terrain/mock/run_mock.py`): 24 meshes, 181 k tufts, 589 lamps, 19 k tree instances. Real-API issues, if any, show in `_scratch/terrain/manhattan/logs/terrain_turn2.log` (look for `STEP ... FAILED` / `SECTION ... FAILED`).
- Note: `unreal/WebHomage/Scripts/run_game.sh` is modified in this worktree by the orchestrator (capture frame cap, 2026-10-01 18:12); NOT committed by this piece.
