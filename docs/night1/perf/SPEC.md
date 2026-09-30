# PERF-SPEC (piece F: 4K output at 60 fps on the Mac Studio M3 Ultra)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Written by the F builder, round 1, from
> `docs/night1/director/PERF-STRATEGY.md` (Fable director, 2026-09-29). Fixed targets; a round only closes on a critic verdict backed by these numbers.

## What "60 fps at 4K" means here (director section 1, owner decision 6.1 pending)
- **Output** 3840x2160, real `-game` run, offscreen, true 3840x2160 back buffer. **Internal (pre-TSR) resolution is always disclosed**
  from `wh_perf.internal_w/h` of the run: `r.ScreenPercentage 50` = 1920x1080, 58 = 2227x1253, 67 = 2573x1447, 100 = native.
  1080p internal is the budget class Marvel's Spider-Man 2 uses in PS5 performance mode.
- No frame generation exists for Metal in UE 5.8, and interpolated frames would not count as gameplay 60 anyway.

## Lines
| id | line | how measured |
|---|---|---|
| P1 | 30 s Manhattan route (piece C `route_30s_warmup15.json`, game seconds 15..45): **p50 frame time <= 16.67 ms (60 fps)** | `tools/perf_ue2/perf_route.py` under `gpu_slot.sh perf`, sidecar `perf_valid: true`, CSV profiler over the window |
| P2 | same run: **p95 <= 18.2 ms (55 fps)**, hitches (frame > 25 ms and > 2x median) = 0 | same |
| P3 | heavy static view (P1 shot S2, 42 m over the avenue): **p50 <= 18.2 ms (55 fps)** | `perf_route.py --script none --map /Game/Maps/Manhattan_View_S2` |
| P4 | no visual regression: S1 / S2 / S7 4K stills before / after, luma stats inside the look spec lines (L1 mean Y 61-100, near-black <= 8 %, clipped <= 1.8 %), SSIM / PSNR vs the pre-change still, blind A/B of before vs after | `tools/perf_ue2/stills.sh`, `compare_stills.py`, `abpack.py` |
| P5 | contamination: every number carries the `gpu_slot.sh summary` line (util before / after, instances before) | sidecar json |

## Must not be sacrificed (director section 5)
Lumen GI (L1-L3 near-black limits, L14 p10 15-30), height fog + aerial perspective + clouds (L9-L12, C11-C15), facade shader at street distance
(C1-C3), trees >= 3 in S1 (C7), Lumen reflections on glass (L17), motion blur (L18 / T20), VSM within 2 km (C3). Cuts only in probe density, far
shadow resolution, fog grid, sky capture, masked-material geometry.

## Method rules
- One variable per run; a config is a screen percentage plus a cvar set applied at startup with `-dpcvars` (and re-applied with `-ExecCmds`),
  or a content transformation (`tools/perf_ue2/perf_apply.py`) with a control run of the untouched content in the same lock session.
- Fixed step (`-benchmark -fps=60`) so every config sees the same frames; the perf window starts after 15 s of standing warm-up.
- Any number not taken inside `gpu_slot.sh perf` is CONTAMINATED and not used as evidence.
- Cvar sets and content changes for other pieces are documented here and in HANDOFF.md; nothing is written to DefaultEngine.ini (integrator-owned).
