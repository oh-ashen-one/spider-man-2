# F perf round 04: critic

> Homage fan game, not official Marvel/Sony/Insomniac.

**Recomputed from the raw CSVs** (`perf/f1`, 1800 frames each, 3840x2160 output, TSR 50 % = 1920x1080 internal):

| run | p50 ms (fps) | p95 ms (fps) | p99 | frames >18.18 | hitches | worst 1 s | in-game counter p95 |
|---|---|---|---|---|---|---|---|
| ship_a | 16.08 (62.2) | 18.03 (55.5) | 18.76 | 63 | 0 | 57.2 fps | **18.21 (54.9)** |
| ship_b | 16.03 (62.4) | 18.03 (55.5) | 18.85 | 71 | 0 | 57.3 fps | **18.23 (54.9)** |
| ship_c | 16.11 (62.1) | 18.05 (55.4) | 18.85 | 69 | 0 | 57.0 fps | **18.28 (54.7)** |

The CSV numbers match the builder's. S2: 14.66 / 15.82 ms. ShadowDepths p95 is 2.44 ms, confirmed.

**Trust:**
- The lock records are valid. All six `perf_gpu.json` records say exclusive, not contaminated and `perf_valid`, with GPU use 0 % before the runs. `f1` ran with one instance.
- **The two instruments disagree on p95.** The game's own `wh_perf` counter (`result.json`) puts p95 above 18.18 ms (below 55 fps) in all three shipped runs. NOTES.md does not report this. p95 therefore passes by 0.13 ms on one instrument and fails by 0.03–0.10 ms on the other, so it is not established.
- The run is not real gameplay: a scripted fixed-step route on the round-03 build, with no traffic or crowd, rendered offscreen with no present.

**Visual regressions** (my measurements, 4K PNGs downsampled to 1080, as-found vs final):
- **Round-02 S1 crop: SSIM 0.955, a fail (gate 0.97).** Canopy luma drops 68.0→61.8 and the crown interior is visibly darker.
- **route_t20:** the worst 64 px tile changes by ΔY 80. Because bark is out of the ray-tracing scene, the trunk and the sidewalk under the crown are brighter, and occlusion and contact darkening are lost.
- **route_t42:** 5.0 % of pixels change by more than 20 in luma, and the park canopy is 6 % brighter and flatter.
- Clouds and saturation are restored: t42 sky gradient ratio 1.01, saturation within 2 %.

**Biggest remaining cost:** the FrameTime−GPUTime gap. It averages 1.40 ms with a p95 of 2.92 ms, and it is 1.29 ms of the 2.41 ms that the slowest 10 % of frames add. It rose from 0.80 ms (`y1/base`) when the 42 k leaf instances went into the ray-tracing scene; GPUTime rose only 0.4 ms. The next GPU cost is LumenScreenProbeGather (2.47 ms mean, 3.43 ms p95).

Instruction: cut the ray-tracing instance count for leaves from 42 k to 1 k or fewer by merging leaf and crown cards per city tile into ray-tracing proxy meshes. Also put the bark in as those same merged proxies. The pass conditions are:
- mean FT−GPU of 0.9 ms or less;
- in-game counter p95 of 17.9 ms or less in 3 runs;
- S1 round-02 crop SSIM of 0.97 or more.

**Verdict: APPROACHES TARGET.** p50 of 62 fps holds on valid evidence. p95 sits right on the line (the in-game counter fails it), and the look gate still fails.
