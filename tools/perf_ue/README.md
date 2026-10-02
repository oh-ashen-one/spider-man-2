# tools/perf_ue: P4 look / perf / capture tooling

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

| file | what |
|---|---|
| `run_perf.py` | real-gameplay perf at 3840x2160: one run per config (`tsr50`, `tsr67`, `native100`, or `name=SP+cvar=val`), CSV profiler + WH_PERF + top GPU passes + GPU utilisation before / during + contamination flag; `--fixed-step` = deterministic hero route; `--reanalyze` recomputes an existing directory |
| `sweep_views.sh` | perf of every static city view under one preset (finds the heaviest view) |
| `make_perf_md.py` | writes `PERF.md` of a round from the run directories |
| `capture_looks.py` | stills (S1..S8 x presets x 4K / 1080p), 60 fps clips (shader warm-up render, 0.8 s pre-roll trimmed), `NOTES.md` (neutral facts) for the critic; runs `night_tests.py` on the night S1 / S6 stills and the night swing |
| `capture_tour.py` | (round 03) ONE game session per preset and resolution visits the eight `city_shots.json` poses through the C++ shot tour (`Source/WebHomage/Look/WHLookTour.*`, `-WHLookTour=<file>`), settling 4 s per pose; `--variants <json>` sweeps live look variants (`! set / post / cvar / exec` lines) in one session; JPEGs + notes into the round folder |
| `look_spec_check.py` | (round 03) numbers of `docs/night1/look/SPEC.md` per still: L1 / L2 / L3 / L5 (mean, near-black, clipped, B-R), L10 / L11 far field of S4, L13 / L14 night pools, L17 glass p10; `--md` / `--json` |
| `sweep_report.py` | ranks the variants of a `capture_tour.py --variants` sweep against the spec lines (`<preset>_<S#>_<res>_<variant>.jpg`) |
| `round_tests.py` | writes `round-NN/TESTS.md` (spec tables for 1080p and 4K, night_tests numbers, clip_check numbers incl. L18 edge / centre sharpness, hero luma) |
| `clip_check.py` | per-frame mean Y, B-R, near-black, clipped and L18 edge / centre sharpness of a swing clip (ffmpeg decode at 960x540) |
| `night_tests.py` | night numbers: mean luma / share of pixels < 10 (`still`), light pools in the bottom third (`pools`), hero pixel-box mean luma per frame from the P3 hero-only depth mask (`hero`) |
| `capture_tod_lapse.py` | (rounds 05 / 06) 24 h time-lapse of the continuous time of day from one shot pose (default S4, 2 h/s, fixed 1/60 s step); round 06: pins the metering speed (`pp.AutoExposureSpeedUp/Down 40`, written into the json as `instrument_condition`), records every frame (hour, mean Y, B-R, clipped %), the L23b checks, `--keys`, `--no-encode`; `lapse_report.py <json>` lists the steps and draws a chart |
| `capture_tod_lapse.py --substeps N`, `lapse_loop.py`, `lapse_opt.py` | (round 06, hold 6) `--substeps 4` renders the lapse at 0.5 h/s (fixed 1/60 s step) and keeps every 4th frame: the same 725-frame 2 h/s lapse with the engine's temporal lighting caches settled between output frames (no render setting changed); `lapse_loop.py` = closed loop on the exposure bias of the twilight keys (sub-stepped lapse -> `lapse_opt.design_target`: the curve closest to the measured one with |dY| <= 1.25 / frame, golden and night anchors pinned, ceiling where the red sky clips -> new bias keys -> next lapse), writes `bias_overrides.json` for `sweeps/r06/make_v2.py --bias-overrides` |
| `sweeps/r06/make_v2.py`, `gen_plans_e.py`, `make_final_knobs.py`, `hold6a.sh`, `hold6b.sh`, `analyze_a.py` | (round 06, hold 6) the round-06 time-of-day table builder with its knobs (`tw_fac_pts`, `tw_hl_r`, `tw_cloud`, `night_hl`, `cloud_offset`, `tw_fog_scale`, `tw_sun_lux`, `sun_ramp`; defaults = the hold-4 table), the 6A variant plan + chain (twilight W1 / W3 / W4, night N1, golden G1 / G2, dawn mist), the 6B knob winners, the 6B final chain (loop -> table in place -> headless rebuild -> lapse -> stills -> clips) and the 6A analysis |
| `sky_poses.json` | (round 06) extra poses next to `city_shots.json`: S4w / S4e = the S4 perch turned to the dusk / dawn sun, S4m = turned to the 22:00 moon, H1 = hero close-up (hero light calibration) |
| `sweeps/run_r06.py`, `sweeps/r06/` | (round 06) groups of (key table, hour, live pins, poses) in ONE game session (8 s settle after each hour change); `gen_plans.py` writes the diagnostic plans, `hold1.sh` is the first diagnostic hold |
| `twilight_check.py` | (round 06) LOOK-SPEC L24 / L25 / L26 on the sky stills: S4 sky band vs far band, B-R of the sun-facing still, moon disk size / peak Y, sky high-pass std, S1 dawn-vs-golden luma correlation |
| `scripts/city_swing_avenue.json` | traversal driver for perf (14 s warm-up, then a swing chain up the avenue) |
| `scripts/city_swing_clip.json` | traversal driver for clips (airborne start, swing chain) |
| `rebuild_city.sh` | P1's city pipeline on P4's own dev port / scratch / editor (never touches P1's) |
| `rebuild_look.sh` | headless `Scripts/build_look.py` (editor closed) |
| `launch_editor.sh`, `job_server.py`, `uejob.py` | P4 editor (MCP 8774, `-RenderOffScreen -NoSound`, waits while 3+ editors run) with a file-based job server; `uejob.py <script.py> [k=v]` runs a Python file in it |

Scratch (never committed): `/Users/midir/sm2-n1/_scratch/look/` (export, textures, job dir, captures). See `docs/night1/look/HANDOFF.md`.
