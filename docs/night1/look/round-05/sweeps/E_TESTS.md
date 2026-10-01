# Time-of-day stills: spec numbers

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Stills: `../_scratch/look/r05/E` (1920x1080 output, internal 100 %). Targets: golden L1 mean 61..100, clipped <= 1.8 % (S7: L5 <= 0.7 %), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %, median <= 42; midday overcast L2 83..97, clipped 0.00 %; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.

| variant | as | n | mean | spec_pass | clip_max | BR | S4 points % | S4 median | S4 mean | L13 blobs | C13 far-sky | C12 dBR | C14 far-river | p5 | p95/p5 | sat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| eN0 | night | 3 | 40..43 | 3/3 | 0.77 | +1..+7 | 3.60 | 30.7 | 42.5 | 9 | +46.0 | -18.8 | +62.7 |  |  |  |
| eN5 | night | 3 | 41..43 | 3/3 | 0.70 | +2..+11 | 3.39 | 32.7 | 42.8 | 9 | +8.5 | -2.9 | +21.9 |  |  |  |
| eN6 | night | 3 | 38..40 | 3/3 | 0.77 | +1..+7 | 4.37 | 24.1 | 39.6 | 9 | +62.3 | -19.8 | +65.3 |  |  |  |
| eN7 | night | 3 | 35..40 | 2/3 | 0.77 | +1..+7 | 4.19 | 19.7 | 35.5 | 9 | +63.2 | -19.1 | +62.7 |  |  |  |
| eN8 | night | 3 | 32..42 | 2/3 | 0.66 | +2..+10 | 3.18 | 20.6 | 31.7 | 8 | +6.7 | +1.0 | +9.1 |  |  |  |
| eG0 | golden | 4 | 68..120 | 0/4 | 3.83 | -76..-60 |  |  |  |  | -18.8 | +7.8 | +23.3 | 5.8..35.1 | 5.3..34.2 | 0.52..0.64 |
| eG1 | golden | 4 | 68..120 | 0/4 | 3.52 | -69..-55 |  |  |  |  | -18.6 | +8.1 | +23.4 | 6.1..35.6 | 5.3..32.6 | 0.46..0.60 |
| eG2 | golden | 4 | 68..120 | 1/4 | 3.41 | -65..-51 |  |  |  |  | -18.6 | +9.2 | +23.3 | 6.1..35.3 | 5.3..32.8 | 0.43..0.57 |
| eG3 | golden | 4 | 70..118 | 1/4 | 3.23 | -66..-52 |  |  |  |  | -23.1 | +13.1 | +26.4 | 7.1..33.1 | 5.7..28.1 | 0.45..0.59 |
| eB0 | night | 2 | 53..54 | 0/2 | 0.98 | -29..-25 | 0.35 | 35.6 | 53.3 |  | +12.0 | -8.0 | +39.9 |  |  |  |
| eB1 | night | 2 | 52..54 | 0/2 | 1.02 | -30..-26 | 0.35 | 34.5 | 52.5 |  | +11.8 | -7.1 | +38.2 |  |  |  |
| eB2 | night | 2 | 52..54 | 0/2 | 1.02 | -30..-26 | 0.35 | 34.3 | 52.3 |  | +10.4 | -6.3 | +38.0 |  |  |  |
| eD0 | midday | 2 | 99..100 | 0/2 | 0.00 | -0..+10 |  |  |  |  | -9.6 | -11.8 | +54.2 |  |  |  |
| eD1 | midday | 2 | 100..101 | 0/2 | 0.00 | -4..+4 |  |  |  |  | -13.6 | -22.9 | +63.8 |  |  |  |
| eD2 | midday | 2 | 100..101 | 0/2 | 0.00 | -4..+3 |  |  |  |  | -11.1 | -25.9 | +66.9 |  |  |  |
| eN1 | night | 2 | 42..44 | 2/2 | 0.36 | +8..+8 | 4.10 | 31.9 | 43.5 |  | +15.7 | -7.8 | +34.0 |  |  |  |
| eN2 | night | 2 | 43..44 | 2/2 | 0.30 | +11..+12 | 3.57 | 32.2 | 42.5 |  | -0.8 | -0.2 | +10.0 |  |  |  |
| eN3 | night | 2 | 45..46 | 0/2 | 0.20 | +16..+17 | 3.48 | 35.4 | 45.7 |  | -1.4 | +2.8 | +1.0 |  |  |  |
| eN4 | night | 2 | 44..44 | 2/2 | 0.29 | +12..+13 | 3.61 | 33.6 | 43.8 |  | +0.2 | +0.4 | +9.8 |  |  |  |
| eO0 | midday | 2 | 84..88 | 2/2 | 0.00 | -9..-8 |  |  |  |  | -6.3 | +0.0 | +16.1 |  |  |  |
| eO1 | midday | 2 | 85..89 | 2/2 | 0.00 | -9..-8 |  |  |  |  | -3.0 | -1.1 | +24.0 |  |  |  |
| eO2 | midday | 2 | 85..89 | 2/2 | 0.00 | -9..-8 |  |  |  |  | -6.2 | -1.5 | +32.6 |  |  |  |
| eO3 | midday | 2 | 85..89 | 2/2 | 0.00 | -9..-8 |  |  |  |  | -5.7 | -0.8 | +20.7 |  |  |  |

