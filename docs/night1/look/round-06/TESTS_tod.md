# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `docs/night1/look/round-06/stills` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | p5 | p95/p5 | sat | C13 far-sky | C12 dBR | C14 far-river | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h18.4 | golden | 8 | 60..101 | 3/8 | 2.14 | -62..-29 | 5.8..24.5 | 7.9..36.3 | 0.45..0.57 | -47.7 | +25.9 | +22.5 |  |  |  |  |
| h22 | night | 8 | 39..52 | 8/8 | 0.85 | -6..+10 |  |  |  | -18.8 | -6.4 | +2.2 | 2.47 | 36.4 | 43.6 | 9/13/3 |
| h13 | midday | 2 | 84..86 | 2/2 | 0.00 | -5..+3 |  |  |  | -40.3 | -2.1 | +44.8 |  |  |  |  |

### h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 84.9 | 6.92 | 0.06 | -40.1 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 91.6 | 2.84 | 0.41 | -62.3 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 59.8 | 8.41 | 0.41 | -29.2 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 100.7 | 0.81 | 0.00 | -62.4 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 70.2 | 8.69 | 0.13 | -47.7 | L1 yes / NO / yes / yes |
| golden_S6_1920x1080.jpg | 82.9 | 3.19 | 0.00 | -49.8 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 68.6 | 10.91 | 2.14 | -50.0 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 72.0 | 6.67 | 0.53 | -52.0 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 8.1 | 25.7 | 0.479 | - |
| golden_S2_1920x1080.jpg | 14.5 | 13.9 | 0.541 | - |
| golden_S3_1920x1080.jpg | 7.5 | 19.4 | 0.447 | - |
| golden_S4_1920x1080.jpg | 24.5 | 7.9 | 0.499 | - |
| golden_S5_1920x1080.jpg | 5.8 | 36.3 | 0.573 | - |
| golden_S6_1920x1080.jpg | 11.6 | 17.8 | 0.557 | - |
| golden_S7_1920x1080.jpg | 7.1 | 28.1 | 0.524 | - |
| golden_S8_1920x1080.jpg | 8.8 | 22.5 | 0.555 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.13 (>= 6.0) ok | C11 flat8 % 10.36 (<= 40) ok | C12 dBR 25.87 (+-10) FAIL | C13 far-sky Y -47.73 (-35..-25) FAIL | C13 far>near 87.38 (> 0) ok | C14 far-river Y 22.5 (5..35) ok | C15 rms far/near 0.23 (0.25..0.45) FAIL

### h22 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 51.6 | 0.00 | 0.68 | -3.6 | L3 yes / yes / yes / yes |
| night_S2_1920x1080.jpg | 43.2 | 0.00 | 0.09 | -6.3 | L3 yes / yes / yes / yes |
| night_S3_1920x1080.jpg | 39.2 | 0.00 | 0.07 | -5.3 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 43.6 | 0.00 | 0.08 | +5.0 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 45.3 | 0.00 | 0.40 | +9.0 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 47.7 | 0.00 | 0.85 | -2.1 | L3 yes / yes / yes / yes |
| night_S7_1920x1080.jpg | 43.7 | 0.00 | 0.56 | +2.9 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 43.1 | 0.00 | 0.17 | +10.5 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 4.2 (>= 6.0) FAIL | C11 flat8 % 40.71 (<= 40) FAIL | C12 dBR -6.44 (+-10) ok | C13 far-sky Y -18.82 (-35..-25) FAIL | C13 far>near -3.04 (> 0) FAIL | C14 far-river Y 2.23 (5..35) FAIL | C15 rms far/near 0.57 (0.25..0.45) FAIL

### h13 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 84.3 | 0.00 | 0.00 | +3.2 | L2 yes / yes / yes / yes |
| midday_S8_1920x1080.jpg | 85.8 | 0.00 | 0.00 | -5.4 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 8.98 (>= 6.0) ok | C11 flat8 % 3.93 (<= 40) ok | C12 dBR -2.13 (+-10) ok | C13 far-sky Y -40.34 (-35..-25) FAIL | C13 far>near 50.93 (> 0) ok | C14 far-river Y 44.84 (5..35) FAIL | C15 rms far/near 0.36 (0.25..0.45) ok

