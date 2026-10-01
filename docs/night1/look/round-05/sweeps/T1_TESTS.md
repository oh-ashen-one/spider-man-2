# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `docs/night1/look/round-05/stills` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | C13 far-sky | C12 dBR | C14 far-river | p5 | p95/p5 | sat | S4 points % | S4 median | S4 mean | L13 blobs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h13 | midday | 8 | 76..113 | 0/8 | 3.25 | -29..+10 | -9.4 | -11.5 | +54.4 |  |  |  |  |  |  |  |
| h13w1 | midday | 8 | 65..95 | 5/8 | 0.02 | -21..-8 | -6.3 | +0.0 | +16.1 |  |  |  |  |  |  |  |
| h18.4 | golden | 8 | 56..116 | 1/8 | 4.00 | -72..-35 | -19.6 | +10.7 | +23.4 | 4.6..32.0 | 5.9..45.2 | 0.51..0.66 |  |  |  |  |
| h19.8 | night | 8 | 28..64 | 2/8 | 1.53 | -29..+1 | +16.4 | -11.3 | +42.4 |  |  |  | 0.44 | 33.1 | 52.8 | 9/13/8 |
| h22 | night | 8 | 37..44 | 8/8 | 0.93 | -1..+9 | +46.9 | -18.7 | +62.5 |  |  |  | 3.58 | 31.5 | 43.0 | 9/14/5 |
| h7.6 | golden | 8 | 54..117 | 5/8 | 1.89 | -65..-33 | -3.5 | -3.9 | +37.3 | 4.8..31.4 | 6.0..37.7 | 0.46..0.61 |  |  |  |  |

### h13 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | 113.4 | 0.00 | 0.19 | -20.7 | L2 NO / yes / NO / NO |
| midday_S2_1920x1080.jpg | 107.3 | 0.00 | 0.01 | -29.4 | L2 NO / yes / NO / NO |
| midday_S3_1920x1080.jpg | 111.9 | 0.00 | 3.25 | -13.7 | L2 NO / yes / NO / yes |
| midday_S4_1920x1080.jpg | 98.7 | 0.00 | 0.00 | +10.0 | L2 NO / yes / yes / NO |
| midday_S5_1920x1080.jpg | 108.6 | 0.00 | 0.11 | -12.0 | L2 NO / yes / NO / yes |
| midday_S6_1920x1080.jpg | 110.5 | 0.00 | 0.48 | -13.2 | L2 NO / yes / NO / yes |
| midday_S7_1920x1080.jpg | 75.9 | 0.00 | 1.27 | +0.6 | L2 NO / yes / NO / yes |
| midday_S8_1920x1080.jpg | 100.0 | 0.00 | 0.00 | -0.5 | L2 NO / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.29 (>= 6.0) ok | C11 flat8 % 3.04 (<= 40) ok | C12 dBR -11.54 (+-10) FAIL | C13 far-sky Y -9.4 (-35..-25) FAIL | C13 far>near 61.46 (> 0) ok | C14 far-river Y 54.44 (5..35) FAIL | C15 rms far/near 0.32 (0.25..0.45) ok

### h13w1 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S1_1920x1080.jpg | 95.5 | 0.00 | 0.00 | -15.0 | L2 yes / yes / yes / yes |
| midday_S2_1920x1080.jpg | 85.9 | 0.00 | 0.00 | -21.2 | L2 yes / yes / yes / NO |
| midday_S3_1920x1080.jpg | 94.3 | 0.00 | 0.00 | -15.5 | L2 yes / yes / yes / yes |
| midday_S4_1920x1080.jpg | 84.0 | 0.00 | 0.00 | -8.7 | L2 yes / yes / yes / yes |
| midday_S5_1920x1080.jpg | 92.6 | 0.00 | 0.00 | -13.6 | L2 yes / yes / yes / yes |
| midday_S6_1920x1080.jpg | 91.3 | 0.00 | 0.02 | -15.8 | L2 yes / yes / NO / yes |
| midday_S7_1920x1080.jpg | 64.8 | 0.00 | 0.01 | -8.1 | L2 NO / yes / NO / yes |
| midday_S8_1920x1080.jpg | 88.2 | 0.00 | 0.00 | -7.7 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 2.29 (>= 6.0) FAIL | C11 flat8 % 37.86 (<= 40) ok | C12 dBR 0.02 (+-10) ok | C13 far-sky Y -6.29 (-35..-25) FAIL | C13 far>near 69.41 (> 0) ok | C14 far-river Y 16.05 (5..35) ok | C15 rms far/near 0.23 (0.25..0.45) FAIL

### h18.4 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 84.4 | 8.29 | 0.16 | -50.5 | L1 yes / NO / yes / yes |
| golden_S2_1920x1080.jpg | 91.5 | 3.07 | 0.88 | -71.1 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 55.7 | 11.23 | 1.34 | -34.9 | L1 NO / NO / yes / yes |
| golden_S4_1920x1080.jpg | 116.2 | 0.40 | 0.05 | -71.9 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 70.4 | 9.90 | 0.90 | -55.1 | L1 yes / NO / yes / NO |
| golden_S6_1920x1080.jpg | 82.2 | 3.39 | 0.13 | -54.3 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 66.5 | 16.04 | 4.00 | -56.3 | L5 yes / NO / NO / NO |
| golden_S8_1920x1080.jpg | 81.1 | 5.85 | 0.97 | -60.1 | L1 yes / yes / yes / NO |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 6.8 | 30.5 | 0.578 | - |
| golden_S2_1920x1080.jpg | 13.9 | 14.5 | 0.612 | - |
| golden_S3_1920x1080.jpg | 5.6 | 24.1 | 0.554 | - |
| golden_S4_1920x1080.jpg | 32.0 | 5.9 | 0.509 | - |
| golden_S5_1920x1080.jpg | 4.6 | 45.2 | 0.658 | - |
| golden_S6_1920x1080.jpg | 11.8 | 17.8 | 0.607 | - |
| golden_S7_1920x1080.jpg | 4.9 | 41.0 | 0.600 | - |
| golden_S8_1920x1080.jpg | 9.4 | 20.5 | 0.586 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.04 (>= 6.0) ok | C11 flat8 % 11.43 (<= 40) ok | C12 dBR 10.71 (+-10) FAIL | C13 far-sky Y -19.57 (-35..-25) FAIL | C13 far>near 101.91 (> 0) ok | C14 far-river Y 23.45 (5..35) ok | C15 rms far/near 0.16 (0.25..0.45) FAIL