### eN0 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 39.6 | 0.00 | 0.77 | +1.0 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 42.5 | 0.00 | 0.15 | +6.6 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 41.5 | 0.00 | 0.36 | +4.7 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 41.23 (>= 6.0) ok | C11 flat8 % 0.0 (<= 40) ok | C12 dBR -18.75 (+-10) FAIL | C13 far-sky Y 46.04 (-35..-25) FAIL | C13 far>near 57.39 (> 0) ok | C14 far-river Y 62.66 (5..35) FAIL | C15 rms far/near 0.71 (0.25..0.45) FAIL

### eN5 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 40.8 | 0.00 | 0.70 | +1.9 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 42.8 | 0.00 | 0.18 | +11.4 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 43.3 | 0.00 | 0.34 | +9.5 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 18.87 (>= 6.0) ok | C11 flat8 % 18.21 (<= 40) ok | C12 dBR -2.93 (+-10) ok | C13 far-sky Y 8.51 (-35..-25) FAIL | C13 far>near 13.27 (> 0) ok | C14 far-river Y 21.89 (5..35) ok | C15 rms far/near 0.84 (0.25..0.45) FAIL

### eN6 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 39.7 | 0.00 | 0.77 | +0.8 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 39.6 | 0.00 | 0.22 | +7.0 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 37.8 | 0.00 | 0.29 | +6.4 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 77.76 (>= 6.0) ok | C11 flat8 % 3.04 (<= 40) ok | C12 dBR -19.81 (+-10) FAIL | C13 far-sky Y 62.32 (-35..-25) FAIL | C13 far>near 59.01 (> 0) ok | C14 far-river Y 65.26 (5..35) FAIL | C15 rms far/near 0.65 (0.25..0.45) FAIL

### eN7 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 39.6 | 0.00 | 0.77 | +0.8 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 35.5 | 0.00 | 0.22 | +7.2 | L3 NO / yes / yes / yes |
| night_S8_1920x1080.jpg | 40.3 | 0.00 | 0.72 | +6.0 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 127.29 (>= 6.0) ok | C11 flat8 % 8.75 (<= 40) ok | C12 dBR -19.09 (+-10) FAIL | C13 far-sky Y 63.21 (-35..-25) FAIL | C13 far>near 59.08 (> 0) ok | C14 far-river Y 62.71 (5..35) FAIL | C15 rms far/near 0.57 (0.25..0.45) FAIL

### eN8 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S1_1920x1080.jpg | 41.7 | 0.00 | 0.66 | +2.4 | L3 yes / yes / yes / yes |
| night_S4_1920x1080.jpg | 31.7 | 0.00 | 0.17 | +10.3 | L3 NO / yes / yes / yes |
| night_S8_1920x1080.jpg | 41.5 | 0.00 | 0.52 | +9.5 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 23.71 (>= 6.0) ok | C11 flat8 % 33.04 (<= 40) ok | C12 dBR 0.98 (+-10) ok | C13 far-sky Y 6.7 (-35..-25) FAIL | C13 far>near 3.66 (> 0) ok | C14 far-river Y 9.13 (5..35) ok | C15 rms far/near 0.47 (0.25..0.45) FAIL

