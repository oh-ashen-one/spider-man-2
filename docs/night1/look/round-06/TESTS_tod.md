# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `docs/night1/look/round-06/stills` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 59..99 | 3/8 | 2.05 | -62..-29 | 5.5..23.8 | 8.1..38.1 | 0.45..0.57 | -48.8 | +27.3 | +22.6 |  |  |  |  |
| h22 | night | 8 | 39..52 | 8/8 | 0.89 | -6..+10 |  |  |  | -17.5 | -5.2 | +3.6 | 1.99 | 33.1 | 41.1 | 9/12/4 |
| h13 | midday | 2 | 85..86 | 2/2 | 0.00 | -5..+4 |  |  |  | -42.4 | -0.3 | +46.3 |  |  |  |  |

### h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 83.1 | 7.25 | 0.05 | -39.7 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 89.6 | 2.90 | 0.38 | -61.6 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 59.0 | 8.59 | 0.43 | -29.1 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 98.6 | 0.91 | 0.00 | -61.8 | L1 yes / yes / yes / NO |
| golden_S5_1920x1080.jpg | 68.7 | 9.10 | 0.12 | -46.8 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 81.2 | 3.50 | 0.00 | -49.2 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 67.2 | 11.66 | 2.05 | -49.3 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 70.6 | 6.99 | 0.50 | -51.3 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 8.0 | 25.9 | 0.481 | - |
| golden_S2_1920x1080.jpg | 14.0 | 14.3 | 0.544 | - |
| golden_S3_1920x1080.jpg | 7.4 | 19.4 | 0.450 | - |
| golden_S4_1920x1080.jpg | 23.8 | 8.1 | 0.503 | - |
| golden_S5_1920x1080.jpg | 5.5 | 38.1 | 0.573 | - |
| golden_S6_1920x1080.jpg | 11.4 | 18.2 | 0.559 | - |
| golden_S7_1920x1080.jpg | 7.0 | 28.2 | 0.525 | - |
| golden_S8_1920x1080.jpg | 8.8 | 22.4 | 0.556 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.46 (>= 6.0) ok | C11 flat8 % 10.0 (<= 40) ok | C12 dBR 27.33 (+-10) FAIL | C13 far-sky Y -48.75 (-35..-25) FAIL | C13 far>near 85.94 (> 0) ok | C14 far-river Y 22.59 (5..35) ok | C15 rms far/near 0.24 (0.25..0.45) FAIL

### h22 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 51.9 | 0.00 | 0.69 | -3.7 | L3 yes / yes / yes / yes |
| night_S2_1920x1080.jpg | 44.0 | 0.00 | 0.10 | -6.5 | L3 yes / yes / yes / yes |
| night_S3_1920x1080.jpg | 38.6 | 0.00 | 0.05 | -5.3 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 41.1 | 0.00 | 0.06 | +3.9 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 45.7 | 0.00 | 0.38 | +7.5 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 47.6 | 0.00 | 0.89 | -1.8 | L3 yes / yes / yes / yes |
| night_S7_1920x1080.jpg | 43.7 | 0.00 | 0.56 | +2.9 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 43.1 | 0.00 | 0.17 | +10.5 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 3.96 (>= 6.0) FAIL | C11 flat8 % 48.93 (<= 40) FAIL | C12 dBR -5.2 (+-10) ok | C13 far-sky Y -17.53 (-35..-25) FAIL | C13 far>near -4.8 (> 0) FAIL | C14 far-river Y 3.57 (5..35) FAIL | C15 rms far/near 0.53 (0.25..0.45) FAIL

### h13 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 84.7 | 0.00 | 0.00 | +3.7 | L2 yes / yes / yes / yes |
| midday_S8_1920x1080.jpg | 86.0 | 0.00 | 0.00 | -5.4 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.45 (>= 6.0) ok | C11 flat8 % 4.11 (<= 40) ok | C12 dBR -0.35 (+-10) ok | C13 far-sky Y -42.39 (-35..-25) FAIL | C13 far>near 53.38 (> 0) ok | C14 far-river Y 46.3 (5..35) FAIL | C15 rms far/near 0.36 (0.25..0.45) ok

