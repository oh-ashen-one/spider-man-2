# Look round capture notes (neutral facts only)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Everything below was rendered by the running game (`Scripts/run_game.sh`: standalone `-game`, offscreen, true back-buffer size; every run inside `gpu_slot.sh capture`), not by an editor viewport.
Presets are defined in `unreal/WebHomage/Scripts/look_presets.json` (midday / golden / night) and built by `unreal/WebHomage/Scripts/build_look.py`.
Camera positions are browser metres (x east, y up, z south); the UE position is (100 x, 100 z, 100 y) cm. Stills are JPEG converted from the PNG screenshot taken at the given game time.

## Stills

| file | preset | view | output | internal resolution | camera pos (m) | camera target (m) | fov | game time (s) |
|---|---|---|---|---|---|---|---|---|

## Clips

| file | preset | map | output | internal resolution | frames | seconds | bytes | time step | script |
|---|---|---|---|---|---|---|---|---|---|
| swing_tod_18h4.mp4 | tod@18.4 | /Game/Tests/Look/Look_Midtown_tod | 1920x1080 60 fps H.264 | 100% of output (1920x1080) | 719 | 11.98 | 14219972 | fixed 1/60 s (-benchmark -fps=60 -dumpmovie) | tools/perf_ue/scripts/city_swing_clip.json (P3 traversal hero, -WHTravScript, 0.8 s pre-roll trimmed) |
| swing_tod_22.mp4 | tod@22 | /Game/Tests/Look/Look_Midtown_tod | 1920x1080 60 fps H.264 | 100% of output (1920x1080) | 719 | 11.98 | 14060489 | fixed 1/60 s (-benchmark -fps=60 -dumpmovie) | tools/perf_ue/scripts/city_swing_clip.json (P3 traversal hero, -WHTravScript, 0.8 s pre-roll trimmed) |

## Night test numbers (tools/perf_ue/night_tests.py; luma Y = 0.2126 R + 0.7152 G + 0.0722 B of the 8-bit sRGB values)

- swing_tod_18h4.mp4: hero pixel bounding box mean luma per frame: min 22.7, p5 54.3, mean 108.4, max 166.8 /255 over 718 frames (16 frames below 40; 0 frames without hero pixels)
- swing_tod_22.mp4: hero pixel bounding box mean luma per frame: min 20.7, p5 36.5, mean 58.2, max 124.8 /255 over 718 frames (91 frames below 40; 0 frames without hero pixels)

## Round 06 captures (hold 8 = commit d81f8f9; real game, offscreen, inside `gpu_slot.sh capture`)

- Stills (`stills/`, 42 files, `stills_session.json`): ONE game session of `Look_Midtown_tod` (plan `tools/perf_ue/sweeps/r06/gen_plans_f.py`), 1920x1080 output, internal 100 % (`r.ScreenPercentage 100`); the first pose of an hour waits 8 s (12-14 s for the first hours of the session), the next poses 5 s (>= 90 frames). Names `tod_<pose>_1920x1080_h<hour>.jpg`; poses S1..S8 = `city_shots.json`, S4w / S4e / S4m = `tools/perf_ue/sky_poses.json` (S4 perch turned to the dusk sun / dawn sun / 22:00 moon); `mist_h7.6` = 07:36. `rt_h22` = the key table loaded at run time (`wh.ToDLoad`) instead of the baked one (see HANDOFF finding 7).
- Lapse `tod_lapse_S4.mp4` (+ `.json`, `_sheet.jpg`, `.png` chart): S4 perch, nominal 2 h/s = 2 game minutes per output frame, 720 frames, 960x540 output, internal 100 % of output, fixed 1/60 s step; STITCHED from five segments rendered at different sub-steps (x4 = clock 0.5 h/s: 04:00-05:30, 08:12-18:24, 21:24-04:00; x16 = clock 0.125 h/s: 05:30-08:12 and 18:24-21:24; every N-th rendered frame kept; each segment starts 0.3 h early and drops those frames; metering pinned per frame, no render setting changed): `tools/perf_ue/lapse_stitch.py`. The earlier x4-only lapse of hold 7 is in git (a130c4b).
- Clips `swing_tod_22.mp4`, `swing_tod_18h4.mp4`: 1920x1080, 60 fps, 719 frames, internal 100 % of output, fixed 1/60 s step, P3 hero swing (`-WHTravScript`), captured in hold 7 (the hold-7 table; hold 8 changed only the twilight keys and the 18:24 exposure bias by -0.05 EV, so the 22:00 clip is identical for the night table and the golden clip is 0.05 EV brighter than the hold-8 table).

Clip frames are rendered offline at a fixed 1/60 s step (`-benchmark -fps=60 -dumpmovie`), so a clip says nothing about real-time frame rate; see `PERF.md` for measured frame times.