### eG0 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S2_1920x1080.jpg | 91.6 | 3.67 | 0.83 | -75.8 | L1 yes / yes / yes / NO |
| golden_S4_1920x1080.jpg | 119.7 | 0.23 | 0.05 | -74.9 | L1 NO / yes / yes / NO |
| golden_S7_1920x1080.jpg | 68.1 | 12.53 | 3.83 | -59.6 | L5 yes / NO / NO / NO |
| golden_S8_1920x1080.jpg | 83.2 | 4.63 | 0.95 | -61.6 | L1 yes / yes / yes / NO |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S2_1920x1080.jpg | 14.3 | 14.0 | 0.638 | - |
| golden_S4_1920x1080.jpg | 35.1 | 5.3 | 0.516 | - |
| golden_S7_1920x1080.jpg | 5.8 | 34.2 | 0.638 | - |
| golden_S8_1920x1080.jpg | 10.6 | 18.2 | 0.591 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.22 (>= 6.0) ok | C11 flat8 % 9.64 (<= 40) ok | C12 dBR 7.78 (+-10) ok | C13 far-sky Y -18.78 (-35..-25) FAIL | C13 far>near 93.94 (> 0) ok | C14 far-river Y 23.33 (5..35) ok | C15 rms far/near 0.18 (0.25..0.45) FAIL

### eG1 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S2_1920x1080.jpg | 90.7 | 3.85 | 0.67 | -68.6 | L1 yes / yes / yes / NO |
| golden_S4_1920x1080.jpg | 120.2 | 0.22 | 0.04 | -66.0 | L1 NO / yes / yes / NO |
| golden_S7_1920x1080.jpg | 68.2 | 11.97 | 3.52 | -55.2 | L5 yes / NO / NO / NO |
| golden_S8_1920x1080.jpg | 82.9 | 4.69 | 0.80 | -55.2 | L1 yes / yes / yes / NO |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S2_1920x1080.jpg | 13.9 | 14.4 | 0.597 | - |
| golden_S4_1920x1080.jpg | 35.6 | 5.3 | 0.464 | - |
| golden_S7_1920x1080.jpg | 6.1 | 32.6 | 0.603 | - |
| golden_S8_1920x1080.jpg | 10.6 | 18.4 | 0.545 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.29 (>= 6.0) ok | C11 flat8 % 8.93 (<= 40) ok | C12 dBR 8.13 (+-10) ok | C13 far-sky Y -18.57 (-35..-25) FAIL | C13 far>near 93.05 (> 0) ok | C14 far-river Y 23.44 (5..35) ok | C15 rms far/near 0.18 (0.25..0.45) FAIL

### eG2 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S2_1920x1080.jpg | 91.4 | 3.92 | 0.61 | -64.7 | L1 yes / yes / yes / NO |
| golden_S4_1920x1080.jpg | 120.3 | 0.23 | 0.03 | -60.4 | L1 NO / yes / yes / NO |
| golden_S7_1920x1080.jpg | 68.0 | 12.29 | 3.41 | -51.2 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 82.9 | 4.76 | 0.74 | -50.7 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S2_1920x1080.jpg | 14.0 | 14.4 | 0.570 | - |
| golden_S4_1920x1080.jpg | 35.3 | 5.3 | 0.431 | - |
| golden_S7_1920x1080.jpg | 6.1 | 32.8 | 0.565 | - |
| golden_S8_1920x1080.jpg | 10.5 | 18.4 | 0.513 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.39 (>= 6.0) ok | C11 flat8 % 9.46 (<= 40) ok | C12 dBR 9.25 (+-10) ok | C13 far-sky Y -18.57 (-35..-25) FAIL | C13 far>near 93.05 (> 0) ok | C14 far-river Y 23.26 (5..35) ok | C15 rms far/near 0.18 (0.25..0.45) FAIL

### eG3 (measured as golden)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| golden_S2_1920x1080.jpg | 88.8 | 4.10 | 0.88 | -65.8 | L1 yes / yes / yes / NO |
| golden_S4_1920x1080.jpg | 118.2 | 0.27 | 0.04 | -62.1 | L1 NO / yes / yes / NO |
| golden_S7_1920x1080.jpg | 70.4 | 9.66 | 3.23 | -52.7 | L5 yes / NO / NO / yes |
| golden_S8_1920x1080.jpg | 80.9 | 5.62 | 0.83 | -51.6 | L1 yes / yes / yes / yes |

| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |
|---|---|---|---|---|
| golden_S2_1920x1080.jpg | 13.5 | 14.9 | 0.588 | - |
| golden_S4_1920x1080.jpg | 33.1 | 5.7 | 0.449 | - |
| golden_S7_1920x1080.jpg | 7.1 | 28.1 | 0.575 | - |
| golden_S8_1920x1080.jpg | 9.6 | 20.2 | 0.527 | - |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 6.95 (>= 6.0) ok | C11 flat8 % 6.07 (<= 40) ok | C12 dBR 13.06 (+-10) FAIL | C13 far-sky Y -23.05 (-35..-25) FAIL | C13 far>near 92.78 (> 0) ok | C14 far-river Y 26.35 (5..35) ok | C15 rms far/near 0.2 (0.25..0.45) FAIL

