# Round 07: sky / time-of-day numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

All numbers from the real game (`Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`); stills and clips 1920x1080 internal 100 % of output; the lapse at the resolution and sub-stepping written in its json (fixed 1/60 s step). Instruments: `tools/perf_ue/{capture_tod_lapse,twilight_check,tod_tests,night_tests,clip_check}.py`.

## L23b time-lapse (S4 perch, 04:00 start, nominal 2 h/s, 720 frames, 960x540 output, internal 100% of output, sub-steps 1)

Instrument condition: metering pinned per frame: pp.AutoExposureSpeedUp / Down = 40 (capture-only live pins; the game keeps 6 / 3) + segmented sub-stepped render: 4-5.5 h x4; 5.5-9.2 h x16; 9.2-17.6 h x4; 17.6-21.4 h x16; 21.4-28 h x4 (each segment starts 0.3 h early and drops those frames: warm-up of the lighting caches); x16 = clock 0.125 h/s, x4 = 0.5 h/s, fixed 1/60 s step, every N-th frame kept; no render setting is changed.

Live commands: `exec wh.ToDSet pp.AutoExposureSpeedUp 40;exec wh.ToDSet pp.AutoExposureSpeedDown 40`.

| max jump | p99 | median | frames > 3 | frames > 1.5 | 05:00-21:30 max mean | at h | max clipped % | at h | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 2.58 | 2.07 | 0.05 | 0 | 33 | 98.2 | 18.34 | 0.14 | 5.39 | FAIL |

Biggest jumps: 20.77 h +2.6 (51 -> 48), 20.27 h +2.5 (42 -> 44), 18.71 h +2.4 (86 -> 84), 7.91 h +2.4 (75 -> 77), 7.87 h +2.4 (72 -> 75), 20.31 h +2.3 (44 -> 47)

## L27 twilight dome continuity (dome_check.py; S4 / S4w at 19:30 19:48 20:00 20:30, S4 / S4e at 06:30 07:00 are the verdict stills)

| still | pose | hour | sky Y | far Y | sky-far (a >= 10) | 8-row step max @row (b <= 25) | worst column band | clip rows 0-150 % (c <= 0.3) | sky B-R (d facing -90..-20) | mean Y | a | b | c | d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h13 | S4 | 13.0 | 123.7 | 118.6 | +5.1 | 8.0 @101 | 18.5 | 0.00 | +30.6 | 80.3 | FAIL | ok | ok |  |
| h18.4 | S4 | 18.4 | 158.5 | 143.6 | +14.9 | 8.5 @101 | 17.2 | 0.00 | -69.1 | 97.7 | ok | ok | ok |  |
| h19.5 | S4 | 19.5 | 108.0 | 93.7 | +14.3 | 4.4 @135 | 18.9 | 0.01 | -57.8 | 54.6 | ok | ok | ok |  |
| h19.8 | S4 | 19.8 | 100.2 | 59.9 | +40.3 | 24.3 @136 | 75.0 | 0.22 | -17.6 | 46.4 | ok | ok | ok |  |
| h19 | S4 | 19.0 | 116.1 | 105.9 | +10.2 | 3.2 @272 | 12.8 | 0.00 | -91.6 | 72.3 | ok | ok | ok |  |
| h20.5 | S4 | 20.5 | 100.0 | 48.8 | +51.2 | 8.4 @100 | 31.6 | 0.00 | -34.4 | 46.6 | ok | ok | ok |  |
| h20 | S4 | 20.0 | 71.3 | 40.4 | +30.9 | 14.3 @136 | 69.0 | 0.00 | -13.9 | 37.1 | ok | ok | ok |  |
| h21.5 | S4 | 21.5 | 47.4 | 32.1 | +15.3 | 11.6 @176 | 30.8 | 0.00 | +12.2 | 44.1 | ok | ok | ok |  |
| h21 | S4 | 21.0 | 28.5 | 40.2 | -11.7 | 5.7 @125 | 20.6 | 0.00 | +9.0 | 44.1 | FAIL | ok | ok |  |
| h22 | S4 | 22.0 | 45.5 | 29.0 | +16.5 | 12.0 @176 | 30.0 | 0.00 | +15.0 | 42.3 | ok | ok | ok |  |
| h6.5 | S4 | 6.5 | 110.9 | 67.4 | +43.5 | 11.5 @104 | 39.7 | 0.00 | -38.6 | 42.7 | ok | ok | ok |  |
| h7.5 | S4 | 7.5 | 119.9 | 77.2 | +42.7 | 11.3 @103 | 30.2 | 0.00 | -13.1 | 61.7 | ok | ok | ok |  |
| h7 | S4 | 7.0 | 146.4 | 83.7 | +62.8 | 18.6 @100 | 51.6 | 0.00 | -64.8 | 56.4 | ok | ok | ok |  |
| mist_h7.6 | S4 | 7.6 | 122.5 | 81.1 | +41.5 | 10.8 @103 | 29.8 | 0.00 | +2.9 | 64.4 | ok | ok | ok |  |
| h6.5 | S4e | 6.5 | 104.7 | 83.3 | +21.3 | 21.2 @100 | 68.2 | 0.00 | -34.2 | 31.7 | ok | ok | ok | ok |
| h7.5 | S4e | 7.5 | 143.9 | 103.5 | +40.5 | 16.8 @108 | 25.1 | 0.00 | -77.8 | 39.1 | ok | ok | ok | ok |
| h7 | S4e | 7.0 | 127.7 | 89.5 | +38.2 | 20.7 @109 | 39.5 | 0.05 | -78.2 | 27.9 | ok | ok | ok | ok |
| mist_h7.6 | S4e | 7.6 | 142.2 | 100.3 | +41.9 | 16.6 @108 | 26.8 | 0.00 | -73.6 | 39.2 | ok | ok | ok | ok |
| h19.5 | S4w | 19.5 | 110.9 | 87.8 | +23.1 | 12.3 @104 | 54.2 | 0.06 | -59.0 | 50.5 | ok | ok | ok | ok |
| h19.8 | S4w | 19.8 | 126.3 | 85.8 | +40.5 | 12.7 @103 | 42.4 | 0.00 | -32.4 | 39.3 | ok | ok | ok | ok |
| h19 | S4w | 19.0 | 127.4 | 110.3 | +17.1 | 9.9 @106 | 22.3 | 0.00 | -96.0 | 48.0 | ok | ok | ok | FAIL |
| h20.5 | S4w | 20.5 | 97.8 | 43.8 | +54.0 | 7.0 @131 | 36.5 | 0.00 | -35.9 | 46.4 | ok | ok | ok | ok |
| h20 | S4w | 20.0 | 136.3 | 81.9 | +54.4 | 17.8 @124 | 50.4 | 0.01 | -36.3 | 44.0 | ok | ok | ok | ok |

