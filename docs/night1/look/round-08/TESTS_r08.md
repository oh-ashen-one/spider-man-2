# Round 08: sky / time-of-day numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

All numbers from the real game (`Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`); stills and clips 1920x1080 internal 100 % of output; the lapse at the resolution and sub-stepping written in its json (fixed 1/60 s step). Instruments: `tools/perf_ue/{capture_tod_lapse,twilight_check,tod_tests,night_tests,clip_check}.py`.

## L23b time-lapse (S4 perch, 04:00 start, nominal 2 h/s, 720 frames, 960x540 output, internal 100% of output, sub-steps 1)

Instrument condition: metering pinned per frame: pp.AutoExposureSpeedUp / Down = 40 (capture-only live pins; the game keeps 6 / 3) + segmented sub-stepped render: 4-5.5 h x4; 5.5-9.2 h x16; 9.2-17.6 h x4; 17.6-21.4 h x16; 21.4-28 h x4 (each segment starts 0.3 h early and drops those frames: warm-up of the lighting caches); x16 = clock 0.125 h/s, x4 = 0.5 h/s, fixed 1/60 s step, every N-th frame kept; no render setting is changed.

Live commands: `exec wh.ToDSet pp.AutoExposureSpeedUp 40;exec wh.ToDSet pp.AutoExposureSpeedDown 40`.

| max jump | p99 | median | frames > 3 | frames > 1.5 | 05:00-21:30 max mean | at h | max clipped % | at h | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 3.07 | 2.20 | 0.05 | 1 | 37 | 98.2 | 18.31 | 0.16 | 5.51 | FAIL |

Biggest jumps: 19.11 h +3.1 (82 -> 79), 20.27 h +2.8 (40 -> 43), 19.94 h +2.8 (48 -> 45), 6.87 h +2.6 (61 -> 64), 19.47 h +2.5 (67 -> 64), 19.54 h +2.4 (64 -> 62)

## L28 twilight city light (r08_check.py: L5 on S4e 07:00 / 07:30 and S4w 19:00, sky saturation, blue hour, sub-horizon disk)

| still | mean (59..118) | Y<10 % (<= 8.8) | clipped % (<= 0.7) | L5 | sky sat (>= .40) | SAT | sky B-R | sky Y |
|---|---|---|---|---|---|---|---|---|
| S4e_7 | 65.7 | 0.00 | 0.006 | ok | 0.490 | ok | -81.6 | 131.5 |
| S4e_7.5 | 71.7 | 0.00 | 0.000 | ok | 0.443 | ok | -78.1 | 146.3 |
| S4w_19 | 70.8 | 0.00 | 0.000 | ok | 0.546 | ok | -96.4 | 127.8 |

Blue hour S4 20:30 sky B-R +6.6 (>= 0: ok), sky Y 77.9, sky sat 0.139

| still | sub-horizon blobs | largest diam px | at (x, y) | peak Y | band peak Y | round-07 disk box: peak Y / over local median | zero disk |
|---|---|---|---|---|---|---|---|
| S4w_19.5 | 0 | - | - | - | 117 | 82 / +24 | ok |
| S4w_19.8 | 0 | - | - | - | 138 | 80 / +41 | ok |
| S4w_20 | 0 | - | - | - | 202 | 66 / +42 | ok |
| S4w_20.5 | 0 | - | - | - | 237 | 157 / +119 | ok |

## L27 twilight dome continuity (dome_check.py; S4 / S4w at 19:30 19:48 20:00 20:30, S4 / S4e at 06:30 07:00 are the verdict stills)

