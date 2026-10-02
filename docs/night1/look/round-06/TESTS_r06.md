# Round 06: sky / time-of-day numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

All numbers from the real game (`Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`); stills 1920x1080 internal 100 % of output; the lapse 1920x1080 at a fixed 1/60 s step. Instruments: `tools/perf_ue/{capture_tod_lapse,twilight_check,tod_tests,night_tests,clip_check}.py`.

## L23b time-lapse (S4 perch, 04:00 start, 2 h/s, 724 frames)

Instrument condition: metering pinned per frame: pp.AutoExposureSpeedUp / Down = 40 (capture-only live pins; the game keeps 6 / 3) + render settings while the clock runs > 0.3 h/s (wh.ToDLapseCvars, the sky light capture and the volumetric fog history have a ~35 frame latency = 0.6 game hour at 2 h/s): r.SkyLight.RealTimeReflectionCapture.TimeSlice=0,r.VolumetricFog=0.

Render settings while the clock runs fast (wh.ToDLapseCvars): see `live_cmds` / HANDOFF.

| max jump | p99 | median | frames > 3 | frames > 1.5 | 05:00-21:30 max mean | at h | max clipped % | at h | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 12.81 | 4.13 | 0.06 | 17 | 50 | 107.9 | 8.00 | 5.36 | 6.87 | FAIL |

Biggest jumps: 18.97 h +12.8 (78 -> 65), 6.47 h +7.9 (33 -> 41), 6.43 h +6.2 (27 -> 33), 6.97 h +5.4 (46 -> 51), 6.40 h +5.2 (22 -> 27), 6.50 h +4.5 (41 -> 45)

## L24 / L25 / L26 sky stills

