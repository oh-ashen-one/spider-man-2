# Round 09: S4 golden sky / aerial perspective numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

All frames from the real game (`Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`), 1920x1080 output, internal 1920x1080 (`r.ScreenPercentage 100`, TSR as anti-aliasing only). Measured on the lossless PNG of each frame where it is kept (`diag/png/`), else on the committed JPEG (q90); JPEG numbers are listed too. Instruments: `tools/export/s4_far_check.py` (city), `tools/perf_ue/sweeps/r09/quick_s4.py` / `quick_all.py` (wrappers), `look_spec_check.py`, `tod_tests.py`, `twilight_check.py`, `dome_check.py`.

## 1. S4 perch: the round lines (1080p)

Targets: sky (0,0,1650,80) mean Y <= 205; far band 25-32 Y under the sky on BOTH (450,192,1350,236) and (0,150,1300,215); T2 <= 10 % of (0,150,1300,300) above Y 204; T4 <= 10 % of the bright 8x8 blocks of (540,110,900,260) flat (and <= 10 % of all blocks); C12 far - sky B-R within +-10; T1 silhouette-top std >= 12 px (three definitions of s4_far_check.py: A first Y < 215, B first |dY| > 4, C first Y < column sky - 12); C11 far / sky Laplacian >= 6 and flat 8x8 <= 40 %; C14 far - river 5..35; C15 rms far / near 0.25..0.45.

| frame | sky Y | far - sky | (0,150,1300,215) - sky | T2 % | T4 flat / bright (bright n) | T4 flat / all % | C12 | T1 A / B / C | C11 lap / flat % | C14 | C15 | frame mean | failing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Manhattan_View_S4 session 1 t=38 s (round frame) | 183.1 | -31.7 | -27.2 | 2.0 | 0.0 (1) | 0.0 | +8.1 | 0.0 / 26.7 / 0.7 | 9.0 / 1.2 | 30.3 | 0.26 | 114.4 | T1 |
| golden tour S4 on /Game/Maps/Manhattan | 181.7 | -28.7 | -24.7 | 2.0 | 0.0 (1) | 0.0 | +5.5 | 0.0 / 26.6 / 0.9 | 8.9 / 1.2 | 28.9 | 0.27 | 117.1 | crit, T1 |
| Manhattan_View_S4 JPEG (committed still) | 183.1 | -31.7 | -27.2 | 2.0 | 0.0 (1) | 0.0 | +8.1 | 0.0 / 26.7 / 0.6 | 10.2 / 0.9 | 30.2 | 0.26 | 114.3 | T1 |
| golden tour S4 JPEG (committed still) | 181.7 | -28.7 | -24.7 | 2.0 | 0.0 (1) | 0.0 | +5.5 | 0.0 / 26.8 / 1.3 | 9.9 / 1.1 | 28.9 | 0.27 | 117.1 | crit, T1 |
| BEFORE: round-08 golden preset, same city build (sweep 15 base, tour S4) | 192.5 | -26.5 | -22.0 | 0.5 | 0.0 (0) | 0.0 | -5.9 | 0.0 / 79.1 / 0.0 | 3.9 / 16.4 | 18.4 | 0.09 | 108.6 | crit, T1, C11, C15 |
| city round-11 frame (city test map + city S4 lighting; reference) | 228.8 | -68.2 | -57.1 | 6.6 | 45.8 (24) | 1.4 | -0.1 | 23.6 / 24.6 / 23.6 | 30.3 / 0.0 | 23.3 | 0.31 | 128.2 | sky, far, crit, T4 |

T1 definition A is 0 on every frame whose sky is below Y 215 (the first row of every column is already "below 215"); the round asks for sky <= 205, so A cannot pass together with the sky line.

## 2. Golden preset S1-S8 on /Game/Maps/Manhattan (L1 61..100 mean, Y<10 <= 8 %, clipped <= 1.8 %, B-R -55..-20; S7 L5 59..118 / 8.8 % / 0.7 %)

