# Island (piece A) — HANDOFF (round 04 IN PROGRESS, checkpoint 2026-10-03 18:20)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/island` (pushed), worktree `/Users/midir/sm2-n1/island`, scratch `/Users/midir/sm2-n1/_scratch/island` (symlink to the exFAT SD card:
exports / GLBs / logs / frames only, never Content or DDC; exFAT writes `._*` files next to every file, skip them in globs).
Owns `tools/export/*`, `Scripts/build_city.py`, `Scripts/build_manhattan.py`, `Scripts/island_wp_sources.py`, `Shaders/City/`, `/Game/City`,
`/Game/Tests/City`, `/Game/Maps/Manhattan*`, `docs/night1/island/`. Traversal C++ is P3's: `REQUEST-traversal-r03.md`, `REQUEST-traversal-r04.md`.
Merged `Opus-5.5-Loop-Night-1` at 8b7a8301 (merge 70ce4f12, no conflicts); C++ rebuilt.

## State at this checkpoint
* A FRESH rebuild is running: `docs/night1/island/build_r04.sh` (log `_scratch/island/r04/logs/build_r04.log`, holds `_scratch/island/BUILDING`).
  Content/City, Content/Tests/City and the WP map were deleted on disk at 16:49 and are being rebuilt commandlet by commandlet, each in its own
  `gpu_slot.sh capture --label island` hold (city_a clean,tex | city_a2 mat | city_mesh_NN (resumable) | city_proto | city_kit_NN (resumable) |
  city_b fsky,map,coll | city_wp | traversal | characters | look | manhattan_map). **Until it finishes there is no playable island map.**
  If it died: resume with `SPLIT_FROM=<mesh|proto|kit|b|wp> docs/night1/island/build_r04.sh` (STEPS=city,traversal,characters,look,map; the
  resumable steps skip what exists), check `tail _scratch/island/logs/<commandlet>.log`.
* Then: `docs/night1/island/capture_r04.sh` (warm-up + r1 r2 r3 r4 r5 r5b into round-04, consecutive holds), then
  `docs/night1/island/analyze_r04.sh`, then the critic pack (`critic_prep_r04.py` + abpack), README sections 6-8, this HANDOFF.

## Round-04 changes (all script-generated)
* Fire escapes (`tools/export/street_kit.py`): only the landings are solids (open stair wells / drop-ladder hatch), railings / stairs / ladders
  are visual-only (street-kit tiles), the landing grating starts 0.40 m off the wall. r3 sim: 0 top-outs at the r03 loop spot (r03: 6).
* WHBox rule 5 (`tools/export/island_boxes.py` `fill_hollow`): raw hollow 17.68 -> 16.43 %, I5 0.25 / 0.36 %.
* `M_CityLeaves` near-lens fade (< 3.5 m cut, dithered to 8.5 m).
* Checkers: `island_fe_check.py`, `island_foliage_check.py`, `island_rope_canopy.py`, `island_traj_diff.py`.
* Build: resumable batched mesh / kit import with a projected deadline, every commandlet in its own GPU hold, free-disk floor 150 GB (decimal).
* `scripts/r5_m2_avenue_alt0.json`: r5 with the traversal tune AltChain=0 (the merged r24 altitude chain fails r5's re-web lines by design).
Details and numbers: `round-04/README.md`.
