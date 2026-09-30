# Water A/B, Sonnet 5.5, round 01: capture notes (facts only)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

Branch `night1/water-ab-sonnet`, build = `unreal/WebHomage/Scripts/build_water.py` on top of `build_manhattan.py` (steps cpp, city_export, city_prep, city, look, map; traversal and characters not run).
Engine: UE 5.8.3, Mac Studio M3 Ultra, Metal SM6, Lumen with hardware RT as the project configures it, TSR, golden rig `Look_Rig_golden` unless a file says midday.

## Files
| file | what | how it was made |
|---|---|---|
| `S4_golden_4k.jpg` / `S4_golden_1080.jpg` | S4_perch_skyline of `Scripts/city_shots.json` (pos 182, 306, -92; target -120, 150, -470; hFOV 75) | map `/Game/Maps/Manhattan_View_S4`, `run_game.sh -shots 28`, `r.ScreenPercentage 100` (internal = output), real-time pacing, JPEG q92 |
| `river_low_4k.jpg` / `river_low_1080.jpg` | low river view, `views.json` `river_low`: pos (-772.0, 4.4, -128.0) (browser x, y, z), north, pitch -3, hFOV 90 | map `/Game/Water/Maps/Water_View_Low`, same settings |
| `river_low_dolly.mp4` | 10.000 s, 1920x1080, 60 fps, 600 frames, 9.9 MB | map `Water_View_Dolly`: level sequence moves the camera 10 m north (z -128 -> -138) at 1 m/s after 3 s of holding still; `-benchmark -fps=60 -dumpmovie` (fixed 1/60 s step), 877 frames rendered, frames 180..779 encoded (crf 20); the first 180 frames (warm-up + still camera) are not in the clip |
| `river_low_west_*`, `river_low_polygon_*`, `river_low_midday_1080.jpg`, `river_low_west_midday_1080.jpg` | supplements (not requested): `river_low` position looking west; the literal LAND_POLY position; midday rig | maps `Water_View_LowWest`, `_LowPoly`, `_Low_Midday`, `_LowWest_Midday` |
| `perf.json`, `perf_runs/` | GPU cost of the water, per-run json + gpu lock sidecars | exclusive `gpu_slot.sh perf`, see below |
| `debug/flat_glossy_mirror_west_1080.jpg` | debug capture of an earlier build (`SM2_WATER_TUNE={"debug": 2}`: flat normal, roughness 0.08, black body): what Lumen reflects at the `river_low_west` position when the surface is a flat glossy mirror | 1080p, `-shots 20,30` |
| `frame_stats.json`, `farfield_S4.json` | whole-frame luma stats (definition of `specs/tools/lum_by_tod.py`: Y = .2126R + .7152G + .0722B, clipped = any channel >= 250, near-black = Y < 10) and `tools/export/spec_farfield.py` (C11-C15) on `S4_golden_4k.jpg` | |

## river_low position (differs from a literal reading of the brief)
`layout.js` `shoreX(z).west` at the Midtown block centre latitude (region z -512..256 -> z = -128) is x = -744.16 (`layout.LAND_POLY`). `waterfront.js` builds the esplanade fill / bump-outs outward of `LAND_POLY`
(the waterline baked from the exported coast meshes is at x = -768.0 west-most and -761.0 median for z in -153..-103). At x = -744.16 the camera hangs over the promenade and open water is a small part of the frame
(`river_low_polygon_*`). `river_low` therefore uses x = -768.0 - 4.0 = -772.0 (over the water, beside the timber bulkhead). Yaw is north (along the river), pitch -3 deg, hFOV 90, y = water level (-1.6) + 6 = 4.4, as briefed.

