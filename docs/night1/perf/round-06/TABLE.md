# F perf round 06: perf tables (3840x2160 output, internal 1920x1080, exclusive gpu_slot perf sessions; official = f1)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

## perf/f1 (perf_route TABLE)

| config | SP | internal | avg ms (fps) | p50 ms (fps) | p95 ms (fps) | p99 | hitches | GPU ms | RT ms | GT ms | RHI ms | draw calls | cvars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| warm | ini | 1920x1080 | 15.56 (64.3) | 15.51 (64.5) | 17.61 (56.8) | 18.78 | 0 | 14.95 | 15.55 | 1.84 | 2.43 | 0 | - |
| ship_a | ini | 1920x1080 | 15.62 (64.0) | 15.58 (64.2) | 17.72 (56.4) | 19.04 | 0 | 13.90 | 15.61 | 1.85 | 2.47 | 0 | - |
| lwarm | ini | 1920x1080 | 16.15 (61.9) | 16.16 (61.9) | 18.28 (54.7) | 19.14 | 0 | 14.31 | 16.14 | 4.36 | 2.95 | 0 | - |
| life_a | ini | 1920x1080 | 16.22 (61.6) | 16.21 (61.7) | 18.38 (54.4) | 19.57 | 0 | 15.27 | 16.21 | 4.33 | 2.91 | 0 | - |
| ship_b | ini | 1920x1080 | 15.52 (64.4) | 15.49 (64.6) | 17.62 (56.8) | 18.77 | 0 | 14.38 | 15.52 | 1.84 | 2.45 | 0 | - |
| life_b | ini | 1920x1080 | 16.48 (60.7) | 16.27 (61.5) | 18.84 (53.1) | 31.70 | 14 | 15.70 | 16.47 | 4.53 | 3.15 | 0 | - |
| ship_c | ini | 1920x1080 | 15.51 (64.5) | 15.44 (64.8) | 17.61 (56.8) | 19.25 | 0 | 14.17 | 15.51 | 1.85 | 2.47 | 0 | - |
| life_c | ini | 1920x1080 | 16.20 (61.7) | 16.19 (61.8) | 18.36 (54.5) | 20.07 | 0 | 15.19 | 16.20 | 4.35 | 2.94 | 0 | - |
| r5life | ini | 1920x1080 | 17.63 (56.7) | 17.25 (58.0) | 22.11 (45.2) | 25.36 | 4 | 16.93 | 17.62 | 4.31 | 6.72 | 0 | r.SkinCache.Mode=1 |
| r5ship | ini | 1920x1080 | 15.78 (63.4) | 15.74 (63.5) | 17.99 (55.6) | 18.95 | 0 | 14.92 | 15.78 | 1.85 | 2.64 | 0 | r.SkinCache.Mode=1 |
| s2 | ini | 1920x1080 | 14.60 (68.5) | 14.52 (68.8) | 15.76 (63.5) | 16.29 | 0 | 14.56 | 14.59 | 1.41 | 2.25 | 0 | - |

## perf/f1 (pass_diff: CSV p95, in-game p95, threads, passes, deltas vs control)

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

## perf/x1 (perf_route TABLE)

