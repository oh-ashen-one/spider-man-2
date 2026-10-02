# Tricks (C) — round 01 shot list

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

| Clip | What | How |
|---|---|---|
| `t60_trick_reel.mp4` | ONE continuous 60.5 s chain in the lit city, a flip program on every web release, the 12 release programs cycled (2nd lap repeats them -> same-type pairs). Route: the y -560 edge street east (sun behind), 5th Av (x 250) south from 12.6 s, south past the detailed block after ~37 s (beyond y 256 the city is the low-detail facade layer) | script `docs/night1/tricks/scripts/t60_trick_reel.json` (turn keys fitted by `tools/tricks/auto_route.py` + `route_search.py`, -nullrhi probes), `tools/tricks/capture.sh` |
| `t60_trick_reel_telemetry.csv` | per-frame traversal telemetry of the run | WebTravCharacter |
| `t60_trick_reel_pose.csv.gz` | rendered bone positions per frame (`-WHTrickPose`) | WebTravFlips.cpp |

## Capture settings

| | |
|---|---|
| output | 1920x1080, 60 fps, H.264 mp4 (<= 15 MB) |
| internal resolution | 1920x1080 (`r.ScreenPercentage 100`, native) |
| time step | fixed 1/60 s (`-benchmark -fps=60 -dumpmovie`), offscreen `-game` (`Scripts/run_game.sh`), 0.8 s pre-roll cut |
| AA / GI | TSR, Lumen (project defaults), map `/Game/Maps/Manhattan` (golden) built in this worktree by `build_manhattan.py` |
| GPU | every run under `gpu_slot.sh capture` on a GPU shared with other sessions (contaminated: no perf claim) |

**Rendered in windows of one deterministic run.** Under the lock's background priority the movie dumps ran at ~1-1.5 frames/s, so 60 s
does not fit one 40-min hold. The same scripted run was rendered three times, each writing frames only for its window
(`-WHTrickDumpFrom/To`, WebTravFlips.cpp): 0-25 s, 25-42.5 s, 42.5-60.5 s, concatenated. Window 0 is the first 25 s of an earlier run whose
keys are identical up to 29.97 s (frame alignment from its log: telemetry frame f = movie frame f + 50, constant over 11 trick starts).
The telemetry of the runs is compared row by row (`capture.sh` prints the determinism line). A window boundary can show a small
lighting / TSR-history difference (each window's engine warmed up separately).
