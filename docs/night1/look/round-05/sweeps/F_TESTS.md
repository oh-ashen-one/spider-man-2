# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `../_scratch/look/r05/F` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | S4 points % | S4 median | S4 mean | L13 blobs | C13 far-sky | C12 dBR | C14 far-river | p5 | p95/p5 | sat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fB0 | night | 3 | 52..55 | 0/3 | 1.29 | -29..-12 | 0.45 | 33.6 | 53.0 | 9 | +16.3 | -11.4 | +42.8 |  |  |  |
| fD1 | midday | 8 | 67..102 | 1/8 | 2.07 | -28..+9 |  |  |  |  | -8.0 | -13.5 | +48.5 |  |  |  |
| fG1 | golden | 8 | 67..119 | 3/8 | 3.58 | -63..-42 |  |  |  |  | -18.9 | +10.7 | +22.9 | 4.1..34.0 | 5.5..51.4 | 0.42..0.60 |
| fG2 | golden | 8 | 56..117 | 3/8 | 3.42 | -53..-23 |  |  |  |  | -20.1 | +8.1 | +23.6 | 4.3..32.2 | 5.8..48.6 | 0.38..0.55 |
| fN1 | night | 4 | 41..44 | 3/4 | 0.67 | +2..+13 | 3.50 | 30.3 | 40.6 | 8/16 | -1.7 | -2.1 | +10.1 |  |  |  |
| fB1 | night | 2 | 49..74 | 0/2 | 0.12 | -92..-56 | 0.61 | 74.9 | 73.6 |  | +13.9 | -1.2 | +29.6 |  |  |  |
| fN2 | night | 2 | 41..45 | 0/2 | 0.24 | +13..+14 | 3.11 | 30.9 | 40.7 |  | -3.4 | +0.9 | +2.7 |  |  |  |
| fN3 | night | 2 | 44..44 | 2/2 | 0.28 | +10..+12 | 3.93 | 33.4 | 44.1 |  | +0.3 | -2.4 | +12.3 |  |  |  |

### fB0 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 51.7 | 3.43 | 1.29 | -11.8 | L3 yes / NO / yes / yes |
| night_S4_1920x1080.jpg | 53.0 | 0.15 | 0.28 | -29.3 | L3 yes / yes / yes / NO |
| night_S8_1920x1080.jpg | 55.0 | 0.18 | 0.86 | -25.1 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 17.45 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -11.4 (+-10) FAIL | C13 far-sky Y 16.32 (-35..-25) FAIL | C13 far>near 28.68 (> 0) ok | C14 far-river Y 42.81 (5..35) FAIL | C15 rms far/near 0.67 (0.25..0.45) FAIL

### fD1 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | 102.0 | 0.00 | 0.07 | -20.8 | L2 NO / yes / NO / NO |
| midday_S2_1920x1080.jpg | 93.2 | 0.00 | 0.00 | -27.8 | L2 yes / yes / yes / NO |
| midday_S3_1920x1080.jpg | 99.6 | 0.00 | 2.07 | -13.6 | L2 NO / yes / NO / yes |
| midday_S4_1920x1080.jpg | 83.5 | 0.00 | 0.00 | +8.9 | L2 yes / yes / yes / NO |
| midday_S5_1920x1080.jpg | 95.4 | 0.00 | 0.05 | -11.3 | L2 yes / yes / NO / yes |
| midday_S6_1920x1080.jpg | 96.9 | 0.00 | 0.38 | -12.9 | L2 yes / yes / NO / yes |
| midday_S7_1920x1080.jpg | 67.3 | 0.00 | 0.72 | -0.1 | L2 NO / yes / NO / yes |
| midday_S8_1920x1080.jpg | 85.4 | 0.00 | 0.00 | -0.5 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.13 (>= 6.0) ok | C11 flat8 % 3.57 (<= 40) ok | C12 dBR -13.53 (+-10) FAIL | C13 far-sky Y -8.02 (-35..-25) FAIL | C13 far>near 54.25 (> 0) ok | C14 far-river Y 48.52 (5..35) FAIL | C15 rms far/near 0.36 (0.25..0.45) ok

### fG1 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 83.3 | 9.59 | 0.05 | -45.2 | L1 yes / NO / yes / yes |
| golden_S2_1920x1080.jpg | 92.3 | 3.48 | 0.72 | -63.5 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 73.5 | 4.91 | 1.09 | -42.2 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 119.1 | 0.25 | 0.03 | -58.8 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 70.5 | 9.88 | 0.16 | -48.2 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 85.1 | 3.36 | 0.02 | -48.0 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 67.0 | 15.00 | 3.58 | -48.6 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 81.8 | 5.65 | 0.75 | -48.6 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 5.8 | 36.1 | 0.539 | - |
| golden_S2_1920x1080.jpg | 13.9 | 14.4 | 0.554 | - |
| golden_S3_1920x1080.jpg | 10.2 | 16.8 | 0.521 | - |
| golden_S4_1920x1080.jpg | 34.0 | 5.5 | 0.424 | - |
| golden_S5_1920x1080.jpg | 4.1 | 51.4 | 0.602 | - |
| golden_S6_1920x1080.jpg | 11.6 | 18.0 | 0.549 | - |
| golden_S7_1920x1080.jpg | 5.1 | 39.5 | 0.524 | - |
| golden_S8_1920x1080.jpg | 9.6 | 20.0 | 0.499 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.32 (>= 6.0) ok | C11 flat8 % 9.64 (<= 40) ok | C12 dBR 10.73 (+-10) FAIL | C13 far-sky Y -18.92 (-35..-25) FAIL | C13 far>near 96.09 (> 0) ok | C14 far-river Y 22.94 (5..35) ok | C15 rms far/near 0.17 (0.25..0.45) FAIL

