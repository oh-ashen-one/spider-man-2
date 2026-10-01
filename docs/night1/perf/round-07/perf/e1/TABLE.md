| config | SP | internal | avg ms (fps) | p50 ms (fps) | p95 ms (fps) | p99 | hitches | GPU ms | RT ms | GT ms | RHI ms | draw calls | cvars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lwarm | ini | 1920x1080 | 16.24 (61.6) | 16.20 (61.7) | 18.37 (54.4) | 19.53 | 0 | 15.61 | 16.22 | 4.73 | 3.22 | 0 | - |
| lctl_a | ini | 1920x1080 | 16.22 (61.7) | 16.15 (61.9) | 18.38 (54.4) | 20.11 | 3 | 14.66 | 16.21 | 4.31 | 2.99 | 0 | - |
| lcr0_a | ini | 1920x1080 | 15.97 (62.6) | 15.94 (62.7) | 18.18 (55.0) | 19.09 | 0 | 15.23 | 15.96 | 4.35 | 2.88 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 |
| lbt0 | ini | 1920x1080 | 16.38 (61.1) | 16.38 (61.1) | 18.58 (53.8) | 20.30 | 0 | 15.37 | 16.37 | 4.29 | 4.24 | 0 | r.GPUSkin.BoneTransformAllocationMode=0 |
| lcrbt | ini | 1920x1080 | 16.36 (61.1) | 16.37 (61.1) | 18.55 (53.9) | 20.12 | 1 | 14.69 | 16.35 | 4.27 | 6.86 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.GPUSkin.BoneTransformAllocationMode=0 |
| lsk300 | ini | 1920x1080 | 16.17 (61.8) | 16.20 (61.7) | 18.25 (54.8) | 19.24 | 0 | 14.75 | 16.17 | 4.50 | 3.15 | 0 | r.Lumen.HardwareRayTracing.SkipTwoSidedHitDistance=300 |
| lctl_b | ini | 1920x1080 | 16.17 (61.9) | 16.17 (61.8) | 18.45 (54.2) | 19.62 | 0 | 15.72 | 16.16 | 4.41 | 2.94 | 0 | - |
| lcr0_b | ini | 1920x1080 | 16.00 (62.5) | 16.01 (62.5) | 18.19 (55.0) | 19.30 | 0 | 15.37 | 15.99 | 4.32 | 2.83 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 |
| lccf | ini | 1920x1080 | 15.87 (63.0) | 15.89 (62.9) | 18.06 (55.4) | 19.02 | 0 | 15.44 | 15.86 | 4.35 | 2.86 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.LumenScene.SurfaceCache.CardCaptureFactor=128 |
| lcrbt_b | ini | 1920x1080 | 16.13 (62.0) | 16.11 (62.1) | 18.31 (54.6) | 19.21 | 0 | 14.65 | 16.12 | 4.33 | 4.38 | 0 | r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0 r.GPUSkin.BoneTransformAllocationMode=0 |
