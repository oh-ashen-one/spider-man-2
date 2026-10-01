# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `../_scratch/look/r05/B` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gA | golden | 8 | 36..112 | 2/8 | 4.10 | -67..-16 | 3.8..27.9 | 6.8..43.8 | 0.44..0.59 | -23.3 | -1.4 | +23.6 |  |  |  |  |
| gB | golden | 8 | 36..116 | 2/8 | 4.31 | -68..-18 | 3.8..28.5 | 6.9..39.2 | 0.47..0.60 | -22.1 | -7.0 | +21.6 |  |  |  |  |
| gC | golden | 8 | 40..108 | 2/8 | 4.42 | -69..-22 | 3.5..25.2 | 7.4..56.5 | 0.52..0.63 | -24.4 | -1.2 | +26.4 |  |  |  |  |
| gD | golden | 8 | 33..116 | 2/8 | 5.35 | -71..-16 | 3.1..26.1 | 7.7..55.4 | 0.48..0.61 | -23.7 | -7.5 | +22.4 |  |  |  |  |
| gE | golden | 8 | 33..139 | 2/8 | 4.32 | -70..-15 | 3.5..38.3 | 5.4..48.8 | 0.43..0.56 | -12.0 | -2.0 | +15.1 |  |  |  |  |
| gF | golden | 8 | 44..139 | 1/8 | 5.20 | -70..-19 | 4.6..38.0 | 5.4..36.9 | 0.42..0.53 | -12.2 | -1.9 | +15.0 |  |  |  |  |
| nA | night | 4 | 40..46 | 4/4 | 1.03 | -1..+10 |  |  |  | +59.3 | -25.0 | +70.0 | 3.42 | 32.4 | 43.3 | 9/14/7 |
| nB | night | 4 | 40..45 | 4/4 | 1.01 | -1..+11 |  |  |  | +56.5 | -23.0 | +66.2 | 3.91 | 30.4 | 42.7 | 9/14/6 |
| nC | night | 4 | 43..50 | 4/4 | 1.25 | -2..+11 |  |  |  | +60.4 | -26.5 | +73.6 | 4.48 | 35.3 | 48.0 | 9/14/6 |
| oA | midday | 6 | 84..95 | 4/6 | 0.01 | -21..-9 |  |  |  | -6.2 | +0.0 | +16.1 |  |  |  |  |

### gA (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 84.4 | 5.07 | 0.17 | -32.8 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 97.1 | 2.54 | 0.95 | -59.6 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 36.0 | 17.64 | 0.02 | -16.2 | L1 NO / NO / yes / NO |
| golden_S4_1920x1080.jpg | 111.7 | 0.57 | 0.05 | -67.1 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 84.7 | 6.90 | 0.17 | -57.5 | L1 yes / yes / yes / NO |
| golden_S6_1920x1080.jpg | 93.3 | 1.28 | 0.05 | -50.0 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 59.2 | 20.88 | 4.10 | -51.2 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 85.8 | 4.72 | 1.09 | -57.4 | L1 yes / yes / yes / NO |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 9.9 | 21.1 | 0.445 | - |
| golden_S2_1920x1080.jpg | 19.1 | 10.9 | 0.518 | - |
| golden_S3_1920x1080.jpg | 3.8 | 22.4 | 0.459 | - |
| golden_S4_1920x1080.jpg | 27.9 | 6.8 | 0.495 | - |
| golden_S5_1920x1080.jpg | 7.5 | 28.9 | 0.587 | - |
| golden_S6_1920x1080.jpg | 16.9 | 12.7 | 0.534 | - |
| golden_S7_1920x1080.jpg | 4.5 | 43.8 | 0.557 | - |
| golden_S8_1920x1080.jpg | 10.5 | 18.8 | 0.547 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.2 (>= 6.0) ok | C11 flat8 % 14.11 (<= 40) ok | C12 dBR -1.41 (+-10) ok | C13 far-sky Y -23.33 (-35..-25) FAIL | C13 far>near 109.65 (> 0) ok | C14 far-river Y 23.64 (5..35) ok | C15 rms far/near 0.14 (0.25..0.45) FAIL

