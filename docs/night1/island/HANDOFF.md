# Island (piece A) — HANDOFF (round 03 finished 2026-10-03; nothing of the island is running)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/island` (pushed), worktree `/Users/midir/sm2-n1/island`, scratch `/Users/midir/sm2-n1/_scratch/island` (symlink to the exFAT SD card:
exports / GLBs / logs / frames only, never Content or DDC; exFAT writes `._*` files next to every file, skip them in globs).
Owns `tools/export/*`, `Scripts/build_city.py`, `Scripts/build_manhattan.py`, `Scripts/island_wp_sources.py`, `Shaders/City/`, `/Game/City`,
`/Game/Tests/City`, `/Game/Maps/Manhattan*`, `docs/night1/island/`. Traversal C++ is P3's: `REQUEST-traversal-r03.md` (§0 is the important one).
Last merge of `Opus-5.5-Loop-Night-1`: aad3ac3 (r26 traversal NOT merged: the C++ stayed the r03 build's; merging would need a C++ rebuild and
every r1-r5 capture repeated; the sims below show the island content is unaffected by the traversal changes only if re-run on the merged build).

## Read first: `round-03/README.md` (pass lines, numbers, honest failures), `REQUEST-traversal-r03.md`, `IP_EXCLUSIONS.md`

## What is true now (verified 2026-10-03)
- **Whole island at full detail (M2)**: 1,793 tile meshes, 23.58 M tris; `/Game/Maps/Manhattan_WP` (World Partition, 256 m cells, 1.2 km range),
  173,097 WHBox cubes (per-tile components), 198,063 instances. I5 audit re-run today: phantom 0.25 %, hollow 0.37 %, facadeLod 0 (unchanged).
- **Two defects found and fixed this round (both invisible while every route stayed inside the old M1 area):**
  1. *Street dressing (trees, parked cars, traffic, furniture) was missing beyond ~1.2 km of the map origin.* All 9,763 per-tile HISM actors were
     spawned at (0, 0, 0); their saved World Partition bounds were empty, so every one sat in the cell at the origin and streamed with it. Fixed in
     `build_city.py` (`spawn_instances`, actor at its tile centre) and applied to the existing map by `build_manhattan.py --steps ism`
     (deletes the old per-tile ISM packages, respawns 198,063 instances in 9,763 actors: 201 s commandlet). Before / after: round-03 stills `r5_*` vs the
     `street_m2` probes in the README.
  2. *The traversal only knows the cells loaded at BeginPlay* (`WebTravWorld::InitWorld`, one `TActorIterator` pass; `AllowedComps`). Streamed-in
     cells are not solids: no anchors, walls or roofs. The default PlayerStart (y 178 m) loads facade tiles y -1024..1536; 17 telemetry-only runs from y 1010
     never web beyond y 1,506 m. Workaround in content: `Scripts/island_wp_sources.py` adds always-loaded streaming source actors (`WH_StreamSrc_M2` at
     (250, 1560)); the build_manhattan map step re-creates them. The real fix is traversal's (`REQUEST-traversal-r03.md` §0). A second PlayerStart is NOT
     an option (AGameModeBase picks one at random: I tried it for 10 minutes on 2026-10-03; the map has one PlayerStart again).
- Route sims and renders agree to the frame: `sim_route.sh` (no renderer, `-nullrhi`, fixed 1/60 s step) reproduces the rendered telemetry with
  0.0000 m deviation (r2 calibration, r5 probe, r1-r4 on the final map). Tune routes with sims (2.5 min), judge frames with `probe_route.sh` (4 min).

## Files you need
| what | where |
|---|---|
| route scripts (r1-r4 as round 02, r5 = the M2 avenue route) | `scripts/` |
| capture driver (one lock per run, or `ISLAND_IN_LOCK=1` inside a hold) | `capture_round.sh <round> r5 a1 ...` |
| telemetry-only route sim (no renderer) | `sim_route.sh <out> <route.json>` |
| rendered still probe at the road-band seconds + road band | `probe_route.sh <out> <route.json> [12,20,26,28]` |
| M2 route pass lines (swing, ground, drawn, road band, overlap) | `tools/export/island_m2_check.py` |
| IP text gate over the round's stills | `ip_gate_r03.py` |
| critic pack inputs | `critic_prep_r03.py` then `/Users/midir/spider-man-2-astra6/tools/night1/abpack.py <pack> <pairs.json> .` |
| search history of the r5 route (every sim, with the map state it ran on) | `round-03/r5_search.json` |

## Rebuild
Everything is script-built (no Content committed). From scratch: `python3 unreal/WebHomage/Scripts/build_manhattan.py` (hours; see `round-03/README.md` timings).
Partial: `--steps ism` (per-tile props, 201 s + 5 s), `--steps map` (maps + WP player start + stream sources, 7 min incl. distance fields),
`python3 ... island_wp_sources.py` as a commandlet (1 min; `SM2_ISLAND_WP_SOURCES="M2:250:1560,N2:250:-2800"`). Wrap each in
`gpu_slot.sh capture --label island --`; a hold is 2,400 s max; `build_manhattan` itself waits while 3+ UnrealEditor processes run.

## Next (round 4)
0. Traversal: index streamed cells (REQUEST §0). Until then add a `WH_StreamSrc_*` per area that is swung in (north: y -2800; south end: y 3000),
   or accept that the swingable area is the union of the sources' 1.2 km discs. Check start-up time / memory before adding many.
1. Street dressing check on every tile row (the ISM fix is verified on rows 1-6 only: `street_m2` probe; look at a few other rows with `probe_route.sh`).
2. Traversal asks still open: topOut loop under decks (r3, 6.43 s), wall-run through decks (r4, 31 overlap frames), r2 steers into the block at
   x 192-216 / y 729 (2.65 s gap, 52 ground frames; unchanged), camera in foliage.
3. IP: the signage atlas shows "THE MARQUIS THEATRE" (street marquee sign); CHOCO LOCO / TOKKA / IRON GUARDIAN still unreviewed (`IP_EXCLUSIONS.md`).
4. Perf of the whole-island map is unmeasured (exclusive perf runs need an attended Mac).

## Gotchas learned
- `?Portal=<tag>` is not a thing for this: UE's portal is the URL `#fragment`, and `ChoosePlayerStart` is random among unoccupied PlayerStarts.
- Python in the running game (`-ExecCmds="py script"`) with a null world SIGSEGVs the engine (my diagnostic, crash 1 of 2 allowed; engine exited cleanly after
  the stack dump). Do not do that again; use commandlets or the traversal dump (`-WHTravDumpPrims`).
- I ran two engines of mine at once for ~2 minutes on 2026-10-03 12:26 (a still and a diagnostic launched from two shells); the health monitor paused
  every launch 12:28-12:39 (WindowServer 95 %). One engine at a time: `pgrep -fl "MacOS/UnrealEditor" | grep sm2-n1/island` before every launch.
- Never edit a shell script in place while a hold is executing it (bash reads by offset): write a new file and `mv` it over.
- `capture_round.sh` waits while `_scratch/island/BUILDING` exists (`build_r03.sh` holds it); a rebuild must not overlap a running game.
- run_game.sh in this worktree was edited by another session (frame caps / perf only under the perf lock): not mine, left as found.

# (older handoffs: `git log -p docs/night1/island/HANDOFF.md`; round 01 / 02 / 03 READMEs hold their results)
