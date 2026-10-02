# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `docs/night1/look/round-06/stills` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 57..100 | 1/8 | 2.12 | -63..-28 | 4.1..23.0 | 8.4..51.7 | 0.47..0.61 | -48.2 | +26.4 | +22.7 |  |  |  |  |
| h22 | night | 8 | 39..52 | 8/8 | 0.84 | -7..+10 |  |  |  | -13.6 | -5.9 | +3.8 | 1.72 | 31.4 | 39.6 | 9/13/4 |
| h13 | midday | 2 | 85..85 | 2/2 | 0.00 | -5..+4 |  |  |  | -40.2 | -1.7 | +46.5 |  |  |  |  |

### h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 82.9 | 8.77 | 0.06 | -39.1 | L1 yes / NO / yes / yes |
| golden_S2_1920x1080.jpg | 89.0 | 3.71 | 0.46 | -60.2 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 57.2 | 11.45 | 0.37 | -28.0 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 99.7 | 1.29 | 0.00 | -62.6 | L1 yes / yes / yes / NO |
| golden_S5_1920x1080.jpg | 68.8 | 10.67 | 0.14 | -47.8 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 82.8 | 4.43 | 0.01 | -50.3 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 67.6 | 13.80 | 2.12 | -50.6 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 71.2 | 8.31 | 0.52 | -52.4 | L1 yes / NO / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 6.4 | 32.6 | 0.497 | - |
| golden_S2_1920x1080.jpg | 11.9 | 16.9 | 0.546 | - |
| golden_S3_1920x1080.jpg | 5.6 | 25.8 | 0.466 | - |
| golden_S4_1920x1080.jpg | 23.0 | 8.4 | 0.507 | - |
| golden_S5_1920x1080.jpg | 4.1 | 51.7 | 0.606 | - |
| golden_S6_1920x1080.jpg | 10.6 | 19.4 | 0.575 | - |
| golden_S7_1920x1080.jpg | 5.5 | 36.1 | 0.550 | - |
| golden_S8_1920x1080.jpg | 7.6 | 26.0 | 0.575 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.36 (>= 6.0) ok | C11 flat8 % 10.36 (<= 40) ok | C12 dBR 26.43 (+-10) FAIL | C13 far-sky Y -48.19 (-35..-25) FAIL | C13 far>near 88.36 (> 0) ok | C14 far-river Y 22.66 (5..35) ok | C15 rms far/near 0.22 (0.25..0.45) FAIL

### h22 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 52.5 | 0.00 | 0.68 | -4.2 | L3 yes / yes / yes / yes |
| night_S2_1920x1080.jpg | 44.4 | 0.00 | 0.07 | -7.2 | L3 yes / yes / yes / yes |
| night_S3_1920x1080.jpg | 38.6 | 0.00 | 0.04 | -6.0 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 39.6 | 0.00 | 0.05 | +4.2 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 45.2 | 0.00 | 0.39 | +8.4 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 48.0 | 0.00 | 0.84 | -3.8 | L3 yes / yes / yes / yes |
| night_S7_1920x1080.jpg | 43.7 | 0.00 | 0.56 | +2.8 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 43.1 | 0.00 | 0.17 | +10.4 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 4.31 (>= 6.0) FAIL | C11 flat8 % 46.25 (<= 40) FAIL | C12 dBR -5.92 (+-10) ok | C13 far-sky Y -13.57 (-35..-25) FAIL | C13 far>near 0.45 (> 0) ok | C14 far-river Y 3.76 (5..35) FAIL | C15 rms far/near 0.55 (0.25..0.45) FAIL

### h13 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 84.6 | 0.00 | 0.00 | +4.1 | L2 yes / yes / yes / yes |
| midday_S8_1920x1080.jpg | 85.4 | 0.00 | 0.00 | -4.8 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.83 (>= 6.0) ok | C11 flat8 % 4.11 (<= 40) ok | C12 dBR -1.68 (+-10) ok | C13 far-sky Y -40.24 (-35..-25) FAIL | C13 far>near 53.75 (> 0) ok | C14 far-river Y 46.51 (5..35) FAIL | C15 rms far/near 0.36 (0.25..0.45) ok

