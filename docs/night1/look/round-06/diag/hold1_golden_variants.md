# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `../_scratch/look/r06/sweep` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G0_base_h18.4 | golden | 4 | 58..117 | 0/4 | 3.64 | -55..-27 | 5.1..32.8 | 5.7..39.4 | 0.41..0.51 | -19.8 | +9.1 | +23.3 |
| G1_mie.6_h18.4 | golden | 4 | 64..116 | 1/4 | 3.12 | -51..-33 | 5.9..31.5 | 6.0..34.3 | 0.39..0.48 | -24.7 | +15.9 | +27.6 |
| G2_aerial3.5_h18.4 | golden | 4 | 66..115 | 1/4 | 3.16 | -53..-37 | 4.9..29.3 | 6.5..43.0 | 0.41..0.55 | -24.7 | +8.5 | +29.4 |
| G3_bias1.05_h18.4 | golden | 4 | 59..103 | 1/4 | 2.50 | -56..-44 | 4.1..28.2 | 6.1..50.3 | 0.45..0.57 | -21.4 | +13.0 | +25.4 |
| G4_mie.6_aer3.5_h18.4 | golden | 4 | 61..116 | 1/4 | 2.38 | -52..-35 | 5.9..28.5 | 6.7..35.5 | 0.40..0.51 | -29.4 | +12.2 | +31.1 |
| G5_hiR.62_h18.4 | golden | 4 | 66..118 | 1/4 | 2.92 | -57..-35 | 5.5..33.8 | 5.6..36.4 | 0.41..0.50 | -19.2 | +10.3 | +23.5 |
| G6_hiR.55_b.8_h18.4 | golden | 4 | 65..113 | 1/4 | 1.62 | -56..-36 | 5.5..30.7 | 6.0..35.9 | 0.42..0.53 | -20.1 | +8.8 | +23.9 |
| G7_shade.2_h18.4 | golden | 6 | 67..84 | 4/6 | 3.64 | -50..-32 | 5.1..12.8 | 16.4..40.9 | 0.43..0.56 |  |  |  |
| G8_shade.28_h18.4 | golden | 6 | 49..84 | 2/6 | 3.59 | -50..-20 | 4.3..10.7 | 19.5..42.7 | 0.41..0.59 |  |  |  |

### G0_base_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 82.3 | 8.74 | 0.08 | -34.6 | L1 yes / NO / yes / yes |
| golden_S3_1920x1080.jpg | 58.3 | 8.91 | 1.12 | -26.6 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 117.3 | 0.36 | 0.03 | -55.3 | L1 NO / yes / yes / NO |
| golden_S7_1920x1080.jpg | 67.0 | 15.35 | 3.64 | -48.5 | L5 yes / NO / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 6.8 | 30.8 | 0.456 | - |
| golden_S3_1920x1080.jpg | 6.5 | 21.3 | 0.442 | - |
| golden_S4_1920x1080.jpg | 32.8 | 5.7 | 0.406 | - |
| golden_S7_1920x1080.jpg | 5.1 | 39.4 | 0.511 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 5.78 (>= 6.0) FAIL | C11 flat8 % 11.43 (<= 40) ok | C12 dBR 9.13 (+-10) ok | C13 far-sky Y -19.75 (-35..-25) FAIL | C13 far>near 99.45 (> 0) ok | C14 far-river Y 23.28 (5..35) ok | C15 rms far/near 0.17 (0.25..0.45) FAIL

### G1_mie.6_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 81.3 | 9.41 | 0.10 | -32.6 | L1 yes / NO / yes / yes |
| golden_S3_1920x1080.jpg | 63.7 | 6.50 | 1.03 | -32.8 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 116.2 | 0.37 | 0.04 | -50.7 | L1 NO / yes / yes / yes |
| golden_S7_1920x1080.jpg | 66.9 | 14.50 | 3.12 | -41.9 | L5 yes / NO / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 6.1 | 34.3 | 0.443 | - |
| golden_S3_1920x1080.jpg | 8.3 | 18.2 | 0.477 | - |
| golden_S4_1920x1080.jpg | 31.5 | 6.0 | 0.386 | - |
| golden_S7_1920x1080.jpg | 5.9 | 33.8 | 0.456 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 7.1 (>= 6.0) ok | C11 flat8 % 8.04 (<= 40) ok | C12 dBR 15.92 (+-10) FAIL | C13 far-sky Y -24.67 (-35..-25) FAIL | C13 far>near 98.59 (> 0) ok | C14 far-river Y 27.59 (5..35) ok | C15 rms far/near 0.19 (0.25..0.45) FAIL

