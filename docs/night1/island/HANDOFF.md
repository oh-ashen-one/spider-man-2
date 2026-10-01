# Island (piece A) — HANDOFF (round 01, resumed 17:05 after the owner's 15:41 pause)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/island` (pushed), worktree `/Users/midir/sm2-n1/island`, scratch `/Users/midir/sm2-n1/_scratch/island`
(a symlink to the exFAT SD card `/Volumes/memory/sm2-n1/island`: exports / GLBs / logs / frames only, never Content or DDC; exFAT writes `._*`
AppleDouble files next to every file, skip them in globs). Dev port 5208 (Vite, only for exports).
Owns `tools/export/*`, `Scripts/build_city.py`, `Scripts/build_manhattan.py`, `Shaders/City/`, `/Game/City`, `/Game/Tests/City`,
`/Game/Maps/Manhattan*`, `docs/night1/island/`.

## State (19:20, WIP)
- Round dir `docs/night1/island/round-01/`: `README.md` (round summary, being filled), `MEASURE.md` (Phase-0 numbers + the resume section),
  a1 north/south 4K stills, r1 + r2 videos / telemetry / route checks (both 0 fall / stuck / mid-air / wall-air / web-air).
- **Collision:** `island_boxes.py` rule 4 (rooftop equipment penthouses >= 2 m both sides -> WHBox): audit hollow 5.81 -> 0.22 %, phantom 0.26 %.
  `/Game/Maps/Manhattan_WP` was rebuilt with it (56,816 actor boxes; game indexes 56,534: `AddBox` skips < 1.0 m tall).
- **Build time:** `SM2_WHBOX_MODE=ism` (build_city.py) = one invisible Cube ISM per 256 m tile, no C++ change (WebTravWorld's ISM branch).
  WP step 45 s vs 2,203 s. Built as the test map `/Game/Maps/Manhattan_WP_ism` (`SM2_ISLAND_WP_MAP=...`). **Not yet verified in game**:
  queued `verify_map.sh /Game/Maps/Manhattan_WP_ism _scratch/island/verify_ism r1 r4` (log `_scratch/island/logs/verify_ism.log`).
  If its box count (~56.5 k instance boxes) and route checks match the actor build, make `ism` the default (`SM2_WHBOX_MODE` default in
  `spawn_boxes`) and rebuild `Manhattan_WP` with `SM2_ISLAND_CITY_STEPS=wp ... --steps city,map` (~2 min).
- **Queued captures:** one GPU-slot hold for r3 + r4 (`ISLAND_IN_LOCK=1 gpu_slot.sh capture --label island -- capture_round.sh round-01 r3 r4`,
  log `_scratch/island/logs/capture_r01d.log`), then the verify hold. Driver PID in `_scratch/island/capture.pid`.
- Critic pack: `/Users/midir/sm2-n1/_scratch/critic-A-r01/prep_pairs.py` (copy: `docs/night1/island/critic_prep_r01.py`) writes pairs.json
  once r3 / r4 exist; then `python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py <pack> <pairs.json>`.

## Rebuild from scratch
`python3 unreal/WebHomage/Scripts/build_manhattan.py` (all steps; editor closed; ~94 min with actor boxes, ~60 min expected with
`SM2_WHBOX_MODE=ism`; needs 150 GB free internal). Partial: `--steps a,b`, `SM2_ISLAND_CITY_STEPS=<build_city steps>` (e.g. `wp`). After
editing `island_boxes.py`: `python3 tools/export/island_boxes.py <export>` then the `wp` step.

## Next
1. ISM verification -> default + rebuild; drop the classic `City_Midtown_Collision` pass for the WP flow.
2. I2 (no facadeLod within 1.2 km) cannot pass in M1 (region is 2.3 km north-south): M2 whole island. Mesh import (2,470 s for M1,
   ~6,200 s island) is the long pole for the 90 min target: split per district across 2 `-nullrhi` commandlets.
3. Swing steering drifts east into facades on the auto-chain routes (r2: wall-runs at x 267 / 289 / 318 from an avenue at x 250): traversal-piece
   behaviour, not collision; reported, not touched.
