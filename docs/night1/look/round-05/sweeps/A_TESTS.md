# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `../_scratch/look/r05/A` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| g1 | golden | 5 | 62..107 | 3/5 | 3.62 | -56..-28 | 8.9..34.1 | 5.1..21.6 | 0.36..0.50 | -23.2 | +3.7 | +23.4 |  |  |  |  |
| g2 | golden | 5 | 47..95 | 1/5 | 4.21 | -66..-25 | 2.0..16.7 | 10.9..95.8 | 0.49..0.64 | -28.7 | -3.9 | +23.7 |  |  |  |  |
| g3 | golden | 3 | 53..95 | 0/3 | 4.88 | -71..-28 | 2.1..16.8 | 10.8..96.5 | 0.50..0.65 | -30.5 | -6.1 | +20.3 |  |  |  |  |
| g4 | golden | 3 | 39..91 | 0/3 | 3.70 | -62..-21 | 2.0..15.6 | 11.9..83.5 | 0.47..0.59 | -36.6 | -5.2 | +28.8 |  |  |  |  |
| g5 | golden | 5 | 43..91 | 0/5 | 4.22 | -65..-18 | 1.0..12.9 | 14.2..190.8 | 0.47..0.65 | -30.5 | -6.6 | +23.0 |  |  |  |  |
| h13w1 | midday | 8 | 69..98 | 3/8 | 0.04 | -22..-8 |  |  |  | -6.0 | +0.3 | +12.7 |  |  |  |  |
| h18.4 | golden | 8 | 73..117 | 6/8 | 3.46 | -56..-25 | 17.6..44.3 | 3.8..11.4 | 0.35..0.45 | -10.7 | +12.5 | +27.6 |  |  |  |  |
| h22 | night | 8 | 42..60 | 6/8 | 2.52 | -12..+9 |  |  |  | +38.6 | -27.5 | +68.4 | 0.92 | 56.6 | 60.5 | 10/14/8 |
| n1 | night | 3 | 43..50 | 3/3 | 1.21 | -2..+8 |  |  |  | +42.2 | -24.9 | +65.0 | 1.08 | 45.4 | 50.4 | 10/7 |
| n2 | night | 3 | 40..45 | 3/3 | 1.00 | -1..+7 |  |  |  | +41.2 | -21.9 | +59.7 | 1.86 | 37.6 | 44.4 | 11/7 |
| n3 | night | 3 | 40..45 | 3/3 | 1.01 | -0..+8 |  |  |  | +51.4 | -22.7 | +63.9 | 2.71 | 32.2 | 41.7 | 10/7 |

### g1 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 87.9 | 1.73 | 0.12 | -27.9 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 106.7 | 0.10 | 0.03 | -56.4 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 82.0 | 2.77 | 1.35 | -46.9 | L1 yes / yes / yes / yes |
| golden_S6_1920x1080.jpg | 89.4 | 0.34 | 0.02 | -37.6 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 61.8 | 8.63 | 3.62 | -42.9 | L5 yes / yes / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 14.8 | 14.1 | 0.361 | - |
| golden_S4_1920x1080.jpg | 34.1 | 5.1 | 0.434 | - |
| golden_S5_1920x1080.jpg | 11.6 | 18.1 | 0.501 | - |
| golden_S6_1920x1080.jpg | 21.9 | 9.8 | 0.431 | - |
| golden_S7_1920x1080.jpg | 8.9 | 21.6 | 0.474 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.38 (>= 6.0) ok | C11 flat8 % 13.21 (<= 40) ok | C12 dBR 3.67 (+-10) ok | C13 far-sky Y -23.19 (-35..-25) FAIL | C13 far>near 92.68 (> 0) ok | C14 far-river Y 23.43 (5..35) ok | C15 rms far/near 0.2 (0.25..0.45) FAIL

### g2 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 56.6 | 13.64 | 0.32 | -24.9 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 95.2 | 2.20 | 0.06 | -66.4 | L1 yes / yes / yes / NO |
| golden_S5_1920x1080.jpg | 73.8 | 10.91 | 0.13 | -57.3 | L1 yes / NO / yes / NO |
| golden_S6_1920x1080.jpg | 70.2 | 4.54 | 0.45 | -39.2 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 46.6 | 37.27 | 4.21 | -48.4 | L5 NO / NO / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 5.1 | 37.7 | 0.491 | - |
| golden_S4_1920x1080.jpg | 16.7 | 10.9 | 0.554 | - |
| golden_S5_1920x1080.jpg | 4.8 | 44.0 | 0.639 | - |
| golden_S6_1920x1080.jpg | 10.6 | 19.6 | 0.549 | - |
| golden_S7_1920x1080.jpg | 2.0 | 95.8 | 0.582 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.28 (>= 6.0) ok | C11 flat8 % 23.57 (<= 40) ok | C12 dBR -3.9 (+-10) ok | C13 far-sky Y -28.67 (-35..-25) ok | C13 far>near 112.92 (> 0) ok | C14 far-river Y 23.68 (5..35) ok | C15 rms far/near 0.14 (0.25..0.45) FAIL

