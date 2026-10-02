# Round 06: sky / time-of-day numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

All numbers from the real game (`Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`); stills and clips 1920x1080 internal 100 % of output; the lapse at the resolution and sub-stepping written in its json (fixed 1/60 s step). Instruments: `tools/perf_ue/{capture_tod_lapse,twilight_check,tod_tests,night_tests,clip_check}.py`.

## L23b time-lapse (S4 perch, 04:00 start, nominal 2 h/s, 720 frames, 960x540 output, internal 100% of output, sub-steps 1)

Instrument condition: metering pinned per frame: pp.AutoExposureSpeedUp / Down = 40 (capture-only live pins; the game keeps 6 / 3) + segmented sub-stepped render: 4-5.5 h x4; 5.5-8.2 h x16; 8.2-18.4 h x4; 18.4-21.4 h x16; 21.4-28 h x4 (each segment starts 0.3 h early and drops those frames: warm-up of the lighting caches); x16 = clock 0.125 h/s, x4 = 0.5 h/s, fixed 1/60 s step, every N-th frame kept; no render setting is changed.

Live commands: `exec wh.ToDSet pp.AutoExposureSpeedUp 40;exec wh.ToDSet pp.AutoExposureSpeedDown 40`.

| max jump | p99 | median | frames > 3 | frames > 1.5 | 05:00-21:30 max mean | at h | max clipped % | at h | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 8.10 | 3.21 | 0.05 | 10 | 62 | 114.3 | 8.43 | 2.42 | 19.04 | FAIL |

Biggest jumps: 19.71 h +8.1 (53 -> 45), 19.67 h +7.9 (61 -> 53), 6.61 h +4.8 (44 -> 49), 6.57 h +4.7 (39 -> 44), 19.61 h +3.7 (58 -> 62), 19.57 h +3.6 (55 -> 58)

## L24 / L25 / L26 sky stills

```
| still | pose | hour | sky band Y | sky B-R | far Y | sky-far | L24a | L24b | mean Y | moon px | moon peak Y | hp std (excl / incl moon) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | S1 | 18.4 | 69.9 | -31.8 |  |  |  |  |  |  |  |  |
| h22 | S1 | 22.0 | 37.9 | +2.7 |  |  |  |  |  |  |  |  |
| mist_h7.6 | S1 | 7.6 | 132.3 | -71.8 |  |  |  |  |  |  |  |  |
| h18.4 | S2 | 18.4 | 129.4 | -79.7 |  |  |  |  |  |  |  |  |
| h22 | S2 | 22.0 | 49.9 | -11.8 |  |  |  |  |  |  |  |  |
| h18.4 | S3 | 18.4 | 81.3 | -28.4 |  |  |  |  |  |  |  |  |
| h22 | S3 | 22.0 | 45.8 | -8.8 |  |  |  |  |  |  |  |  |
| h13 | S4 | 13.0 | 155.4 | +17.3 | 117.3 | +38.1 | ok |  | 84.7 |  |  | 2.91 |
| h18.4 | S4 | 18.4 | 183.6 | -87.1 | 139.0 | +44.5 | ok |  | 98.6 |  |  | 4.57 |
| h19.5 | S4 | 19.5 | 107.4 | -71.9 | 68.8 | +38.5 | ok |  | 49.7 |  |  | 8.01 |
| h19.8 | S4 | 19.8 | 34.9 | -40.8 | 38.6 | -3.7 | FAIL |  | 35.0 |  |  | 14.88 |
| h19 | S4 | 19.0 | 135.0 | -218.9 | 112.4 | +22.6 | ok |  | 73.7 |  |  | 5.51 |
| h20.5 | S4 | 20.5 | 23.7 | +2.9 | 19.6 | +4.1 | ok |  | 22.8 |  |  | 2.29 |
| h20 | S4 | 20.0 | 13.8 | -2.6 | 38.1 | -24.3 | FAIL |  | 31.9 |  |  | 7.24 |
| h21.5 | S4 | 21.5 | 51.7 | +11.1 | 32.2 | +19.5 | ok |  | 43.5 |  |  | 3.46 |
| h21 | S4 | 21.0 | 47.7 | +1.8 | 35.9 | +11.8 | ok |  | 39.8 |  |  | 5.36 |
| h22 | S4 | 22.0 | 42.4 | +11.0 | 27.0 | +15.5 | ok |  | 41.1 |  |  | 2.67 |
| h6.5 | S4 | 6.5 | 89.3 | -64.8 | 67.6 | +21.7 | ok |  | 39.5 |  |  | 5.83 |
| h7.5 | S4 | 7.5 | 164.2 | -28.2 | 93.3 | +70.9 | ok |  | 80.6 |  |  | 3.13 |
| h7 | S4 | 7.0 | 155.3 | -156.8 | 89.7 | +65.7 | ok |  | 63.6 |  |  | 3.11 |
| mist_h7.6 | S4 | 7.6 | 168.5 | -9.6 | 93.4 | +75.1 | ok |  | 82.4 |  |  | 2.97 |
| rt_h22 | S4 | 22.0 | 45.3 | +14.8 | 31.4 | +14.0 | ok |  | 43.8 |  |  | 2.81 |
| h6.5 | S4e | 6.5 | 69.3 | -55.6 |  |  |  | ok | 43.0 |  |  |  |
| h7.5 | S4e | 7.5 | 192.6 | -76.9 |  |  |  | ok | 63.1 |  |  |  |
| h7 | S4e | 7.0 | 145.3 | -215.6 |  |  |  | ok | 39.0 |  |  |  |
| mist_h7.6 | S4e | 7.6 | 194.4 | -56.0 |  |  |  |  | 65.0 |  |  |  |
| h22 | S4m | 22.0 | 74.6 | -0.7 |  |  |  |  | 43.6 | 20.5 | 255 | 2.17 / 2.31 |
| rt_h22 | S4m | 22.0 | 88.8 | +33.2 |  |  |  |  | 104.8 | 44.6 | 255 | 1.62 / 1.69 |
| h19.5 | S4w | 19.5 | 32.3 | -30.3 |  |  |  | ok | 41.4 |  |  |  |
| h19.8 | S4w | 19.8 | 76.4 | -71.8 |  |  |  | ok | 72.8 |  |  |  |
| h19 | S4w | 19.0 | 158.4 | -246.7 |  |  |  | ok | 57.1 |  |  |  |
| h20.5 | S4w | 20.5 | 23.9 | +4.4 |  |  |  | FAIL | 32.7 |  |  |  |
| h20 | S4w | 20.0 | 36.5 | -49.2 |  |  |  | ok | 67.8 |  |  |  |
| h18.4 | S5 | 18.4 | 130.5 | -61.3 |  |  |  |  |  |  |  |  |
| h22 | S5 | 22.0 | 33.3 | +2.5 |  |  |  |  |  |  |  |  |
| h18.4 | S6 | 18.4 | 94.8 | -49.4 |  |  |  |  |  |  |  |  |
| h22 | S6 | 22.0 | 31.1 | +10.1 |  |  |  |  |  |  |  |  |
| h18.4 | S7 | 18.4 | 81.8 | -51.1 |  |  |  |  | 67.2 |  |  |  |
| h22 | S7 | 22.0 | 32.7 | +7.0 |  |  |  |  | 43.7 |  |  |  |
| h13 | S8 | 13.0 | 136.8 | +18.3 |  |  |  |  |  |  |  |  |
| h18.4 | S8 | 18.4 | 152.7 | -66.2 |  |  |  |  |  |  |  |  |
| h22 | S8 | 22.0 | 56.7 | +11.8 |  |  |  |  |  |  |  |  |

L26 S1 correlation vs golden (tod_S1_1920x1080_h18.4.jpg): mist_h7.6 0.597
```