| config | SP | internal | avg ms (fps) | p50 ms (fps) | p95 ms (fps) | p99 | hitches | GPU ms | RT ms | GT ms | RHI ms | draw calls | cvars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| warm | ini | 1920x1080 | 15.76 (63.5) | 15.72 (63.6) | 17.91 (55.8) | 18.99 | 0 | 12.64 | 15.75 | 1.86 | 2.79 | 0 | - |
| ship | ini | 1920x1080 | 16.03 (62.4) | 15.96 (62.7) | 18.40 (54.4) | 19.93 | 0 | 15.57 | 16.03 | 2.07 | 3.27 | 0 | - |
| spga | ini | 1920x1080 | 15.77 (63.4) | 15.70 (63.7) | 17.86 (56.0) | 18.86 | 0 | 14.06 | 15.76 | 1.87 | 2.68 | 0 | r.Lumen.ScreenProbeGather.DownsampleFactor=32 r.Lumen.ScreenProbeGather.NumAdaptiveProbes=16 |
| spgb | ini | 1920x1080 | 15.71 (63.7) | 15.72 (63.6) | 17.80 (56.2) | 18.79 | 0 | 15.09 | 15.71 | 1.85 | 2.67 | 0 | r.Lumen.ScreenProbeGather.DownsampleFactor=32 r.Lumen.ScreenProbeGather.NumAdaptiveProbes=16 r.Lumen.ScreenProbeGather.IrradianceFormat=1 r.Lumen.ScreenProbeGather.StochasticInterpolation=1 r.Lumen.ScreenProbeGather.ShortRangeAO.DownsampleFactor=2 |
| spgc | ini | 1920x1080 | 16.05 (62.3) | 16.02 (62.4) | 18.15 (55.1) | 19.24 | 0 | 15.30 | 16.04 | 1.86 | 2.67 | 0 | r.Lumen.ScreenProbeGather.DownsampleFactor=24 |
| lwarm | ini | 1920x1080 | 17.24 (58.0) | 17.17 (58.2) | 20.39 (49.0) | 21.89 | 0 | 16.55 | 17.23 | 4.34 | 8.10 | 0 | - |
| life | ini | 1920x1080 | 17.09 (58.5) | 17.12 (58.4) | 19.47 (51.4) | 20.61 | 0 | 16.58 | 17.08 | 4.33 | 5.09 | 0 | - |
| lspgb | ini | 1920x1080 | 17.15 (58.3) | 17.18 (58.2) | 19.63 (50.9) | 20.49 | 0 | 16.98 | 17.15 | 4.35 | 5.23 | 0 | r.Lumen.ScreenProbeGather.DownsampleFactor=32 r.Lumen.ScreenProbeGather.NumAdaptiveProbes=16 r.Lumen.ScreenProbeGather.IrradianceFormat=1 r.Lumen.ScreenProbeGather.StochasticInterpolation=1 r.Lumen.ScreenProbeGather.ShortRangeAO.DownsampleFactor=2 |
| lnocrowd | ini | 1920x1080 | 15.88 (63.0) | 15.87 (63.0) | 17.97 (55.7) | 19.25 | 0 | 13.47 | 15.88 | 2.24 | 2.88 | 0 | - |
| lnotraf | ini | 1920x1080 | 17.01 (58.8) | 17.05 (58.7) | 19.50 (51.3) | 20.47 | 0 | 16.33 | 17.00 | 3.91 | 5.66 | 0 | - |
| lnoshad | ini | 1920x1080 | 16.98 (58.9) | 17.04 (58.7) | 19.38 (51.6) | 20.31 | 0 | 16.77 | 16.98 | 4.32 | 5.30 | 0 | - |
| lsk0 | ini | 1920x1080 | 16.11 (62.1) | 16.08 (62.2) | 18.23 (54.8) | 19.35 | 1 | 15.51 | 16.10 | 4.37 | 2.90 | 0 | r.SkinCache.Mode=0 |

## perf/x1 (pass_diff: CSV p95, in-game p95, threads, passes, deltas vs control)

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

## perf/y1 (perf_route TABLE)

