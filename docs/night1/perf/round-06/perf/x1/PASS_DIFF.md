| config | CSV p50 | CSV p95 | in-game p95 | p99 | >18.18 | hitches | GPUTime | GT | RHI | ScreenProbeGather | Unaccounted | ShadowDepths | vs control (largest pass deltas, ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| life | 17.12 | 19.47 | 19.93 | 20.61 | 435 | 0 | 16.58 | 4.33 | 5.09 | 3.01 | 2.31 | 2.11 |  |
| lnocrowd | 15.87 | 17.97 | 18.08 | 19.25 | 71 | 0 | 13.47 | 2.24 | 2.88 | 2.98 | 1.54 | 2.04 | life: FT -1.21 GPU -3.11; Unaccounted -0.77, RenderVelocities -0.14, Prepass -0.13, Basepass -0.11, NaniteVisBuffer -0.11, ShadowDepths -0.07, Lights -0.05, RenderDeferredLighting -0.05, BuildRenderingCommandsDeferred -0.04 |
| lnoshad | 17.04 | 19.38 | 19.82 | 20.31 | 394 | 0 | 16.77 | 4.32 | 5.30 | 3.07 | 2.31 | 2.01 | life: FT -0.11 GPU +0.18; ShadowDepths -0.10, LumenScreenProbeGather +0.06 |
| lnotraf | 17.05 | 19.50 | 19.83 | 20.47 | 396 | 0 | 16.33 | 3.91 | 5.66 | 3.00 | 2.28 | 2.10 | life: FT -0.08 GPU -0.25; Basepass -0.05, NaniteBasePass +0.04 |
| lsk0 | 16.08 | 18.23 | 18.65 | 19.35 | 96 | 1 | 15.51 | 4.37 | 2.90 | 3.02 | 1.25 | 2.11 | life: FT -0.98 GPU -1.07; Unaccounted -1.05, LumenSceneUpdate -0.21, Prepass -0.13, NaniteVisBuffer -0.08, RenderVelocities -0.05, BuildRenderingCommandsDeferred -0.04, NaniteBasePass +0.03 |
| lspgb | 17.18 | 19.63 | 20.03 | 20.49 | 462 | 0 | 16.98 | 4.35 | 5.23 | 3.08 | 2.29 | 2.11 | life: FT +0.06 GPU +0.39; LumenScreenProbeGather +0.07 |
| lwarm | 17.17 | 20.39 | 20.81 | 21.89 | 514 | 0 | 16.55 | 4.34 | 8.10 | 3.07 | 2.34 | 2.09 | life: FT +0.15 GPU -0.04; LumenScreenProbeGather +0.06, Unaccounted +0.03 |
| ship | 15.96 | 18.40 | 18.56 | 19.93 | 119 | 0 | 15.57 | 2.07 | 3.27 | 3.00 | 1.27 | 2.06 | warm: FT +0.28 GPU +2.93; LumenScreenProbeGather +0.05, ShadowDepths +0.04 |
| spga | 15.70 | 17.86 | 17.86 | 18.86 | 51 | 0 | 14.06 | 1.87 | 2.68 | 2.95 | 1.25 | 2.02 | warm: FT +0.01 GPU +1.42; NaniteVisBuffer -0.03 |
| spgb | 15.72 | 17.80 | 17.81 | 18.79 | 48 | 0 | 15.09 | 1.85 | 2.67 | 2.95 | 0.69 | 2.01 | warm: FT -0.05 GPU +2.45; Unaccounted -0.56, Postprocessing +0.50 |
| spgc | 16.02 | 18.15 | 18.23 | 19.24 | 87 | 0 | 15.30 | 1.86 | 2.67 | 3.25 | 0.69 | 2.01 | warm: FT +0.29 GPU +2.66; Unaccounted -0.56, Postprocessing +0.51, LumenScreenProbeGather +0.30, NaniteVisBuffer -0.03 |
| warm | 15.72 | 17.91 | 17.99 | 18.99 | 58 | 0 | 12.64 | 1.86 | 2.79 | 2.95 | 1.25 | 2.02 |  |