### h19.8 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 52.3 | 1.48 | 1.25 | -12.7 | L3 yes / NO / yes / yes |
| night_S2_1920x1080.jpg | 39.6 | 0.34 | 0.07 | -11.8 | L3 yes / yes / yes / yes |
| night_S3_1920x1080.jpg | 28.3 | 4.81 | 0.03 | +0.7 | L3 NO / NO / yes / yes |
| night_S4_1920x1080.jpg | 52.8 | 0.23 | 0.28 | -28.8 | L3 yes / yes / yes / NO |
| night_S5_1920x1080.jpg | 60.0 | 0.84 | 0.83 | -0.1 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 64.2 | 1.14 | 1.53 | -15.7 | L3 NO / NO / yes / NO |
| night_S7_1920x1080.jpg | 50.8 | 0.39 | 1.13 | -16.1 | L3 yes / yes / yes / NO |
| night_S8_1920x1080.jpg | 55.3 | 0.17 | 0.91 | -24.8 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 16.96 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -11.26 (+-10) FAIL | C13 far-sky Y 16.38 (-35..-25) FAIL | C13 far>near 29.08 (> 0) ok | C14 far-river Y 42.42 (5..35) FAIL | C15 rms far/near 0.66 (0.25..0.45) FAIL

### h22 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 40.3 | 0.00 | 0.77 | +0.4 | L3 yes / yes / yes / yes |
| night_S2_1920x1080.jpg | 41.6 | 0.00 | 0.27 | -1.1 | L3 yes / yes / yes / yes |
| night_S3_1920x1080.jpg | 37.3 | 0.00 | 0.42 | +2.2 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 43.0 | 0.00 | 0.14 | +6.5 | L3 yes / yes / yes / yes |
| night_S5_1920x1080.jpg | 42.4 | 0.00 | 0.57 | +9.1 | L3 yes / yes / yes / yes |
| night_S6_1920x1080.jpg | 44.5 | 0.00 | 0.93 | -0.8 | L3 yes / yes / yes / yes |
| night_S7_1920x1080.jpg | 42.9 | 0.00 | 0.92 | +1.7 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 41.7 | 0.00 | 0.38 | +5.7 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 39.31 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -18.71 (+-10) FAIL | C13 far-sky Y 46.89 (-35..-25) FAIL | C13 far>near 56.48 (> 0) ok | C14 far-river Y 62.45 (5..35) FAIL | C15 rms far/near 0.73 (0.25..0.45) FAIL

### h7.6 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 84.6 | 6.23 | 1.35 | -49.7 | L1 yes / yes / yes / yes |
| golden_S2_1920x1080.jpg | 90.0 | 3.22 | 0.85 | -65.3 | L1 yes / yes / yes / NO |
| golden_S3_1920x1080.jpg | 78.1 | 6.18 | 0.78 | -51.8 | L1 yes / yes / yes / yes |
| golden_S4_1920x1080.jpg | 117.1 | 0.46 | 0.21 | -64.1 | L1 NO / yes / yes / NO |
| golden_S5_1920x1080.jpg | 72.4 | 7.85 | 0.03 | -42.0 | L1 yes / yes / yes / yes |
| golden_S6_1920x1080.jpg | 84.2 | 3.09 | 0.53 | -51.4 | L1 yes / yes / yes / yes |
| golden_S7_1920x1080.jpg | 54.5 | 16.75 | 1.89 | -33.0 | L5 NO / NO / NO / yes |
| golden_S8_1920x1080.jpg | 77.9 | 2.85 | 1.05 | -36.9 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S1_1920x1080.jpg | 8.8 | 23.7 | 0.580 | - |
| golden_S2_1920x1080.jpg | 18.1 | 10.8 | 0.607 | - |
| golden_S3_1920x1080.jpg | 8.8 | 20.7 | 0.598 | - |
| golden_S4_1920x1080.jpg | 31.4 | 6.0 | 0.458 | - |
| golden_S5_1920x1080.jpg | 5.6 | 37.7 | 0.554 | - |
| golden_S6_1920x1080.jpg | 12.7 | 16.5 | 0.585 | - |
| golden_S7_1920x1080.jpg | 4.8 | 35.0 | 0.493 | - |
| golden_S8_1920x1080.jpg | 12.2 | 16.2 | 0.455 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.91 (>= 6.0) ok | C11 flat8 % 4.46 (<= 40) ok | C12 dBR -3.93 (+-10) ok | C13 far-sky Y -3.48 (-35..-25) FAIL | C13 far>near 90.55 (> 0) ok | C14 far-river Y 37.32 (5..35) FAIL | C15 rms far/near 0.19 (0.25..0.45) FAIL

