# Look round 08: capture notes (neutral facts only)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Everything in this folder was rendered by the running game (`unreal/WebHomage/Scripts/run_game.sh`: standalone `-game`, offscreen, true back-buffer size), every run inside `/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture` (shared GPU, background priority; no perf numbers in this round).
Map `/Game/Tests/Look/Look_Midtown_tod` (rig `Look_Rig_tod`, C++ driver `AWHLookTimeOfDay`); the table is baked from `unreal/WebHomage/Scripts/look_presets.json` = `tools/perf_ue/sweeps/r08/make_v4.py --knobs diag/knobs_r08.json --r07-bias lapse_bias_overrides.json`.

## Builds
- `stills/tod_*`: bake of `diag/knobs_r08.json` with the loop biases + the hand-set 19:54 / 20:12 keys (`/Users/midir/sm2-n1/_scratch/look/r08/final6`). The final bake (the committed table) differs from it ONLY in exposure-bias keys 06:42-06:54, 07:06-07:09, 18:54 and 19:06-19:15 (tapered next to the held keys, `HANDOFF.md`). The still hours (06:30, 07:00, 07:30, 07:36, 19:00, 19:30, 19:48, 20:00, 20:30 and every other) are keys or segments whose Catmull-Rom neighbours are unchanged, so their exposure is identical; `diag/second_capture/` is a 17-pose capture of an intermediate taper build with the same still-hour values (L28a 65.7 / 71.8 / 70.9 against 65.7 / 71.7 / 70.8).
- `stills/midday_S*` (the fixed midday preset map `Look_Midtown`, the round-03 floor): captured from the bake of knobs v5 (`final5`); the midday preset and its rig inputs are identical in every round-08 bake (only time-of-day keys and the fills' specular changed; the midday preset has no fills).
- `tod_lapse_S4.*`: the final bake (stitched; the day / night x4 segments 03:42-05:30, 08:36-17:36 reused from the previous bake, whose keys there are identical).
- `swing_tod_19.mp4`, `swing_tod_22.mp4`: the intermediate taper build (19:00 and 22:00 are keys whose neighbours did not change).

## Stills
`stills/tod_<pose>_1920x1080_<variant>.jpg`: 1920x1080 output, internal resolution 100 % of output (`r.ScreenPercentage 100`), ONE game session (`tools/perf_ue/sweeps/run_r06.py`, plan in `stills_session.json`, generator `gen_plans_r08.py --set full`); the first pose of an hour waits 8-14 s after the hour change, the next poses 5 s, at least 90 frames each. Poses: `Scripts/city_shots.json` (S1-S8) and `tools/perf_ue/sky_poses.json` (S4w: perch turned to compass azimuth 250, S4e: azimuth 60, S4m: the 22:00 moon). `w1_h13` = 13:00 with `wh.Weather 1` (overcast), `mist_h7.6` = 07:36.
The volumetric cloud pattern differs between sessions (same table, same hour): `diag/second_capture/DOME.md` vs `DOME_r08.md` (S4e 06:30 sky-far +9.3 / +18.0, S4w 19:30 rows 0-150 clipped 1.72 % / 0.05 %, S4e 06:30 8-row step 12.4 / 25.1).

## Time-lapse
`tod_lapse_S4.mp4` (+ `.json`, `_sheet.jpg`): stitched from five segments (`tools/perf_ue/lapse_stitch.py`; x4 sub-steps by day and night, x16 in the twilights 05:12-09:12 and 17:18-21:24, each segment rendered 0.3 game hours early and those frames dropped), 960x540 output, internal 100 % of output, fixed 1/60 s step, nominal 2 game hours per second; eye adaptation metered per frame for the capture (`pp.AutoExposureSpeedUp/Down 40`, live pins written in the json).

## Clips
`swing_tod_19.mp4`, `swing_tod_22.mp4`: 1920x1080 output, internal 100 %, 60 fps H.264, fixed 1/60 s step (`-benchmark -fps=60 -dumpmovie`), P3 traversal hero on `tools/perf_ue/scripts/city_swing_clip.json`, 0.8 s pre-roll trimmed; < 15 MB each. A clip says nothing about real-time frame rate.