### fG2 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 83.5 | 8.83 | 0.07 | -33.2 | L1 yes / NO / yes / yes |
| golden_S2_1920x1080.jpg | 90.5 | 3.11 | 0.68 | -53.0 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 56.1 | 9.97 | 1.05 | -23.4 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 116.8 | 0.35 | 0.03 | -50.4 | L1 NO / yes / yes / yes |
| golden_S5_1920x1080.jpg | 69.7 | 9.99 | 0.10 | -42.0 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 82.6 | 3.34 | 0.01 | -38.9 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 66.9 | 15.85 | 3.42 | -45.2 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 81.5 | 6.11 | 0.66 | -44.6 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 6.4 | 32.9 | 0.443 | - |
| golden_S2_1920x1080.jpg | 13.6 | 14.9 | 0.485 | - |
| golden_S3_1920x1080.jpg | 5.9 | 23.0 | 0.419 | - |
| golden_S4_1920x1080.jpg | 32.2 | 5.8 | 0.379 | - |
| golden_S5_1920x1080.jpg | 4.3 | 48.6 | 0.548 | - |
| golden_S6_1920x1080.jpg | 11.9 | 17.7 | 0.487 | - |
| golden_S7_1920x1080.jpg | 5.0 | 40.1 | 0.481 | - |
| golden_S8_1920x1080.jpg | 8.9 | 21.7 | 0.468 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.09 (>= 6.0) ok | C11 flat8 % 11.96 (<= 40) ok | C12 dBR 8.07 (+-10) ok | C13 far-sky Y -20.1 (-35..-25) FAIL | C13 far>near 101.29 (> 0) ok | C14 far-river Y 23.56 (5..35) ok | C15 rms far/near 0.16 (0.25..0.45) FAIL

### fN1 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 41.9 | 0.00 | 0.67 | +2.4 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 40.6 | 0.00 | 0.17 | +8.5 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 43.2 | 0.00 | 0.32 | +13.5 | L3 yes / yes / yes / NO |
| night_S8_1920x1080.jpg | 43.6 | 0.00 | 0.29 | +7.8 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.97 (>= 6.0) ok | C11 flat8 % 32.32 (<= 40) ok | C12 dBR -2.09 (+-10) ok | C13 far-sky Y -1.69 (-35..-25) FAIL | C13 far>near -1.7 (> 0) FAIL | C14 far-river Y 10.05 (5..35) ok | C15 rms far/near 0.62 (0.25..0.45) FAIL

### fB1 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 73.6 | 2.20 | 0.07 | -92.5 | L3 NO / NO / yes / NO |
| night_S8_1920x1080.jpg | 49.5 | 18.44 | 0.12 | -56.5 | L3 yes / NO / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 5.9 (>= 6.0) FAIL | C11 flat8 % 3.93 (<= 40) ok | C12 dBR -1.16 (+-10) ok | C13 far-sky Y 13.92 (-35..-25) FAIL | C13 far>near 67.26 (> 0) ok | C14 far-river Y 29.58 (5..35) ok | C15 rms far/near 0.3 (0.25..0.45) ok

### fN2 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 40.7 | 0.00 | 0.15 | +13.1 | L3 yes / yes / yes / NO |
| night_S8_1920x1080.jpg | 44.8 | 0.00 | 0.24 | +14.0 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 3.52 (>= 6.0) FAIL | C11 flat8 % 66.79 (<= 40) FAIL | C12 dBR 0.92 (+-10) ok | C13 far-sky Y -3.41 (-35..-25) FAIL | C13 far>near -7.55 (> 0) FAIL | C14 far-river Y 2.67 (5..35) FAIL | C15 rms far/near 0.28 (0.25..0.45) ok

### fN3 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 44.1 | 0.00 | 0.17 | +10.3 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 43.9 | 0.00 | 0.28 | +11.8 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 11.54 (>= 6.0) ok | C11 flat8 % 29.11 (<= 40) ok | C12 dBR -2.38 (+-10) ok | C13 far-sky Y 0.32 (-35..-25) FAIL | C13 far>near 0.61 (> 0) ok | C14 far-river Y 12.32 (5..35) ok | C15 rms far/near 0.73 (0.25..0.45) FAIL

