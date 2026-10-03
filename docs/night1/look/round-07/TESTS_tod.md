# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `docs/night1/look/round-07/stills` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 47..98 | 3/8 | 1.80 | -55..-23 | 5.8..26.3 | 6.3..36.1 | 0.44..0.57 | -21.7 | +15.8 | +25.2 |  |  |  |  |
| h22 | night | 8 | 39..57 | 8/8 | 0.80 | -5..+10 |  |  |  | -18.9 | -1.6 | +7.1 | 2.71 | 33.9 | 42.3 | 10/13/4 |
| h13 | midday | 2 | 80..82 | 0/2 | 0.00 | -1..+9 |  |  |  | -11.0 | -11.6 | +46.9 |  |  |  |  |

### h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 77.9 | 9.54 | 0.02 | -34.1 | L1 yes / NO / yes / yes |
| golden_S2_1920x1080.jpg | 86.3 | 3.57 | 0.38 | -55.1 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 46.8 | 12.27 | 0.07 | -23.2 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 97.7 | 0.62 | 0.00 | -53.0 | L1 yes / yes / yes / yes |
| golden_S5_1920x1080.jpg | 70.2 | 8.70 | 0.05 | -47.6 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 79.5 | 3.41 | 0.00 | -46.9 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 61.3 | 15.24 | 1.80 | -44.7 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 70.9 | 7.02 | 0.26 | -43.7 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 6.9 | 30.1 | 0.451 | - |
| golden_S2_1920x1080.jpg | 12.8 | 15.5 | 0.515 | - |
| golden_S3_1920x1080.jpg | 6.0 | 19.0 | 0.450 | - |
| golden_S4_1920x1080.jpg | 26.3 | 6.3 | 0.443 | - |
| golden_S5_1920x1080.jpg | 5.8 | 36.1 | 0.572 | - |
| golden_S6_1920x1080.jpg | 11.5 | 17.9 | 0.549 | - |
| golden_S7_1920x1080.jpg | 6.1 | 32.0 | 0.497 | - |
| golden_S8_1920x1080.jpg | 8.8 | 20.5 | 0.490 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.22 (>= 6.0) ok | C11 flat8 % 9.11 (<= 40) ok | C12 dBR 15.76 (+-10) FAIL | C13 far-sky Y -21.7 (-35..-25) FAIL | C13 far>near 87.96 (> 0) ok | C14 far-river Y 25.2 (5..35) ok | C15 rms far/near 0.23 (0.25..0.45) FAIL

### h22 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 56.5 | 0.00 | 0.69 | -4.5 | L3 yes / yes / yes / yes |
| night_S2_1920x1080.jpg | 44.3 | 0.00 | 0.08 | -4.9 | L3 yes / yes / yes / yes |
| night_S3_1920x1080.jpg | 39.4 | 0.00 | 0.07 | -3.6 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 42.3 | 0.00 | 0.10 | +9.1 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 45.1 | 0.00 | 0.41 | +10.3 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 47.1 | 0.00 | 0.80 | -1.9 | L3 yes / yes / yes / yes |
| night_S7_1920x1080.jpg | 43.9 | 0.00 | 0.57 | +3.0 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 42.8 | 0.00 | 0.25 | +9.5 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 5.4 (>= 6.0) FAIL | C11 flat8 % 39.11 (<= 40) ok | C12 dBR -1.61 (+-10) ok | C13 far-sky Y -18.86 (-35..-25) FAIL | C13 far>near -3.77 (> 0) FAIL | C14 far-river Y 7.08 (5..35) ok | C15 rms far/near 0.63 (0.25..0.45) FAIL

### h13 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 80.3 | 0.00 | 0.00 | +8.5 | L2 NO / yes / yes / NO |
| midday_S8_1920x1080.jpg | 82.4 | 0.00 | 0.00 | -0.6 | L2 NO / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.33 (>= 6.0) ok | C11 flat8 % 4.29 (<= 40) ok | C12 dBR -11.55 (+-10) FAIL | C13 far-sky Y -11.04 (-35..-25) FAIL | C13 far>near 52.68 (> 0) ok | C14 far-river Y 46.85 (5..35) FAIL | C15 rms far/near 0.36 (0.25..0.45) ok

