# Round 06: sky / time-of-day numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

All numbers from the real game (`Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`); stills and clips 1920x1080 internal 100 % of output; the lapse at the resolution and sub-stepping written in its json (fixed 1/60 s step). Instruments: `tools/perf_ue/{capture_tod_lapse,twilight_check,tod_tests,night_tests,clip_check}.py`.

## L23b time-lapse (S4 perch, 04:00 start, nominal 2 h/s, 726 frames, 960x540 output, internal 100% of output, sub-steps 4)

Instrument condition: metering pinned per frame: pp.AutoExposureSpeedUp / Down = 40 (capture-only live pins; the game keeps 6 / 3) + sub-stepped render: 4 frames per output frame (clock 0.5 h/s, fixed 1/60 s step, every 4-th frame kept) so the temporal lighting caches (Lumen GI, sky light capture, volumetric fog history, ~35 frames) settle between output frames; no render setting is changed.

Live commands: `exec wh.ToDSet pp.AutoExposureSpeedUp 40;exec wh.ToDSet pp.AutoExposureSpeedDown 40`.

| max jump | p99 | median | frames > 3 | frames > 1.5 | 05:00-21:30 max mean | at h | max clipped % | at h | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5.75 | 3.48 | 0.06 | 11 | 43 | 105.4 | 18.32 | 1.94 | 6.66 | FAIL |

Biggest jumps: 6.53 h +5.8 (51 -> 57), 6.42 h +5.6 (35 -> 40), 6.39 h +5.5 (29 -> 35), 6.46 h +5.5 (40 -> 46), 6.49 h +5.0 (46 -> 51), 6.56 h +4.5 (57 -> 61)

## L24 / L25 / L26 sky stills

