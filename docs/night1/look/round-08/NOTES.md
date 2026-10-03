# Look round 08: capture notes (neutral facts only)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Everything in this folder was rendered by the running game (`unreal/WebHomage/Scripts/run_game.sh`: standalone `-game`, offscreen, true back-buffer size), every run inside `/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture` (shared GPU, background priority; contaminated for perf, no perf numbers in this round).
Map `/Game/Tests/Look/Look_Midtown_tod` (rig `Look_Rig_tod`, C++ driver `AWHLookTimeOfDay`), table baked from `unreal/WebHomage/Scripts/look_presets.json` (written by `tools/perf_ue/sweeps/r08/make_v4.py` from `diag/knobs_r08.json` on top of the round-07 table builder).

## Stills
`stills/tod_<pose>_1920x1080_<variant>.jpg`: 1920x1080 output, internal resolution 100 % of output (`r.ScreenPercentage 100`), one game session per plan (`tools/perf_ue/sweeps/run_r06.py`, plan in `stills_session.json`), the first pose of an hour waits 8-14 s after the hour change, the next poses 5 s, at least 90 frames each. Poses: `Scripts/city_shots.json` (S1-S8) and `tools/perf_ue/sky_poses.json` (S4w: perch turned to compass azimuth 250, S4e: azimuth 60, S4m: the 22:00 moon). Variant `w1_h13` = 13:00 with `wh.Weather 1` (overcast), `mist_h7.6` = 07:36.

## Time-lapse
`tod_lapse_S4.mp4` (+ `.json`, `_sheet.jpg`): stitched from five segments (`tools/perf_ue/lapse_stitch.py`, x4 sub-steps by day and night, x16 in the twilights, each segment rendered 0.3 game hours early and those frames dropped), 960x540 output, internal 100 % of output, fixed 1/60 s step, nominal 2 game hours per second; eye adaptation metered per frame for the capture (`pp.AutoExposureSpeedUp/Down 40`, live pins written in the json).

## Clips
`swing_tod_*.mp4`: 1920x1080 output, internal 100 %, fixed 1/60 s step (`-benchmark -fps=60 -dumpmovie`), P3 traversal hero on `tools/perf_ue/scripts/city_swing_clip.json`, 0.8 s pre-roll trimmed. A clip says nothing about real-time frame rate.
