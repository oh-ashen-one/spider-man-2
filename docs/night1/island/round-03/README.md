# Island (piece A) — round 03: M2, the whole island at full detail

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Resumed from the interrupted r03 WIP (d9d6823; the builder died on an API 502 after the export). Branch `night1/island` = r02 + merged
`Opus-5.5-Loop-Night-1` (aad3ac3). All captures: REAL game (`-game`, offscreen, `Scripts/run_game.sh`), map `/Game/Maps/Manhattan_WP`,
every run inside `gpu_slot.sh capture --label island` (holds are `contaminated=true`: not perf runs, no frame times here). Internal
resolution: no `r.ScreenPercentage` passed (CAPTURE.md auto: **1920x1080 output = 1399x787 internal, TSR**; 3840x2160 stills = 1920x1080
internal). Movies: fixed 1/60 s step (`-benchmark -fps=60 -dumpmovie`), frame-capped 30 fps wall clock (run_game), 2-3 other pieces'
engines on the GPU during every hold.

## What changed (all script-generated; no Content committed)
| change | where |
|---|---|
| Detailed region default = whole island (ix -4..3, iz -14..13, export `island`): 1,793 tile meshes, 23.58 M tris, 3.08 GB GLB, export 172 s | `build_manhattan.py` (r03 WIP) |
| Incremental M1 -> M2 import: every GLB shared with the M1 export is byte-identical (1,032 / 1,032 md5), so `SM2_ISLAND_MESH_ONLY=missing` imports only the 761 new meshes (a clean build still imports all) | `build_city.py` mesh step, `build_r03.sh` |
| WHBox cubes as plain invisible Cube **components**, one always-loaded actor per 256 m tile (`SM2_WHBOX_MODE=comp`, default): 173,097 boxes in 170 actors, 973 s. Actor mode was quadratic (`AddActor` label scan: ~3 h for 140 k, `probe_spawn_r03.py` b) | `build_city.py spawn_boxes` |
| Street layer + r02 solids (cooked-triangle facade / roofs / detail / fire-escape kit, QueryOnly) + city_extra (trees, parked cars, traffic, signs) on every island tile: WP populate 1,642 meshes (316 ground, 757 solid, 542 visual-only), 272 kit tiles (136 street kit + 136 fire-escape solids), 198,063 instances | `build_city.py` (unchanged rules, whole-island inputs) |
| IP: `signs.png` rows CHASE BANK -> HARBOR SAVINGS, DUANE PHARMACY -> CORNER PHARMACY, SUBWAY EATS -> HERO SUBS (repainted, original lettering) | `tools/export/ip_sanitize.py`, `../IP_EXCLUSIONS.md` |
| Build robustness: city_prep resume point (`SM2_ISLAND_PREP_FROM`), commandlet timeout 6 h (`SM2_ISLAND_UE_TIMEOUT`; the 2 h default killed the first pass at 07:24), every build invocation's timings appended | `build_manhattan.py` |
| Capture safety: a route starts only with >= 1,500 s of hold left; run_game `-timeout` = hold left - 450 s, so gpu_slot's max hold (SIGTERM, SIGKILL after 10 s) never reaches a rendering engine | `../capture_round.sh` |
| Checkers: r2 pass lines (`island_r2_check.py`), road band (`island_road_band.py`, r03 WIP) | `tools/export/` |

## Build (timed; `build_timings_island.json`)
| step | seconds |
|---|---|
| export whole island (vite + headless Chrome) | 172 |
| city_prep (patch, split_giants, prep_textures 604 on the SD card, street kit 227, props 52) | ~945 |
| city_extra (cars, trees, traffic, far skyline, sunmask 77, island_boxes 86: 173,097 boxes) | 191 |
| city_pass1 first attempt (tex + 342 meshes imported/finished; killed by the 7,200 s subprocess timeout, -nullrhi) | 7,206 |
| city_pass1 resumed: mesh (419 remaining) 4,325 + kit (272 tiles, ~20 s each: 3 distance-field builds per mesh) 5,360 + fsky/map/coll ~490 + **wp 1,610 (boxes 973)** | 11,869 |
| build_manhattan map step | 34 |
Content: 1.5 GB (`du -sh unreal/WebHomage/Content`). Internal disk >= 273 GB free throughout (exports / frames on the SD card).
Long poles: the double static-mesh build per mesh (import, then `finish_mesh` collision / Nanite settings rebuild) and distance fields.