### gB (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 85.5 | 4.96 | 0.13 | -37.9 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 97.1 | 2.43 | 0.98 | -61.7 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 36.0 | 17.29 | 0.01 | -18.1 | L1 NO / NO / yes / NO |
| golden_S4_1920x1080.jpg | 116.1 | 0.51 | 0.05 | -68.3 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 87.1 | 6.71 | 3.70 | -60.9 | L1 yes / yes / NO / NO |
| golden_S6_1920x1080.jpg | 97.8 | 1.10 | 1.27 | -52.0 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 61.8 | 20.42 | 4.31 | -55.3 | L5 yes / NO / NO / NO |
| golden_S8_1920x1080.jpg | 90.4 | 2.98 | 1.32 | -60.4 | L1 yes / yes / yes / NO |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 10.1 | 20.8 | 0.473 | - |
| golden_S2_1920x1080.jpg | 20.9 | 10.0 | 0.531 | - |
| golden_S3_1920x1080.jpg | 3.8 | 22.4 | 0.490 | - |
| golden_S4_1920x1080.jpg | 28.5 | 6.9 | 0.492 | - |
| golden_S5_1920x1080.jpg | 8.0 | 26.8 | 0.601 | - |
| golden_S6_1920x1080.jpg | 18.5 | 11.9 | 0.526 | - |
| golden_S7_1920x1080.jpg | 5.1 | 39.2 | 0.594 | - |
| golden_S8_1920x1080.jpg | 11.6 | 17.4 | 0.547 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.22 (>= 6.0) ok | C11 flat8 % 21.25 (<= 40) ok | C12 dBR -6.99 (+-10) ok | C13 far-sky Y -22.1 (-35..-25) FAIL | C13 far>near 114.6 (> 0) ok | C14 far-river Y 21.55 (5..35) ok | C15 rms far/near 0.12 (0.25..0.45) FAIL

### gC (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 86.8 | 6.95 | 0.31 | -41.5 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 91.2 | 3.09 | 1.17 | -63.0 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 39.7 | 20.19 | 0.10 | -22.3 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 107.6 | 0.92 | 0.07 | -69.3 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 76.2 | 8.93 | 3.06 | -55.0 | L1 yes / NO / NO / yes |
| golden_S6_1920x1080.jpg | 84.7 | 3.03 | 0.21 | -47.2 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 57.1 | 26.56 | 4.42 | -50.8 | L5 NO / NO / NO / yes |
| golden_S8_1920x1080.jpg | 80.5 | 7.58 | 1.14 | -55.6 | L1 yes / yes / yes / NO |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 7.9 | 27.1 | 0.517 | - |
| golden_S2_1920x1080.jpg | 13.8 | 15.1 | 0.566 | - |
| golden_S3_1920x1080.jpg | 4.1 | 25.2 | 0.532 | - |
| golden_S4_1920x1080.jpg | 25.2 | 7.4 | 0.522 | - |
| golden_S5_1920x1080.jpg | 5.5 | 39.5 | 0.629 | - |
| golden_S6_1920x1080.jpg | 12.6 | 17.4 | 0.555 | - |
| golden_S7_1920x1080.jpg | 3.5 | 56.5 | 0.576 | - |
| golden_S8_1920x1080.jpg | 7.9 | 24.3 | 0.566 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.8 (>= 6.0) ok | C11 flat8 % 10.0 (<= 40) ok | C12 dBR -1.25 (+-10) ok | C13 far-sky Y -24.4 (-35..-25) FAIL | C13 far>near 106.98 (> 0) ok | C14 far-river Y 26.37 (5..35) ok | C15 rms far/near 0.17 (0.25..0.45) FAIL

