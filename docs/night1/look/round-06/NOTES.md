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
| swing_tod_18h4.mp4 | tod@18.4 | /Game/Tests/Look/Look_Midtown_tod | 1920x1080 60 fps H.264 | 100% of output (1920x1080) | 719 | 11.98 | 14159820 | fixed 1/60 s (-benchmark -fps=60 -dumpmovie) | tools/perf_ue/scripts/city_swing_clip.json (P3 traversal hero, -WHTravScript, 0.8 s pre-roll trimmed) |
| swing_tod_22.mp4 | tod@22 | /Game/Tests/Look/Look_Midtown_tod | 1920x1080 60 fps H.264 | 100% of output (1920x1080) | 719 | 11.98 | 14115426 | fixed 1/60 s (-benchmark -fps=60 -dumpmovie) | tools/perf_ue/scripts/city_swing_clip.json (P3 traversal hero, -WHTravScript, 0.8 s pre-roll trimmed) |

## Night test numbers (tools/perf_ue/night_tests.py; luma Y = 0.2126 R + 0.7152 G + 0.0722 B of the 8-bit sRGB values)

- swing_tod_18h4.mp4: hero pixel bounding box mean luma per frame: min 20.9, p5 53.0, mean 106.7, max 166.4 /255 over 718 frames (16 frames below 40; 0 frames without hero pixels)
- swing_tod_22.mp4: hero pixel bounding box mean luma per frame: min 20.6, p5 36.4, mean 58.0, max 124.7 /255 over 718 frames (92 frames below 40; 0 frames without hero pixels)

Clip frames are rendered offline at a fixed 1/60 s step (`-benchmark -fps=60 -dumpmovie`), so a clip says nothing about real-time frame rate; see `PERF.md` for measured frame times.