| variant prefix | S4 mean 20:30 | S4 mean 22:00 | L27e (no pit) |
|---|---|---|---|
| (none) | 46.58 | 42.28 | ok |

## L24 / L25 / L26 sky stills

```
| still | pose | hour | sky band Y | sky B-R | far Y | sky-far | L24a | L24b | mean Y | moon px | moon peak Y | hp std (excl / incl moon) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | S1 | 18.4 | 64.7 | -26.0 |  |  |  |  |  |  |  |  |
| h22 | S1 | 22.0 | 45.4 | +2.5 |  |  |  |  |  |  |  |  |
| mist_h7.6 | S1 | 7.6 | 83.1 | -53.0 |  |  |  |  |  |  |  |  |
| h18.4 | S2 | 18.4 | 125.7 | -73.4 |  |  |  |  |  |  |  |  |
| h22 | S2 | 22.0 | 50.3 | -10.3 |  |  |  |  |  |  |  |  |
| h18.4 | S3 | 18.4 | 68.9 | -23.0 |  |  |  |  |  |  |  |  |
| h22 | S3 | 22.0 | 45.1 | -6.5 |  |  |  |  |  |  |  |  |
| h13 | S4 | 13.0 | 123.7 | +30.5 | 118.6 | +5.1 | ok |  | 80.3 |  |  | 2.00 |
| h18.4 | S4 | 18.4 | 158.5 | -69.1 | 143.6 | +14.9 | ok |  | 97.7 |  |  | 3.16 |
| h19.5 | S4 | 19.5 | 108.0 | -57.8 | 93.7 | +14.3 | ok |  | 54.6 |  |  | 3.28 |
| h19.8 | S4 | 19.8 | 100.2 | -17.6 | 59.9 | +40.3 | ok |  | 46.4 |  |  | 13.82 |
| h19 | S4 | 19.0 | 116.1 | -91.6 | 105.9 | +10.2 | ok |  | 72.3 |  |  | 2.74 |
| h20.5 | S4 | 20.5 | 100.0 | -34.4 | 48.8 | +51.2 | ok |  | 46.6 |  |  | 13.28 |
| h20 | S4 | 20.0 | 71.3 | -13.9 | 40.3 | +30.9 | ok |  | 37.1 |  |  | 11.00 |
| h21.5 | S4 | 21.5 | 47.3 | +12.2 | 32.1 | +15.3 | ok |  | 44.2 |  |  | 3.24 |
| h21 | S4 | 21.0 | 28.5 | +9.0 | 40.2 | -11.7 | FAIL |  | 44.1 |  |  | 1.30 |
| h22 | S4 | 22.0 | 45.6 | +15.0 | 29.0 | +16.5 | ok |  | 42.3 |  |  | 3.23 |
| h6.5 | S4 | 6.5 | 110.9 | -38.6 | 67.4 | +43.5 | ok |  | 42.7 |  |  | 8.27 |
| h7.5 | S4 | 7.5 | 119.9 | -13.1 | 77.2 | +42.7 | ok |  | 61.7 |  |  | 2.41 |
| h7 | S4 | 7.0 | 146.4 | -64.8 | 83.7 | +62.8 | ok |  | 56.4 |  |  | 5.31 |
| mist_h7.6 | S4 | 7.6 | 122.5 | +2.9 | 81.1 | +41.4 | ok |  | 64.4 |  |  | 2.38 |
| h6.5 | S4e | 6.5 | 104.7 | -34.2 |  |  |  | ok | 31.7 |  |  |  |
| h7.5 | S4e | 7.5 | 143.9 | -77.8 |  |  |  | ok | 39.1 |  |  |  |
| h7 | S4e | 7.0 | 127.7 | -78.2 |  |  |  | ok | 27.9 |  |  |  |
| mist_h7.6 | S4e | 7.6 | 142.2 | -73.6 |  |  |  |  | 39.2 |  |  |  |
| h22 | S4m | 22.0 | 65.8 | +2.0 |  |  |  |  | 42.5 | 30.8 | 255 | 2.32 / 2.41 |
| h19.5 | S4w | 19.5 | 110.9 | -59.0 |  |  |  | ok | 50.5 |  |  |  |
| h19.8 | S4w | 19.8 | 126.3 | -32.4 |  |  |  | ok | 39.3 |  |  |  |
| h19 | S4w | 19.0 | 127.4 | -96.0 |  |  |  | ok | 48.0 |  |  |  |
| h20.5 | S4w | 20.5 | 97.8 | -35.9 |  |  |  | ok | 46.4 |  |  |  |
| h20 | S4w | 20.0 | 136.3 | -36.3 |  |  |  | ok | 44.0 |  |  |  |
| h18.4 | S5 | 18.4 | 129.6 | -58.4 |  |  |  |  |  |  |  |  |
| h22 | S5 | 22.0 | 30.5 | +5.9 |  |  |  |  |  |  |  |  |
| h18.4 | S6 | 18.4 | 92.4 | -45.8 |  |  |  |  |  |  |  |  |
| h22 | S6 | 22.0 | 30.7 | +10.9 |  |  |  |  |  |  |  |  |
| h18.4 | S7 | 18.4 | 75.7 | -46.3 |  |  |  |  | 61.3 |  |  |  |
| h22 | S7 | 22.0 | 32.1 | +7.3 |  |  |  |  | 43.9 |  |  |  |
| h13 | S8 | 13.0 | 126.4 | +20.3 |  |  |  |  |  |  |  |  |
| h18.4 | S8 | 18.4 | 146.7 | -61.0 |  |  |  |  |  |  |  |  |
| h22 | S8 | 22.0 | 51.2 | +12.5 |  |  |  |  |  |  |  |  |

L26 S1 correlation vs golden (tod_S1_1920x1080_h18.4.jpg): mist_h7.6 0.541
```