| still | pose | hour | sky Y | far Y | sky-far (a >= 10) | 8-row step max @row (b <= 25) | worst column band | clip rows 0-150 % (c <= 0.3) | sky B-R (d facing -90..-20) | mean Y | a | b | c | d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h13 | S4 | 13.0 | 122.0 | 118.4 | +3.5 | 8.0 @101 | 18.7 | 0.00 | +31.2 | 80.3 | FAIL | ok | ok |  |
| h18.4 | S4 | 18.4 | 158.5 | 143.4 | +15.1 | 8.4 @101 | 17.2 | 0.00 | -69.2 | 97.3 | ok | ok | ok |  |
| h19.5 | S4 | 19.5 | 105.7 | 90.1 | +15.6 | 6.4 @117 | 23.4 | 0.03 | -57.4 | 60.8 | ok | ok | ok |  |
| h19.8 | S4 | 19.8 | 108.0 | 59.3 | +48.7 | 21.8 @135 | 71.2 | 0.05 | -15.7 | 51.7 | ok | ok | ok |  |
| h19 | S4 | 19.0 | 116.1 | 105.8 | +10.3 | 3.0 @272 | 12.7 | 0.00 | -91.6 | 82.3 | ok | ok | ok |  |
| h20.5 | S4 | 20.5 | 77.9 | 45.9 | +32.0 | 6.5 @134 | 24.9 | 0.00 | +6.6 | 46.1 | ok | ok | ok |  |
| h20 | S4 | 20.0 | 56.5 | 39.6 | +16.8 | 13.9 @136 | 67.5 | 0.00 | -10.8 | 34.8 | ok | ok | ok |  |
| h21.5 | S4 | 21.5 | 50.2 | 32.8 | +17.5 | 12.8 @176 | 33.1 | 0.00 | +11.2 | 42.2 | ok | ok | ok |  |
| h21 | S4 | 21.0 | 50.1 | 63.5 | -13.4 | 14.9 @133 | 71.3 | 0.00 | -4.7 | 42.7 | FAIL | ok | ok |  |
| h22 | S4 | 22.0 | 48.2 | 29.5 | +18.7 | 12.7 @176 | 31.5 | 0.00 | +15.1 | 42.6 | ok | ok | ok |  |
| h6.5 | S4 | 6.5 | 119.5 | 74.6 | +44.9 | 10.3 @103 | 31.4 | 0.00 | -39.6 | 48.5 | ok | ok | ok |  |
| h7.5 | S4 | 7.5 | 120.3 | 77.5 | +42.9 | 11.4 @102 | 30.1 | 0.00 | -12.8 | 69.8 | ok | ok | ok |  |
| h7 | S4 | 7.0 | 146.2 | 83.9 | +62.3 | 18.5 @108 | 48.7 | 0.00 | -65.1 | 69.0 | ok | ok | ok |  |
| mist_h7.6 | S4 | 7.6 | 122.7 | 81.3 | +41.4 | 10.7 @103 | 29.7 | 0.00 | +3.0 | 71.3 | ok | ok | ok |  |
| w1_h13 | S4 | 13.0 | 124.6 | 117.8 | +6.8 | 8.5 @128 | 24.5 | 0.00 | -11.4 | 84.1 | FAIL | ok | ok |  |
| h6.5 | S4e | 6.5 | 110.4 | 92.4 | +18.0 | 25.1 @100 | 83.9 | 0.00 | -35.0 | 40.6 | ok | FAIL | ok | ok |
| h7.5 | S4e | 7.5 | 146.3 | 105.5 | +40.8 | 15.9 @109 | 25.1 | 0.00 | -78.1 | 71.7 | ok | ok | ok | ok |
| h7 | S4e | 7.0 | 131.5 | 92.9 | +38.6 | 18.7 @109 | 39.1 | 0.04 | -81.7 | 65.7 | ok | ok | ok | ok |
| mist_h7.6 | S4e | 7.6 | 144.5 | 102.6 | +41.8 | 15.8 @108 | 26.8 | 0.00 | -74.2 | 71.1 | ok | ok | ok | ok |
| h19.5 | S4w | 19.5 | 110.3 | 87.3 | +23.0 | 10.7 @122 | 39.3 | 0.05 | -58.6 | 57.3 | ok | ok | ok | ok |
| h19.8 | S4w | 19.8 | 128.5 | 84.9 | +43.6 | 18.2 @122 | 78.5 | 0.00 | -32.9 | 41.2 | ok | ok | ok | ok |
| h19 | S4w | 19.0 | 127.8 | 114.0 | +13.9 | 9.5 @106 | 17.3 | 0.00 | -96.4 | 70.8 | ok | ok | ok | FAIL |
| h20.5 | S4w | 20.5 | 84.6 | 50.0 | +34.6 | 17.6 @189 | 49.9 | 0.00 | -13.2 | 43.3 | ok | ok | ok | FAIL |
| h20 | S4w | 20.0 | 135.7 | 82.0 | +53.7 | 23.6 @140 | 62.4 | 0.07 | -36.5 | 42.4 | ok | ok | ok | ok |