## Golden 18.4 and night 22 spec numbers (tod_tests.py)

```
| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 59..99 | 3/8 | 2.05 | -62..-29 | 5.5..23.8 | 8.1..38.1 | 0.45..0.57 | -48.8 | +27.3 | +22.6 |  |  |  |  |
| h22 | night | 8 | 39..52 | 8/8 | 0.89 | -6..+10 |  |  |  | -17.5 | -5.2 | +3.6 | 1.99 | 33.1 | 41.1 | 9/12/4 |
| h13 | midday | 2 | 85..86 | 2/2 | 0.00 | -5..+4 |  |  |  | -42.4 | -0.3 | +46.3 |  |  |  |  |
```

Per-still tables: `TESTS_tod.md`.

## Hero box (swing_tod_18h4_hero_luma.json)

| frames_measured | bbox_mean_luma_min | bbox_mean_luma_p5 | bbox_mean_luma_mean | bbox_mean_luma_max | frames_below_threshold | L15b_frames_with_clipped_px | L15b_max_clipped_px_in_box |
|---|---|---|---|---|---|---|---|
| 718 | 22.7 | 54.3 | 108.4 | 166.8 | 16 | 695 | 15871 |

## Hero box (swing_tod_22_hero_luma.json)

| frames_measured | bbox_mean_luma_min | bbox_mean_luma_p5 | bbox_mean_luma_mean | bbox_mean_luma_max | frames_below_threshold | L15b_frames_with_clipped_px | L15b_max_clipped_px_in_box |
|---|---|---|---|---|---|---|---|
| 718 | 20.7 | 36.5 | 58.2 | 124.8 | 91 | 676 | 2104 |

## swing_tod_18h4.mp4

mean Y 73.0 (min 28.6 max 94.2), B-R mean -44.3, clipped mean 0.46 %, L18 edge/centre p50 0.76

## swing_tod_22.mp4

mean Y 35.9 (min 22.0 max 55.4), B-R mean +3.5, clipped mean 0.52 %, L18 edge/centre p50 0.57

