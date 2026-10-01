# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `../_scratch/look/r05/G` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gG1 | golden | 8 | 67..102 | 2/8 | 3.65 | -64..-39 | 4.3..24.3 | 8.0..48.1 | 0.50..0.60 | -47.9 | +25.0 | +22.4 |  |  |  |
| gB0 | night | 1 | 53..53 | 0/1 | 0.28 | -29..-29 |  |  |  | +16.3 | -11.3 | +42.7 | 0.45 | 33.6 | 53.0 |
| gBall | night | 1 | 43..43 | 0/1 | 1.01 | -14..-14 |  |  |  | -13.1 | +16.1 | +30.5 | 0.53 | 19.0 | 43.3 |
| gBfill0 | night | 1 | 52..52 | 0/1 | 0.30 | -29..-29 |  |  |  | +13.5 | -10.9 | +41.9 | 0.41 | 32.1 | 52.1 |
| gBmoon0 | night | 1 | 49..49 | 0/1 | 0.84 | -21..-21 |  |  |  | -5.3 | +13.2 | +31.1 | 0.39 | 27.3 | 49.4 |
| gBsky | night | 1 | 49..49 | 0/1 | 0.66 | -17..-17 |  |  |  | -5.0 | +8.9 | +38.2 | 0.45 | 26.5 | 49.2 |
| gBsun0 | night | 1 | 26..26 | 0/1 | 0.01 | +2..+2 |  |  |  | +29.2 | -10.6 | +32.5 | 0.36 | 20.1 | 26.0 |
| gN1 | night | 2 | 43..43 | 2/2 | 0.23 | +9..+11 |  |  |  | +8.6 | -13.6 | +36.7 | 2.80 | 32.6 | 42.6 |
| gN2 | night | 2 | 43..43 | 2/2 | 0.24 | +11..+11 |  |  |  | -21.5 | -2.6 | +8.7 | 3.09 | 34.2 | 43.4 |
| gN3 | night | 2 | 43..43 | 2/2 | 0.24 | +11..+11 |  |  |  | -21.8 | -2.8 | +8.5 | 3.15 | 34.1 | 43.5 |

### gG1 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 81.8 | 9.61 | 0.07 | -42.3 | L1 yes / NO / yes / yes |
| golden_S2_1920x1080.jpg | 91.4 | 3.49 | 0.84 | -64.1 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 70.9 | 5.48 | 0.86 | -38.6 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 101.6 | 1.02 | 0.02 | -62.5 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 70.3 | 9.91 | 0.29 | -48.6 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 81.9 | 3.70 | 0.03 | -45.4 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 66.6 | 16.14 | 3.65 | -49.1 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 69.8 | 9.21 | 0.85 | -51.6 | L1 yes / NO / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 5.8 | 36.1 | 0.527 | - |
| golden_S2_1920x1080.jpg | 13.5 | 14.9 | 0.557 | - |
| golden_S3_1920x1080.jpg | 9.6 | 17.4 | 0.502 | - |
| golden_S4_1920x1080.jpg | 24.3 | 8.0 | 0.502 | - |
| golden_S5_1920x1080.jpg | 4.3 | 48.1 | 0.605 | - |
| golden_S6_1920x1080.jpg | 10.9 | 19.2 | 0.543 | - |
| golden_S7_1920x1080.jpg | 5.0 | 39.9 | 0.523 | - |
| golden_S8_1920x1080.jpg | 6.9 | 28.8 | 0.573 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.81 (>= 6.0) ok | C11 flat8 % 10.54 (<= 40) ok | C12 dBR 25.02 (+-10) FAIL | C13 far-sky Y -47.86 (-35..-25) FAIL | C13 far>near 86.88 (> 0) ok | C14 far-river Y 22.41 (5..35) ok | C15 rms far/near 0.23 (0.25..0.45) FAIL

