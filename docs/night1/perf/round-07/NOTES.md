# F perf round 07: notes (every fact of the round)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Builder: Claude Opus 5.5 (round started 2026-09-30 20:37, stopped by a usage limit at ~23:29, resumed 23:30 from the committed WIP).
All 4K numbers: 3840x2160 output, **internal 1920x1080** (TSR, `r.ScreenPercentage 50` from `Config/Mac/MacEngine.ini`), fixed 1/60 s step route (`-benchmark -fps=60`), exclusive GPU lock (`gpu_slot.sh perf`), other processes' GPU time recorded per run (`gpu_procs.py`; a run is VOID when another process used the GPU). No Unreal Insights / trace server; CSV profiler and stat columns only.

## 0. Round target (round-06 critic) and result in one table
(filled at the end of the round, section 6)

## 1. Look gate first
`tools/perf_ue2/look_gate.py` (round-07 edition) was committed in 746c4da BEFORE any round-07 optimisation and was not edited afterwards (`git log -- tools/perf_ue2/look_gate.py` shows one commit). Every gate output of the round is in `look/*.gate.md`; the final one is pasted verbatim in section 5.
On the round-06 shipped stills it FAILS (4 GATE rows: S1 canopy tile foliage 0.57x, S2 tree line 0.83x, S2 tile 0.33x, S7 tile 0.02x vs as found) - the losses the round-06 critic found and round 06 did not disclose.

## 2. The frame-pacing "bubble": what it is (sessions d1, e1, g1; `perf/*/`, `frame_windows_wip.md`, `perf/g1_gap.md`)
The critic measured mean(FrameTime - GPUTime) over the slowest 5 % of frames (same CSV row) = 3.1-3.2 ms and asked for the sync / BLAS update that opens it.
Findings (all from the CSVs, `tools/perf_ue2/frame_gap.py`, `tools/perf_ue2/frame_windows.py`):
1. **There is no ray-tracing geometry work in the slow frames.** `GPU/RayTracingGeometry` (BLAS builds / refits) reads 0 in EVERY frame of every round-07 run (d1, e1, g1; max over all frames = 0); `RayTracingGeometryManager_Tick` p99 <= 0.07 ms; `GPU/RayTracingScene` (TLAS) 0.03-0.04 ms. `RayTracingGeometry/ReferencedSizeMB` grows 404 -> 598 MB and back to 314 MB along the route: it follows WHAT is in view (more city blocks in the frames 450-1050), it is not a per-frame build.
2. **The gap is the same with no movement, no traffic, no crowd.** Static S2 view (session d1 `ds2`, GPU-bound, RT geometry constant 403 MB): FT-GPU mean **1.26 ms** in every 150-frame window (1.21-1.32), same-row top-5 % gap **2.77 ms**. Ship route (no life) top-5 % gap 2.72. Life route 2.2-3.3. The life route does not have a bubble the static camera does not have.
3. **The CSV GPUTime is the previous frame's.** corr(FrameTime[n], GPUTime[n-1]) = 0.70-0.86 vs corr(FrameTime[n], GPUTime[n]) = 0.25-0.66 in every run. Taking the top 5 % frames by FrameTime and subtracting the SAME row's GPUTime subtracts an unrelated (on average ordinary) frame: with GPU frame-to-frame std ~0.9 ms and lag-1 autocorrelation 0.1-0.25, that selection alone adds ~1.3-1.5 ms on top of the constant ~1.0 ms FT-GPU offset. Aligned (GPUTime of the previous row) the top-5 % gap is 1.2-1.9 ms.
4. **The slow life frames are GPU-heavy frames.** Per 150-frame window (`frame_windows_wip.md`, g1 `lctl`): the top-5 % frames sit in windows 450-750 and 900-1050, where mean GPUTime is 16.0-16.2 ms (vs 13.5-15.5 elsewhere) and FT-GPU stays at its usual 1.0-1.1 ms. Per pass, the top-5 % minus median-frames delta is led by LumenScreenProbeGather (+0.38 ms), LumenSceneUpdate (+0.19, card captures of newly revealed blocks), ShadowDepths (+0.14), NaniteVisBuffer (+0.13), Basepass (+0.10). The render thread's `EventWait/Visibility` (11-12 ms of a 16 ms frame in EVERY run incl. static S2) is the render thread waiting for the GPU-paced frame, not a sync that grows in slow frames (+0.7 ms in them, same as the GPU).
5. Stall categories: `-csvCategories=RHITStalls,RHITFlushes` emitted no columns on this Metal build (session d1); `RenderThreadIdle/*` columns are ~0.
6. Sync / pacing levers tried (d1): `r.GTSyncType 1` (p95 18.75, worse), `r.RayTracing.AsyncBuild 1` (18.55, = control), sky-capture one cube face per frame (18.48, = control).

Conclusion: the 3 ms "bubble" is a constant ~1.0-1.3 ms FrameTime-vs-GPUTime offset of this Metal pipeline (present in a static GPU-bound view) plus a one-frame alignment artefact of the same-row measure. There is no sync or BLAS update to remove. **The same-row top-5 % gap pass line (<= 1.2 ms) cannot be reached by removing a stall**; it is reported per run with both alignments. What moves p95 is GPU work in the GPU-heavy windows (probe gather, Lumen card captures, shadows).

## 3. p95 levers measured (life route, sessions e1 / g1; `perf/e1/TABLE.md`, `perf/g1/TABLE.md`)
(see TABLE.md files; summary in section 6)

## 4. Look: what removed the S2 / S7 / S1 foliage (fixed-step stills, `look/*.gate.md`)
(filled at the end)