| config | SP | internal | avg ms (fps) | p50 ms (fps) | p95 ms (fps) | p99 | hitches | GPU ms | RT ms | GT ms | RHI ms | draw calls | cvars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| warm | ini | 1920x1080 | 15.48 (64.6) | 15.48 (64.6) | 17.57 (56.9) | 18.46 | 0 | 13.80 | 15.47 | 1.84 | 2.46 | 0 | r.SkinCache.Mode=0 |
| k0 | ini | 1920x1080 | 15.67 (63.8) | 15.49 (64.6) | 17.99 (55.6) | 24.91 | 10 | 13.98 | 15.67 | 1.93 | 2.73 | 0 | r.SkinCache.Mode=0 |
| ktv0 | ini | 1920x1080 | 15.33 (65.3) | 15.31 (65.3) | 17.38 (57.5) | 18.44 | 0 | 14.68 | 15.32 | 1.84 | 2.48 | 0 | r.SkinCache.Mode=0 r.Lumen.TranslucencyVolume.Enable=0 |
| krc | ini | 1920x1080 | 15.50 (64.5) | 15.45 (64.7) | 17.57 (56.9) | 18.60 | 0 | 13.88 | 15.50 | 1.86 | 2.45 | 0 | r.SkinCache.Mode=0 r.Lumen.ScreenProbeGather.RadianceCache.ProbeResolution=16 r.Lumen.ScreenProbeGather.RadianceCache.NumProbesToTraceBudget=100 |
| koct4 | ini | 1920x1080 | 15.18 (65.9) | 15.21 (65.7) | 17.35 (57.6) | 18.10 | 0 | 13.57 | 15.18 | 1.84 | 2.45 | 0 | r.SkinCache.Mode=0 r.Lumen.ScreenProbeGather.TracingOctahedronResolution=4 |
| ksrao0 | ini | 1920x1080 | 15.40 (64.9) | 15.34 (65.2) | 17.42 (57.4) | 18.69 | 0 | 14.82 | 15.39 | 1.85 | 2.48 | 0 | r.SkinCache.Mode=0 r.Lumen.ScreenProbeGather.ShortRangeAO=0 |
| lwarm | ini | 1920x1080 | 16.21 (61.7) | 16.24 (61.6) | 18.26 (54.8) | 19.11 | 0 | 15.38 | 16.20 | 4.38 | 2.85 | 0 | r.SkinCache.Mode=0 |
| lk0 | ini | 1920x1080 | 16.19 (61.8) | 16.20 (61.7) | 18.31 (54.6) | 19.11 | 0 | 15.59 | 16.18 | 4.34 | 2.83 | 0 | r.SkinCache.Mode=0 |
| lktv0 | ini | 1920x1080 | 16.01 (62.5) | 16.01 (62.4) | 18.17 (55.0) | 19.06 | 0 | 14.58 | 16.00 | 4.37 | 2.89 | 0 | r.SkinCache.Mode=0 r.Lumen.TranslucencyVolume.Enable=0 |
| lkrc | ini | 1920x1080 | 16.18 (61.8) | 16.20 (61.7) | 18.34 (54.5) | 19.40 | 0 | 15.29 | 16.17 | 4.36 | 2.87 | 0 | r.SkinCache.Mode=0 r.Lumen.ScreenProbeGather.RadianceCache.ProbeResolution=16 r.Lumen.ScreenProbeGather.RadianceCache.NumProbesToTraceBudget=100 |
| lksh30 | ini | 1920x1080 | 16.18 (61.8) | 16.15 (61.9) | 18.36 (54.5) | 19.50 | 0 | 14.88 | 16.17 | 4.33 | 2.85 | 0 | r.SkinCache.Mode=0 |
| lkm15 | ini | 1920x1080 | 16.21 (61.7) | 16.22 (61.6) | 18.32 (54.6) | 19.40 | 0 | 14.57 | 16.21 | 4.29 | 2.84 | 0 | r.SkinCache.Mode=0 |

## perf/y1 (pass_diff: CSV p95, in-game p95, threads, passes, deltas vs control)

