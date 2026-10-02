# Island (piece A) — HANDOFF (round 03 IN PROGRESS, 2026-10-02 05:35)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

## Round 03 (M2 whole island) — state when this was written
- Merged `origin/Opus-5.5-Loop-Night-1` (aad3ac3). Export of the whole island done (ix -4..3, iz -14..13: 1,793 tile meshes, 23.58 M tris,
  3.08 GB, 172 s) at `_scratch/island/export/island`; city_prep + city_extra done (885 s + 191 s; 173,097 WHBox boxes).
- I5 island-wide (`round-03/coll_audit.json`): phantom 0.25 %, hollow 0.37 %, facadeLod inside region 0.
- signs.png rows sanitised (CHASE BANK -> HARBOR SAVINGS etc., `IP_EXCLUSIONS.md`), verified on `_scratch/island/tex/signs.png`.
- Every M1 GLB is byte-identical in the island export (1,032 / 1,032 md5), so the Unreal rebuild is incremental:
  `docs/night1/island/build_r03.sh` (`SM2_ISLAND_MESH_ONLY=missing`, steps tex,mesh,kit,fsky,map,coll,wp + build_manhattan map;
  log `_scratch/island/logs/build_r03.log`, commandlet log `city_pass1.log`; started 05:24). WHBox cubes = per-tile components
  (`SM2_WHBOX_MODE=comp`, probe d: 40 k components in 14 s).
- 07:24: the city_pass1 commandlet hit build_manhattan's 7,200 s subprocess timeout mid-finish (killed, -nullrhi: no GPU); ~420 finished meshes were saved. Timeout now SM2_ISLAND_UE_TIMEOUT (6 h). Resumed 07:25 with SM2_ISLAND_CITY_STEPS=mesh,kit,fsky,map,coll,wp (log build_r03b.log): only the still-missing meshes are imported.
- 08:37: mesh step done (419 resumed meshes in 4,325 s); kit step (whole-island street kit + fire-escape tiles) running, then fsky, map, coll, wp.
- Next: when the build ends -> captures (`capture_round.sh docs/night1/island/round-03 warmup r1 r2 r3 r4 a1`, GPU lock), route checks,
  `tools/export/island_r2_check.py`, `tools/export/island_road_band.py` on r2 t26/t28 stills, critic pack `_scratch/critic-A-r03`.
- Build timings: `_scratch/island/logs/build_timings_island.json` (every invocation appended).

# (round 02 handoff, kept for reference)

## Round 02 result — read `round-02/README.md`
Target: collision that matches what is drawn under traversal r20 (merged at 70e914a). Done + measured:
- Cooked triangle collision + QueryOnly on facade / roofs (parapets, copings) / detail (browser fire escapes) / landmarks / plazas /
  bridges / seawalls / facadeLod; fire-escape kit tiles `fireescape__t*` as solids; sheds / subway solid; other ISM props A/B-ready.
- `split_giants.py`: bridges / seawalls no longer de-collided as r20 "giants" (93 -> 72 far-off components, 490 -> 642 solids).
- Dump: every streamed facade / roofs / detail / fire-escape tile solid, ctf 3, QueryOnly; WHBox cubes index only.
- r3 take 2: 0 % ground, 21 anchors, 0 webs on nothing; FAILS "re-web <= 0.5 s" (6.4 s traversal topOut loop under a fire-escape deck).
- r4: roof run ends in a vault over the parapet (r01: ran inside it), drop lands on the street without passing through anything;
  wall-run still passes up through kit decks (traversal: horizontal-only push-out).
- r1: 0 overlaps, 0 fall / stuck / mid-air / wall-air. I5 unchanged 0.26 / 0.22 %.

