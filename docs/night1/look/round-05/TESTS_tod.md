# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `docs/night1/look/round-05/stills` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | C13 far-sky | C12 dBR | C14 far-river | p5 | p95/p5 | sat | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h13 | midday | 8 | 70..100 | 0/8 | 2.24 | -27..+9 | -9.4 | -12.9 | +47.3 |  |  |  |  |  |  |  |
| h13w1 | midday | 8 | 66..98 | 4/8 | 0.03 | -21..-8 | -6.3 | +0.0 | +16.2 |  |  |  |  |  |  |  |
| h18.4 | golden | 8 | 56..117 | 2/8 | 3.53 | -57..-26 | -19.4 | +11.1 | +23.4 | 4.1..31.9 | 5.9..52.1 | 0.41..0.58 |  |  |  |  |
| h19.8 | night | 8 | 38..63 | 4/8 | 1.36 | -22..+5 | +14.8 | -1.4 | +28.0 |  |  |  | 0.52 | 28.4 | 41.1 | 11/13/9 |
| h22 | night | 8 | 38..62 | 7/8 | 0.90 | -8..+10 | -8.4 | -2.1 | -4.2 |  |  |  | 1.73 | 28.7 | 37.8 | 12/13/4 |
| h7.6 | golden | 8 | 57..118 | 5/8 | 1.76 | -53..-27 | -3.0 | -3.6 | +37.5 | 5.6..32.0 | 5.9..37.9 | 0.36..0.53 |  |  |  |  |

### h13 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | 100.1 | 0.00 | 0.07 | -20.0 | L2 NO / yes / NO / NO |
| midday_S2_1920x1080.jpg | 89.8 | 0.00 | 0.00 | -27.4 | L2 yes / yes / yes / NO |
| midday_S3_1920x1080.jpg | 96.7 | 0.00 | 2.24 | -12.2 | L2 yes / yes / NO / yes |
| midday_S4_1920x1080.jpg | 80.1 | 0.00 | 0.00 | +8.9 | L2 NO / yes / yes / NO |
| midday_S5_1920x1080.jpg | 92.7 | 0.00 | 0.04 | -10.6 | L2 yes / yes / NO / yes |
| midday_S6_1920x1080.jpg | 94.0 | 0.00 | 0.35 | -13.4 | L2 yes / yes / NO / yes |
| midday_S7_1920x1080.jpg | 70.0 | 0.00 | 0.87 | -2.4 | L2 NO / yes / NO / yes |
| midday_S8_1920x1080.jpg | 81.9 | 0.00 | 0.00 | -0.6 | L2 NO / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.85 (>= 6.0) ok | C11 flat8 % 3.75 (<= 40) ok | C12 dBR -12.91 (+-10) FAIL | C13 far-sky Y -9.39 (-35..-25) FAIL | C13 far>near 52.95 (> 0) ok | C14 far-river Y 47.27 (5..35) FAIL | C15 rms far/near 0.36 (0.25..0.45) ok

### h13w1 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | 97.9 | 0.00 | 0.00 | -14.7 | L2 NO / yes / yes / yes |
| midday_S2_1920x1080.jpg | 86.1 | 0.00 | 0.00 | -20.9 | L2 yes / yes / yes / NO |
| midday_S3_1920x1080.jpg | 91.3 | 0.00 | 0.00 | -14.7 | L2 yes / yes / yes / yes |
| midday_S4_1920x1080.jpg | 84.1 | 0.00 | 0.00 | -8.7 | L2 yes / yes / yes / yes |
| midday_S5_1920x1080.jpg | 92.7 | 0.00 | 0.00 | -13.3 | L2 yes / yes / yes / yes |
| midday_S6_1920x1080.jpg | 91.6 | 0.00 | 0.03 | -15.8 | L2 yes / yes / NO / yes |
| midday_S7_1920x1080.jpg | 65.5 | 0.00 | 0.02 | -8.3 | L2 NO / yes / NO / yes |
| midday_S8_1920x1080.jpg | 88.3 | 0.00 | 0.00 | -7.7 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 2.29 (>= 6.0) FAIL | C11 flat8 % 37.68 (<= 40) ok | C12 dBR 0.03 (+-10) ok | C13 far-sky Y -6.3 (-35..-25) FAIL | C13 far>near 70.25 (> 0) ok | C14 far-river Y 16.17 (5..35) ok | C15 rms far/near 0.22 (0.25..0.45) FAIL