| config | CSV p50 | CSV p95 | in-game p95 | p99 | >18.18 | hitches | GPUTime | GT | RHI | ScreenProbeGather | Unaccounted | ShadowDepths | vs control (largest pass deltas, ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k0 | 15.49 | 17.99 | 18.18 | 24.91 | 77 | 10 | 13.98 | 1.93 | 2.73 | 2.95 | 1.30 | 2.02 | warm: FT +0.20 GPU +0.19; Unaccounted +0.06 |
| koct4 | 15.21 | 17.35 | 17.34 | 18.10 | 18 | 0 | 13.57 | 1.84 | 2.45 | 2.69 | 1.23 | 2.02 | warm: FT -0.29 GPU -0.23; LumenScreenProbeGather -0.27 |
| krc | 15.45 | 17.57 | 17.69 | 18.60 | 35 | 0 | 13.88 | 1.86 | 2.45 | 2.98 | 1.25 | 2.03 | warm: FT +0.02 GPU +0.09;  |
| ksrao0 | 15.34 | 17.42 | 17.57 | 18.69 | 35 | 0 | 14.82 | 1.85 | 2.48 | 2.89 | 1.27 | 2.02 | warm: FT -0.08 GPU +1.02; LumenScreenProbeGather -0.07, LumenReflections -0.04, Unaccounted +0.03 |
| ktv0 | 15.31 | 17.38 | 17.46 | 18.44 | 26 | 0 | 14.68 | 1.84 | 2.48 | 3.03 | 0.69 | 2.02 | warm: FT -0.15 GPU +0.89; Unaccounted -0.55, Postprocessing +0.51, LumenReflections -0.23, LumenScreenProbeGather +0.06 |
| lk0 | 16.20 | 18.31 | 18.77 | 19.11 | 109 | 0 | 15.59 | 4.34 | 2.83 | 3.07 | 1.23 | 2.12 |  |
| lkm15 | 16.22 | 18.32 | 18.82 | 19.40 | 121 | 0 | 14.57 | 4.29 | 2.84 | 3.07 | 1.23 | 2.11 | lk0: FT +0.03 GPU -1.02;  |
| lkrc | 16.20 | 18.34 | 18.81 | 19.40 | 114 | 0 | 15.29 | 4.36 | 2.87 | 3.07 | 1.25 | 2.11 | lk0: FT -0.01 GPU -0.30;  |
| lksh30 | 16.15 | 18.36 | 18.72 | 19.50 | 114 | 0 | 14.88 | 4.33 | 2.85 | 3.07 | 1.25 | 2.11 | lk0: FT -0.01 GPU -0.71;  |
| lktv0 | 16.01 | 18.17 | 18.54 | 19.06 | 85 | 0 | 14.58 | 4.37 | 2.89 | 3.14 | 1.27 | 2.10 | lk0: FT -0.18 GPU -1.01; LumenReflections -0.24, LumenScreenProbeGather +0.07, Unaccounted +0.04 |
| lwarm | 16.24 | 18.26 | 18.77 | 19.11 | 101 | 0 | 15.38 | 4.38 | 2.85 | 3.05 | 0.99 | 2.12 | lk0: FT +0.02 GPU -0.21; Unaccounted -0.24, Basepass -0.03 |
| warm | 15.48 | 17.57 | 17.62 | 18.46 | 31 | 0 | 13.80 | 1.84 | 2.46 | 2.97 | 1.24 | 2.03 |  |

## perf/z1 (perf_route TABLE)

| config | SP | internal | avg ms (fps) | p50 ms (fps) | p95 ms (fps) | p99 | hitches | GPU ms | RT ms | GT ms | RHI ms | draw calls | cvars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| warm | ini | 1920x1080 | 15.64 (64.0) | 15.58 (64.2) | 17.79 (56.2) | 18.97 | 0 | 14.48 | 15.63 | 1.90 | 2.66 | 0 | r.SkinCache.Mode=0 |
| k_a | ini | 1920x1080 | 15.63 (64.0) | 15.59 (64.2) | 17.81 (56.2) | 18.82 | 0 | 14.31 | 15.63 | 1.87 | 2.67 | 0 | r.SkinCache.Mode=0 |
| ku_a | ini | 1920x1080 | 15.62 (64.0) | 15.56 (64.3) | 17.83 (56.1) | 19.08 | 0 | 14.21 | 15.61 | 1.86 | 2.58 | 0 | r.SkinCache.Mode=0 r.LumenScene.DirectLighting.UpdateFactor=64 r.LumenScene.Radiosity.UpdateFactor=128 |
| k_b | ini | 1920x1080 | 15.50 (64.5) | 15.50 (64.5) | 17.48 (57.2) | 18.60 | 0 | 14.06 | 15.49 | 1.88 | 2.67 | 0 | r.SkinCache.Mode=0 |
| ku_b | ini | 1920x1080 | 15.56 (64.3) | 15.53 (64.4) | 17.69 (56.5) | 18.88 | 0 | 13.88 | 15.55 | 1.85 | 2.69 | 0 | r.SkinCache.Mode=0 r.LumenScene.DirectLighting.UpdateFactor=64 r.LumenScene.Radiosity.UpdateFactor=128 |
| lwarm | ini | 1920x1080 | 16.14 (62.0) | 16.11 (62.1) | 18.34 (54.5) | 19.56 | 0 | 15.74 | 16.13 | 4.36 | 2.95 | 0 | r.SkinCache.Mode=0 |
| lk_a | ini | 1920x1080 | 16.29 (61.4) | 16.26 (61.5) | 18.48 (54.1) | 19.87 | 2 | 15.22 | 16.28 | 4.46 | 2.99 | 0 | r.SkinCache.Mode=0 |
| lku_a | ini | 1920x1080 | 16.25 (61.5) | 16.25 (61.6) | 18.48 (54.1) | 19.61 | 0 | 15.68 | 16.24 | 4.38 | 2.96 | 0 | r.SkinCache.Mode=0 r.LumenScene.DirectLighting.UpdateFactor=64 r.LumenScene.Radiosity.UpdateFactor=128 |
| lk_b | ini | 1920x1080 | 16.26 (61.5) | 16.25 (61.5) | 18.49 (54.1) | 19.69 | 0 | 15.74 | 16.25 | 4.40 | 3.02 | 0 | r.SkinCache.Mode=0 |
| lku_b | ini | 1920x1080 | 16.22 (61.6) | 16.20 (61.7) | 18.52 (54.0) | 19.84 | 0 | 15.46 | 16.22 | 4.41 | 3.00 | 0 | r.SkinCache.Mode=0 r.LumenScene.DirectLighting.UpdateFactor=64 r.LumenScene.Radiosity.UpdateFactor=128 |
| lk_c | ini | 1920x1080 | 16.14 (62.0) | 16.14 (62.0) | 18.22 (54.9) | 19.39 | 1 | 15.21 | 16.13 | 4.34 | 2.92 | 0 | r.SkinCache.Mode=0 |
| lku_c | ini | 1920x1080 | 16.17 (61.9) | 16.22 (61.7) | 18.28 (54.7) | 19.33 | 0 | 13.07 | 16.16 | 4.38 | 3.06 | 0 | r.SkinCache.Mode=0 r.LumenScene.DirectLighting.UpdateFactor=64 r.LumenScene.Radiosity.UpdateFactor=128 |
| lkd75 | ini | 1920x1080 | 16.27 (61.5) | 16.22 (61.7) | 18.50 (54.1) | 19.39 | 1 | 15.32 | 16.26 | 4.65 | 3.17 | 0 | r.SkinCache.Mode=0 r.LumenScene.DirectLighting.UpdateFactor=64 r.LumenScene.Radiosity.UpdateFactor=128 |

## perf/z1 (pass_diff: CSV p95, in-game p95, threads, passes, deltas vs control)

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

## perf/w1 (perf_route TABLE)

| config | SP | internal | avg ms (fps) | p50 ms (fps) | p95 ms (fps) | p99 | hitches | GPU ms | RT ms | GT ms | RHI ms | draw calls | cvars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| warm | ini | 1920x1080 | 15.56 (64.3) | 15.50 (64.5) | 17.70 (56.5) | 18.83 | 0 | 14.32 | 15.56 | 1.90 | 2.61 | 0 | r.SkinCache.Mode=0 |
| s48 | ini | 1920x1080 | 15.37 (65.1) | 15.34 (65.2) | 17.55 (57.0) | 18.71 | 0 | 14.13 | 15.37 | 1.93 | 2.75 | 0 | r.SkinCache.Mode=0 r.Lumen.ScreenProbeGather.DownsampleFactor=48 |
| s64 | ini | 1920x1080 | 15.27 (65.5) | 15.23 (65.7) | 17.41 (57.4) | 18.40 | 0 | 13.00 | 15.26 | 1.84 | 2.48 | 0 | r.SkinCache.Mode=0 r.Lumen.ScreenProbeGather.DownsampleFactor=64 |
| lwarm | ini | 1920x1080 | 16.26 (61.5) | 16.28 (61.4) | 18.42 (54.3) | 20.03 | 0 | 15.66 | 16.25 | 4.35 | 2.86 | 0 | r.SkinCache.Mode=0 |
| lk_a | ini | 1920x1080 | 16.24 (61.6) | 16.20 (61.7) | 18.45 (54.2) | 19.95 | 0 | 15.23 | 16.23 | 4.40 | 2.99 | 0 | r.SkinCache.Mode=0 |
| l48_a | ini | 1920x1080 | 16.04 (62.3) | 16.02 (62.4) | 18.22 (54.9) | 19.86 | 0 | 14.15 | 16.03 | 4.35 | 2.87 | 0 | r.SkinCache.Mode=0 r.Lumen.ScreenProbeGather.DownsampleFactor=48 |
| l64_a | ini | 1920x1080 | 16.02 (62.4) | 15.98 (62.6) | 18.23 (54.9) | 19.67 | 1 | 15.34 | 16.01 | 4.73 | 3.30 | 0 | r.SkinCache.Mode=0 r.Lumen.ScreenProbeGather.DownsampleFactor=64 |
| lk_b | ini | 1920x1080 | 16.15 (61.9) | 16.13 (62.0) | 18.28 (54.7) | 19.45 | 0 | 15.52 | 16.15 | 4.36 | 2.86 | 0 | r.SkinCache.Mode=0 |
| l48_b | ini | 1920x1080 | 16.05 (62.3) | 16.05 (62.3) | 18.32 (54.6) | 19.31 | 0 | 14.26 | 16.04 | 4.34 | 2.88 | 0 | r.SkinCache.Mode=0 r.Lumen.ScreenProbeGather.DownsampleFactor=48 |
| l64_b | ini | 1920x1080 | 16.01 (62.5) | 16.02 (62.4) | 18.14 (55.1) | 19.51 | 0 | 15.37 | 16.00 | 4.36 | 2.84 | 0 | r.SkinCache.Mode=0 r.Lumen.ScreenProbeGather.DownsampleFactor=64 |
| lf0 | ini | 1920x1080 | 16.14 (62.0) | 16.13 (62.0) | 18.27 (54.7) | 19.48 | 0 | 15.50 | 16.13 | 4.31 | 2.84 | 0 | r.SkinCache.Mode=0 |

## perf/w1 (pass_diff: CSV p95, in-game p95, threads, passes, deltas vs control)

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