### eB0 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 53.3 | 0.33 | 0.34 | -28.6 | L3 yes / yes / yes / NO |
| night_S8_1920x1080.jpg | 54.3 | 0.16 | 0.98 | -24.9 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 14.63 (>= 6.0) ok | C11 flat8 % 0.18 (<= 40) ok | C12 dBR -7.98 (+-10) ok | C13 far-sky Y 11.97 (-35..-25) FAIL | C13 far>near 27.67 (> 0) ok | C14 far-river Y 39.87 (5..35) FAIL | C15 rms far/near 0.55 (0.25..0.45) FAIL

### eB1 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 52.5 | 0.24 | 0.36 | -29.5 | L3 yes / yes / yes / NO |
| night_S8_1920x1080.jpg | 53.7 | 0.18 | 1.02 | -25.6 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 14.01 (>= 6.0) ok | C11 flat8 % 0.18 (<= 40) ok | C12 dBR -7.1 (+-10) ok | C13 far-sky Y 11.76 (-35..-25) FAIL | C13 far>near 26.04 (> 0) ok | C14 far-river Y 38.25 (5..35) FAIL | C15 rms far/near 0.54 (0.25..0.45) FAIL

### eB2 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 52.3 | 0.27 | 0.36 | -29.6 | L3 yes / yes / yes / NO |
| night_S8_1920x1080.jpg | 53.6 | 0.19 | 1.02 | -25.7 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 13.27 (>= 6.0) ok | C11 flat8 % 0.36 (<= 40) ok | C12 dBR -6.28 (+-10) ok | C13 far-sky Y 10.43 (-35..-25) FAIL | C13 far>near 25.59 (> 0) ok | C14 far-river Y 37.98 (5..35) FAIL | C15 rms far/near 0.54 (0.25..0.45) FAIL

### eD0 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 98.7 | 0.00 | 0.00 | +9.8 | L2 NO / yes / yes / NO |
| midday_S8_1920x1080.jpg | 100.0 | 0.00 | 0.00 | -0.3 | L2 NO / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.05 (>= 6.0) ok | C11 flat8 % 3.75 (<= 40) ok | C12 dBR -11.79 (+-10) FAIL | C13 far-sky Y -9.56 (-35..-25) FAIL | C13 far>near 61.28 (> 0) ok | C14 far-river Y 54.24 (5..35) FAIL | C15 rms far/near 0.32 (0.25..0.45) ok

### eD1 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 100.0 | 0.00 | 0.00 | +4.4 | L2 NO / yes / yes / yes |
| midday_S8_1920x1080.jpg | 100.5 | 0.00 | 0.00 | -3.9 | L2 NO / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.04 (>= 6.0) ok | C11 flat8 % 3.04 (<= 40) ok | C12 dBR -22.85 (+-10) FAIL | C13 far-sky Y -13.61 (-35..-25) FAIL | C13 far>near 61.25 (> 0) ok | C14 far-river Y 63.83 (5..35) FAIL | C15 rms far/near 0.36 (0.25..0.45) ok

### eD2 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 100.3 | 0.00 | 0.00 | +3.5 | L2 NO / yes / yes / yes |
| midday_S8_1920x1080.jpg | 100.6 | 0.00 | 0.00 | -4.2 | L2 NO / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.52 (>= 6.0) ok | C11 flat8 % 2.86 (<= 40) ok | C12 dBR -25.94 (+-10) FAIL | C13 far-sky Y -11.14 (-35..-25) FAIL | C13 far>near 62.87 (> 0) ok | C14 far-river Y 66.89 (5..35) FAIL | C15 rms far/near 0.37 (0.25..0.45) ok

### eN1 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 43.5 | 0.00 | 0.21 | +8.1 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 42.4 | 0.00 | 0.36 | +7.8 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 25.35 (>= 6.0) ok | C11 flat8 % 10.71 (<= 40) ok | C12 dBR -7.79 (+-10) ok | C13 far-sky Y 15.7 (-35..-25) FAIL | C13 far>near 24.14 (> 0) ok | C14 far-river Y 33.99 (5..35) ok | C15 rms far/near 0.81 (0.25..0.45) FAIL

