# Island (piece A) — HANDOFF (round 01, resumed 17:05 after the owner's 15:41 pause)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/island` (pushed), worktree `/Users/midir/sm2-n1/island`, scratch `/Users/midir/sm2-n1/_scratch/island`
(a symlink to the exFAT SD card `/Volumes/memory/sm2-n1/island`: exports / GLBs / logs / frames only, never Content or DDC; exFAT writes `._*`
AppleDouble files next to every file, skip them in globs). Dev port 5208 (Vite, only for exports).
Owns `tools/export/*`, `Scripts/build_city.py`, `Scripts/build_manhattan.py`, `Shaders/City/`, `/Game/City`, `/Game/Tests/City`,
`/Game/Maps/Manhattan*`, `docs/night1/island/`.

## State (17:31, WIP — being updated through the round)
- **Collision fix this session:** `tools/export/island_boxes.py` rule 4: rooftop EQUIPMENT boxes (mechanical penthouses, >= 2 m both sides,
  >= 0.8 m tall) become WHBox cubes. The 5.81 % hollow cells sat a near-constant 5.0 m above their box (the hero stood inside the penthouse).
  Static audit now: hollow **0.22 %** (<= 2 %), phantom **0.26 %** (<= 1 %), 56,816 boxes (+3,411). `round-01/coll_audit_equip.json` + map.
- WP map rebuild with the new boxes running: `SM2_ISLAND_CITY_STEPS=wp python3 unreal/WebHomage/Scripts/build_manhattan.py --steps city,map`
  (log `_scratch/island/logs/build_manhattan4.log`, `city_pass1.log`). WHBox spawn slows with actor count (~19 actors/s at 47 k vs ~51/s average
  in the 53 k run): per-tile collision bodies are the build-time fix.
- Only the WP map (`/Game/Maps/Manhattan_WP`) has the new boxes; the classic `City_Midtown_Collision` level still has the 53,405 old ones.
- Captures: a1 north/south 4K stills done (17:05, pre-fix build — penthouses are visual, the stills are unaffected). r1-r4 route videos to be
  captured on the fixed build: `docs/night1/island/capture_round.sh docs/night1/island/round-01 r1 r2 r3 r4`.

## Rebuild from scratch
`python3 unreal/WebHomage/Scripts/build_manhattan.py` (all steps; editor closed; ~94 min; needs 150 GB free internal). Partial re-runs:
`--steps a,b` and `SM2_ISLAND_CITY_STEPS=<build_city steps>` for the city step (e.g. `wp`). After editing `island_boxes.py`, regenerate
`python3 tools/export/island_boxes.py <export>` then re-run the `wp` step.

## Next
Route checks on the fixed build; build time (per-tile collision bodies instead of 57 k actors, drop the classic collision pass, 2 parallel
import commandlets); M2 (whole island).
