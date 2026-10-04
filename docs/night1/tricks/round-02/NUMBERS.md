# Tricks (C) — round 02 measured numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

**Source: the `-nullrhi` probe of the real game, not a rendered reel.** The reel render of this build was started (window 0, 20:02) and
stopped at 20:05 by the GPU health monitor (`health.log`: "WS-STARVE-WARN(gpu 100% ws 0%) probe=FAIL STOP(TERM) newest -game
pid=33556"); that engine then stayed in the exiting state inside the GPU driver (`ps`: `33556 ?E`, still there at 20:29) with the GPU at
100 % and WindowServer at 0 % CPU, the lock PAUSED and DEMOTED. No further engine was launched; the remaining render holds were cancelled.
So there is no r02 movie, no 13 Mbps encode and no blind critic pack in this round.

The probe is the same deterministic run the render would have been (fixed 1/60 s step, `-WHTravScript=t60_trick_reel.json`, 0.8 s
pre-roll; r01: the rendered run's telemetry equalled its probe row for row). The pose log (`-WHTrickPose`) holds the posed skeleton of
every frame (the anim graph runs without the renderer), so every pose line below is measured on the same bones a render would show:
`t60_trick_reel_probe_telemetry.csv` (3665 rows, 61.07 s) and `t60_trick_reel_probe_pose.csv.gz`; full checker output `CHECK_probe.txt`
(`tools/tricks/tricks_check.py`). Build: night1/tricks after merging Opus-5.5-Loop-Night-1 035c2c92, WebTravFlips.cpp = this commit.

| Line | Target | Measured (r02 probe) | r01 (rendered) | |
|---|---|---|---|---|
| C | catch: chest <= 250 deg/s in every 0.1 s window, trick end - 3 frames .. + 0.4 s, all 22 | 0 of 22; median of the per-trick maxima 435 deg/s, worst 821 (frontDouble 16.45 s), largest single frame 2104 deg/s | 0 of 21 measured; median 603, worst 921, frame 1894 | FAIL |
| P | >= 10 programs in one clip | 12 programs, 22 instances, route airborne / swinging for the whole 61 s | 12 / 22 | PASS |
| V1 | same-type pairs differ >= 40 deg/s | 10 of 10 pairs | 10 of 10 | PASS |
| V2 | durations +-10-20 % | flip_scale 0.850-1.131, 12 of 22 deviate >= 10 % | same | PASS |
| K | tight tuck held >= .25 s | 9 holds, all tight >= .25 s; knee gap max .197 m | same | PASS |
| G2 | pointed toes >= 90 % | 96.7 % of 4378 foot samples | 99.9 % | PASS |
| G3 | head spot >= 15 deg in the open-out | 22 of 22 | 22 of 22 | PASS |
| G4 | last 0.15 s open shape <= 300 deg/s | 22 of 22 | 22 of 22 | PASS |
| R | only WebTravFlips.* changed vs integration | `git diff origin/Opus-5.5-Loop-Night-1 -- unreal/` = WebTravFlips.{h,cpp} | | PASS (code); axes need the critic |
| L | 0 slow limb samples | 8 of 345 (catch poses held while a late web is searched: 7.20, 35.60, 42.90 s; kick-out 23.40 / 23.60; r01's 28.50, 45.00, 54.10) | 4 of 345 | FAIL |
| G1 (median rule) | layout >= 170 deg | PASS (lowest held-layout medians unchanged from r01) | PASS | PASS |
| G1f | layout knees / hips >= 170 deg in EVERY frame | knees below in 102 of 516 leg samples (min 73.8), hips 71 of 402 (min 126.3) | 100 / 520, 70 / 406 | FAIL |
| PEN | pencil knee median >= 170 | 134.9 deg (p10 82.9) | 134.9 | FAIL |
| PIK | pike hip median <= 90, knee p10 >= 165 | hip 125.4, knee p10 105.3 | same | FAIL |
| X | more than one exit pose | Reach 10, CatchBank 4, CatchLow 3, Kickout 2, CatchBankL 2, CatchLowL 1 | Reach 19, Kickout 2 | PASS |
| encode | one continuous 60 s clip >= 12 Mbps | not rendered (see above); capture.sh now encodes 13 Mbps, 8 s parts + a local full file | 1.8 Mbps | — |
| light | hero reads against dark facades | not verified (render stopped); the render was set to `-WHHeroFill=16000,36000` | | — |

## Catch rotation per trick end (`tools/tricks/catch_table.py`)

| # | program | end (s) | r01 max 0.1 s (deg/s) | r02 max 0.1 s (deg/s) | r02 max frame | next | r02 exit shape | r02 predicted (lean pitch / sideways rest, deg) |
|---|---|---|---|---|---|---|---|---|
| 1 | backSingle | 2.63 | 255 | 275 | 348 | swing | CatchLow | swing 30.6 / -15.4 |
| 2 | frontSingle | 5.20 | 548 | 547 | 1063 | swing | Reach | swing 82.6 / -10.0 |
| 3 | backPike | 7.57 | 543 | 483 | 1240 | swing | Reach | swing 32.7 / -23.9 |
| 4 | barani | 10.63 | 724 | 455 | 1298 | air | Reach | air 92.8 / 0.0 |
| 5 | backLayout | 13.30 | 632 | 670 | 1429 | air | Reach | swing 75.8 / 18.7 |
| 6 | frontDouble | 16.45 | 921 | 821 | 1790 | swing | CatchBank | swing 29.4 / -5.1 |
| 7 | fullTwist | 18.95 | 724 | 384 | 543 | swing | Reach | swing 77.2 / -21.2 |
| 8 | frontPikeSwan | 21.25 | 699 | 520 | 885 | swing | CatchBank | swing 78.0 / 12.1 |
| 9 | backDouble | 23.70 | 598 | 365 | 487 | swing | Kickout | swing 71.1 / -30.7 |
| 10 | rudi | 26.57 | 772 | 365 | 468 | swing | CatchLowL | swing 75.5 / 25.1 |
| 11 | corkscrew | 29.47 | 720 | 458 | 625 | swing | CatchLow | swing 71.5 / -22.5 |
| 12 | backTripleChain | 33.57 | 422 | 324 | 1268 | swing | CatchBankL | swing 16.0 / 44.3 |
| 13 | backSingle | 35.88 | 771 | 415 | 631 | swing | Reach | swing 80.1 / -21.3 |
| 14 | frontSingle | 38.30 | 603 | 633 | 935 | swing | Reach | swing 45.0 / 68.4 |
| 15 | backPike | 40.65 | 313 | 292 | 1247 | swing | CatchBank | swing 38.9 / -16.7 |
| 16 | barani | 43.08 | 349 | 326 | 485 | swing | Reach | swing 28.6 / 32.6 |
| 17 | backLayout | 45.73 | 652 | 364 | 387 | air | Reach | air 88.1 / 0.0 |
| 18 | frontDouble | 49.40 | 900 | 717 | 939 | air | Reach | air 92.1 / 0.0 |
| 19 | fullTwist | 52.20 | 422 | 277 | 816 | swing | CatchBank | swing 31.3 / -16.6 |
| 20 | frontPikeSwan | 54.82 | 375 | 300 | 467 | swing | CatchBankL | swing 19.1 / 39.3 |
| 21 | backDouble | 57.92 | 314 | 651 | 938 | swing | Kickout | air 92.9 / 0.0 |
| 22 | rudi | 60.43 | (clip ended) | 565 | 2104 | swing | CatchLow | swing 69.7 / -17.6 |

## Where the remaining rotation comes from (probe b-f, pose log mesh / body / predicted-frame quaternions)
- The predicted anchor equals the traversal's own catch anchor in 19 of 20 web catches (frontDouble 16.45 s: 45.7 m off; backDouble
  57.92 s: no web predicted, caught).
- Body frame 0.1 s after the catch vs the predicted swing frame (18 catches): yaw about the rope 0-55 deg (the swing frame's forward is
  the small velocity component off a rope that runs almost along the velocity; the twist is applied x0.3, the best measured factor:
  residual mean 35 deg vs 46 deg at x1), pitch about -10 deg (the swing itself), roll 5-56 deg -- the rope's sideways lean plus
  `S.Roll = Sw.Bank * 0.5` from the previous swing's stale bank. A flip has no roll channel (PoseFigure applies pitch + twist).
- Single-frame chest jumps at the attach frame reach 2104 deg/s (rudi 60.43 s). One source in the code: WebTravAnimInstance sets
  `SpineBank = -0.35 * Swing.Bank` (rad, on spine1 + spine2) in the first swing frame, unramped, from the same stale bank -- up to ~20 deg
  in one frame; the share of each source per catch was not separated (REQUEST-traversal.md items 7-9).
- Programs that run out of web (barani 10.63, backLayout 45.73, frontDouble 49.40 s) now lean into the streamlined air frame before the
  end (windows starting in the first 0.1 s after the end: barani 2-29, backLayout 10-69, frontDouble 36-281 deg/s); the web then catches
  0.1-0.3 s later from the dive frame (the 364-717 deg/s maxima of those three are the later catches).