| set | L1 / L5 pass | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | Y<25 S3 / S7 / S8 % |
|---|---|---|---|---|---|---|---|---|---|---|
| round 09 (final) | 3 / 8 | 84 / 7.5 / 0.11 / -12 x | 94 / 2.9 / 0.79 / -34 | 36 / 27.9 / 0.00 / -10 x | 117 / 0.8 / 0.12 / -47 x | 74 / 8.3 / 1.62 / -37 x | 92 / 2.3 / 0.02 / -37 | 42 / 29.5 / 0.53 / -23 x | 83 / 5.2 / 1.46 / -39 | 51.9 / 53.2 / 17.9 |
| before (round-08 golden preset, same city) | 3 / 8 | 83 / 6.4 / 0.08 / -8 x | 87 / 3.4 / 0.76 / -29 | 35 / 17.8 / 0.00 / -7 x | 109 / 1.3 / 0.00 / -47 x | 73 / 9.4 / 1.68 / -39 x | 84 / 2.6 / 0.02 / -29 | 60 / 27.9 / 3.90 / -41 x | 78 / 7.3 / 0.82 / -43 | 51.7 / 44.1 / 19.2 |
| merged look round 03 (round-03 city) | 5 / 8 | 96 / 0.0 / 0.11 / -25 | 93 / 0.0 / 0.17 / -43 | 74 / 0.0 / 0.36 / -20 x | 111 / 0.0 / 0.06 / -52 x | 89 / 0.0 / 0.10 / -42 | 94 / 0.0 / 0.02 / -37 | 88 / 0.0 / 3.19 / -43 x | 84 / 0.0 / 0.72 / -39 | 12.4 / 10.1 / 13.7 |

Cells: mean / Y<10 % / clipped % / B-R (x = outside the band). City round-10 Y<25 limits of the round: S3 13.2, S7 1.4, S8 7.8 %.

## 3. Fixed midday / night preset maps (round-03 floors)