```
| still | pose | hour | sky band Y | sky B-R | far Y | sky-far | L24a | L24b | mean Y | moon px | moon peak Y | hp std (excl / incl moon) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | S1 | 18.4 | 68.4 | -31.1 |  |  |  |  |  |  |  |  |
| h22 | S1 | 22.0 | 37.7 | +2.5 |  |  |  |  |  |  |  |  |
| mist_h7.4 | S1 | 7.4 | 96.0 | -75.6 |  |  |  |  |  |  |  |  |
| mist_h7.6 | S1 | 7.6 | 144.3 | -67.7 |  |  |  |  |  |  |  |  |
| mist_h7 | S1 | 7.0 | 53.2 | -62.2 |  |  |  |  |  |  |  |  |
| mist_h8 | S1 | 8.0 | 140.6 | -34.5 |  |  |  |  |  |  |  |  |
| h18.4 | S2 | 18.4 | 128.5 | -78.6 |  |  |  |  |  |  |  |  |
| h22 | S2 | 22.0 | 49.8 | -12.0 |  |  |  |  |  |  |  |  |
| h18.4 | S3 | 18.4 | 80.3 | -27.7 |  |  |  |  |  |  |  |  |
| h22 | S3 | 22.0 | 45.8 | -9.7 |  |  |  |  |  |  |  |  |
| h13 | S4 | 13.0 | 153.8 | +18.7 | 117.7 | +36.1 | ok |  | 84.6 |  |  | 2.85 |
| h18.4 | S4 | 18.4 | 185.4 | -86.5 | 141.3 | +44.1 | ok |  | 99.7 |  |  | 4.58 |
| h19.5 | S4 | 19.5 | 113.6 | -130.7 | 38.7 | +74.9 | ok |  | 35.7 |  |  | 16.29 |
| h19.8 | S4 | 19.8 | 29.7 | -47.9 | 17.2 | +12.5 | ok |  | 19.8 |  |  | 11.97 |
| h19 | S4 | 19.0 | 111.1 | -209.9 | 85.1 | +26.0 | ok |  | 53.1 |  |  | 7.30 |
| h20.5 | S4 | 20.5 | 22.5 | +3.9 | 19.4 | +3.1 | ok |  | 21.8 |  |  | 2.20 |
| h20 | S4 | 20.0 | 10.7 | +6.2 | 18.0 | -7.3 | FAIL |  | 17.1 |  |  | 1.37 |
| h21.5 | S4 | 21.5 | 51.9 | +11.3 | 32.6 | +19.3 | ok |  | 43.8 |  |  | 3.42 |
| h21 | S4 | 21.0 | 50.6 | +0.0 | 37.8 | +12.8 | ok |  | 41.8 |  |  | 5.64 |
| h22 | S4 | 22.0 | 41.5 | +10.3 | 30.1 | +11.4 | ok |  | 39.6 |  |  | 2.48 |
| h6.5 | S4 | 6.5 | 120.1 | -129.1 | 49.9 | +70.2 | ok |  | 35.1 |  |  | 14.26 |
| h7.5 | S4 | 7.5 | 177.6 | -28.1 | 114.0 | +63.6 | ok |  | 90.1 |  |  | 3.69 |
| h7 | S4 | 7.0 | 153.6 | -176.2 | 74.8 | +78.8 | ok |  | 51.4 |  |  | 8.39 |
| mist_h7.4 | S4 | 7.4 | 173.9 | -61.0 | 116.9 | +57.0 | ok |  | 85.4 |  |  | 4.54 |
| mist_h7.6 | S4 | 7.6 | 179.3 | -7.2 | 107.7 | +71.6 | ok |  | 90.9 |  |  | 2.76 |
| mist_h7 | S4 | 7.0 | 155.3 | -158.1 | 88.1 | +67.2 | ok |  | 57.5 |  |  | 7.04 |
| mist_h8 | S4 | 8.0 | 174.8 | +5.8 | 134.1 | +40.7 | ok |  | 106.2 |  |  | 2.57 |
| h6.5 | S4e | 6.5 | 93.7 | -124.3 |  |  |  | ok | 31.1 |  |  |  |
| h7.5 | S4e | 7.5 | 198.5 | -68.7 |  |  |  | ok | 67.7 |  |  |  |
| h7 | S4e | 7.0 | 157.8 | -212.5 |  |  |  | ok | 40.7 |  |  |  |
| mist_h7.4 | S4e | 7.4 | 196.8 | -94.4 |  |  |  | ok | 65.3 |  |  |  |
| mist_h7.6 | S4e | 7.6 | 199.0 | -49.4 |  |  |  |  | 69.1 |  |  |  |
| mist_h7 | S4e | 7.0 | 153.1 | -206.8 |  |  |  | ok | 39.7 |  |  |  |
| mist_h8 | S4e | 8.0 | 196.4 | -39.3 |  |  |  |  | 73.8 |  |  |  |
| Mv1_h22 | S4m | 22.0 | 62.4 | -10.8 |  |  |  |  | 42.7 | 5.2 | 255 | 2.80 / 2.85 |
| Mv2_h22 | S4m | 22.0 | 76.4 | -1.4 |  |  |  |  | 42.6 | 3.4 | 255 | 3.26 / 3.24 |
| Mv3_h22 | S4m | 22.0 | 73.0 | -0.2 |  |  |  |  | 42.1 | 1.6 | 255 | 3.33 / 3.29 |
| Mv4_h22 | S4m | 22.0 | 75.1 | -0.6 |  |  |  |  | 41.8 | 1.1 | 255 | 3.42 / 3.46 |
| h22 | S4m | 22.0 | 74.6 | -0.6 |  |  |  |  | 43.0 | 2.0 | 255 | 2.06 / 2.20 |
| h19.5 | S4w | 19.5 | 78.9 | -121.9 |  |  |  | ok | 34.1 |  |  |  |
| h19.8 | S4w | 19.8 | 55.9 | -93.4 |  |  |  | ok | 38.4 |  |  |  |
| h19 | S4w | 19.0 | 162.4 | -246.5 |  |  |  | ok | 56.6 |  |  |  |
| h20.5 | S4w | 20.5 | 23.1 | +4.4 |  |  |  | FAIL | 30.2 |  |  |  |
| h20 | S4w | 20.0 | 16.7 | -20.0 |  |  |  | ok | 38.1 |  |  |  |
| h21.5 | S4w | 21.5 | 44.3 | +11.6 |  |  |  |  | 43.3 |  |  |  |
| h21 | S4w | 21.0 | 43.2 | +4.5 |  |  |  |  | 42.8 |  |  |  |
| h18.4 | S5 | 18.4 | 131.2 | -62.1 |  |  |  |  |  |  |  |  |
| h22 | S5 | 22.0 | 32.0 | +3.3 |  |  |  |  |  |  |  |  |
| h18.4 | S6 | 18.4 | 96.3 | -50.1 |  |  |  |  |  |  |  |  |
| h22 | S6 | 22.0 | 30.2 | +9.7 |  |  |  |  |  |  |  |  |
| h18.4 | S7 | 18.4 | 82.4 | -52.2 |  |  |  |  | 67.6 |  |  |  |
| h22 | S7 | 22.0 | 33.0 | +6.9 |  |  |  |  | 43.7 |  |  |  |
| h13 | S8 | 13.0 | 132.3 | +22.7 |  |  |  |  |  |  |  |  |
| h18.4 | S8 | 18.4 | 154.1 | -65.4 |  |  |  |  |  |  |  |  |
| h22 | S8 | 22.0 | 55.8 | +11.9 |  |  |  |  |  |  |  |  |

L26 S1 correlation vs golden (tod_S1_1920x1080_h18.4.jpg): mist_h7.4 0.701, mist_h7.6 0.620, mist_h7 0.755, mist_h8 0.806
```

