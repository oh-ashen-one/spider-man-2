# F perf round 02: independent critic (Opus 5.5)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

## Recomputed from the raw CSVs (1800 frames each, 4K output, route 15..45 s)
| run | internal | p50 ms (fps) | p95 | p99 | hitches | >18.18 ms | GPU p50 |
|---|---|---|---|---|---|---|---|
| fin46_a | 1766x994 (46 %) | 16.01 (62.5) | 18.05 (55.4) | 19.08 | 0 | 73 | 13.14 |
| fin46_b | 1766x994 | 16.02 (62.4) | 18.06 (55.4) | 19.08 | 0 | 75 | 13.13 |
| b50 (same preset, 50 %) | 1920x1080 | 16.75 | 18.95 (52.8) | 20.48 | 0 | 218 | 15.39 |
| sw4_50 (software Lumen) | 1920x1080 | 15.32 | 17.48 (57.2) | 18.68 | 0 | 41 | 14.46 |
| s2_fin46 (static) | 1766x994 | 13.20 | 13.98 | 14.46 | 0 | 4 | 12.56 |

Builder numbers reproduce to 0.01 ms; a/b repeat within 0.01 ms; four 50 km controls agree (p95 19.75-19.99). The scene captures are really off (no SceneCapture tick column).

## Trustworthy?
- Lock: `s4_official/perf_gpu.json` says exclusive, util_before 0 %, not contaminated, perf_valid. `instances_max_during` is 2, and the foreign check only counts captures, not editors. health.log shows ue=1 for every 15 s sample from 06:35 to 06:47, so this is probably the run's own launch/exit overlap. I accept it.
- **Not the integrated map.** The runs used the round-01 binaries on a local copy (`/Game/PerfF/Cl4RT/Manhattan`). Integration e0ada6c (water, combat, life) was never built. Cloud 4 km and RT-lite are not in shipped content, and `perf_apply.py` never ran. The p95 margin is 0.12 ms, so any added cost breaks it.
- Per-pass GPU timers are unreliable on Metal: LumenReflections and TSR read 0.00.

## Visual regressions (my own box-SSIM on luma, 1920x1080)
- The builder's own crop gate fails (`_pass: false`): S1 glass 0.921, S2 gold 0.947 against the 0.97 threshold.
- Full frames: S1 0.962, S2 0.961, S7 0.977. The route stills are 4 Y darker (about 6 %: 67.7->63.5, 69.2->65.4). At t28, trees and the glass tower's reflection of trees are visibly duller. This is software GI, but the stills are not pixel-locked.
- Horizon clouds are gone at t42: pink pixels in the top-left sky fall from 11.9 % to 2.1 % (`cloud/cmp_cloudhz/cl4/route_t42_sbs.jpg`).

## Single biggest remaining frame-time cost
The recommended preset is no longer GPU-bound. **FrameTime - GPUTime = 2.89 ms per frame** (p95 4.65), against 0.81 ms for software Lumen. Going from 50 % to 46 % saved 2.3 ms of GPU time but only 0.75 ms of frame time. The render thread spends 12.0 of 16.1 ms in `EventWait/Visibility`.

Instruction: take an Unreal Insights trace (`-trace=cpu,gpu,frame,rhicommands`) of fin46 on the route under `gpu_slot.sh perf`. Find the serialisation between the render/RHI threads and the GPU that the hardware-RT reflection path adds: TLAS/instance gather, skeletal BLAS refit (sk0 showed -1.5 ms p50) or occlusion readback. Remove it. Pass line: mean FrameTime-GPUTime ≤ 1.0 ms. That would put p95 at about 16.3 ms and allow TSR 50 % again.

## Verdict: APPROACHES TARGET
p50 62.4 and p95 55.4 fps hold under a valid exclusive lock. But they were measured on a stale, non-integrated map copy, and the "no visual regression" condition fails.