## Golden 18.4 and night 22 spec numbers (tod_tests.py)

```
| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 47..98 | 3/8 | 1.80 | -55..-23 | 5.8..26.3 | 6.3..36.1 | 0.44..0.57 | -21.7 | +15.8 | +25.2 |  |  |  |  |
| h22 | night | 8 | 39..57 | 8/8 | 0.80 | -5..+10 |  |  |  | -18.9 | -1.6 | +7.1 | 2.71 | 33.9 | 42.3 | 10/13/4 |
| h13 | midday | 2 | 80..82 | 0/2 | 0.00 | -1..+9 |  |  |  | -11.0 | -11.6 | +46.9 |  |  |  |  |
```

Per-still tables: `TESTS_tod.md`.

## Hero box (swing_tod_18h4_hero_luma.json)

| frames_measured | bbox_mean_luma_min | bbox_mean_luma_p5 | bbox_mean_luma_mean | bbox_mean_luma_max | frames_below_threshold | L15b_frames_with_clipped_px | L15b_max_clipped_px_in_box |
|---|---|---|---|---|---|---|---|
| 718 | 17.1 | 43.2 | 89.6 | 150.4 | 24 | 635 | 11041 |

## Hero box (swing_tod_22_hero_luma.json)

| frames_measured | bbox_mean_luma_min | bbox_mean_luma_p5 | bbox_mean_luma_mean | bbox_mean_luma_max | frames_below_threshold | L15b_frames_with_clipped_px | L15b_max_clipped_px_in_box |
|---|---|---|---|---|---|---|---|
| 718 | 19.9 | 35.9 | 58.0 | 124.8 | 91 | 674 | 2159 |

## swing_tod_18h4.mp4

mean Y 57.9 (min 19.6 max 76.8), B-R mean -33.4, clipped mean 0.33 %, L18 edge/centre p50 0.74

## swing_tod_22.mp4

mean Y 35.6 (min 21.8 max 55.3), B-R mean +3.5, clipped mean 0.54 %, L18 edge/centre p50 0.57

