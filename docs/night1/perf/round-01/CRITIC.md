# F perf, round 01: independent critic

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

**Verdict: FAILS TARGET** (p95 misses, visual regression)

## Recomputed from raw CSVs (FrameTime, 1800 frames, game s 15-45, 3840x2160 output)
| run | internal | p50 ms | p95 ms | p99 ms | max | >18.18 ms | >33.3 ms |
|---|---|---|---|---|---|---|---|
| base50 (before) | 1920x1080 | 26.45 | 32.09 | 34.53 | 41.65 | 1799 | 50 |
| **perf60_50 (shipped preset)** | 1920x1080 | **16.44 (60.8 fps)** | **19.86 (50.4 fps)** | 21.10 | 23.73 | 356 | 0 |
| perf60_mpe6_50 | 1920x1080 | 15.79 | 19.00 (52.6 fps) | 20.23 | 25.09 | 178 | 0 |
| s2_perf60_50 (static view, no swing) | 1920x1080 | 13.39 | 17.32 | 20.70 | 30.82 | 64 | 0 |

These match the builder's TABLE to 0.01 ms. There are no hitches (no frame is above 33 ms). The p95 target is 18.18 ms, and perf60 misses it by 1.7 ms. The route also gets worse as it goes: the p50 of each third is 15.05, 16.19 and **17.96 ms**. In the last 10 s even the p50 misses 60 fps.

## Trust
- gpu_slot JSONs for all 4 sessions: `exclusive: true`, `contaminated: false`, `instances_max_during: 1`, `util_before` 0 %. The health log shows no other Unreal instance inside any perf window. Valid.
- Caveats:
  - Only 6 of 16 runs keep a raw CSV. The only config that reaches p95 55 fps is `f_mpe6_sp42` (internal 1613x907, 17.47 ms), and it has no CSV and no look check, so it cannot be verified.
  - The build under test is `1bbd260`, from before the look R2 / water / combat / life merge. The current HEAD has not been measured.
  - `route_30s.mp4` is 1080p with MaxPixelsPerEdge 2, not the config that was measured.

## Visual regressions (perf60 vs before, TSR 50 %, crops measured)
Software Lumen (`r.Lumen.HardwareRayTracing 0`) visibly changes the look:
- S2: the warm lit windows on the left facade are gone. The share of warm pixels drops from 1.45 % to 0.14 %.
- S2: reflections on the gold glass tower lose their warmth (warm pixels 9.4 % → 4.1 %; mean R 104 → 87).
- S1: the glass tower's reflections are replaced by a flat, bluer sky tone. Crop PSNR is 15.2 dB and mean luma rises by 17.
- Route t28: the warm bounce on the facade is lost and the frame is 14 % brighter overall.

Whole-frame PSNR is 23-25 dB on the fixed views, which is a regression, not noise. The Nanite error bound of 4 px on its own is clean (SSIM ≥ 0.99).

## Single biggest remaining frame-time cost
The late-route horizon view. From the first 600 frames to the last 600:
- VolumetricCloud rises from 0.52 to 2.32 ms.
- NaniteVisBuffer rises from 1.32 to 2.88 ms.
- Unaccounted rises from 0.17 to 1.56 ms.

**Instruction:** lower the VolumetricCloud component's `TracingMaxDistance` from 50 km to ≤15 km (the builder names this lever in its notes but has not tested it). Then re-run the route under `gpu_slot perf`. It passes if:
- VolumetricCloud over the last 600 frames is ≤ 0.7 ms;
- route p95 is ≤ 18.18 ms;
- the horizon stills (t20/t28) keep SSIM ≥ 0.98.

In the same round, restore the lost reflections and lit windows. Either keep hardware ray tracing for reflections only (`Reflections.HardwareRayTracing 1`, which the notes measure at +0.7 ms), or show SSIM ≥ 0.97 on crops of S1 and S2.