### gD (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 82.3 | 6.05 | 1.24 | -35.7 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 95.0 | 2.78 | 2.44 | -62.4 | L1 yes / yes / NO / NO |
| golden_S3_1920x1080.jpg | 33.4 | 21.61 | 0.23 | -16.1 | L1 NO / NO / yes / NO |
| golden_S4_1920x1080.jpg | 116.4 | 0.80 | 0.16 | -70.6 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 87.6 | 7.30 | 0.89 | -62.8 | L1 yes / yes / yes / NO |
| golden_S6_1920x1080.jpg | 98.3 | 1.31 | 1.37 | -51.7 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 58.8 | 26.54 | 5.35 | -54.0 | L5 NO / NO / NO / yes |
| golden_S8_1920x1080.jpg | 88.8 | 5.18 | 1.86 | -61.6 | L1 yes / yes / NO / NO |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 9.3 | 22.8 | 0.478 | - |
| golden_S2_1920x1080.jpg | 19.6 | 10.8 | 0.541 | - |
| golden_S3_1920x1080.jpg | 3.1 | 27.0 | 0.483 | - |
| golden_S4_1920x1080.jpg | 26.1 | 7.7 | 0.504 | - |
| golden_S5_1920x1080.jpg | 7.5 | 29.3 | 0.611 | - |
| golden_S6_1920x1080.jpg | 17.9 | 12.3 | 0.526 | - |
| golden_S7_1920x1080.jpg | 3.6 | 55.4 | 0.578 | - |
| golden_S8_1920x1080.jpg | 9.8 | 21.0 | 0.562 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.39 (>= 6.0) ok | C11 flat8 % 20.89 (<= 40) ok | C12 dBR -7.45 (+-10) ok | C13 far-sky Y -23.71 (-35..-25) FAIL | C13 far>near 119.16 (> 0) ok | C14 far-river Y 22.37 (5..35) ok | C15 rms far/near 0.12 (0.25..0.45) FAIL

### gE (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 77.8 | 5.78 | 0.23 | -28.9 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 92.2 | 2.55 | 1.03 | -56.3 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 33.4 | 19.68 | 0.01 | -14.7 | L1 NO / NO / yes / NO |
| golden_S4_1920x1080.jpg | 138.7 | 0.14 | 0.12 | -69.5 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 119.7 | 1.51 | 2.84 | -70.3 | L1 NO / yes / NO / NO |
| golden_S6_1920x1080.jpg | 94.6 | 1.22 | 0.12 | -45.2 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 59.5 | 24.87 | 4.32 | -52.8 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 122.8 | 0.03 | 3.46 | -69.7 | L1 NO / yes / NO / NO |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 9.6 | 21.5 | 0.426 | - |
| golden_S2_1920x1080.jpg | 20.6 | 10.1 | 0.510 | - |
| golden_S3_1920x1080.jpg | 3.5 | 22.2 | 0.454 | - |
| golden_S4_1920x1080.jpg | 38.3 | 5.4 | 0.440 | - |
| golden_S5_1920x1080.jpg | 14.7 | 16.0 | 0.530 | - |
| golden_S6_1920x1080.jpg | 18.1 | 12.1 | 0.491 | - |
| golden_S7_1920x1080.jpg | 4.1 | 48.8 | 0.562 | - |
| golden_S8_1920x1080.jpg | 19.8 | 11.0 | 0.492 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 5.61 (>= 6.0) FAIL | C11 flat8 % 35.36 (<= 40) ok | C12 dBR -2.03 (+-10) ok | C13 far-sky Y -11.96 (-35..-25) FAIL | C13 far>near 118.41 (> 0) ok | C14 far-river Y 15.05 (5..35) ok | C15 rms far/near 0.06 (0.25..0.45) FAIL

