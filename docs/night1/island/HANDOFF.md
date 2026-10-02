# Island (piece A) — HANDOFF (round 01 finished except r3 take 2 + the ISM in-game check)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/island` (pushed), worktree `/Users/midir/sm2-n1/island`, scratch `/Users/midir/sm2-n1/_scratch/island`
(a symlink to the exFAT SD card `/Volumes/memory/sm2-n1/island`: exports / GLBs / logs / frames only, never Content or DDC; exFAT writes `._*`
AppleDouble files next to every file, skip them in globs). Dev port 5208 (Vite, only for exports).
Owns `tools/export/*`, `Scripts/build_city.py`, `Scripts/build_manhattan.py`, `Shaders/City/`, `/Game/City`, `/Game/Tests/City`,
`/Game/Maps/Manhattan*`, `docs/night1/island/`.

## Round 01 result (read `round-01/README.md` first; numbers in `round-01/MEASURE.md`)
- Captures from the real game on `/Game/Maps/Manhattan_WP`: a1 north / south 4K stills; r1, r2, r4 30 s 1080p60 videos + telemetry + route
  checks; r3 take 1 archived in `round-01/r3_take1/` (the first rope swung the hero back west, it landed at 5.3 s and ran the sidewalk).
- Every route: 0 fall-through / stuck / mid-air / wall-air / webs-on-nothing. I5 audit hollow 0.22 %, phantom 0.26 % (was 5.81 % hollow:
  rooftop equipment penthouses had no box; `island_boxes.py` rule 4). I2 (>= 1.2 km to facadeLod) cannot pass in M1 (region 2.3 km N-S).
- Blind critic pack (provisional, r3 pair from take 1): `/Users/midir/sm2-n1/_scratch/critic-A-r01/pack` (key `pack.key.json` beside it),
  inputs `pairs.json`, built by `prep_pairs.py` (copy: `docs/night1/island/critic_prep_r01.py`) then
  `python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py <pack> <pairs.json>`. Rebuild it after r3 take 2.

## In flight at hand-off time
- **Hold B** (queued in the GPU lock, PID in `_scratch/island/capture.pid`, log `_scratch/island/logs/holdB.log`): one slot hold running
  `_scratch/island/holdB.sh` = (1) `verify_map.sh /Game/Maps/Manhattan_WP_ism _scratch/island/verify_ism r1 r4` (telemetry-only, 960x540;
  log `verify_ism.log`) and (2) `capture_round.sh round-01 r3` (r3 take 2 from x -300 / 40 m / 26 m/s; log `capture_r01e.log`).
  The health monitor auto-PAUSED all launches at 20:43 (WindowServer starved under another piece's capture): the waiter just waits.
- When hold B finishes: route-check r3 (`python3 tools/export/island_route_check.py <export> round-01/r3_crosstown_east_telemetry.csv --out
  round-01/route_check_r3.json`), update the README table, re-run `prep_pairs.py` + abpack, commit. Compare `verify_ism/route_check.json` and the
  `WebTravWorld:` lines (expect ~56.5 k *instance* boxes) with the actor build; if they match, make `ism` the default in `spawn_boxes` and
  rebuild `Manhattan_WP` (`SM2_WHBOX_MODE=ism SM2_ISLAND_CITY_STEPS=wp python3 unreal/WebHomage/Scripts/build_manhattan.py --steps city,map`,
  ~2 min). The test map `/Game/Maps/Manhattan_WP_ism` can then be deleted (git-ignored Content).

## Rebuild from scratch
`python3 unreal/WebHomage/Scripts/build_manhattan.py` (all steps; editor closed; ~94 min with actor boxes, ~60 min expected with
`SM2_WHBOX_MODE=ism`; needs 150 GB free internal). Partial: `--steps a,b`, `SM2_ISLAND_CITY_STEPS=<build_city steps>` (e.g. `wp`),
`SM2_ISLAND_WP_MAP=/Game/Maps/<test>` builds a test WP map beside the real one. After editing `island_boxes.py`:
`python3 tools/export/island_boxes.py <export>` then the `wp` step. Captures: `docs/night1/island/capture_round.sh <round dir> r1 r2 r3 r4 a1`
(each run its own lock cycle) or `ISLAND_IN_LOCK=1 gpu_slot.sh capture --label island -- capture_round.sh <round> r3 r4` (one hold, <= 2
movie routes inside the 2,400 s max hold).

## Next (round 2)
1. ISM boxes default (above), drop the classic `City_Midtown_Collision` pass from the WP flow.
2. M2 whole island: export (spike: 22.1 M tris, 2.85 GB, ~5 min), import split per district across 2 `-nullrhi` commandlets (mesh import is
   now the long pole: 2,470 s for M1, ~6,200 s island). I2 can only pass once the island is detailed.
3. Route scripts: r2 drifts east into the facades (wall-runs at x 267 / 289 / 318 from the x 250 avenue) — traversal steering, reported, not
   ours to change. The traversal's `AddBox` skips boxes < 1.0 m tall (282 of 56,816).

## Not mine, left as found
`unreal/WebHomage/Scripts/run_game.sh` was edited in this worktree at 18:12 by another session (non-perf captures frame-capped to 30 / 45 fps
after a WindowServer starvation probe). It is uncommitted; I neither reverted nor committed it. Movie frames are unaffected (fixed 1/60 s step).