## Golden 18.4 and night 22 spec numbers (tod_tests.py)

```
| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 57..100 | 1/8 | 2.12 | -63..-28 | 4.1..23.0 | 8.4..51.7 | 0.47..0.61 | -48.2 | +26.4 | +22.7 |  |  |  |  |
| h22 | night | 8 | 39..52 | 8/8 | 0.84 | -7..+10 |  |  |  | -13.6 | -5.9 | +3.8 | 1.72 | 31.4 | 39.6 | 9/13/4 |
| h13 | midday | 2 | 85..85 | 2/2 | 0.00 | -5..+4 |  |  |  | -40.2 | -1.7 | +46.5 |  |  |  |  |
```

Per-still tables: `TESTS_tod.md`.

## Hero box (swing_tod_18h4_hero_luma.json)

| frames_measured | bbox_mean_luma_min | bbox_mean_luma_p5 | bbox_mean_luma_mean | bbox_mean_luma_max | frames_below_threshold | L15b_frames_with_clipped_px | L15b_max_clipped_px_in_box |
|---|---|---|---|---|---|---|---|
| 718 | 20.9 | 53.0 | 106.7 | 166.4 | 16 | 694 | 15820 |

## Hero box (swing_tod_22_hero_luma.json)

| frames_measured | bbox_mean_luma_min | bbox_mean_luma_p5 | bbox_mean_luma_mean | bbox_mean_luma_max | frames_below_threshold | L15b_frames_with_clipped_px | L15b_max_clipped_px_in_box |
|---|---|---|---|---|---|---|---|
| 718 | 20.6 | 36.4 | 58.0 | 124.7 | 92 | 675 | 2103 |

## swing_tod_18h4.mp4

mean Y 71.5 (min 27.4 max 93.0), B-R mean -43.9, clipped mean 0.47 %, L18 edge/centre p50 0.76

## swing_tod_22.mp4

mean Y 35.8 (min 21.9 max 52.1), B-R mean +3.5, clipped mean 0.52 %, L18 edge/centre p50 0.57

