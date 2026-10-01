# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `../_scratch/look/r05/CD` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gG | golden | 8 | 35..112 | 4/8 | 3.82 | -63..-15 | 2.9..27.3 | 6.9..54.4 | 0.43..0.56 | -23.4 | -2.1 | +23.7 |  |  |  |
| gH | golden | 8 | 42..113 | 4/8 | 4.01 | -63..-20 | 3.8..28.6 | 6.7..44.6 | 0.46..0.59 | -22.6 | -5.1 | +23.6 |  |  |  |
| gI | golden | 8 | 45..113 | 3/8 | 4.41 | -64..-23 | 4.0..28.2 | 6.8..49.8 | 0.47..0.60 | -23.7 | -3.5 | +23.9 |  |  |  |
| gJ | golden | 8 | 40..113 | 4/8 | 4.17 | -64..-18 | 3.5..27.8 | 6.8..50.1 | 0.44..0.59 | -22.9 | -5.4 | +23.3 |  |  |  |
| h13c1 | midday | 2 | 99..100 | 0/2 | 0.00 | -1..+10 |  |  |  | -9.6 | -11.0 | +55.7 |  |  |  |
| h13c2 | midday | 2 | 99..100 | 0/2 | 0.00 | -1..+10 |  |  |  | -9.2 | -12.1 | +54.4 |  |  |  |
| h18.4c1 | golden | 3 | 85..117 | 1/3 | 3.09 | -65..-52 | 18.8..46.8 | 3.6..10.7 | 0.45..0.50 | -3.2 | +18.6 | +26.8 |  |  |  |
| h18.4c2 | golden | 3 | 85..117 | 1/3 | 3.05 | -66..-53 | 19.1..46.9 | 3.6..10.6 | 0.46..0.50 | -1.1 | +20.2 | +26.1 |  |  |  |
| h19.8c2 | night | 2 | 61..61 | 0/2 | 1.13 | -35..-29 |  |  |  | +32.4 | -25.7 | +45.8 | 0.97 | 44.1 | 61.0 |
| h22c1 | night | 2 | 53..62 | 1/2 | 0.10 | -1..+5 |  |  |  | +21.9 | -18.2 | +62.0 | 0.72 | 57.8 | 61.7 |
| h22c2 | night | 2 | 56..61 | 1/2 | 0.03 | +7..+7 |  |  |  | +23.6 | -18.1 | +62.4 | 0.66 | 57.1 | 60.9 |

### gG (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 84.1 | 5.91 | 0.13 | -30.7 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 96.9 | 2.68 | 0.90 | -55.6 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 35.3 | 19.26 | 0.01 | -14.8 | L1 NO / NO / yes / NO |
| golden_S4_1920x1080.jpg | 111.6 | 0.75 | 0.04 | -63.1 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 84.5 | 7.33 | 0.13 | -54.0 | L1 yes / yes / yes / yes |
| golden_S6_1920x1080.jpg | 93.0 | 1.59 | 0.03 | -47.0 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 58.9 | 22.94 | 3.82 | -47.4 | L5 NO / NO / NO / yes |
| golden_S8_1920x1080.jpg | 85.5 | 5.71 | 0.98 | -53.4 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 9.1 | 23.0 | 0.425 | - |
| golden_S2_1920x1080.jpg | 18.6 | 11.2 | 0.493 | - |
| golden_S3_1920x1080.jpg | 2.9 | 29.3 | 0.438 | - |
| golden_S4_1920x1080.jpg | 27.3 | 6.9 | 0.472 | - |
| golden_S5_1920x1080.jpg | 6.8 | 31.9 | 0.563 | - |
| golden_S6_1920x1080.jpg | 16.2 | 13.2 | 0.513 | - |
| golden_S7_1920x1080.jpg | 3.6 | 54.4 | 0.519 | - |
| golden_S8_1920x1080.jpg | 9.6 | 20.5 | 0.523 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.21 (>= 6.0) ok | C11 flat8 % 12.68 (<= 40) ok | C12 dBR -2.07 (+-10) ok | C13 far-sky Y -23.39 (-35..-25) FAIL | C13 far>near 110.02 (> 0) ok | C14 far-river Y 23.7 (5..35) ok | C15 rms far/near 0.14 (0.25..0.45) FAIL

