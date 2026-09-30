| config | CSV p50 | CSV p95 | in-game p95 | p99 | >18.18 | hitches | GPUTime | GT | RHI | ScreenProbeGather | Unaccounted | ShadowDepths | vs control (largest pass deltas, ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| l48_a | 16.02 | 18.22 | 18.73 | 19.86 | 98 | 0 | 14.15 | 4.35 | 2.87 | 2.88 | 1.23 | 2.11 | lk_a: FT -0.20 GPU -1.09; LumenScreenProbeGather -0.19 |
| l48_b | 16.05 | 18.32 | 18.70 | 19.31 | 111 | 0 | 14.26 | 4.34 | 2.88 | 2.88 | 1.22 | 2.11 | lk_a: FT -0.19 GPU -0.97; LumenScreenProbeGather -0.18 |
| l64_a | 15.98 | 18.23 | 18.91 | 19.67 | 96 | 1 | 15.34 | 4.73 | 3.30 | 2.79 | 1.26 | 2.10 | lk_a: FT -0.22 GPU +0.10; LumenScreenProbeGather -0.28, Unaccounted +0.04 |
| l64_b | 16.02 | 18.14 | 18.69 | 19.51 | 88 | 0 | 15.37 | 4.36 | 2.84 | 2.79 | 1.25 | 2.12 | lk_a: FT -0.23 GPU +0.14; LumenScreenProbeGather -0.28 |
| lf0 | 16.13 | 18.27 | 18.62 | 19.48 | 102 | 0 | 15.50 | 4.31 | 2.84 | 3.04 | 1.27 | 2.11 | lk_a: FT -0.10 GPU +0.27; Lights -0.06, Unaccounted +0.05, RenderDeferredLighting -0.05 |
| lk_a | 16.20 | 18.45 | 18.89 | 19.95 | 133 | 0 | 15.23 | 4.40 | 2.99 | 3.07 | 1.22 | 2.11 |  |
| lk_b | 16.13 | 18.28 | 18.81 | 19.45 | 102 | 0 | 15.52 | 4.36 | 2.86 | 2.98 | 1.25 | 2.10 | lk_a: FT -0.08 GPU +0.29; LumenScreenProbeGather -0.09, Unaccounted +0.03 |
| lwarm | 16.28 | 18.42 | 18.92 | 20.03 | 130 | 0 | 15.66 | 4.35 | 2.86 | 3.07 | 1.25 | 2.11 | lk_a: FT +0.02 GPU +0.43; Unaccounted +0.03 |
| s48 | 15.34 | 17.55 | 17.71 | 18.71 | 38 | 0 | 14.13 | 1.93 | 2.75 | 2.80 | 0.69 | 2.04 | warm: FT -0.19 GPU -0.19; LumenScreenProbeGather -0.19 |
| s64 | 15.23 | 17.41 | 17.49 | 18.40 | 28 | 0 | 13.00 | 1.84 | 2.48 | 2.71 | 1.24 | 2.02 | warm: FT -0.29 GPU -1.32; Unaccounted +0.55, Postprocessing -0.52, LumenScreenProbeGather -0.28, NaniteBasePass +0.22, Basepass -0.22 |
| warm | 15.50 | 17.70 | 17.78 | 18.83 | 37 | 0 | 14.32 | 1.90 | 2.61 | 2.99 | 0.70 | 2.02 |  |
