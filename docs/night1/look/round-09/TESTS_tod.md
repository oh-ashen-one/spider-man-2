# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `docs/night1/look/round-09/stills` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 43..95 | 5/8 | 1.86 | -53..-22 | 3.5..23.9 | 6.9..55.3 | 0.45..0.57 | -27.5 | +14.9 | +18.8 |  |  |  |  |
| h22 | night | 8 | 39..56 | 8/8 | 0.86 | -5..+10 |  |  |  | -16.8 | -2.3 | +7.7 | 2.69 | 32.8 | 41.0 | 10/13/4 |

### h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 80.3 | 7.82 | 0.02 | -34.6 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 87.3 | 3.74 | 0.07 | -51.0 | L1 yes / yes / yes / yes |
| golden_S3_1920x1080.jpg | 43.1 | 16.64 | 0.01 | -22.4 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 94.7 | 1.19 | 0.00 | -53.2 | L1 yes / yes / yes / yes |
| golden_S5_1920x1080.jpg | 72.0 | 8.08 | 0.06 | -49.4 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 81.2 | 2.94 | 0.00 | -46.9 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 58.8 | 21.11 | 1.86 | -43.9 | L5 NO / NO / NO / yes |
| golden_S8_1920x1080.jpg | 70.4 | 7.28 | 0.27 | -48.0 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 7.2 | 28.5 | 0.448 | - |
| golden_S2_1920x1080.jpg | 13.0 | 14.8 | 0.502 | - |
| golden_S3_1920x1080.jpg | 5.5 | 19.7 | 0.456 | - |
| golden_S4_1920x1080.jpg | 23.9 | 6.9 | 0.453 | - |
| golden_S5_1920x1080.jpg | 5.9 | 34.6 | 0.574 | - |
| golden_S6_1920x1080.jpg | 11.9 | 16.1 | 0.542 | - |
| golden_S7_1920x1080.jpg | 3.5 | 55.3 | 0.505 | - |
| golden_S8_1920x1080.jpg | 8.1 | 23.8 | 0.508 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 5.16 (>= 6.0) FAIL | C11 flat8 % 6.61 (<= 40) ok | C12 dBR 14.88 (+-10) FAIL | C13 far-sky Y -27.51 (-35..-25) ok | C13 far>near 84.93 (> 0) ok | C14 far-river Y 18.75 (5..35) ok | C15 rms far/near 0.16 (0.25..0.45) FAIL

### h22 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 56.5 | 0.00 | 0.69 | -4.6 | L3 yes / yes / yes / yes |
| night_S2_1920x1080.jpg | 47.1 | 0.00 | 0.10 | -3.8 | L3 yes / yes / yes / yes |
| night_S3_1920x1080.jpg | 38.7 | 0.00 | 0.07 | -4.1 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 41.0 | 0.00 | 0.10 | +8.7 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 45.4 | 0.00 | 0.41 | +9.7 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 47.4 | 0.00 | 0.86 | -1.2 | L3 yes / yes / yes / yes |
| night_S7_1920x1080.jpg | 44.1 | 0.00 | 0.52 | +3.8 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 42.4 | 0.00 | 0.28 | +9.5 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 10.82 (>= 6.0) ok | C11 flat8 % 29.29 (<= 40) ok | C12 dBR -2.29 (+-10) ok | C13 far-sky Y -16.83 (-35..-25) FAIL | C13 far>near -1.89 (> 0) FAIL | C14 far-river Y 7.7 (5..35) ok | C15 rms far/near 0.92 (0.25..0.45) FAIL

