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