### gB0 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 53.0 | 0.13 | 0.28 | -29.3 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 16.5 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -11.35 (+-10) FAIL | C13 far-sky Y 16.33 (-35..-25) FAIL | C13 far>near 28.48 (> 0) ok | C14 far-river Y 42.73 (5..35) FAIL | C15 rms far/near 0.68 (0.25..0.45) FAIL

### gBall (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 43.3 | 13.46 | 1.01 | -13.9 | L3 yes / NO / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 18.25 (>= 6.0) ok | C11 flat8 % 9.64 (<= 40) ok | C12 dBR 16.06 (+-10) FAIL | C13 far-sky Y -13.13 (-35..-25) FAIL | C13 far>near 26.53 (> 0) ok | C14 far-river Y 30.46 (5..35) ok | C15 rms far/near 0.44 (0.25..0.45) ok

### gBfill0 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 52.1 | 0.77 | 0.30 | -29.1 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 16.89 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -10.89 (+-10) FAIL | C13 far-sky Y 13.54 (-35..-25) FAIL | C13 far>near 29.29 (> 0) ok | C14 far-river Y 41.93 (5..35) FAIL | C15 rms far/near 0.64 (0.25..0.45) FAIL

### gBmoon0 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 49.4 | 0.73 | 0.84 | -20.7 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 16.89 (>= 6.0) ok | C11 flat8 % 3.75 (<= 40) ok | C12 dBR 13.22 (+-10) FAIL | C13 far-sky Y -5.35 (-35..-25) FAIL | C13 far>near 21.68 (> 0) ok | C14 far-river Y 31.12 (5..35) ok | C15 rms far/near 0.49 (0.25..0.45) FAIL

### gBsky (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 49.2 | 0.41 | 0.66 | -17.1 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 15.98 (>= 6.0) ok | C11 flat8 % 0.89 (<= 40) ok | C12 dBR 8.86 (+-10) ok | C13 far-sky Y -5.0 (-35..-25) FAIL | C13 far>near 31.56 (> 0) ok | C14 far-river Y 38.25 (5..35) FAIL | C15 rms far/near 0.5 (0.25..0.45) FAIL

### gBsun0 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 26.0 | 0.27 | 0.01 | +2.3 | L3 NO / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 46.69 (>= 6.0) ok | C11 flat8 % 0.89 (<= 40) ok | C12 dBR -10.63 (+-10) FAIL | C13 far-sky Y 29.22 (-35..-25) FAIL | C13 far>near 30.47 (> 0) ok | C14 far-river Y 32.48 (5..35) ok | C15 rms far/near 0.82 (0.25..0.45) FAIL

### gN1 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 42.6 | 0.00 | 0.12 | +9.0 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 42.7 | 0.00 | 0.23 | +10.6 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 19.76 (>= 6.0) ok | C11 flat8 % 6.43 (<= 40) ok | C12 dBR -13.56 (+-10) FAIL | C13 far-sky Y 8.6 (-35..-25) FAIL | C13 far>near 27.29 (> 0) ok | C14 far-river Y 36.67 (5..35) FAIL | C15 rms far/near 1.2 (0.25..0.45) FAIL

### gN2 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 43.4 | 0.00 | 0.14 | +11.0 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 43.0 | 0.00 | 0.24 | +11.4 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.31 (>= 6.0) ok | C11 flat8 % 34.11 (<= 40) ok | C12 dBR -2.59 (+-10) ok | C13 far-sky Y -21.53 (-35..-25) FAIL | C13 far>near -2.05 (> 0) FAIL | C14 far-river Y 8.7 (5..35) ok | C15 rms far/near 0.6 (0.25..0.45) FAIL

### gN3 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 43.5 | 0.00 | 0.14 | +11.1 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 43.0 | 0.00 | 0.24 | +11.4 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.57 (>= 6.0) ok | C11 flat8 % 32.86 (<= 40) ok | C12 dBR -2.84 (+-10) ok | C13 far-sky Y -21.8 (-35..-25) FAIL | C13 far>near -2.19 (> 0) FAIL | C14 far-river Y 8.53 (5..35) ok | C15 rms far/near 0.59 (0.25..0.45) FAIL

