| config | CSV p50 | CSV p95 | in-game p95 | p99 | >18.18 | hitches | GPUTime | GT | RHI | ScreenProbeGather | Unaccounted | ShadowDepths | vs control (largest pass deltas, ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| life_a | 16.21 | 18.38 | 18.93 | 19.57 | 122 | 0 | 15.27 | 4.33 | 2.91 | 3.07 | 1.24 | 2.10 |  |
| life_b | 16.27 | 18.84 | 19.58 | 31.70 | 179 | 14 | 15.70 | 4.53 | 3.15 | 3.08 | 1.31 | 2.12 | life_a: FT +0.26 GPU +0.43; Unaccounted +0.07 |
| life_c | 16.19 | 18.36 | 18.94 | 20.07 | 116 | 0 | 15.19 | 4.35 | 2.94 | 3.07 | 1.24 | 2.10 | life_a: FT -0.02 GPU -0.08;  |
| lwarm | 16.16 | 18.28 | 18.68 | 19.14 | 98 | 0 | 14.31 | 4.36 | 2.95 | 3.07 | 1.24 | 2.10 | life_a: FT -0.07 GPU -0.96;  |
| r5life | 17.25 | 22.11 | 22.43 | 25.36 | 584 | 4 | 16.93 | 4.31 | 6.72 | 3.07 | 2.44 | 2.08 | ship_a: FT +2.01 GPU +3.04; Unaccounted +1.20, NaniteVisBuffer +0.22, LumenSceneUpdate +0.20, RenderVelocities +0.16, Prepass +0.13, Basepass +0.13, LumenScreenProbeGather +0.08, Lights +0.06, RenderDeferredLighting +0.05, ShadowDepths +0.05, BuildRenderingCommandsDeferred +0.04 |
| r5ship | 15.74 | 17.99 | 18.02 | 18.95 | 68 | 0 | 14.92 | 1.85 | 2.64 | 2.98 | 1.24 | 2.00 | ship_a: FT +0.16 GPU +1.02; LumenSceneUpdate +0.20, NaniteBasePass +0.11, Basepass -0.10, NaniteVisBuffer +0.07, ShadowDepths -0.03 |
| s2 | 14.52 | 15.76 | 15.79 | 16.29 | 0 | 0 | 14.56 | 1.41 | 2.25 | 3.24 | 1.72 | 1.32 | ship_a: FT -1.02 GPU +0.67; ShadowDepths -0.71, Basepass +0.50, Postprocessing -0.49, Unaccounted +0.48, NaniteVisBuffer -0.34, LumenScreenProbeGather +0.25, MotionBlur +0.22, LumenSceneUpdate -0.22, NaniteBasePass -0.14, Lights -0.13, LumenReflections +0.13, VolumetricCloud -0.09, RenderAnisotropyPass -0.05 |
| ship_a | 15.58 | 17.72 | 17.70 | 19.04 | 44 | 0 | 13.90 | 1.85 | 2.47 | 3.00 | 1.24 | 2.03 |  |
| ship_b | 15.49 | 17.62 | 17.68 | 18.77 | 36 | 0 | 14.38 | 1.84 | 2.45 | 2.99 | 1.24 | 2.02 | ship_a: FT -0.10 GPU +0.48;  |
| ship_c | 15.44 | 17.61 | 17.63 | 19.25 | 41 | 0 | 14.17 | 1.85 | 2.47 | 2.94 | 0.69 | 2.02 | ship_a: FT -0.10 GPU +0.27; Unaccounted -0.55, Postprocessing +0.51, LumenScreenProbeGather -0.06 |
| warm | 15.51 | 17.61 | 17.68 | 18.78 | 39 | 0 | 14.95 | 1.84 | 2.43 | 2.95 | 0.69 | 2.03 | ship_a: FT -0.06 GPU +1.05; Unaccounted -0.55, Postprocessing +0.49, LumenScreenProbeGather -0.05 |