```
| still | pose | hour | sky band Y | sky B-R | far Y | sky-far | L24a | L24b | mean Y | moon px | moon peak Y | hp std (excl / incl moon) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | S1 | 18.4 | 71.5 | -32.5 |  |  |  |  |  |  |  |  |
| h22 | S1 | 22.0 | 37.5 | +2.9 |  |  |  |  |  |  |  |  |
| mist_h7.6 | S1 | 7.6 | 157.9 | -79.1 |  |  |  |  |  |  |  |  |
| h18.4 | S2 | 18.4 | 131.4 | -79.7 |  |  |  |  |  |  |  |  |
| h22 | S2 | 22.0 | 48.4 | -11.3 |  |  |  |  |  |  |  |  |
| h18.4 | S3 | 18.4 | 82.3 | -28.5 |  |  |  |  |  |  |  |  |
| h22 | S3 | 22.0 | 46.9 | -8.8 |  |  |  |  |  |  |  |  |
| h13 | S4 | 13.0 | 152.0 | +18.1 | 115.7 | +36.3 | ok |  | 84.3 |  |  | 2.86 |
| h18.4 | S4 | 18.4 | 185.6 | -85.8 | 142.0 | +43.7 | ok |  | 100.7 |  |  | 4.54 |
| h19.5 | S4 | 19.5 | 119.4 | -73.9 | 77.6 | +41.9 | ok |  | 55.2 |  |  | 7.69 |
| h19.8 | S4 | 19.8 | 18.5 | -19.1 | 13.5 | +5.0 | ok |  | 15.0 |  |  | 9.49 |
| h19 | S4 | 19.0 | 130.2 | -217.0 | 107.5 | +22.7 | ok |  | 70.4 |  |  | 5.49 |
| h20.5 | S4 | 20.5 | 22.2 | +4.9 | 19.1 | +3.1 | ok |  | 22.0 |  |  | 2.21 |
| h20 | S4 | 20.0 | 10.5 | +7.1 | 14.4 | -3.9 | FAIL |  | 14.9 |  |  | 1.30 |
| h21.5 | S4 | 21.5 | 51.5 | +10.8 | 32.2 | +19.3 | ok |  | 43.3 |  |  | 3.46 |
| h21 | S4 | 21.0 | 51.1 | -0.7 | 37.8 | +13.3 | ok |  | 41.7 |  |  | 5.62 |
| h22 | S4 | 22.0 | 48.8 | +11.2 | 32.5 | +16.3 | ok |  | 43.6 |  |  | 3.11 |
| h6.5 | S4 | 6.5 | 140.8 | -68.8 | 106.9 | +33.9 | ok |  | 62.1 |  |  | 4.70 |
| h7.5 | S4 | 7.5 | 174.5 | -19.9 | 109.6 | +64.9 | ok |  | 89.2 |  |  | 2.98 |
| h7 | S4 | 7.0 | 174.6 | -111.2 | 113.2 | +61.4 | ok |  | 72.0 |  |  | 3.47 |
| mist_h7.6 | S4 | 7.6 | 179.1 | -8.8 | 106.3 | +72.9 | ok |  | 92.1 |  |  | 2.78 |
| h6.5 | S4e | 6.5 | 74.0 | -57.6 |  |  |  | ok | 43.8 |  |  |  |
| h7.5 | S4e | 7.5 | 195.8 | -67.5 |  |  |  | ok | 66.0 |  |  |  |
| h7 | S4e | 7.0 | 143.9 | -206.1 |  |  |  | ok | 37.9 |  |  |  |
| mist_h7.6 | S4e | 7.6 | 200.1 | -50.4 |  |  |  |  | 70.4 |  |  |  |
| h22 | S4m | 22.0 | 74.7 | -0.7 |  |  |  |  | 43.3 | 21.2 | 255 | 2.11 / 2.27 |
| h19.5 | S4w | 19.5 | 36.7 | -34.5 |  |  |  | ok | 44.9 |  |  |  |
| h19.8 | S4w | 19.8 | 48.0 | -58.5 |  |  |  | ok | 41.2 |  |  |  |
| h19 | S4w | 19.0 | 155.4 | -245.7 |  |  |  | ok | 55.2 |  |  |  |
| h20.5 | S4w | 20.5 | 23.2 | +4.1 |  |  |  | FAIL | 31.7 |  |  |  |
| h20 | S4w | 20.0 | 22.5 | -30.7 |  |  |  | ok | 39.6 |  |  |  |
| h18.4 | S5 | 18.4 | 132.2 | -61.5 |  |  |  |  |  |  |  |  |
| h22 | S5 | 22.0 | 31.7 | +4.1 |  |  |  |  |  |  |  |  |
| h18.4 | S6 | 18.4 | 96.3 | -49.8 |  |  |  |  |  |  |  |  |
| h22 | S6 | 22.0 | 34.0 | +7.8 |  |  |  |  |  |  |  |  |
| h18.4 | S7 | 18.4 | 83.3 | -51.7 |  |  |  |  | 68.6 |  |  |  |
| h22 | S7 | 22.0 | 32.7 | +7.1 |  |  |  |  | 43.7 |  |  |  |
| h13 | S8 | 13.0 | 135.9 | +18.5 |  |  |  |  |  |  |  |  |
| h18.4 | S8 | 18.4 | 154.7 | -66.0 |  |  |  |  |  |  |  |  |
| h22 | S8 | 22.0 | 56.3 | +11.9 |  |  |  |  |  |  |  |  |

L26 S1 correlation vs golden (tod_S1_1920x1080_h18.4.jpg): mist_h7.6 0.602
```

## Golden 18.4 and night 22 spec numbers (tod_tests.py)

```
| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 60..101 | 3/8 | 2.14 | -62..-29 | 5.8..24.5 | 7.9..36.3 | 0.45..0.57 | -47.7 | +25.9 | +22.5 |  |  |  |  |
| h22 | night | 8 | 39..52 | 8/8 | 0.85 | -6..+10 |  |  |  | -18.8 | -6.4 | +2.2 | 2.47 | 36.4 | 43.6 | 9/13/3 |
| h13 | midday | 2 | 84..86 | 2/2 | 0.00 | -5..+3 |  |  |  | -40.3 | -2.1 | +44.8 |  |  |  |  |
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