### gH (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 84.5 | 6.78 | 0.10 | -35.2 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 88.5 | 2.92 | 0.79 | -54.2 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 42.4 | 15.27 | 0.03 | -19.8 | L1 NO / NO / yes / NO |
| golden_S4_1920x1080.jpg | 113.0 | 0.66 | 0.04 | -63.5 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 69.8 | 9.89 | 1.70 | -47.2 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 82.1 | 2.58 | 0.27 | -42.9 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 63.8 | 18.88 | 4.01 | -51.2 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 81.9 | 6.30 | 0.86 | -52.0 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 8.4 | 24.9 | 0.456 | - |
| golden_S2_1920x1080.jpg | 15.9 | 12.9 | 0.516 | - |
| golden_S3_1920x1080.jpg | 3.8 | 27.1 | 0.463 | - |
| golden_S4_1920x1080.jpg | 28.6 | 6.7 | 0.471 | - |
| golden_S5_1920x1080.jpg | 4.9 | 42.9 | 0.593 | - |
| golden_S6_1920x1080.jpg | 13.2 | 16.1 | 0.523 | - |
| golden_S7_1920x1080.jpg | 4.5 | 44.6 | 0.552 | - |
| golden_S8_1920x1080.jpg | 8.9 | 21.4 | 0.529 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.35 (>= 6.0) ok | C11 flat8 % 13.93 (<= 40) ok | C12 dBR -5.07 (+-10) ok | C13 far-sky Y -22.56 (-35..-25) FAIL | C13 far>near 109.35 (> 0) ok | C14 far-river Y 23.59 (5..35) ok | C15 rms far/near 0.14 (0.25..0.45) FAIL

### gI (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 85.3 | 6.15 | 0.23 | -37.8 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 87.7 | 3.04 | 0.92 | -55.6 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 45.1 | 14.11 | 0.10 | -22.7 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 113.2 | 0.65 | 0.04 | -64.2 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 69.7 | 10.06 | 2.12 | -48.1 | L1 yes / NO / NO / yes |
| golden_S6_1920x1080.jpg | 82.0 | 2.74 | 0.09 | -42.7 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 62.5 | 23.64 | 4.41 | -49.8 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 82.0 | 6.54 | 0.94 | -52.4 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 8.8 | 23.5 | 0.478 | - |
| golden_S2_1920x1080.jpg | 15.3 | 13.4 | 0.528 | - |
| golden_S3_1920x1080.jpg | 4.4 | 25.6 | 0.486 | - |
| golden_S4_1920x1080.jpg | 28.2 | 6.8 | 0.474 | - |
| golden_S5_1920x1080.jpg | 4.8 | 42.9 | 0.599 | - |
| golden_S6_1920x1080.jpg | 12.9 | 16.4 | 0.521 | - |
| golden_S7_1920x1080.jpg | 4.0 | 49.8 | 0.507 | - |
| golden_S8_1920x1080.jpg | 8.8 | 21.9 | 0.529 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.3 (>= 6.0) ok | C11 flat8 % 14.29 (<= 40) ok | C12 dBR -3.49 (+-10) ok | C13 far-sky Y -23.74 (-35..-25) FAIL | C13 far>near 110.17 (> 0) ok | C14 far-river Y 23.91 (5..35) ok | C15 rms far/near 0.14 (0.25..0.45) FAIL

### gJ (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 83.8 | 6.35 | 0.25 | -33.3 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 87.3 | 3.01 | 0.92 | -54.6 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 40.3 | 17.30 | 0.11 | -17.5 | L1 NO / NO / yes / NO |
| golden_S4_1920x1080.jpg | 112.8 | 0.73 | 0.04 | -64.5 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 73.0 | 9.31 | 0.12 | -50.1 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 82.4 | 2.42 | 0.04 | -42.1 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 62.0 | 22.16 | 4.17 | -49.8 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 79.9 | 7.25 | 0.86 | -52.2 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 8.8 | 23.7 | 0.449 | - |
| golden_S2_1920x1080.jpg | 15.8 | 13.0 | 0.516 | - |
| golden_S3_1920x1080.jpg | 3.5 | 28.6 | 0.440 | - |
| golden_S4_1920x1080.jpg | 27.8 | 6.8 | 0.476 | - |
| golden_S5_1920x1080.jpg | 5.5 | 38.0 | 0.592 | - |
| golden_S6_1920x1080.jpg | 13.8 | 15.3 | 0.515 | - |
| golden_S7_1920x1080.jpg | 4.0 | 50.1 | 0.516 | - |
| golden_S8_1920x1080.jpg | 8.5 | 22.8 | 0.534 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.41 (>= 6.0) ok | C11 flat8 % 14.46 (<= 40) ok | C12 dBR -5.36 (+-10) ok | C13 far-sky Y -22.85 (-35..-25) FAIL | C13 far>near 110.1 (> 0) ok | C14 far-river Y 23.33 (5..35) ok | C15 rms far/near 0.14 (0.25..0.45) FAIL