### h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 83.1 | 8.79 | 0.09 | -37.6 | L1 yes / NO / yes / yes |
| golden_S2_1920x1080.jpg | 90.9 | 3.60 | 0.77 | -57.2 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 56.3 | 11.60 | 1.08 | -26.5 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 116.7 | 0.41 | 0.04 | -55.9 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 69.9 | 10.26 | 0.24 | -46.3 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 82.7 | 3.80 | 0.03 | -46.2 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 67.8 | 13.40 | 3.53 | -50.1 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 82.9 | 5.26 | 0.77 | -49.5 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 6.4 | 32.5 | 0.483 | - |
| golden_S2_1920x1080.jpg | 12.9 | 15.7 | 0.520 | - |
| golden_S3_1920x1080.jpg | 5.5 | 25.7 | 0.455 | - |
| golden_S4_1920x1080.jpg | 31.9 | 5.9 | 0.411 | - |
| golden_S5_1920x1080.jpg | 4.1 | 52.1 | 0.585 | - |
| golden_S6_1920x1080.jpg | 11.3 | 18.6 | 0.544 | - |
| golden_S7_1920x1080.jpg | 5.5 | 36.3 | 0.540 | - |
| golden_S8_1920x1080.jpg | 9.8 | 19.7 | 0.501 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.02 (>= 6.0) ok | C11 flat8 % 11.25 (<= 40) ok | C12 dBR 11.13 (+-10) FAIL | C13 far-sky Y -19.39 (-35..-25) FAIL | C13 far>near 101.71 (> 0) ok | C14 far-river Y 23.41 (5..35) ok | C15 rms far/near 0.16 (0.25..0.45) FAIL

### h19.8 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 57.1 | 0.07 | 0.69 | -16.1 | L3 yes / yes / yes / NO |
| night_S2_1920x1080.jpg | 51.7 | 0.02 | 0.08 | -21.6 | L3 yes / yes / yes / NO |
| night_S3_1920x1080.jpg | 41.7 | 0.40 | 0.02 | -8.9 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 41.1 | 0.02 | 0.02 | -11.5 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 60.6 | 0.07 | 0.80 | +5.0 | L3 NO / yes / yes / yes |
| night_S6_1920x1080.jpg | 63.1 | 1.27 | 1.36 | -11.6 | L3 NO / NO / yes / yes |
| night_S7_1920x1080.jpg | 43.9 | 0.46 | 0.31 | -7.3 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 37.8 | 0.30 | 0.04 | -6.1 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 22.18 (>= 6.0) ok | C11 flat8 % 2.86 (<= 40) ok | C12 dBR -1.35 (+-10) ok | C13 far-sky Y 14.76 (-35..-25) FAIL | C13 far>near 20.39 (> 0) ok | C14 far-river Y 27.99 (5..35) ok | C15 rms far/near 0.75 (0.25..0.45) FAIL

### h22 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 62.3 | 0.00 | 0.72 | -8.4 | L3 NO / yes / yes / yes |
| night_S2_1920x1080.jpg | 43.6 | 0.00 | 0.19 | -6.5 | L3 yes / yes / yes / yes |
| night_S3_1920x1080.jpg | 38.3 | 0.00 | 0.03 | -7.0 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 37.8 | 0.00 | 0.05 | +8.5 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 45.2 | 0.00 | 0.39 | +9.0 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 47.2 | 0.00 | 0.90 | -1.5 | L3 yes / yes / yes / yes |
| night_S7_1920x1080.jpg | 44.1 | 0.00 | 0.58 | +2.7 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 42.8 | 0.00 | 0.24 | +10.2 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 5.86 (>= 6.0) FAIL | C11 flat8 % 48.57 (<= 40) FAIL | C12 dBR -2.08 (+-10) ok | C13 far-sky Y -8.37 (-35..-25) FAIL | C13 far>near -2.68 (> 0) FAIL | C14 far-river Y -4.21 (5..35) FAIL | C15 rms far/near 0.53 (0.25..0.45) FAIL

### h7.6 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 80.0 | 5.26 | 0.11 | -27.4 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 89.3 | 3.17 | 0.12 | -53.4 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 79.9 | 5.68 | 1.32 | -39.0 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 118.0 | 0.47 | 0.12 | -48.1 | L1 NO / yes / yes / yes |
| golden_S5_1920x1080.jpg | 73.7 | 8.00 | 0.01 | -34.0 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 83.1 | 4.03 | 0.07 | -42.1 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 57.2 | 13.15 | 1.76 | -27.3 | L5 NO / NO / NO / yes |
| golden_S8_1920x1080.jpg | 79.4 | 2.56 | 0.86 | -27.5 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 9.7 | 21.2 | 0.417 | - |
| golden_S2_1920x1080.jpg | 17.8 | 10.9 | 0.526 | - |
| golden_S3_1920x1080.jpg | 9.3 | 20.0 | 0.486 | - |
| golden_S4_1920x1080.jpg | 32.0 | 5.9 | 0.357 | - |
| golden_S5_1920x1080.jpg | 5.6 | 37.9 | 0.471 | - |
| golden_S6_1920x1080.jpg | 11.3 | 18.2 | 0.520 | - |
| golden_S7_1920x1080.jpg | 6.0 | 28.7 | 0.412 | - |
| golden_S8_1920x1080.jpg | 12.8 | 15.3 | 0.381 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 10.09 (>= 6.0) ok | C11 flat8 % 3.75 (<= 40) ok | C12 dBR -3.6 (+-10) ok | C13 far-sky Y -2.99 (-35..-25) FAIL | C13 far>near 89.64 (> 0) ok | C14 far-river Y 37.55 (5..35) FAIL | C15 rms far/near 0.19 (0.25..0.45) FAIL

