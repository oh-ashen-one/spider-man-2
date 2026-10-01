# F perf round 06: independent critic

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

**Verdict: FAILS TARGET.**

## Recomputed from the raw `perf/f1/*/csv.csv.gz` (1800 frames each, 3840x2160 out, internal 1920x1080 = TSR 50 %)
| run | p50 ms (fps) | p95 ms (fps) | p99 | frames >18.18 | hitches (>25 ms, >2x median) | in-game p95 |
|---|---|---|---|---|---|---|
| life_a | 16.21 (61.7) | **18.38 (54.4)** | 19.57 | 122 | 0 | 18.93 |
| life_b | 16.27 (61.5) | **18.84 (53.1)** | 31.70 | 179 | **14** | 19.58 |
| life_c | 16.19 (61.8) | **18.36 (54.5)** | 20.07 | 116 | 0 | 18.94 |
| ship_a/b/c (no traffic/crowd) | 15.44-15.58 | 17.61-17.72 (56.4-56.8) | 18.8-19.3 | 36-44 | 0 | 17.63-17.70 |

Builder table matches to 0.01 ms. With traffic and crowd on (the real city), p50 passes and p95 fails in all three runs (53.1-54.5 fps). The in-game `wh_perf` p95 is 0.5-0.7 ms worse still. Only the empty-street map passes.

## Trust
`perf_gpu.json` for f1, x1, y1, z1 and w1 all show `exclusive=true`, `contaminated=false` and one Unreal instance. Before the f1 runs GPU use read 0. The lock only counts Unreal processes, so the other session's MLX model is invisible to it, and life_b's 80-frame stall is unexplained. Runs use a scripted route with a fixed step (`-benchmark -fps=60`). That is acceptable but it is not player input.

## Visual (my SSIM and pixel counts on the 3840 PNGs, `r03/before` vs `r06/final`)
- S1 glass crop SSIM 0.935 (gate 0.97, **fails**). In the canopy tile (480,180) the share of green pixels drops from 84 % to 65 % because the leaf interiors are darker.
- S2 avenue tree line, tile (960,540): foliage pixels drop from **7.8 % to 2.5 %**. The trees are visibly thinner and this is **not disclosed**.
- S7 lower-left tile (0,720): foliage drops from **12.2 % to 0.2 %**, so the lit leaves are gone. **Not disclosed.**
- The route stills use a different camera (SSIM 0.23 / 0.30), so no valid gameplay before/after exists.

## Single biggest remaining cost
The p95 is not a GPU-work problem. In the slowest 5 % of life frames, FrameTime minus GPUTime grows from **0.87 to 3.1-3.2 ms**, while GPUTime rises only 1.0 ms. Life GPUTime p95 is 17.5 ms, which would pass on its own. The slow frames are in window frames 300-1200, where RayTracingGeometry ReferencedSizeMB is +66 MB and 10 more skeletal ticks run.

**Instruction:** take one life run with the RHI/render-thread wait stats in the CSV (`-csvCategories` with RHI and RenderThread waits, no Insights). Find the sync or BLAS/RT-geometry update that opens the gap and remove it. Pass condition: the top-5 % FrameTime-GPUTime gap is at or below 1.2 ms and CSV p95 is at or below 18.0 ms in 3 of 3 life runs. Restore S2/S7 foliage before claiming the look gate.

| | Hari's target | measured (life) |
|---|---|---|
| p50 | ≥ 60 fps | 61.5-61.8 fps (pass) |
| p95 | ≥ 55 fps | 53.1-54.5 fps (**fail**) |
| look | no regression | 3 regressions (**fail**) |