| variant prefix | S4 mean 20:30 | S4 mean 22:00 | L27e (no pit) |
|---|---|---|---|
| (none) | 46.13 | 42.63 | ok |

## Round-03 midday floor (L2 / L7) on the fixed midday preset map Look_Midtown (look_spec_check.py; the round-03 critic counted mean + B-R: 8 of 8)

| still | spec | mean Y | Y<10 % | clipped % | B-R | lit blobs (bottom half) | bottom-third p90 / p10 | within (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | L2 | 94.2 | 0.00 | 0.00 | -3.8 | 5 | 155 / 94 | yes / yes / yes / yes |
| midday_S2_1920x1080.jpg | L2 | 88.5 | 0.00 | 0.00 | -11.0 | 8 | 124 / 34 | yes / yes / yes / yes |
| midday_S3_1920x1080.jpg | L2 | 90.0 | 0.00 | 0.01 | -5.0 | 9 | 151 / 31 | yes / yes / NO / yes |
| midday_S4_1920x1080.jpg | L2 | 85.9 | 0.00 | 0.00 | +3.5 | 7 | 78 / 30 | yes / yes / yes / yes |
| midday_S5_1920x1080.jpg | L2 | 95.4 | 0.00 | 0.00 | -4.3 | 8 | 166 / 21 | yes / yes / yes / yes |
| midday_S6_1920x1080.jpg | L2 | 93.8 | 0.00 | 0.00 | -5.5 | 11 | 161 / 52 | yes / yes / yes / yes |
| midday_S7_1920x1080.jpg | L2 | 75.4 | 0.00 | 0.05 | -0.2 | 6 | 113 / 20 | NO / yes / NO / yes |
| midday_S8_1920x1080.jpg | L2 | 91.5 | 0.00 | 0.00 | +3.5 | 7 | 96 / 27 | yes / yes / yes / yes |

## L24 / L25 / L26 sky stills

```
| still | pose | hour | sky band Y | sky B-R | far Y | sky-far | L24a | L24b | mean Y | moon px | moon peak Y | hp std (excl / incl moon) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | S1 | 18.4 | 66.8 | -27.4 |  |  |  |  |  |  |  |  |
| h22 | S1 | 22.0 | 47.4 | +2.0 |  |  |  |  |  |  |  |  |
| mist_h7.6 | S1 | 7.6 | 88.7 | -55.9 |  |  |  |  |  |  |  |  |
| w1_h13 | S1 | 13.0 | 82.8 | -14.1 |  |  |  |  |  |  |  |  |
| h18.4 | S2 | 18.4 | 126.3 | -74.1 |  |  |  |  |  |  |  |  |
| h22 | S2 | 22.0 | 50.4 | -11.0 |  |  |  |  |  |  |  |  |
| w1_h13 | S2 | 13.0 | 106.3 | -23.1 |  |  |  |  |  |  |  |  |
| h18.4 | S3 | 18.4 | 68.4 | -22.7 |  |  |  |  |  |  |  |  |
| h22 | S3 | 22.0 | 44.4 | -7.8 |  |  |  |  |  |  |  |  |
| w1_h13 | S3 | 13.0 | 113.9 | -14.1 |  |  |  |  |  |  |  |  |
| h13 | S4 | 13.0 | 122.0 | +31.2 | 118.4 | +3.5 | ok |  | 80.3 |  |  | 1.94 |
| h18.4 | S4 | 18.4 | 158.5 | -69.2 | 143.4 | +15.1 | ok |  | 97.3 |  |  | 3.13 |
| h19.5 | S4 | 19.5 | 105.7 | -57.4 | 90.1 | +15.6 | ok |  | 60.8 |  |  | 4.73 |
| h19.8 | S4 | 19.8 | 108.0 | -15.7 | 59.3 | +48.7 | ok |  | 51.7 |  |  | 13.44 |
| h19 | S4 | 19.0 | 116.1 | -91.6 | 105.8 | +10.3 | ok |  | 82.3 |  |  | 2.82 |
| h20.5 | S4 | 20.5 | 77.9 | +6.6 | 45.9 | +32.0 | ok |  | 46.1 |  |  | 9.85 |
| h20 | S4 | 20.0 | 56.5 | -10.8 | 39.7 | +16.8 | ok |  | 34.8 |  |  | 10.72 |
| h21.5 | S4 | 21.5 | 50.2 | +11.2 | 32.8 | +17.5 | ok |  | 42.2 |  |  | 3.58 |
| h21 | S4 | 21.0 | 50.1 | -4.7 | 63.5 | -13.4 | FAIL |  | 42.7 |  |  | 9.14 |
| h22 | S4 | 22.0 | 48.2 | +15.1 | 29.5 | +18.7 | ok |  | 42.6 |  |  | 3.55 |
| h6.5 | S4 | 6.5 | 119.5 | -39.6 | 74.6 | +44.9 | ok |  | 48.5 |  |  | 8.71 |
| h7.5 | S4 | 7.5 | 120.3 | -12.8 | 77.5 | +42.9 | ok |  | 69.8 |  |  | 2.39 |
| h7 | S4 | 7.0 | 146.2 | -65.1 | 83.9 | +62.3 | ok |  | 69.0 |  |  | 5.12 |
| mist_h7.6 | S4 | 7.6 | 122.7 | +3.0 | 81.3 | +41.4 | ok |  | 71.3 |  |  | 2.32 |
| w1_h13 | S4 | 13.0 | 124.6 | -11.4 | 117.8 | +6.8 | ok |  | 84.1 |  |  | 3.77 |
| h6.5 | S4e | 6.5 | 110.4 | -35.0 |  |  |  | ok | 40.6 |  |  |  |
| h7.5 | S4e | 7.5 | 146.3 | -78.1 |  |  |  | ok | 71.7 |  |  |  |
| h7 | S4e | 7.0 | 131.5 | -81.6 |  |  |  | ok | 65.7 |  |  |  |
| mist_h7.6 | S4e | 7.6 | 144.5 | -74.2 |  |  |  |  | 71.1 |  |  |  |
| h22 | S4m | 22.0 | 61.1 | +2.8 |  |  |  |  | 43.0 | 22.5 | 255 | 2.53 / 2.67 |
| h19.5 | S4w | 19.5 | 110.3 | -58.6 |  |  |  | ok | 57.3 |  |  |  |
| h19.8 | S4w | 19.8 | 128.5 | -32.9 |  |  |  | ok | 41.2 |  |  |  |
| h19 | S4w | 19.0 | 127.8 | -96.4 |  |  |  | ok | 70.8 |  |  |  |
| h20.5 | S4w | 20.5 | 84.6 | -13.2 |  |  |  | FAIL | 43.3 |  |  |  |
| h20 | S4w | 20.0 | 135.7 | -36.5 |  |  |  | ok | 42.4 |  |  |  |
| h18.4 | S5 | 18.4 | 129.9 | -58.1 |  |  |  |  |  |  |  |  |
| h22 | S5 | 22.0 | 31.1 | +5.5 |  |  |  |  |  |  |  |  |
| w1_h13 | S5 | 13.0 | 145.9 | -11.3 |  |  |  |  |  |  |  |  |
| h18.4 | S6 | 18.4 | 90.6 | -45.7 |  |  |  |  |  |  |  |  |
| h22 | S6 | 22.0 | 30.6 | +9.7 |  |  |  |  |  |  |  |  |
| w1_h13 | S6 | 13.0 | 103.3 | -12.5 |  |  |  |  |  |  |  |  |
| h18.4 | S7 | 18.4 | 76.4 | -46.8 |  |  |  |  | 61.9 |  |  |  |
| h22 | S7 | 22.0 | 33.5 | +7.3 |  |  |  |  | 44.1 |  |  |  |
| w1_h13 | S7 | 13.0 | 82.7 | -9.6 |  |  |  |  | 66.4 |  |  |  |
| h13 | S8 | 13.0 | 126.5 | +20.6 |  |  |  |  |  |  |  |  |
| h18.4 | S8 | 18.4 | 147.0 | -61.3 |  |  |  |  |  |  |  |  |
| h22 | S8 | 22.0 | 51.2 | +12.8 |  |  |  |  |  |  |  |  |
| w1_h13 | S8 | 13.0 | 130.1 | -4.2 |  |  |  |  |  |  |  |  |

L26 S1 correlation vs golden (tod_S1_1920x1080_h18.4.jpg): mist_h7.6 0.436
```

## Golden 18.4 and night 22 spec numbers (tod_tests.py)

```
| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 46..97 | 4/8 | 1.80 | -57..-23 | 5.6..26.0 | 6.4..36.1 | 0.44..0.57 | -21.9 | +15.9 | +25.2 |  |  |  |  |
| h22 | night | 8 | 38..58 | 8/8 | 0.77 | -6..+10 |  |  |  | -21.4 | -1.9 | +7.3 | 2.83 | 34.7 | 42.6 | 10/13/3 |
| w1_h13 | midday | 8 | 66..95 | 5/8 | 0.01 | -21..-8 |  |  |  | -6.2 | -0.0 | +16.1 |  |  |  |  |
| h13 | midday | 2 | 80..82 | 0/2 | 0.00 | -0..+8 |  |  |  | -9.6 | -12.7 | +46.8 |  |  |  |  |
```

Per-still tables: `TESTS_tod.md`.

## Hero box (swing_tod_19_hero_luma.json)

| frames_measured | bbox_mean_luma_min | bbox_mean_luma_p5 | bbox_mean_luma_mean | bbox_mean_luma_max | frames_below_threshold | L15b_frames_with_clipped_px | L15b_max_clipped_px_in_box |
|---|---|---|---|---|---|---|---|
| 718 | 64.2 | 74.3 | 96.5 | 132.8 | 0 | 84 | 86 |

## Hero box (swing_tod_22_hero_luma.json)

| frames_measured | bbox_mean_luma_min | bbox_mean_luma_p5 | bbox_mean_luma_mean | bbox_mean_luma_max | frames_below_threshold | L15b_frames_with_clipped_px | L15b_max_clipped_px_in_box |
|---|---|---|---|---|---|---|---|
| 718 | 18.6 | 34.7 | 55.7 | 121.9 | 108 | 676 | 2191 |

## swing_tod_19.mp4

mean Y 72.5 (min 57.9 max 88.2), B-R mean -59.8, clipped mean 0.04 %, L18 edge/centre p50 0.72

## swing_tod_22.mp4

mean Y 35.3 (min 21.4 max 52.1), B-R mean +3.8, clipped mean 0.54 %, L18 edge/centre p50 0.57