## Captures: all done (3 holds, 04:25)
r1, r2, r3, r4 movies + telemetry, a1 4K stills, r1 `-WHTravIsmSolid=1` A/B + its prims dump; critic pack built (9 pairs):
`/Users/midir/sm2-n1/_scratch/critic-A-r02/pack` (key `pack.key.json`, inputs `pairs.json`, `docs/night1/island/critic_prep_r02.py`).
Also measured after the handoff draft: r2 0 overlaps / 0 fall-stuck-mid-air-wall-air, but it now swings OUT of M1 after ~19 s (webs on
facadeLod walls, verified on the triangles); A/B: stuck 0 / 0, trunk overlap 0 / 0, `=1` puts one web on a street-tree branch; final
dump: 2 far-off rows with centre in M1 (`SM_farLand_roos`, `SM_hinterland`: scenery by name / horizon ISM), no M1 building, bridge or
seawall de-collided. Nothing of the island is running (driver, rebuild and engines all exited).

## Next (round 3)
0. r2 route: start further north (or wait for M2) so the 30 s chain stays inside the detailed region; a sidewalk route for the
   trunk A/B. Roosevelt Island land (`farLand_roos`) is far-by-name: it is not a floor (hero would sink to the water plane).
1. Traversal asks (REQUEST-traversal-r02.md): ISM cube per-instance index (then make `SM2_WHBOX_MODE=ism` default: WP build 20 s vs
   ~35 min), topOut loop under decks, wall-run through decks, IsmSolid default from the A/B.
2. M2 whole island (export ~22 M tris; mesh import is the long pole). Run `split_giants.py` in city_prep (wired) — it is idempotent.
3. Remaining far-off rows overlapping M1 are `SM_far*` scenery by name (far shore from x 882 m, flat far land incl. Roosevelt Island).

## Gotchas learned this round
- Never edit a shell script in place while a hold is executing it (bash reads by offset): write a new file and `mv` it over (new inode).
- `capture_round.sh` waits while `_scratch/island/BUILDING` exists (`rebuild_r02b.sh` holds it); a rebuild must not overlap a running game.
- `unreal/WebHomage/Scripts/run_game.sh` was edited in this worktree by another session (22:41, frame caps / perf only under the perf
  lock). Not mine: left uncommitted, as found.
- Movie routes take ~12-18 min each in a hold when the other slot renders; a 2-route hold can hit the 2,400 s max hold.

# (round 01 handoff, kept for reference)

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

## Not done (blocked by the GPU auto-pause) — do these first
Hold B never ran: queued 20:41, the health monitor auto-PAUSED every launch at 20:43 (WindowServer starved under another piece's capture),
`gpu_slot` wait-timed-out at 21:53 (exit 75). Nothing of the island is running. When `/Users/midir/sm2-n1/_scratch/gpu/PAUSED` is gone:
`/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label island -- /Users/midir/sm2-n1/island/docs/night1/island/holdB_r01.sh`
(~25 min hold) = (1) `verify_map.sh /Game/Maps/Manhattan_WP_ism _scratch/island/verify_ism r1 r4` (telemetry-only ISM collision check, log
`_scratch/island/logs/verify_ism.log`) and (2) r3 take 2 movie (route now starts x -300 / 40 m / 26 m/s; log `capture_r01e.log`). Then:
route-check r3 (`python3 tools/export/island_route_check.py /Users/midir/sm2-n1/_scratch/island/export/midtown
docs/night1/island/round-01/r3_crosstown_east_telemetry.csv --out docs/night1/island/round-01/route_check_r3.json`), README table, re-run
`/Users/midir/sm2-n1/_scratch/critic-A-r01/prep_pairs.py` + abpack, commit. ISM verdict: `verify_ism/route_check.json` must show 0 events
and the game log `WebTravWorld:` line ~56.5 k *instance* boxes; then make `ism` the default in `spawn_boxes` and rebuild `Manhattan_WP`
(`SM2_WHBOX_MODE=ism SM2_ISLAND_CITY_STEPS=wp python3 unreal/WebHomage/Scripts/build_manhattan.py --steps city,map`, ~2 min).

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