### g3 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 60.4 | 12.42 | 0.74 | -28.0 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 94.7 | 2.12 | 0.04 | -71.1 | L1 yes / yes / yes / NO |
| golden_S7_1920x1080.jpg | 53.3 | 33.08 | 4.88 | -56.8 | L5 NO / NO / NO / NO |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 5.8 | 33.8 | 0.503 | - |
| golden_S4_1920x1080.jpg | 16.8 | 10.8 | 0.585 | - |
| golden_S7_1920x1080.jpg | 2.1 | 96.5 | 0.648 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 4.83 (>= 6.0) FAIL | C11 flat8 % 28.04 (<= 40) ok | C12 dBR -6.1 (+-10) ok | C13 far-sky Y -30.46 (-35..-25) ok | C13 far>near 113.24 (> 0) ok | C14 far-river Y 20.27 (5..35) ok | C15 rms far/near 0.11 (0.25..0.45) FAIL

### g4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 52.6 | 16.87 | 0.77 | -21.2 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 91.5 | 2.50 | 0.07 | -62.1 | L1 yes / yes / yes / NO |
| golden_S7_1920x1080.jpg | 39.3 | 39.79 | 3.70 | -41.3 | L5 NO / NO / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 4.1 | 45.5 | 0.466 | - |
| golden_S4_1920x1080.jpg | 15.6 | 11.9 | 0.543 | - |
| golden_S7_1920x1080.jpg | 2.0 | 83.5 | 0.585 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 7.9 (>= 6.0) ok | C11 flat8 % 15.71 (<= 40) ok | C12 dBR -5.25 (+-10) ok | C13 far-sky Y -36.6 (-35..-25) FAIL | C13 far>near 111.73 (> 0) ok | C14 far-river Y 28.82 (5..35) ok | C15 rms far/near 0.17 (0.25..0.45) FAIL

### g5 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 43.4 | 20.61 | 0.91 | -18.1 | L1 NO / NO / yes / NO |
| golden_S4_1920x1080.jpg | 91.1 | 3.16 | 0.06 | -64.6 | L1 yes / yes / yes / NO |
| golden_S5_1920x1080.jpg | 72.5 | 12.21 | 0.15 | -57.7 | L1 yes / NO / yes / NO |
| golden_S6_1920x1080.jpg | 58.3 | 8.62 | 2.15 | -33.7 | L1 NO / NO / NO / yes |
| golden_S7_1920x1080.jpg | 44.0 | 40.99 | 4.22 | -48.9 | L5 NO / NO / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 4.0 | 41.1 | 0.472 | - |
| golden_S4_1920x1080.jpg | 12.9 | 14.2 | 0.563 | - |
| golden_S5_1920x1080.jpg | 5.1 | 42.3 | 0.646 | - |
| golden_S6_1920x1080.jpg | 7.0 | 28.6 | 0.562 | - |
| golden_S7_1920x1080.jpg | 1.0 | 190.8 | 0.626 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.07 (>= 6.0) ok | C11 flat8 % 29.46 (<= 40) ok | C12 dBR -6.64 (+-10) ok | C13 far-sky Y -30.5 (-35..-25) ok | C13 far>near 115.91 (> 0) ok | C14 far-river Y 23.01 (5..35) ok | C15 rms far/near 0.13 (0.25..0.45) FAIL

### h13w1 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | 98.5 | 0.00 | 0.00 | -15.3 | L2 NO / yes / yes / yes |
| midday_S2_1920x1080.jpg | 89.1 | 0.00 | 0.00 | -21.7 | L2 yes / yes / yes / NO |
| midday_S3_1920x1080.jpg | 97.2 | 0.00 | 0.00 | -15.8 | L2 NO / yes / yes / yes |
| midday_S4_1920x1080.jpg | 86.3 | 0.00 | 0.00 | -9.0 | L2 yes / yes / yes / yes |
| midday_S5_1920x1080.jpg | 95.7 | 0.00 | 0.00 | -13.5 | L2 yes / yes / yes / yes |
| midday_S6_1920x1080.jpg | 94.4 | 0.00 | 0.04 | -16.1 | L2 yes / yes / NO / yes |
| midday_S7_1920x1080.jpg | 68.6 | 0.00 | 0.00 | -8.4 | L2 NO / yes / yes / yes |
| midday_S8_1920x1080.jpg | 90.1 | 0.00 | 0.00 | -8.4 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 1.94 (>= 6.0) FAIL | C11 flat8 % 53.93 (<= 40) FAIL | C12 dBR 0.31 (+-10) ok | C13 far-sky Y -5.97 (-35..-25) FAIL | C13 far>near 64.0 (> 0) ok | C14 far-river Y 12.69 (5..35) ok | C15 rms far/near 0.2 (0.25..0.45) FAIL