### G2_aerial3.5_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 81.3 | 11.20 | 0.06 | -45.5 | L1 yes / NO / yes / yes |
| golden_S3_1920x1080.jpg | 66.3 | 7.94 | 1.32 | -36.6 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 114.9 | 0.42 | 0.04 | -53.4 | L1 NO / yes / yes / yes |
| golden_S7_1920x1080.jpg | 70.7 | 9.37 | 3.16 | -51.4 | L5 yes / NO / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 4.9 | 43.0 | 0.543 | - |
| golden_S3_1920x1080.jpg | 7.9 | 20.8 | 0.500 | - |
| golden_S4_1920x1080.jpg | 29.3 | 6.5 | 0.407 | - |
| golden_S7_1920x1080.jpg | 7.1 | 27.9 | 0.554 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 7.3 (>= 6.0) ok | C11 flat8 % 7.5 (<= 40) ok | C12 dBR 8.5 (+-10) ok | C13 far-sky Y -24.68 (-35..-25) FAIL | C13 far>near 100.53 (> 0) ok | C14 far-river Y 29.36 (5..35) ok | C15 rms far/near 0.2 (0.25..0.45) FAIL

### G3_bias1.05_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 71.1 | 14.12 | 0.01 | -43.7 | L1 yes / NO / yes / yes |
| golden_S3_1920x1080.jpg | 71.3 | 4.85 | 0.94 | -46.7 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 103.0 | 0.51 | 0.01 | -55.9 | L1 NO / yes / yes / NO |
| golden_S7_1920x1080.jpg | 58.6 | 16.94 | 2.50 | -46.2 | L5 NO / NO / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 4.1 | 50.3 | 0.570 | - |
| golden_S3_1920x1080.jpg | 10.2 | 16.8 | 0.563 | - |
| golden_S4_1920x1080.jpg | 28.2 | 6.1 | 0.451 | - |
| golden_S7_1920x1080.jpg | 5.1 | 37.3 | 0.574 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.3 (>= 6.0) ok | C11 flat8 % 7.68 (<= 40) ok | C12 dBR 12.99 (+-10) FAIL | C13 far-sky Y -21.37 (-35..-25) FAIL | C13 far>near 87.59 (> 0) ok | C14 far-river Y 25.42 (5..35) ok | C15 rms far/near 0.23 (0.25..0.45) FAIL

### G4_mie.6_aer3.5_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 82.9 | 9.18 | 1.01 | -37.1 | L1 yes / NO / yes / yes |
| golden_S3_1920x1080.jpg | 61.4 | 7.03 | 1.39 | -35.2 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 115.6 | 0.35 | 0.04 | -51.5 | L1 NO / yes / yes / yes |
| golden_S7_1920x1080.jpg | 64.8 | 12.31 | 2.38 | -41.2 | L5 yes / NO / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 5.9 | 35.5 | 0.470 | - |
| golden_S3_1920x1080.jpg | 8.5 | 17.8 | 0.510 | - |
| golden_S4_1920x1080.jpg | 28.5 | 6.7 | 0.396 | - |
| golden_S7_1920x1080.jpg | 6.5 | 29.6 | 0.488 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.42 (>= 6.0) ok | C11 flat8 % 5.18 (<= 40) ok | C12 dBR 12.2 (+-10) FAIL | C13 far-sky Y -29.42 (-35..-25) ok | C13 far>near 92.69 (> 0) ok | C14 far-river Y 31.11 (5..35) ok | C15 rms far/near 0.23 (0.25..0.45) FAIL