### h13c1 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 98.8 | 0.00 | 0.00 | +9.8 | L2 NO / yes / yes / NO |
| midday_S8_1920x1080.jpg | 100.1 | 0.00 | 0.00 | -0.8 | L2 NO / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.13 (>= 6.0) ok | C11 flat8 % 3.39 (<= 40) ok | C12 dBR -11.04 (+-10) FAIL | C13 far-sky Y -9.62 (-35..-25) FAIL | C13 far>near 62.72 (> 0) ok | C14 far-river Y 55.73 (5..35) FAIL | C15 rms far/near 0.32 (0.25..0.45) ok

### h13c2 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 98.7 | 0.00 | 0.00 | +10.2 | L2 NO / yes / yes / NO |
| midday_S8_1920x1080.jpg | 100.3 | 0.00 | 0.00 | -0.6 | L2 NO / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.25 (>= 6.0) ok | C11 flat8 % 3.75 (<= 40) ok | C12 dBR -12.06 (+-10) FAIL | C13 far-sky Y -9.15 (-35..-25) FAIL | C13 far>near 61.74 (> 0) ok | C14 far-river Y 54.41 (5..35) FAIL | C15 rms far/near 0.32 (0.25..0.45) ok

### h18.4c1 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S4_1920x1080.jpg | 117.3 | 0.00 | 0.02 | -64.8 | L1 NO / yes / yes / NO |
| golden_S7_1920x1080.jpg | 84.8 | 0.00 | 3.09 | -52.3 | L5 yes / yes / NO / yes |
| golden_S8_1920x1080.jpg | 89.4 | 0.00 | 0.89 | -52.8 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S4_1920x1080.jpg | 46.8 | 3.6 | 0.453 | - |
| golden_S7_1920x1080.jpg | 18.8 | 10.7 | 0.500 | - |
| golden_S8_1920x1080.jpg | 21.5 | 9.1 | 0.489 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 7.8 (>= 6.0) ok | C11 flat8 % 2.32 (<= 40) ok | C12 dBR 18.6 (+-10) FAIL | C13 far-sky Y -3.25 (-35..-25) FAIL | C13 far>near 53.79 (> 0) ok | C14 far-river Y 26.82 (5..35) ok | C15 rms far/near 0.37 (0.25..0.45) ok

### h18.4c2 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S4_1920x1080.jpg | 116.6 | 0.00 | 0.01 | -65.8 | L1 NO / yes / yes / NO |
| golden_S7_1920x1080.jpg | 85.1 | 0.00 | 3.05 | -52.6 | L5 yes / yes / NO / yes |
| golden_S8_1920x1080.jpg | 90.1 | 0.00 | 0.90 | -54.3 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S4_1920x1080.jpg | 46.9 | 3.6 | 0.460 | - |
| golden_S7_1920x1080.jpg | 19.1 | 10.6 | 0.503 | - |
| golden_S8_1920x1080.jpg | 22.1 | 8.9 | 0.496 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.23 (>= 6.0) ok | C11 flat8 % 2.5 (<= 40) ok | C12 dBR 20.16 (+-10) FAIL | C13 far-sky Y -1.12 (-35..-25) FAIL | C13 far>near 50.08 (> 0) ok | C14 far-river Y 26.15 (5..35) ok | C15 rms far/near 0.38 (0.25..0.45) ok

### h19.8c2 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 61.0 | 0.00 | 0.38 | -34.9 | L3 NO / yes / yes / NO |
| night_S8_1920x1080.jpg | 60.7 | 0.00 | 1.13 | -29.4 | L3 NO / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 21.81 (>= 6.0) ok | C11 flat8 % 0.18 (<= 40) ok | C12 dBR -25.69 (+-10) FAIL | C13 far-sky Y 32.42 (-35..-25) FAIL | C13 far>near 24.18 (> 0) ok | C14 far-river Y 45.8 (5..35) FAIL | C15 rms far/near 0.92 (0.25..0.45) FAIL

### h22c1 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 61.7 | 0.00 | 0.10 | +5.0 | L3 NO / yes / yes / yes |
| night_S8_1920x1080.jpg | 53.0 | 0.00 | 0.01 | -1.2 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 14.73 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -18.17 (+-10) FAIL | C13 far-sky Y 21.9 (-35..-25) FAIL | C13 far>near 45.51 (> 0) ok | C14 far-river Y 62.05 (5..35) FAIL | C15 rms far/near 0.99 (0.25..0.45) FAIL

### h22c2 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 60.9 | 0.00 | 0.01 | +6.8 | L3 NO / yes / yes / yes |
| night_S8_1920x1080.jpg | 55.8 | 0.00 | 0.03 | +6.5 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 18.33 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -18.06 (+-10) FAIL | C13 far-sky Y 23.6 (-35..-25) FAIL | C13 far>near 48.2 (> 0) ok | C14 far-river Y 62.43 (5..35) FAIL | C15 rms far/near 0.92 (0.25..0.45) FAIL

