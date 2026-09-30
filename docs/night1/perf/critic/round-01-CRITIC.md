# F perf, round 01: independent critic

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

**Verdict: FAILS TARGET**: p95 misses, and the look regressed.

## Recomputed from raw CSVs
FrameTime, 1800 frames, game s 15-45, 3840x2160 output, 1920x1080 internal (TSR 50 %).
- base50 (before): p50 26.45 ms, p95 32.09, p99 34.53. 50 frames are above 33 ms.
- **perf60 (the preset): p50 16.44 ms (60.8 fps), p95 19.86 ms (50.4 fps), p99 21.10, max 23.73.** 356 frames are above 18.18 ms. None are above 33 ms.
- perf60 with MaxPixelsPerEdge 6: p50 15.79, p95 19.00 (52.6 fps).

These match the builder's table. The p95 target is 18.18 ms, so perf60 misses by 1.7 ms. The route also gets worse over time: the p50 of each third is 15.05, 16.19 and **17.96 ms**, so the last 10 s miss 60 fps even at p50.

## Trust
The gpu_slot JSONs for all 4 sessions show `exclusive: true`, `contaminated: false`, one Unreal instance and 0 % GPU use before the run. The health log confirms no other Unreal instance was running during those windows. The measurements are valid, with these caveats:
- Only 6 of 16 runs keep a raw CSV. The one config that reaches 55 fps at p95 is `f_mpe6_sp42` (907p internal). It has no CSV and no look check, so it is unverified.
- The build tested is `1bbd260`, from before the look R2 / water / combat merge. The current HEAD has not been measured.
- `route_30s.mp4` is 1080p with MaxPixelsPerEdge 2, not the config that was measured.

## Visual regressions (perf60 vs before, crops measured)
Software Lumen (`r.Lumen.HardwareRayTracing 0`) changes the look:
- **S2:** the warm lit windows are gone (warm pixels 1.45 % → 0.14 %). The gold glass tower's warm reflections are halved (9.4 % → 4.1 %).
- **S1:** the glass tower's reflections turn into a flat blue sky tone (crop PSNR 15.2 dB, mean luma +17).
- **Route t28:** the warm bounce on the facade is lost.

Whole-frame PSNR on the fixed views is 23-25 dB. For comparison, MaxPixelsPerEdge 4 on its own is clean (SSIM ≥ 0.99).

## Biggest remaining cost
The late-route horizon view. From the first 600 frames to the last 600:
- VolumetricCloud goes from 0.52 to 2.32 ms.
- NaniteVisBuffer goes from 1.32 to 2.88 ms.

**Instruction:** set the VolumetricCloud component's `TracingMaxDistance` from 50 km to ≤15 km. This lever has not been tested yet. Then re-run the route under `gpu_slot perf`. It passes if all three hold:
- VolumetricCloud over the last 600 frames is ≤0.7 ms;
- route p95 is ≤18.18 ms;
- the t20 and t28 stills keep SSIM ≥0.98.

In the same round, bring back the lost reflections and lit windows:
- either turn hardware ray-traced reflections back on: `r.Lumen.HardwareRayTracing 1` with `ScreenProbeGather.HardwareRayTracing 0`. Budget about +4 ms, because building the ray-tracing scene is most of the cost;
- or reach crop SSIM ≥0.97 on S1 and S2 with software Lumen.