### G5_hiR.62_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 84.3 | 8.97 | 0.03 | -40.3 | L1 yes / NO / yes / yes |
| golden_S3_1920x1080.jpg | 66.1 | 6.68 | 0.78 | -34.6 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 118.2 | 0.28 | 0.02 | -56.8 | L1 NO / yes / yes / NO |
| golden_S7_1920x1080.jpg | 65.6 | 15.96 | 2.92 | -47.1 | L5 yes / NO / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 6.3 | 33.2 | 0.500 | - |
| golden_S3_1920x1080.jpg | 8.1 | 19.4 | 0.487 | - |
| golden_S4_1920x1080.jpg | 33.8 | 5.6 | 0.414 | - |
| golden_S7_1920x1080.jpg | 5.5 | 36.4 | 0.502 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 5.74 (>= 6.0) FAIL | C11 flat8 % 11.07 (<= 40) ok | C12 dBR 10.26 (+-10) FAIL | C13 far-sky Y -19.19 (-35..-25) FAIL | C13 far>near 98.25 (> 0) ok | C14 far-river Y 23.46 (5..35) ok | C15 rms far/near 0.17 (0.25..0.45) FAIL

### G6_hiR.55_b.8_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 79.3 | 10.23 | 0.02 | -40.1 | L1 yes / NO / yes / yes |
| golden_S3_1920x1080.jpg | 64.7 | 7.11 | 0.82 | -36.5 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 112.9 | 0.39 | 0.00 | -56.2 | L1 NO / yes / yes / NO |
| golden_S7_1920x1080.jpg | 65.1 | 14.94 | 1.62 | -48.2 | L5 yes / NO / NO / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 5.8 | 35.7 | 0.516 | - |
| golden_S3_1920x1080.jpg | 7.8 | 19.9 | 0.509 | - |
| golden_S4_1920x1080.jpg | 30.7 | 6.0 | 0.423 | - |
| golden_S7_1920x1080.jpg | 5.5 | 35.9 | 0.533 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 5.9 (>= 6.0) FAIL | C11 flat8 % 10.0 (<= 40) ok | C12 dBR 8.81 (+-10) ok | C13 far-sky Y -20.14 (-35..-25) FAIL | C13 far>near 98.33 (> 0) ok | C14 far-river Y 23.95 (5..35) ok | C15 rms far/near 0.17 (0.25..0.45) FAIL

### G7_shade.2_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 83.8 | 7.12 | 0.99 | -32.3 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 69.1 | 5.48 | 0.18 | -36.9 | L1 yes / yes / yes / yes |
| golden_S5_1920x1080.jpg | 75.2 | 8.27 | 0.30 | -47.4 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 83.4 | 2.79 | 0.02 | -38.7 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 67.3 | 14.79 | 3.64 | -49.8 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 81.0 | 6.44 | 0.81 | -48.3 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 7.9 | 26.6 | 0.431 | - |
| golden_S3_1920x1080.jpg | 9.6 | 16.7 | 0.494 | - |
| golden_S5_1920x1080.jpg | 5.1 | 40.9 | 0.564 | - |
| golden_S6_1920x1080.jpg | 12.8 | 16.4 | 0.483 | - |
| golden_S7_1920x1080.jpg | 5.1 | 39.4 | 0.531 | - |
| golden_S8_1920x1080.jpg | 8.8 | 22.0 | 0.499 | - |

### G8_shade.28_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 83.9 | 8.25 | 0.49 | -41.5 | L1 yes / NO / yes / yes |
| golden_S3_1920x1080.jpg | 49.1 | 14.29 | 1.35 | -20.1 | L1 NO / NO / yes / yes |
| golden_S5_1920x1080.jpg | 72.3 | 9.08 | 0.19 | -48.7 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 82.0 | 4.09 | 0.04 | -46.7 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 66.6 | 16.08 | 3.59 | -48.7 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 82.0 | 5.86 | 0.80 | -49.6 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 6.9 | 30.6 | 0.506 | - |
| golden_S3_1920x1080.jpg | 4.3 | 28.9 | 0.415 | - |
| golden_S5_1920x1080.jpg | 4.8 | 42.7 | 0.590 | - |
| golden_S6_1920x1080.jpg | 10.7 | 19.5 | 0.551 | - |
| golden_S7_1920x1080.jpg | 5.0 | 39.9 | 0.516 | - |
| golden_S8_1920x1080.jpg | 9.3 | 20.9 | 0.506 | - |

