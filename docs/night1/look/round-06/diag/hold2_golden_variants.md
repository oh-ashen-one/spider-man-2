# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `../_scratch/look/r06/sweep_b` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G10_h18.4 | golden | 8 | 54..96 | 2/8 | 1.42 | -48..-31 | 3.1..21.9 | 8.0..67.8 | 0.42..0.59 | -33.9 | +17.8 | +33.7 |
| G11_cut_h18.4 | golden | 8 | 49..82 | 2/8 | 1.73 | -56..-26 | 2.9..17.3 | 10.3..68.5 | 0.49..0.60 | -55.9 | +35.0 | +21.2 |
| G9_h18.4 | golden | 8 | 55..98 | 3/8 | 1.71 | -53..-31 | 3.5..24.8 | 6.8..53.8 | 0.45..0.57 | -23.0 | +15.9 | +25.1 |

### G10_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 70.0 | 11.08 | 0.05 | -30.5 | L1 yes / NO / yes / yes |
| golden_S2_1920x1080.jpg | 72.6 | 5.14 | 0.30 | -47.7 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 55.5 | 14.46 | 1.09 | -32.5 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 96.0 | 1.00 | 0.00 | -47.2 | L1 yes / yes / yes / yes |
| golden_S5_1920x1080.jpg | 57.2 | 15.63 | 0.01 | -37.1 | L1 NO / NO / yes / yes |
| golden_S6_1920x1080.jpg | 65.0 | 10.19 | 0.01 | -38.3 | L1 yes / NO / yes / yes |
| golden_S7_1920x1080.jpg | 54.0 | 18.26 | 1.42 | -36.7 | L5 NO / NO / NO / yes |
| golden_S8_1920x1080.jpg | 66.2 | 10.83 | 0.27 | -39.8 | L1 yes / NO / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 5.0 | 40.6 | 0.466 | - |
| golden_S2_1920x1080.jpg | 9.6 | 19.7 | 0.534 | - |
| golden_S3_1920x1080.jpg | 6.3 | 23.0 | 0.512 | - |
| golden_S4_1920x1080.jpg | 21.9 | 8.0 | 0.421 | - |
| golden_S5_1920x1080.jpg | 3.1 | 67.8 | 0.590 | - |
| golden_S6_1920x1080.jpg | 7.1 | 28.6 | 0.565 | - |
| golden_S7_1920x1080.jpg | 4.9 | 35.7 | 0.505 | - |
| golden_S8_1920x1080.jpg | 5.9 | 30.2 | 0.501 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.11 (>= 6.0) ok | C11 flat8 % 3.39 (<= 40) ok | C12 dBR 17.79 (+-10) FAIL | C13 far-sky Y -33.86 (-35..-25) ok | C13 far>near 86.29 (> 0) ok | C14 far-river Y 33.72 (5..35) ok | C15 rms far/near 0.3 (0.25..0.45) ok

### G11_cut_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 69.7 | 12.06 | 0.02 | -36.0 | L1 yes / NO / yes / yes |
| golden_S2_1920x1080.jpg | 72.3 | 5.12 | 0.12 | -52.4 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 49.5 | 11.82 | 0.19 | -26.2 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 81.9 | 2.43 | 0.00 | -56.1 | L1 yes / yes / yes / NO |
| golden_S5_1920x1080.jpg | 57.3 | 15.21 | 0.07 | -39.3 | L1 NO / NO / yes / yes |
| golden_S6_1920x1080.jpg | 65.9 | 7.80 | 0.00 | -35.6 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 56.4 | 21.14 | 1.73 | -44.5 | L5 NO / NO / NO / yes |
| golden_S8_1920x1080.jpg | 59.1 | 13.98 | 0.37 | -46.4 | L1 NO / NO / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 5.0 | 40.6 | 0.521 | - |
| golden_S2_1920x1080.jpg | 9.8 | 19.2 | 0.562 | - |
| golden_S3_1920x1080.jpg | 5.1 | 23.0 | 0.494 | - |
| golden_S4_1920x1080.jpg | 17.3 | 10.3 | 0.531 | - |
| golden_S5_1920x1080.jpg | 2.9 | 68.5 | 0.599 | - |
| golden_S6_1920x1080.jpg | 8.5 | 24.2 | 0.534 | - |
| golden_S7_1920x1080.jpg | 3.5 | 53.8 | 0.552 | - |
| golden_S8_1920x1080.jpg | 5.0 | 36.8 | 0.595 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.98 (>= 6.0) ok | C11 flat8 % 13.04 (<= 40) ok | C12 dBR 35.02 (+-10) FAIL | C13 far-sky Y -55.94 (-35..-25) FAIL | C13 far>near 76.31 (> 0) ok | C14 far-river Y 21.17 (5..35) ok | C15 rms far/near 0.27 (0.25..0.45) ok

### G9_h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 68.8 | 13.24 | 0.00 | -35.4 | L1 yes / NO / yes / yes |
| golden_S2_1920x1080.jpg | 74.6 | 4.68 | 0.12 | -51.3 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 56.3 | 7.84 | 0.02 | -30.9 | L1 NO / yes / yes / yes |
| golden_S4_1920x1080.jpg | 97.6 | 0.94 | 0.00 | -52.8 | L1 yes / yes / yes / yes |
| golden_S5_1920x1080.jpg | 62.2 | 12.63 | 0.05 | -40.1 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 69.4 | 5.60 | 0.00 | -31.9 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 55.3 | 24.91 | 1.71 | -42.8 | L5 NO / NO / NO / yes |
| golden_S8_1920x1080.jpg | 68.1 | 9.53 | 0.27 | -43.8 | L1 yes / NO / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 4.3 | 47.3 | 0.518 | - |
| golden_S2_1920x1080.jpg | 11.0 | 17.1 | 0.542 | - |
| golden_S3_1920x1080.jpg | 7.3 | 18.5 | 0.501 | - |
| golden_S4_1920x1080.jpg | 24.8 | 6.8 | 0.445 | - |
| golden_S5_1920x1080.jpg | 3.8 | 52.4 | 0.567 | - |
| golden_S6_1920x1080.jpg | 9.6 | 21.2 | 0.486 | - |
| golden_S7_1920x1080.jpg | 3.5 | 53.8 | 0.519 | - |
| golden_S8_1920x1080.jpg | 6.8 | 25.8 | 0.518 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.04 (>= 6.0) ok | C11 flat8 % 10.0 (<= 40) ok | C12 dBR 15.88 (+-10) FAIL | C13 far-sky Y -23.04 (-35..-25) FAIL | C13 far>near 91.63 (> 0) ok | C14 far-river Y 25.06 (5..35) ok | C15 rms far/near 0.21 (0.25..0.45) FAIL