| still | spec | mean Y | Y<10 % | clipped % | B-R | lit blobs (bottom half) | bottom-third p90 / p10 | within (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | L2 | 94.0 | 0.00 | 0.00 | -3.9 | 5 | 155 / 95 | yes / yes / yes / yes |
| midday_S2_1920x1080.jpg | L2 | 89.2 | 0.00 | 0.00 | -7.7 | 10 | 129 / 36 | yes / yes / yes / yes |
| midday_S3_1920x1080.jpg | L2 | 83.5 | 0.00 | 0.00 | -6.6 | 10 | 146 / 28 | yes / yes / yes / yes |
| midday_S4_1920x1080.jpg | L2 | 86.5 | 0.00 | 0.00 | +2.4 | 7 | 80 / 29 | yes / yes / yes / yes |
| midday_S5_1920x1080.jpg | L2 | 95.3 | 0.00 | 0.00 | -4.6 | 7 | 167 / 21 | yes / yes / yes / yes |
| midday_S6_1920x1080.jpg | L2 | 93.6 | 0.00 | 0.00 | -5.7 | 12 | 162 / 53 | yes / yes / yes / yes |
| midday_S7_1920x1080.jpg | L2 | 71.1 | 0.00 | 0.03 | -1.2 | 6 | 111 / 17 | NO / yes / NO / yes |
| midday_S8_1920x1080.jpg | L2 | 88.3 | 0.00 | 0.00 | +2.0 | 9 | 104 / 26 | yes / yes / yes / yes |
| night_S1_1920x1080.jpg | L3 | 43.2 | 0.00 | 0.66 | -6.6 | 9 | 108 / 23 | yes / yes / yes / yes |
| night_S2_1920x1080.jpg | L3 | 45.6 | 0.00 | 0.17 | -11.6 | 15 | 79 / 21 | yes / yes / yes / yes |
| night_S3_1920x1080.jpg | L3 | 33.2 | 0.00 | 0.30 | +3.2 | 6 | 41 / 15 | NO / yes / yes / yes |
| night_S4_1920x1080.jpg | L3 | 42.1 | 0.00 | 0.14 | +4.7 | 8 | 75 / 19 | yes / yes / yes / yes |
| night_S5_1920x1080.jpg | L3 | 45.2 | 0.00 | 0.42 | -3.8 | 14 | 122 / 21 | yes / yes / yes / yes |
| night_S6_1920x1080.jpg | L3 | 47.9 | 0.00 | 0.92 | -10.6 | 4 | 69 / 19 | yes / yes / yes / yes |
| night_S7_1920x1080.jpg | L3 | 44.8 | 0.00 | 0.38 | -7.9 | 10 | 156 / 18 | yes / yes / yes / yes |
| night_S8_1920x1080.jpg | L3 | 41.6 | 0.00 | 0.29 | +0.0 | 7 | 77 / 18 | yes / yes / yes / yes |

### Far field (S4, boxes of docs/night1/city/spec_regions.json v1, 1080p)

| still | sky Y (B-R) | horizon_far Y (B-R) | far_shore Y (B-R) | river Y | L10 far-shore Y - sky Y (-32..-15) | L10 far-shore B-R - sky B-R (+-10) | L11 horizon_far - sky (>= +3, midday) | far-shore - river Y (P1 C14: 5..35) |
|---|---|---|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 144.2 (+4.2) | 129.1 (+5.0) | 122.2 (+4.8) | 112.3 | -21.9 yes | +0.5 yes | -15.0 NO | +9.9 yes |
| night_S4_1920x1080.jpg | 45.4 (+16.4) | 38.0 (+9.0) | 35.4 (+10.5) | 21.5 | -9.9 NO | -5.9 yes | -7.4 (n/a) | +13.9 yes |

### Glass p10 (L17: >= 20; glass-only boxes)

| still | box | p10 Y | mean Y | B-R | L17 |
|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | s1_left_glass | 31.5 | 68.7 | -8.8 | yes |
| midday_S2_1920x1080.jpg | s2_gold_glass | 34.5 | 60.3 | -22.6 | yes |
| midday_S5_1920x1080.jpg | s5_teal_glass | 94.8 | 129.3 | +4.6 | yes |
| midday_S7_1920x1080.jpg | s7_left_glass | 16.9 | 32.3 | -0.1 | NO |
| midday_S8_1920x1080.jpg | s8_glass_right | 21.9 | 86.4 | +8.0 | yes |
| midday_S8_1920x1080.jpg | s8_pale_glass | 49.6 | 79.9 | +5.9 | yes |

### Night street views (L13 / L14)

| still | lit blobs (L13 >= 5) | bottom-third p10 (L14 15..30) | bottom-third p90 (L14 >= 100) |
|---|---|---|---|
| night_S1_1920x1080.jpg | 9 yes | 22.6 yes | 107.7 yes |
| night_S5_1920x1080.jpg | 14 yes | 21.1 yes | 122.0 yes |
| night_S6_1920x1080.jpg | 4 NO | 18.6 yes | 69.2 NO |


## 4. Time of day (round-08 key table, unchanged; round-09 city)

See `TESTS_tod.md` (tod_tests.py). Summary:

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 43..95 | 5/8 | 1.86 | -53..-22 | 3.5..23.9 | 6.9..55.3 | 0.45..0.57 | -27.5 | +14.9 | +18.8 |  |  |  |  |
| h22 | night | 8 | 39..56 | 8/8 | 0.86 | -5..+10 |  |  |  | -16.8 | -2.3 | +7.7 | 2.69 | 32.8 | 41.0 | 10/13/4 |
| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 80.3 | 7.82 | 0.02 | -34.6 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 87.3 | 3.74 | 0.07 | -51.0 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 43.1 | 16.64 | 0.01 | -22.4 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 94.7 | 1.19 | 0.00 | -53.2 | L1 yes / yes / yes / yes |
| golden_S5_1920x1080.jpg | 72.0 | 8.08 | 0.06 | -49.4 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 81.2 | 2.94 | 0.00 | -46.9 | L1 yes / yes / yes / yes |

L25 / L24 / L26: `TWILIGHT_r09.md`.

L27: `DOME_r09.md`:

# Twilight dome checks (dome_check.py, LOOK-SPEC L27)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

| still | pose | hour | sky Y | far Y | sky-far (a >= 10) | 8-row step max @row (b <= 25) | worst column band | clip rows 0-150 % (c <= 0.3) | sky B-R (d facing -90..-20) | mean Y | a | b | c | d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h13 | S4 | 13.0 | 128.7 | 107.8 | +20.8 | 6.6 @101 | 21.3 | 0.00 | +30.4 | 80.7 | ok | ok | ok |  |
| h18.4 | S4 | 18.4 | 158.5 | 139.9 | +18.6 | 7.0 @101 | 21.7 | 0.00 | -68.5 | 94.7 | ok | ok | ok |  |
| h19.5 | S4 | 19.5 | 109.2 | 89.8 | +19.4 | 4.2 @126 | 17.0 | 0.16 | -57.7 | 60.5 | ok | ok | ok |  |
| h19.8 | S4 | 19.8 | 95.3 | 64.0 | +31.3 | 14.8 @117 | 67.5 | 0.02 | -16.3 | 49.6 | ok | ok | ok |  |
| h19 | S4 | 19.0 | 117.8 | 104.3 | +13.5 | 2.4 @169 | 10.9 | 0.00 | -91.5 | 81.4 | ok | ok | ok |  |
| h20.5 | S4 | 20.5 | 87.3 | 49.0 | +38.3 | 6.9 @255 | 25.3 | 0.00 | +6.8 | 46.0 | ok | ok | ok |  |
| h20 | S4 | 20.0 | 52.7 | 44.6 | +8.1 | 9.7 @101 | 49.0 | 0.00 | -8.5 | 33.8 | FAIL | ok | ok |  |
| h21.5 | S4 | 21.5 | 50.1 | 36.4 | +13.7 | 8.2 @174 | 32.8 | 0.00 | +11.7 | 42.0 | ok | ok | ok |  |
| h21 | S4 | 21.0 | 49.5 | 65.7 | -16.2 | 10.0 @134 | 52.1 | 0.00 | -4.5 | 42.4 | FAIL | ok | ok |  |
| h22 | S4 | 22.0 | 45.2 | 31.1 | +14.2 | 7.5 @174 | 30.6 | 0.00 | +15.1 | 41.0 | ok | ok | ok |  |
| h6.5 | S4 | 6.5 | 119.8 | 76.1 | +43.7 | 11.2 @104 | 45.2 | 0.00 | -38.8 | 48.2 | ok | ok | ok |  |
| h7.5 | S4 | 7.5 | 122.5 | 76.7 | +45.8 | 7.0 @102 | 25.5 | 0.00 | -13.7 | 70.2 | ok | ok | ok |  |
| h7 | S4 | 7.0 | 145.0 | 81.4 | +63.7 | 12.9 @100 | 26.9 | 0.00 | -65.3 | 68.9 | ok | ok | ok |  |
| mist_h7.6 | S4 | 7.6 | 124.4 | 79.8 | +44.5 | 7.4 @102 | 24.3 | 0.00 | +3.0 | 71.3 | ok | ok | ok |  |
| w1_h13 | S4 | 13.0 | 129.9 | 120.0 | +9.9 | 6.0 @128 | 27.8 | 0.00 | -11.6 | 84.4 | FAIL | ok | ok |  |
| h6.5 | S4e | 6.5 | 113.1 | 91.7 | +21.4 | 17.6 @100 | 63.6 | 0.00 | -35.5 | 40.2 | ok | ok | ok | ok |
| h7.5 | S4e | 7.5 | 147.1 | 105.0 | +42.1 | 16.4 @108 | 25.6 | 0.00 | -81.0 | 71.7 | ok | ok | ok | ok |
| h7 | S4e | 7.0 | 132.2 | 92.3 | +39.9 | 20.8 @109 | 40.8 | 0.05 | -82.2 | 65.6 | ok | ok | ok | ok |
| mist_h7.6 | S4e | 7.6 | 145.1 | 102.1 | +43.0 | 16.5 @108 | 26.7 | 0.00 | -76.8 | 71.4 | ok | ok | ok | ok |
| h19.5 | S4w | 19.5 | 107.7 | 83.9 | +23.8 | 11.5 @104 | 61.4 | 0.09 | -57.9 | 56.4 | ok | ok | ok | ok |
| h19.8 | S4w | 19.8 | 123.2 | 83.6 | +39.7 | 16.9 @126 | 54.0 | 0.00 | -31.5 | 41.3 | ok | ok | ok | ok |
| h19 | S4w | 19.0 | 128.3 | 111.9 | +16.5 | 9.2 @107 | 17.5 | 0.00 | -96.3 | 70.3 | ok | ok | ok | FAIL |
| h20.5 | S4w | 20.5 | 88.0 | 50.6 | +37.4 | 17.3 @187 | 50.7 | 0.00 | -13.7 | 43.2 | ok | ok | ok | FAIL |
| h20 | S4w | 20.0 | 131.3 | 79.7 | +51.5 | 25.6 @125 | 55.3 | 0.15 | -34.6 | 42.8 | ok | FAIL | ok | ok |

| variant prefix | S4 mean 20:30 | S4 mean 22:00 | L27e (no pit) |
|---|---|---|---|
| (none) | 45.97 | 41.0 | ok |