## Numbers
- CITY-SPEC C11-C15 on `S4_golden_4k.jpg` (`farfield_S4.json`): C14 far-shore Y minus river Y = 45.8 (target 5..35). Region Y: sky 159.5, far shore 172.1, river 126.3. C13 far shore minus sky = +12.6 (target -35..-25). C12 = -27.5. C15 = 0.31.
  For comparison the same tool on `docs/night1/manhattan/round-01/stills/view_S4.jpg` (P1's flat water plane): river Y 132.1, C14 = 40.4, C13 = +16.1.
  Test builds on this view: a nearly calm surface (slope_k 0.25, dn_k 0.2, alpha 0.012) gave river Y 130.5; lower far-field roughness alone gave 127.6; body albedo x1.4 changed it by +0.4. The river band is dominated by the height fog.
- Frame stats (`frame_stats.json`): S4_golden mean Y 91.7 (L1 golden 61..100), near-black 0.44 %, clipped 0.66 %; river_low mean Y 101.6, near-black 0.10 %, clipped 0.09 %; open-water region of river_low_1080 (x 0-1000, y 560-1080) mean Y 64.7, std 11.9, p10 48, p90 79.
  Reference stills measured for comparison (same luma definition, 1920 px wide): river-pier-golden water mean Y 67.8 / 82.5 (std 31.5 / 35.9), river-queens-aerial 70.8 (std 23.1), river-golden-bridge 72.8 (std 45.2).
- GPU cost of the water (`perf.json`): see the table below. Every perf run was taken under the exclusive lock with `perf_valid: true`, GPU utilisation 0-2 % before the run.

### GPU cost of the water (3840x2160 output, TSR 67 % = 2573x1447 internal, static camera, 20 s window, exclusive `gpu_slot.sh perf`, M3 Ultra)
GPU ms = `gpu_avg_ms` of `WH_PERF` (RHI GPU frame time); "water" = view with water on minus the same view with `MPC_Water.Off = 1`. Budget: 2.5 ms.

| view (water share of the frame, by eye) | assets | on: frame / p50 / GPU ms | off: frame / p50 / GPU ms | delta GPU ms | delta frame p50 ms | run validity |
|---|---|---|---|---|---|---|
| river_low (~30 %) | final | 27.12 / 26.59 / 26.34 | 25.26 / 24.68 / 24.48 | **1.86** | 1.91 | both `perf_valid` (low_on5 / low_off5) |
| river_low | final | 27.12 / 26.57 / 26.36 | 25.17 / 24.59 / 24.40 | 1.96 | 1.98 | `low_on4` contaminated (foreign capture process appeared during the run) |
| river_low | final | 28.79 / 26.71 / 27.01 | 25.15 / 24.60 / 24.39 | 2.63 | 2.11 | valid, but `low_on3` holds one 300.7 ms frame (first launch after the asset rebuild) that lifts its averages |
| S4 perch (~12 %) | final | 31.91 / 31.43 / 31.25 | 31.54 / 31.02 / 30.90 | **0.35** | 0.41 | both valid (s4_on4 / s4_off4) |
| S4 perch | final | 34.33 / 31.43 / 32.20 | 31.43 / 30.88 / 30.79 | 1.42 | 0.54 | valid, `s4_on3` holds one 298.8 ms frame |
| river_low | superseded look v0 | 27.20 / 26.64 / 26.06, 27.08 / 26.52 / 26.31 | 25.90 / 24.73 / 24.68, 25.34 / 24.79 / 24.58 | 1.38, 1.73 | 1.90, 1.73 | valid (same shader code; ripple band 24 cycles, dn_k 0.6, slope_k 0.7, sw_k 0.5) |
| S4 perch | superseded look v0 | 31.91 / 31.40 / 31.25, 32.78 / 31.70 / 31.17 | 31.55 / 31.07 / 30.88, 31.46 / 30.96 / 30.80 | 0.37, 0.37 | 0.34, 0.74 | valid |

Whole-frame GPU time of the scene at this resolution is 24.4-31.3 ms (city + look rig; not the water's budget). Not measured: per-pass breakdown, water filling the whole frame, midday rig, fast camera motion, the old P1 plane on the same views.
Sidecars with lock state (`util_before` 0-2 %, `exclusive`, `wait_s`, instance counts): `perf_runs/*_gpu.json`; per-run `WH_PERF` json: `perf_runs/*_perf.json`; all runs: `perf.json`.


## Conditions and caveats
- The stills and the clip were captured under `gpu_slot.sh capture` while other agents' captures ran (shared GPU). That affects wall time only: the frames are deterministic renders of a static or scripted camera.
  Stills are taken at game time t = 28 s of a real-time run (not fixed-step), so Lumen / TSR / auto-exposure state is whatever had converged by then.
- The perf baseline "water off" is `MPC_Water.Off = 1` on maps `*_Off` (a level sequence), i.e. the wave surface is moved out of the frustum; everything else in the scene is identical.
- The engine logs one handled ensure at startup ("Found precision loss while converting matrix to GPU format", `UpdateDistanceFieldObjectBuffers`); it appears in the city agent's and the look agent's captures with the old flat plane too.
- The lens flare / ghost shapes in `river_low_west_*` are produced by the golden rig's post process (bloom lens flare), not by the water.
- Not implemented: boats and wakes, splash ripple simulation and spray, underwater view, river bed, gameplay-height query. The contact-foam map knows the coast meshes and bridge piers of the export only.
- Known engine interaction: the surface's vertices follow the camera (WPO), so per-vertex velocity for TSR equals camera motion; fast camera motion over near water was not measured.