### eN2 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 42.5 | 0.00 | 0.18 | +11.8 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 43.9 | 0.00 | 0.30 | +11.5 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.59 (>= 6.0) ok | C11 flat8 % 30.54 (<= 40) ok | C12 dBR -0.22 (+-10) ok | C13 far-sky Y -0.75 (-35..-25) FAIL | C13 far>near 0.14 (> 0) ok | C14 far-river Y 10.02 (5..35) ok | C15 rms far/near 0.58 (0.25..0.45) FAIL

### eN3 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 45.7 | 0.00 | 0.14 | +16.7 | L3 yes / yes / yes / NO |
| night_S8_1920x1080.jpg | 44.7 | 0.00 | 0.20 | +16.3 | L3 yes / yes / yes / NO |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 2.92 (>= 6.0) FAIL | C11 flat8 % 77.14 (<= 40) FAIL | C12 dBR 2.75 (+-10) ok | C13 far-sky Y -1.39 (-35..-25) FAIL | C13 far>near -3.86 (> 0) FAIL | C14 far-river Y 1.03 (5..35) FAIL | C15 rms far/near 0.19 (0.25..0.45) FAIL

### eN4 (measured as night)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| night_S4_1920x1080.jpg | 43.8 | 0.00 | 0.18 | +12.8 | L3 yes / yes / yes / yes |
| night_S8_1920x1080.jpg | 44.0 | 0.00 | 0.29 | +12.1 | L3 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 9.92 (>= 6.0) ok | C11 flat8 % 29.64 (<= 40) ok | C12 dBR 0.39 (+-10) ok | C13 far-sky Y 0.16 (-35..-25) FAIL | C13 far>near 0.51 (> 0) ok | C14 far-river Y 9.83 (5..35) ok | C15 rms far/near 0.57 (0.25..0.45) FAIL

### eO0 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 84.1 | 0.00 | 0.00 | -8.7 | L2 yes / yes / yes / yes |
| midday_S8_1920x1080.jpg | 88.2 | 0.00 | 0.00 | -7.7 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 2.29 (>= 6.0) FAIL | C11 flat8 % 37.5 (<= 40) ok | C12 dBR 0.02 (+-10) ok | C13 far-sky Y -6.35 (-35..-25) FAIL | C13 far>near 69.57 (> 0) ok | C14 far-river Y 16.12 (5..35) ok | C15 rms far/near 0.23 (0.25..0.45) FAIL

### eO1 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 84.7 | 0.00 | 0.00 | -9.1 | L2 yes / yes / yes / yes |
| midday_S8_1920x1080.jpg | 89.1 | 0.00 | 0.00 | -7.7 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 3.42 (>= 6.0) FAIL | C11 flat8 % 13.57 (<= 40) ok | C12 dBR -1.09 (+-10) ok | C13 far-sky Y -3.03 (-35..-25) FAIL | C13 far>near 76.53 (> 0) ok | C14 far-river Y 23.96 (5..35) ok | C15 rms far/near 0.24 (0.25..0.45) FAIL

### eO2 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 85.2 | 0.00 | 0.00 | -9.4 | L2 yes / yes / yes / yes |
| midday_S8_1920x1080.jpg | 89.5 | 0.00 | 0.00 | -7.7 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 4.54 (>= 6.0) FAIL | C11 flat8 % 7.86 (<= 40) ok | C12 dBR -1.51 (+-10) ok | C13 far-sky Y -6.22 (-35..-25) FAIL | C13 far>near 77.07 (> 0) ok | C14 far-river Y 32.63 (5..35) ok | C15 rms far/near 0.27 (0.25..0.45) ok

### eO3 (measured as midday)

| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |
|---|---|---|---|---|---|
| midday_S4_1920x1080.jpg | 85.4 | 0.00 | 0.00 | -9.1 | L2 yes / yes / yes / yes |
| midday_S8_1920x1080.jpg | 89.4 | 0.00 | 0.00 | -7.8 | L2 yes / yes / yes / yes |

S4 far band (s4_far_check.py, current spec_regions.json): C11 lap/sky 2.74 (>= 6.0) FAIL | C11 flat8 % 22.68 (<= 40) ok | C12 dBR -0.75 (+-10) ok | C13 far-sky Y -5.67 (-35..-25) FAIL | C13 far>near 78.24 (> 0) ok | C14 far-river Y 20.66 (5..35) ok | C15 rms far/near 0.24 (0.25..0.45) FAIL