## Pass lines
| # | target | result |
|---|---|---|
| 1a | 0 facadeLod inside the detailed region | **0** (`coll_audit.json` `facadeLod_meshes_inside_region`; the island export has 0 facadeLod meshes at all) PASS |
| 1b | facadeLod_min_dist >= 1,200 m on r1-r3 | **no facadeLod mass in the build** (route checker: 0 facadeLod tiles, distance undefined = infinite) PASS. Far layer = far shores / far skyline / hinterland only |
| 2 | r2 (swing held, autoChain gap 0.3 s): no unanswered release to t=30 s | **0 unanswered** PASS |
| 2 | max re-web gap <= 1.5 s | **2.65 s FAIL** (t 20.13 s: swing into the block at x 192-216 / y 729, topOut + wall-run, see below) |
| 2 | >= 60 % of gaps <= 0.5 s | **68.8 %** (11 / 16) PASS |
| 2 | every anchor on a drawn facade | **0 webs on nothing** (18 distinct anchors) PASS |
| 2 | 0 ground / land frames after t = 1 s | **52 FAIL** (t 20.55 s: land on a fire-escape deck at 41 m, then ground on that roof; 0 street frames) |
| 3 | r2 stills t=26 / 28 s: road band >= 1 % lane paint, luminance std >= 35 | **t26 7.38 % / 25.7, t28 0.68 % / 37.8: FAIL** — both frames are at roof height (z 65-72 m) in the block west of the avenue, no road in frame (the test needs the hero over the avenue). Over the avenue the street layer reads: t12 frame (y 480) shows asphalt, double yellow, crosswalks, bus lane, cars, trees |
| 4 | I5 phantom <= 1 % / hollow <= 2 % island-wide | **0.25 % / 0.37 %** (4.07 M building cells; raw 1.35 / 17.68 %) PASS |
| 4 | I6 0 fall / stuck / mid-air / wall-air on r1-r4 (drawn checks) | r1 **0/0/0/0**, r2 **0/0/0/0**, r3 **0/0/0/0**, r4 **0/0/0/0** PASS |
| 4 | capsule-overlap frames <= r02 (0 / 0 / 7 / 31) | r1 **0**, r2 **20** (fire-escape decks during the t 20.4 s wall-run: traversal's wall-run-through-decks, `../REQUEST-traversal-r03.md` §2; r02's r2 never reached that block), r3 **7**, r4 **31**: r2 FAIL, others equal |
| 5 | CHASE BANK excluded | `signs.png` row 4 repainted (HARBOR SAVINGS), verified on the built texture source `_scratch/island/tex/signs.png` PASS |
| 5 | internal disk >= 150 GB; every build step timed | 273 GB free; `build_timings_island.json` PASS |

## Routes (`route_check_r*.json`, `r2_check.json`, `r4_check.json`)
| route | captured | path | anchors | max re-web gap | overlap frames | notes |
|---|---|---|---|---|---|---|
| r1 north avenue | 29.1 s (1,751 frames: stopped with stop_ue.sh 55 s before the hold's max; 3-4 engines on the GPU, ~45 frames/min) | 1,142 m | 14 | 1.73 s | 0 | identical behaviour to r02 (1,166 m) |
| r2 south avenue | 30.4 s | 866 m (r02: 1,273 m with gap 0.8 s) | 18 | 2.65 s | 20 | ends at y 817, z 95 m on roofs west of the avenue |
| r3 crosstown east | 30.4 s | 489 m | 22 | 6.43 s (topOut loop under a fire-escape deck, unchanged since r02: REQUEST §1) | 7 | identical to r02 |
| r4 wall-run / roofs | 29.65 s (run_game timeout, graceful) | 489 m | 6 | — | 31 | identical to r02 (run ends in a vault, drop lands on the street) |
All four routes run inside the old M1 rectangle (y -784 .. 817): the shot list's routes start in Midtown. M2 coverage is shown by the
a1 stills (north / south over the island) and by the game log (`warmup_webtravworld_log.txt`: 172,553 boxes indexed island-wide,
775 visible solids at init) and the dump (`dump_check.json`: 55 / 55 facade / roofs / detail / fire-escape tiles solid, ctf 3, QueryOnly;
far-off rows overlapping the region = far shore + Roosevelt Island land by name, as in r02).

### Why r2 fails
`r2_south_avenue_telemetry.csv`: with the 0.3 s re-press the chain is faster and swings wider; at y ~700 (Madison Sq., where the west
building line steps back) the hero is pulled west by an anchor at (223, 702), meets the block at x 192-216 / y 729 at 27 m, tops out, wall-runs
it (fire-escape decks: the 20 overlap frames), lands on a deck at 41 m and continues on roofs to z 95 m. The geometry is drawn and solid;
nothing is phantom or hollow there (I5). The steering away from the avenue is traversal behaviour (`../REQUEST-traversal-r03.md`); the
route script was not changed to dodge it.

## Files
`r1_north_avenue.mp4`, `r2_south_avenue.mp4`, `r3_crosstown_east.mp4`, `r4_wallrun_roofs.mp4` (1920x1080 60 fps, H.264 2-pass,
<= 14.7 MB), `*_telemetry.csv`, `*_log_excerpt.txt`, `stills/` (contact frames 5/12/20/26/28 s; a1 3840x2160), `route_check_r*.json`,
`r2_check.json`, `road_band_r2.json`, `r4_check.json`, `dump_check.json`, `prims_dump.csv.gz`, `coll_audit.json` + map,
`build_timings_island.json`, `gpu_hold_*.json`.
