# Island (piece A) — round 01 (Phase-0 spike + Midtown M1)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

All captures come from the REAL game (`-game`, offscreen, `Scripts/run_game.sh`), map `/Game/Maps/Manhattan_WP` (World Partition, 256 m cells,
1.2 km loading range), golden look rig, every run through `/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label island` (cap 1).
Not perf runs: no frame-time numbers here (the capture holds were `contaminated=true`, no exclusive lock).

## Captures (`-movie` = fixed 1/60 s step)
Internal resolution (CAPTURE.md: `r.ScreenPercentage` auto by display size, TSR upscale; no `-exec r.ScreenPercentage` was passed):
**1920x1080 output = 1399x787 internal; 3840x2160 output = 1920x1080 internal (50 %).**

| file | what | output |
|---|---|---|
| `r1_north_avenue.mp4` + `_telemetry.csv` | 30 s: street sprint north up the avenue (x 250 m), first swing, chain to y -991 | 1920x1080 60 fps, H.264 2-pass 14.6 MB |
| `r2_south_avenue.mp4` + csv | 30 s: swing chain south into the tiles that were bare masses before M1 | ROUTE_R2 |
| `r3_crosstown_east.mp4` + csv | 30 s: swing chain east along the y 640 m cross street (new tiles) | ROUTE_R3 |
| `r4_wallrun_roofs.mp4` + csv | 30 s: wall-run, top-out, roof run, jumps, swing | ROUTE_R4 |
| `stills/a1_high_north_*_3840x2160.jpg`, `a1_high_south_*` | high stills over Midtown looking north / south | 3840x2160 |
| `stills/r*_t{5,12,20,28}s_1920x1080.jpg` | contact frames of each route | 1920x1080 |

## SPEC numbers (checkers: `tools/export/island_coll_audit.py`, `tools/export/island_route_check.py`)
ROUTE_TABLE

## What changed this round (resumed part, 17:05 onward)
1. **Rooftop equipment boxes** (`tools/export/island_boxes.py` rule 4): mechanical penthouses (`equipment` BOX solids >= 2 m both sides) are
   now WHBox cubes. They were drawn but had no collision: the hollow cells sat a near-constant 5.0 m above their box. Hollow 5.81 -> 0.22 %.
2. **Route checker fix**: the telemetry z is the body centre (H = 0.95 m above the feet); the checker now compares the feet.
3. **Per-tile collision ISMs** (`SM2_WHBOX_MODE=ism` in `build_city.py`): one invisible Cube ISM per 256 m tile instead of one actor per box;
   WP step 45 s instead of 2,203 s, 6,227 instead of 62,985 external-actor packages. Built as `/Game/Maps/Manhattan_WP_ism`; ISM_STATUS
4. `build_manhattan.py`: instance gate counts real UnrealEditor processes; `SM2_ISLAND_WP_MAP` builds a test map beside the real one.
5. `capture_round.sh`: route videos are 2-pass sized from run_game's master (the crf loop overshot to 15.9 MB).

## Known gaps
- **I2 cannot pass in M1 by construction**: the detailed region is 2,304 m north-south, so no point in it is 1.2 km from both edges; r1 reaches
  y -991 m, 289 m from the first facadeLod tile at y -1280. M2 (whole island) is the fix.
- The traversal's `AddBox` skips boxes under 1.0 m tall (282 of 56,816: thin roof tiers / plant): they collide physically but are not perch /
  anchor boxes.
- Build time: M1 fresh ~94 min with one actor per box; with ISM boxes the WP step drops by ~35 min. Mesh import (2,470 s for M1) is now the
  long pole for the 90 min whole-island target.
