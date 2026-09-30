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
