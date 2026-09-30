# F perf, round 02: notes (neutral facts, no self-assessment)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Numbers are from the RUNNING game (`-game`, offscreen, 3840x2160 back buffer) on piece C's
> integrated `/Game/Maps/Manhattan` (golden rig), the 30 s swing route `route_30s_warmup15.json`, window = game seconds 15..45, fixed step (`-benchmark -fps=60`), CSV profiler
> (1800 frames per run), every run inside `gpu_slot.sh perf` (exclusive lock; `perf_gpu.json` next to every session: `util_before` 0 %, `perf_valid: true`, one Unreal instance).
> Build under test = the round-01 build (binaries of integration 1bbd260, Manhattan content of 2026-09-29 22:25); the merge of integration e0ada6c is source-only and NOT rebuilt here.
> Critic instruction of round 01 (`../critic/round-01-CRITIC.md`): (1) cloud `TracingMaxDistance` <= 15 km, route p95 <= 18.18 ms, cloud last 600 frames <= 0.7 ms, t20 / t28 SSIM >= 0.98;
> (2) restore the lit windows / glass reflections: hardware-RT reflections back on, or crop SSIM >= 0.97 on S1 and S2 with software Lumen.

## 1. Cloud tracing distance (session `perf/s1_cloud`, TSR 50 % = 1920x1080 internal, perf60 = software Lumen; control in the same session, twice)
The shader clamps the marched segment to `min(TracingMaxDistance, distance through the layer)` from the layer entry point (engine `VolumetricCloud.usf` 671-675, mode `DistanceFromCloudLayerEntryPoint`), and
the sample count is `SampleCountMax * saturate(segment / DistanceToSampleMaxCount)` with `DistanceToSampleMaxCount` = 15 km (709-711). Measured: **15 km changes little (-0.4 ms on the pass, -0.4 ms route p95)**;
the pass only falls below 15 km, close to proportionally to the distance. Lowering `r.VolumetricCloud.ViewRaySampleMaxCount` from 256 to 96 instead did not move it (`vrs96`, 2.29 ms), so the segment
length, not the count cap, is the lever here.

| TracingMaxDistance | cloud pass, last 600 frames (ms) | first 600 | route p50 | route p95 | p95 last 600 | frames > 18.18 ms | t20 / t28 SSIM vs control run |
|---|---|---|---|---|---|---|---|
| 50 km (as found; control 1 / 2 / 3) | 2.34 / 2.32 / 2.32 | 0.52 | 16.52 / 16.42 / 16.40 | 19.92 / 19.85 / 19.75 | 20.70 | 266 | 0.9973 / 0.9968 (control vs control, noise floor) |
| 15 km (critic's value) | 1.97 | 0.44 | 16.33 | 19.55 | 20.33 | 210 | 0.9963 / 0.9953 |
| 10 km | 1.22 | 0.31 | 15.88 | 18.41 | 18.91 | 82 | - |
| **6 km** | **0.62** | 0.19 | 15.49 | 17.81 | 18.19 | 31 | 0.9954 / 0.9945 |
| **4 km** | **0.41** | 0.13 | 15.33 | 17.62 | 17.98 | 23 | 0.9939 / 0.9946 |
| 3 km | 0.31 | 0.11 | 15.26 | 17.39 | 17.74 | 14 | 0.9934 / 0.9945 |
Cloud pass = CSV column `GPU/VolumetricCloud` (the three cloud passes together: 2.45 -> 0.51 ms at 4 km). NaniteVisBuffer is unchanged (1.34 first / 2.88 last 600): the late-route Nanite rise is a separate cost.
Implementation for the shipped content: `look_presets.json` `clouds.tracing_max_distance` (50 / 40 / 30 for golden / midday / night) -> 4.0 (or the value you choose); F does not own that file.
Local reproduction: `tools/perf_ue2/make_variants.py` (map copies under `/Game/PerfF/Cl<N>/`, the shipped content is untouched) or `perf_content.sh apply cloud` (edits the rigs in place, backed up).