### gF (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 98.3 | 2.76 | 1.42 | -34.6 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 115.4 | 0.21 | 2.63 | -65.2 | L1 NO / yes / NO / NO |
| golden_S3_1920x1080.jpg | 43.8 | 15.30 | 0.31 | -19.5 | L1 NO / NO / yes / NO |
| golden_S4_1920x1080.jpg | 138.5 | 0.14 | 0.12 | -69.3 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 123.6 | 1.38 | 1.00 | -69.7 | L1 NO / yes / yes / NO |
| golden_S6_1920x1080.jpg | 113.7 | 0.59 | 2.06 | -48.6 | L1 NO / yes / NO / yes |
| golden_S7_1920x1080.jpg | 72.7 | 17.10 | 5.20 | -59.0 | L5 yes / NO / NO / NO |
| golden_S8_1920x1080.jpg | 122.8 | 0.03 | 3.46 | -69.2 | L1 NO / yes / NO / NO |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 13.3 | 16.2 | 0.418 | - |
| golden_S2_1920x1080.jpg | 29.3 | 7.4 | 0.486 | - |
| golden_S3_1920x1080.jpg | 4.6 | 23.0 | 0.450 | - |
| golden_S4_1920x1080.jpg | 38.0 | 5.4 | 0.439 | - |
| golden_S5_1920x1080.jpg | 16.0 | 14.8 | 0.513 | - |
| golden_S6_1920x1080.jpg | 24.1 | 9.5 | 0.455 | - |
| golden_S7_1920x1080.jpg | 5.6 | 36.9 | 0.531 | - |
| golden_S8_1920x1080.jpg | 20.1 | 10.9 | 0.488 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 5.33 (>= 6.0) FAIL | C11 flat8 % 35.0 (<= 40) ok | C12 dBR -1.93 (+-10) ok | C13 far-sky Y -12.17 (-35..-25) FAIL | C13 far>near 118.55 (> 0) ok | C14 far-river Y 15.04 (5..35) ok | C15 rms far/near 0.06 (0.25..0.45) FAIL

### nA (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 40.0 | 0.00 | 0.79 | +0.5 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 43.3 | 0.00 | 0.13 | +6.7 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 41.1 | 0.00 | 0.41 | +9.9 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 45.5 | 0.00 | 1.03 | -1.0 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 58.96 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -25.02 (+-10) FAIL | C13 far-sky Y 59.27 (-35..-25) FAIL | C13 far>near 64.41 (> 0) ok | C14 far-river Y 70.02 (5..35) FAIL | C15 rms far/near 0.77 (0.25..0.45) FAIL

### nB (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 39.7 | 0.00 | 0.76 | +0.8 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 42.7 | 0.00 | 0.17 | +7.0 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 40.9 | 0.00 | 0.40 | +10.6 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 45.2 | 0.00 | 1.01 | -0.7 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 52.32 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -23.04 (+-10) FAIL | C13 far-sky Y 56.54 (-35..-25) FAIL | C13 far>near 61.18 (> 0) ok | C14 far-river Y 66.17 (5..35) FAIL | C15 rms far/near 0.68 (0.25..0.45) FAIL

### nC (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 43.4 | 0.00 | 1.01 | -0.5 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 48.0 | 0.00 | 0.21 | +6.8 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 45.6 | 0.00 | 0.52 | +10.5 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 50.0 | 0.00 | 1.25 | -1.9 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 52.38 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -26.49 (+-10) FAIL | C13 far-sky Y 60.38 (-35..-25) FAIL | C13 far>near 67.54 (> 0) ok | C14 far-river Y 73.56 (5..35) FAIL | C15 rms far/near 0.67 (0.25..0.45) FAIL

### oA (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | 95.3 | 0.00 | 0.00 | -15.0 | L2 yes / yes / yes / yes |
| midday_S2_1920x1080.jpg | 85.9 | 0.00 | 0.00 | -21.2 | L2 yes / yes / yes / NO |
| midday_S3_1920x1080.jpg | 94.3 | 0.00 | 0.00 | -15.5 | L2 yes / yes / yes / yes |
| midday_S4_1920x1080.jpg | 84.0 | 0.00 | 0.00 | -8.7 | L2 yes / yes / yes / yes |
| midday_S5_1920x1080.jpg | 92.7 | 0.00 | 0.00 | -13.6 | L2 yes / yes / yes / yes |
| midday_S6_1920x1080.jpg | 91.4 | 0.00 | 0.01 | -15.8 | L2 yes / yes / NO / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 2.27 (>= 6.0) FAIL | C11 flat8 % 37.14 (<= 40) ok | C12 dBR 0.02 (+-10) ok | C13 far-sky Y -6.17 (-35..-25) FAIL | C13 far>near 69.13 (> 0) ok | C14 far-river Y 16.06 (5..35) ok | C15 rms far/near 0.23 (0.25..0.45) FAIL

