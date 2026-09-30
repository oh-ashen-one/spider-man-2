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
