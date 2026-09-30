| config | CSV p50 | CSV p95 | in-game p95 | p99 | >18.18 | hitches | GPUTime | GT | RHI | ScreenProbeGather | Unaccounted | ShadowDepths | vs control (largest pass deltas, ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k_a | 15.59 | 17.81 | 17.86 | 18.82 | 45 | 0 | 14.31 | 1.87 | 2.67 | 2.99 | 0.69 | 2.02 | warm: FT -0.00 GPU -0.17; Unaccounted -0.53, Postprocessing +0.50 |
| k_b | 15.50 | 17.48 | 17.57 | 18.60 | 36 | 0 | 14.06 | 1.88 | 2.67 | 2.99 | 1.25 | 2.02 | warm: FT -0.14 GPU -0.43; NaniteVisBuffer +0.05, LumenSceneUpdate -0.04 |
| ku_a | 15.56 | 17.83 | 17.85 | 19.08 | 62 | 0 | 14.21 | 1.86 | 2.58 | 2.96 | 0.69 | 2.02 | warm: FT -0.02 GPU -0.27; Unaccounted -0.53, Postprocessing +0.50 |
| ku_b | 15.53 | 17.69 | 17.74 | 18.88 | 51 | 0 | 13.88 | 1.85 | 2.69 | 2.97 | 1.25 | 2.03 | warm: FT -0.08 GPU -0.60; NaniteVisBuffer +0.03, Unaccounted +0.03 |
| lk_a | 16.26 | 18.48 | 18.90 | 19.87 | 130 | 2 | 15.22 | 4.46 | 2.99 | 3.08 | 1.23 | 2.12 |  |
| lk_b | 16.25 | 18.49 | 18.96 | 19.69 | 140 | 0 | 15.74 | 4.40 | 3.02 | 3.08 | 1.21 | 2.11 | lk_a: FT -0.03 GPU +0.52; LumenSceneUpdate +0.04 |
| lk_c | 16.14 | 18.22 | 18.68 | 19.39 | 96 | 1 | 15.21 | 4.34 | 2.92 | 3.06 | 1.23 | 2.10 | lk_a: FT -0.15 GPU -0.01;  |
| lkd75 | 16.22 | 18.50 | 19.09 | 19.39 | 139 | 1 | 15.32 | 4.65 | 3.17 | 3.08 | 1.26 | 2.09 | lk_a: FT -0.02 GPU +0.10; NaniteVisBuffer +0.05, Unaccounted +0.04, ShadowDepths -0.03 |
| lku_a | 16.25 | 18.48 | 18.95 | 19.61 | 143 | 0 | 15.68 | 4.38 | 2.96 | 3.08 | 1.21 | 2.11 | lk_a: FT -0.04 GPU +0.46; LumenSceneUpdate +0.03 |
| lku_b | 16.20 | 18.52 | 18.90 | 19.84 | 133 | 0 | 15.46 | 4.41 | 3.00 | 3.04 | 1.21 | 2.10 | lk_a: FT -0.07 GPU +0.24; LumenScreenProbeGather -0.04 |
| lku_c | 16.22 | 18.28 | 18.86 | 19.33 | 105 | 0 | 13.07 | 4.38 | 3.06 | 3.08 | 0.68 | 2.11 | lk_a: FT -0.13 GPU -2.15; Unaccounted -0.54, Postprocessing +0.50, NaniteVisBuffer +0.04 |
| lwarm | 16.11 | 18.34 | 18.69 | 19.56 | 114 | 0 | 15.74 | 4.36 | 2.95 | 3.04 | 1.23 | 2.11 | lk_a: FT -0.15 GPU +0.52; NaniteVisBuffer +0.04, LumenScreenProbeGather -0.04 |
| warm | 15.58 | 17.79 | 17.77 | 18.97 | 53 | 0 | 14.48 | 1.90 | 2.66 | 2.99 | 1.22 | 2.03 |  |
