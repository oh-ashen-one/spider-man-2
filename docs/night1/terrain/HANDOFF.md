# Terrain (piece E) — HANDOFF (round 02 in progress: content rebuilt, GPU hold queued)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/terrain` (pushed), worktree `/Users/midir/sm2-n1/terrain`, scratch `/Users/midir/sm2-n1/_scratch/terrain`, dev port 5209 (Vite, exports only).
Owns `/Game/Terrain`, `tools/export/{export_terrain.mjs,collect_terrain.js,gen_terrain_shaders.mjs}`, `tools/terrain/`, `unreal/WebHomage/Scripts/{build_terrain.py,terrain_materials.py}`,
`unreal/WebHomage/Shaders/Terrain/`, `docs/night1/terrain/`. Spec / shot list / cameras: `SPEC.md`, `SHOTLIST.md`, `shots.json`.

## State at the time of writing (round 02, before the captures)
Round-02 target (from the round-01 critic): trees / canopy at swing height. Done (committed, content rebuilt with the nullrhi commandlet, NOT yet rendered):
- `collect_terrain.js` now exports the browser's whole park-tree chain: `trees-{park,elm,conifer}-near` (leaf-card canopies 44-165 m, shadows), `trees-*-crown` (lumpy clump crowns 165-520 m), `trunks-*` (near / mid / far),
  with each pool's `near / far / fadeIn / fadeOut` (the dither bands of `src/world/pool.js`).
- UE draws every HISM instance at every distance, so every band is a dithered material clip by camera distance: `Shaders/Terrain/Foliage.ush` (`tfBand`, `TerrainClumpCrown` = port of trees.js `crownMaterial`, `TerrainLeafCards` = port of `leafMaterial`),
  materials `M_TerrainLeaves` (ez L0 < 20 m / L1 20-44 m), `M_TerrainBark` (ez bark + trunks), `M_TerrainCards`, `M_TerrainClump`, `M_TerrainCrown` (crownfar, only >= 520 m). `build_terrain.py` makes one HISM per pool (46 pools, 47,710 instances) with a
  material instance per pool carrying its band. The band clip is skipped in shadow-depth and Lumen-card-capture passes (macros `SHADOW_DEPTH_SHADER`, `LUMEN_CARD_CAPTURE`), so trees cast shadows / bounce light at every distance.
  The ez materials now carry the Nanite usage flag (the round-01 game log said "missing usage flag Nanite! Default Material will be used in game" for the ez L1 MIs).
- Secondary: lawn albedo grade `LAWN_GRADE` (greener: R x0.68, G x1.16, B x0.62, in `terrain_materials.py`), picnic blankets brightened (their exported colours are linearised twice: near-black slabs on the lawn).
- Merge preconditions: the two round-01 movies (+ contact frames) showing the dev suit emblem are `git rm`ed; round-02 movies hide the hero (`ShowFlag.SkeletalMeshes 0`, `HIDE_HERO=1`); the park-reservoir pair uses a park-water-basin aerial frame
  cut from the library's pond clip (the private refs have no frame of the Reservoir itself: all 127 street / traversal stills were scanned).

## NEXT (a fresh session continues here)
1. The capture hold is queued: `gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round2.sh` (waiter pid in `_scratch/terrain/round2_hold.pid`, log `_scratch/terrain/logs/round2_hold.log`). If it is gone, re-enqueue the same command from the worktree
   (rebuild first only if sources changed: recipe below; never rebuild inside the hold). It writes `docs/night1/terrain/round-02/` (stills 3840x2160 internal 1920x1080, 2 movies 1920x1080 hero hidden, `warm_shader_check.txt`).
2. Measure: `tools/terrain/measure_round.sh docs/night1/terrain/round-02` (needs `round-02/crops.json`: lawn boxes under `crops`, crown boxes under `crowns`; boxes are picked by eye on the new stills with
   `_scratch/terrain/mock/grid_overlay.py`), then `python3 tools/terrain/make_pairs.py docs/night1/terrain/round-02 /Users/midir/sm2-n1/_scratch/critic-E-r02/pairs.json docs/night1/terrain/round-01` and
   `python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py /Users/midir/sm2-n1/_scratch/critic-E-r02/pack /Users/midir/sm2-n1/_scratch/critic-E-r02/pairs.json`.
3. Not built: pickets, wet bands, pond shallows, ballfield fences, Met-like museum (skipped on purpose), lamp night look, collision on rocks / esplanades; street trees island-wide belong to the island piece; lawn micro-detail (E1) is still the round-01 shader.

## Rebuild recipe (CPU steps need no slot)
1. `npx vite --port 5209 --host 127.0.0.1 --strictPort` (needs `npm ci`), then `node tools/export/export_terrain.mjs`, `python3 tools/terrain/prep_terrain.py`, `node tools/export/gen_terrain_shaders.mjs`, `python3 tools/terrain/check_hlsl.py` (12 / 12 materials compile offline).
2. Base Manhattan content (city + traversal + look + map) exists in this worktree's `unreal/WebHomage/Content` (see the round-01 recipe in git history: `git show 77d0946:docs/night1/terrain/HANDOFF.md`).
3. `build_terrain.py` through the nullrhi commandlet (about 2 min, no GPU): wrapper `_scratch/terrain/jobs_terrain_r02.py` (`JOB_ARGS steps clean,tex,mat,mesh,foliage,trees,map,views`); touch `_scratch/terrain/BUILDING` while it runs (the hold driver waits for it).
4. Captures only through the lock; always `--timeout 28800`.