### h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 91.1 | 0.00 | 0.10 | -29.6 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 96.7 | 0.00 | 0.47 | -49.6 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 73.4 | 0.00 | 0.41 | -24.6 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 116.5 | 0.00 | 0.02 | -56.0 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 85.8 | 0.00 | 0.11 | -42.8 | L1 yes / yes / yes / yes |
| golden_S6_1920x1080.jpg | 91.5 | 0.00 | 0.00 | -40.6 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 83.5 | 0.00 | 3.46 | -45.0 | L5 yes / yes / NO / yes |
| golden_S8_1920x1080.jpg | 87.2 | 0.00 | 0.66 | -43.9 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 18.6 | 11.2 | 0.363 | - |
| golden_S2_1920x1080.jpg | 24.2 | 8.1 | 0.439 | - |
| golden_S3_1920x1080.jpg | 19.8 | 7.8 | 0.346 | - |
| golden_S4_1920x1080.jpg | 44.3 | 3.8 | 0.404 | - |
| golden_S5_1920x1080.jpg | 17.6 | 11.3 | 0.454 | - |
| golden_S6_1920x1080.jpg | 23.1 | 8.7 | 0.437 | - |
| golden_S7_1920x1080.jpg | 17.6 | 11.4 | 0.428 | - |
| golden_S8_1920x1080.jpg | 20.0 | 9.9 | 0.434 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 7.97 (>= 6.0) ok | C11 flat8 % 3.39 (<= 40) ok | C12 dBR 12.53 (+-10) FAIL | C13 far-sky Y -10.65 (-35..-25) FAIL | C13 far>near 70.62 (> 0) ok | C14 far-river Y 27.58 (5..35) ok | C15 rms far/near 0.31 (0.25..0.45) ok

### h22 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 49.3 | 0.00 | 1.40 | -3.8 | L3 yes / yes / yes / yes |
| night_S2_1920x1080.jpg | 57.3 | 0.00 | 0.26 | -11.9 | L3 yes / yes / yes / yes |
| night_S3_1920x1080.jpg | 41.9 | 0.00 | 0.06 | -4.2 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 60.5 | 0.00 | 0.02 | +8.0 | L3 NO / yes / yes / yes |
| night_S5_1920x1080.jpg | 53.0 | 0.00 | 0.86 | +9.4 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 57.9 | 0.00 | 1.55 | -4.2 | L3 yes / yes / yes / yes |
| night_S7_1920x1080.jpg | 54.0 | 0.00 | 2.52 | -5.7 | L3 yes / yes / NO / yes |
| night_S8_1920x1080.jpg | 55.4 | 0.00 | 0.05 | +6.7 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 21.25 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -27.49 (+-10) FAIL | C13 far-sky Y 38.59 (-35..-25) FAIL | C13 far>near 57.21 (> 0) ok | C14 far-river Y 68.39 (5..35) FAIL | C15 rms far/near 0.89 (0.25..0.45) FAIL

### n1 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 42.9 | 0.00 | 1.01 | -0.6 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 50.4 | 0.00 | 0.02 | +7.8 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 49.6 | 0.00 | 1.21 | -2.2 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 30.51 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -24.94 (+-10) FAIL | C13 far-sky Y 42.19 (-35..-25) FAIL | C13 far>near 56.31 (> 0) ok | C14 far-river Y 64.96 (5..35) FAIL | C15 rms far/near 1.04 (0.25..0.45) FAIL

### n2 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 40.2 | 0.00 | 0.78 | +0.3 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 44.4 | 0.00 | 0.05 | +7.3 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 45.5 | 0.00 | 1.00 | -0.9 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 35.61 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -21.91 (+-10) FAIL | C13 far-sky Y 41.24 (-35..-25) FAIL | C13 far>near 52.77 (> 0) ok | C14 far-river Y 59.68 (5..35) FAIL | C15 rms far/near 0.92 (0.25..0.45) FAIL

### n3 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 39.7 | 0.00 | 0.83 | +0.8 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 41.7 | 0.00 | 0.09 | +7.7 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 44.7 | 0.00 | 1.01 | -0.5 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 47.78 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -22.66 (+-10) FAIL | C13 far-sky Y 51.36 (-35..-25) FAIL | C13 far>near 59.13 (> 0) ok | C14 far-river Y 63.93 (5..35) FAIL | C15 rms far/near 0.81 (0.25..0.45) FAIL

