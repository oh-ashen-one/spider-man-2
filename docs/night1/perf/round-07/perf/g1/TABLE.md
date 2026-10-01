| config | SP | internal | avg ms (fps) | p50 ms (fps) | p95 ms (fps) | p99 | hitches | GPU ms | RT ms | GT ms | RHI ms | draw calls | cvars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lwarm | ini | 1920x1080 | 16.16 (61.9) | 16.19 (61.8) | 18.33 (54.6) | 19.28 | 0 | 14.33 | 16.16 | 4.34 | 3.03 | 0 | - |
| lccf_a | ini | 1920x1080 | 16.02 (62.4) | 15.99 (62.5) | 18.18 (55.0) | 19.17 | 0 | 15.21 | 16.01 | 4.34 | 2.89 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.LumenScene.SurfaceCache.CardCaptureFactor=128 |
| lcc256_a | ini | 1920x1080 | 16.00 (62.5) | 16.02 (62.4) | 18.19 (55.0) | 19.54 | 0 | 15.34 | 15.99 | 4.33 | 2.83 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.LumenScene.SurfaceCache.CardCaptureFactor=256 |
| lcc256pf | ini | 1920x1080 | 15.89 (62.9) | 15.90 (62.9) | 18.20 (54.9) | 19.12 | 0 | 14.53 | 15.88 | 4.33 | 2.87 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.LumenScene.SurfaceCache.CardCaptureFactor=256 r.LumenScene.SurfaceCache.CardCapturesPerFrame=150 |
| lsky4 | ini | 1920x1080 | 15.88 (63.0) | 15.88 (63.0) | 17.98 (55.6) | 18.93 | 0 | 14.81 | 15.87 | 4.31 | 3.00 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.LumenScene.SurfaceCache.CardCaptureFactor=128 r.SkyLight.RealTimeReflectionCapture.VolumetricCloudResolutionDivider=4 |
| lccf_b | ini | 1920x1080 | 16.00 (62.5) | 15.95 (62.7) | 18.23 (54.9) | 19.15 | 0 | 15.46 | 15.99 | 4.35 | 2.88 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.LumenScene.SurfaceCache.CardCaptureFactor=128 |
| lcc256_b | ini | 1920x1080 | 16.02 (62.4) | 16.03 (62.4) | 18.15 (55.1) | 19.20 | 0 | 15.32 | 16.01 | 4.37 | 2.88 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.LumenScene.SurfaceCache.CardCaptureFactor=256 |
| sccf | ini | 1920x1080 | 15.31 (65.3) | 15.31 (65.3) | 17.46 (57.3) | 18.67 | 0 | 13.64 | 15.30 | 1.83 | 2.44 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.LumenScene.SurfaceCache.CardCaptureFactor=128 |
| lctl | ini | 1920x1080 | 16.21 (61.7) | 16.20 (61.7) | 18.33 (54.6) | 19.50 | 0 | 15.18 | 16.20 | 4.36 | 2.91 | 0 | - |
| lccf_c | ini | 1920x1080 | 15.99 (62.6) | 16.00 (62.5) | 18.13 (55.2) | 19.21 | 0 | 14.97 | 15.98 | 4.34 | 2.86 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.LumenScene.SurfaceCache.CardCaptureFactor=128 |
