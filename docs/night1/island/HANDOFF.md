# Island (piece A) — HANDOFF (round 01, resumed after the 2026-10-01 14:24 reboot)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/island` (pushed), worktree `/Users/midir/sm2-n1/island`, scratch `/Users/midir/sm2-n1/_scratch/island`
(a symlink to the exFAT SD card `/Volumes/memory/sm2-n1/island`: exports / GLBs / logs / frames only, never Content or DDC; exFAT writes `._*`
AppleDouble files next to every file, skip them in globs). Dev port 5208 (Vite, only for exports).
Owns `tools/export/*`, `Scripts/build_city.py`, `Scripts/build_manhattan.py`, `Shaders/City/`, `/Game/City`, `/Game/Tests/City`,
`/Game/Maps/Manhattan*`, `docs/night1/island/`.

## State (verified 15:25)
- Content (git-ignored, script-built) is complete for M1 Midtown 7 x 9: `/Game/Maps/Manhattan_WP` (World Partition, 256 m cells, 1.2 km
  loading range, block on slow streaming; 793 meshes, 127,250 instances, 53,405 WHBox cubes; player start + golden rig level instance) and the
  classic `/Game/Maps/Manhattan*` maps. Content 1.4 GB.
- The 13:20 build's city pass finished every step but `wp`, then got the system quit at 14:24 (reboot after the owner's GTA V froze
  WindowServer). Resumed with `SM2_ISLAND_CITY_STEPS=wp python3 unreal/WebHomage/Scripts/build_manhattan.py --steps city,characters,map`
  (14:41-15:01, all rc 0 with the script-success line). Logs: `_scratch/island/logs/build_manhattan3.log`, `city_pass1.log`, `manhattan_map.log`.
- Measurements: `round-01/MEASURE.md` (full-island spike 22.1 M tris / 2.85 GB / 159 geo tiles; M1 fresh build ~94 min; island estimate ~4 h
  vs the 90 min target; collision audit phantom 0.21 %, hollow 5.81 % = FAIL).
- Captures: `docs/night1/island/capture_round.sh docs/night1/island/round-01 warmup r1 r2 r3 r4 a1` (log `_scratch/island/logs/capture_r01.log`)
  queued in the GPU lock; the owner was playing GTA V (lock refuses renders, correct) from 15:02.

## Rebuild from scratch
`python3 unreal/WebHomage/Scripts/build_manhattan.py` (all steps; editor closed; ~94 min; needs 150 GB free internal). Partial re-runs:
`--steps a,b` and `SM2_ISLAND_CITY_STEPS=<build_city steps>` for the city step (e.g. `wp`).

## Next
See the round README once written; candidate next gaps: hollow collision (perimeter cornice rings + roof structures in the audit map),
build time (drop the classic collision pass, per-tile collision bodies instead of 53 k actors, 2 parallel import commandlets).
