# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `docs/night1/look/round-08/stills` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 46..97 | 4/8 | 1.80 | -57..-23 | 5.6..26.0 | 6.4..36.1 | 0.44..0.57 | -21.9 | +15.9 | +25.2 |  |  |  |  |
| h22 | night | 8 | 38..58 | 8/8 | 0.77 | -6..+10 |  |  |  | -21.4 | -1.9 | +7.3 | 2.83 | 34.7 | 42.6 | 10/13/3 |
| w1_h13 | midday | 8 | 66..95 | 5/8 | 0.01 | -21..-8 |  |  |  | -6.2 | -0.0 | +16.1 |  |  |  |  |
| h13 | midday | 2 | 80..82 | 0/2 | 0.00 | -0..+8 |  |  |  | -9.6 | -12.7 | +46.8 |  |  |  |  |

### h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 79.6 | 7.95 | 0.02 | -35.6 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 86.8 | 3.01 | 0.33 | -56.5 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 46.2 | 12.88 | 0.07 | -22.9 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 97.3 | 0.64 | 0.00 | -52.7 | L1 yes / yes / yes / yes |
| golden_S5_1920x1080.jpg | 70.1 | 8.68 | 0.05 | -47.1 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 78.4 | 3.76 | 0.00 | -47.3 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 61.9 | 14.74 | 1.80 | -45.2 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 70.9 | 6.89 | 0.26 | -43.7 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 7.5 | 27.5 | 0.458 | - |
| golden_S2_1920x1080.jpg | 13.6 | 14.6 | 0.521 | - |
| golden_S3_1920x1080.jpg | 5.6 | 20.2 | 0.450 | - |
| golden_S4_1920x1080.jpg | 26.0 | 6.4 | 0.441 | - |
| golden_S5_1920x1080.jpg | 5.8 | 36.1 | 0.569 | - |
| golden_S6_1920x1080.jpg | 10.8 | 19.0 | 0.556 | - |
| golden_S7_1920x1080.jpg | 6.1 | 32.0 | 0.503 | - |
| golden_S8_1920x1080.jpg | 8.8 | 20.5 | 0.490 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.22 (>= 6.0) ok | C11 flat8 % 10.18 (<= 40) ok | C12 dBR 15.93 (+-10) FAIL | C13 far-sky Y -21.91 (-35..-25) FAIL | C13 far>near 88.73 (> 0) ok | C14 far-river Y 25.24 (5..35) ok | C15 rms far/near 0.23 (0.25..0.45) FAIL

### h22 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 58.0 | 0.00 | 0.70 | -5.1 | L3 yes / yes / yes / yes |
| night_S2_1920x1080.jpg | 45.0 | 0.00 | 0.07 | -5.6 | L3 yes / yes / yes / yes |
| night_S3_1920x1080.jpg | 38.5 | 0.00 | 0.04 | -4.5 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 42.6 | 0.00 | 0.11 | +8.6 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 45.2 | 0.00 | 0.41 | +9.9 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 46.9 | 0.00 | 0.77 | -2.3 | L3 yes / yes / yes / yes |
| night_S7_1920x1080.jpg | 44.1 | 0.00 | 0.51 | +4.0 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 42.6 | 0.00 | 0.25 | +9.7 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 4.91 (>= 6.0) FAIL | C11 flat8 % 38.93 (<= 40) ok | C12 dBR -1.9 (+-10) ok | C13 far-sky Y -21.37 (-35..-25) FAIL | C13 far>near -7.62 (> 0) FAIL | C14 far-river Y 7.31 (5..35) ok | C15 rms far/near 0.65 (0.25..0.45) FAIL

### w1_h13 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | 94.8 | 0.00 | 0.00 | -14.9 | L2 yes / yes / yes / yes |
| midday_S2_1920x1080.jpg | 85.8 | 0.00 | 0.00 | -21.1 | L2 yes / yes / yes / NO |
| midday_S3_1920x1080.jpg | 93.5 | 0.00 | 0.00 | -15.2 | L2 yes / yes / yes / yes |
| midday_S4_1920x1080.jpg | 84.1 | 0.00 | 0.00 | -8.7 | L2 yes / yes / yes / yes |
| midday_S5_1920x1080.jpg | 92.8 | 0.00 | 0.00 | -13.4 | L2 yes / yes / yes / yes |
| midday_S6_1920x1080.jpg | 91.2 | 0.00 | 0.01 | -15.7 | L2 yes / yes / NO / yes |
| midday_S7_1920x1080.jpg | 66.4 | 0.00 | 0.01 | -8.4 | L2 NO / yes / NO / yes |
| midday_S8_1920x1080.jpg | 88.3 | 0.00 | 0.00 | -7.7 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 2.29 (>= 6.0) FAIL | C11 flat8 % 37.32 (<= 40) ok | C12 dBR -0.02 (+-10) ok | C13 far-sky Y -6.24 (-35..-25) FAIL | C13 far>near 69.66 (> 0) ok | C14 far-river Y 16.09 (5..35) ok | C15 rms far/near 0.22 (0.25..0.45) FAIL

### h13 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 80.3 | 0.00 | 0.00 | +8.2 | L2 NO / yes / yes / NO |
| midday_S8_1920x1080.jpg | 82.3 | 0.00 | 0.00 | -0.4 | L2 NO / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.4 (>= 6.0) ok | C11 flat8 % 3.93 (<= 40) ok | C12 dBR -12.67 (+-10) FAIL | C13 far-sky Y -9.62 (-35..-25) FAIL | C13 far>near 52.04 (> 0) ok | C14 far-river Y 46.83 (5..35) FAIL | C15 rms far/near 0.36 (0.25..0.45) ok

