# F perf round 05: independent critic (Opus 5.5)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

**Verdict: APPROACHES TARGET.**

## Recomputed from the raw CSVs (`perf/g1/*/csv.csv.gz`, 1800 frames each; 4K output, TSR 50 %, internal 1920x1080)
| config | p50 ms (fps) | p95 ms (fps) | p99 | max | >18.18 ms | hitches (>25 ms and >2x median) |
|---|---|---|---|---|---|---|
| ship_a/b/c | 15.65/15.68/15.72 (63.6-63.9) | 17.79/17.76/17.75 (56.2-56.3) | 18.8-18.9 | 28.3/22.0/25.8 | 50-51 | 0 |
| life_a/b/c (traffic + crowd) | 17.11-17.13 (58.4) | 19.37-19.61 (51.0-51.6) | 20.5-20.9 | up to 37.8 | 416-428 | 1 (life_a) |
| notree | 14.83 | 16.93 | 17.68 | 22.8 | 7 | 0 |

These match the builder's table to 0.01 ms.

## Can the numbers be trusted?
- The `perf_gpu.json` lock record reads exclusive=true, contaminated=false and perf_valid=true, with GPU utilisation 0 % before the run and at most one Unreal instance.
- The hero moved: frame time changes across the route in 5 s blocks from 14.7 to 16.5 ms, while in the void no-hero runs it stayed flat at 14.8. `trav_telemetry.csv` was not kept, so this is indirect proof.
- Caveats:
  - The runs used a fixed step (`-benchmark -fps=60`) and rendered offscreen, so they measure what a frame costs, not how frames were paced on screen.
  - The build is behind the integration branch: traversal r15/r16 (trick camera) and characters r7 are not merged.
  - The p95 margin is 0.4 ms.

**The shipped map passes both lines only because it has no traffic or crowd.** With the merged life piece turned on, both lines fail: p50 is 58.4 fps and p95 is 51 fps. Life adds +1.4 ms at p50, +1.24 ms of `GPU/Unaccounted`, raises the game thread from 1.8 to 3.5 ms and the RHI thread from 2.7 to 5.2 ms.

## Visual regressions (full-res PNGs, my own SSIM)
- **S1 canopy crop:** SSIM against the as-found image is **0.931**, below the 0.97 gate (the round-04 control scored 0.947). Brightness matches (luma 68.0 vs 67.4), but the leaf-level GI pattern is different, with darker deep crown and harsher speckle. The builder measured a repeat noise floor of 0.986, so noise does not explain it.
- **Recess under the elevated structure behind the taxi** (S1, x1700-1850 y540-650): luma is 17.5 as found and **30.0 now (+71 %)**. The round-04 control reads 29.3, so this light leak is older than this round and was never caught. The contact occlusion is gone.
- Full-frame SSIM: S1 0.972, S2 0.978, S7 0.988. Route stills cannot be compared because the camera changed.

## Biggest remaining frame-time cost
`GPU/LumenScreenProbeGather` averages **2.96 ms** across the ship runs. It is the largest pass, and 0.76 ms of it comes from the tree proxies (notree 2.20).

**Instruction:**
1. In the P4 preset only, lower screen-probe density or tracing resolution (`r.Lumen.ScreenProbeGather.DownsampleFactor`, `TracingOctahedronResolution`) until the pass saves at least 1.3 ms.
2. Re-run 3 ship and 3 life runs in one exclusive session.
3. It passes when life p95 is at most 18.0 ms, the S1 crop SSIM is at least 0.97 and the recess luma is within ±10 % of the as-found image.
4. Attribute the +1.24 ms that life adds to `GPU/Unaccounted` in the same session.

## Scores
Measurement validity 8, shipped-map numbers 7, real-gameplay coverage (life) 3, visual fidelity 4, margin 4.
