# Tricks (C) — round 02 shot list

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

Round target (director after the r01 critic): the web catch at the end of every trick must not snap. Test: the rendered chest frame
(pose log `chest_f` / `chest_u`) turns <= 250 deg/s in every 0.1 s window from the trick end to the end + 0.4 s, on all 22 tricks
(`tools/tricks/tricks_check.py` line `C`).

**r02 status: the reel render was stopped by the GPU health monitor at 20:05 and its engine stuck exiting in the GPU driver (see
NUMBERS.md); no part below exists yet except the probe CSVs.** Committed now: `t60_trick_reel_probe_telemetry.csv`,
`t60_trick_reel_probe_pose.csv.gz` (the `-nullrhi` probe of the same build and script) and `CHECK_probe.txt`.

| Clip (planned) | What | How |
|---|---|---|
| `t60_trick_reel_part1.mp4` .. `_part8.mp4` | ONE continuous 61 s web-swing chain in the lit city with a flip program on every release (the r01 route and script; the 12 release programs, twice), split into 8 s parts for the 15 MB file limit. Concatenated in order they are the whole clip (frame-exact cuts of one encode source) | script `docs/night1/tricks/scripts/t60_trick_reel.json`, `tools/tricks/capture.sh` (windows 0:15, 15:30, 30:45, 45:61 of one deterministic run), route verified by a `-nullrhi` probe of the same build (`tools/tricks/probe_reel.py`) |
| local only: `_scratch/tricks/capture/t60_trick_reel/t60_trick_reel_full.mp4` | the same 61 s clip as one 13 Mbps file (and `_hq.mp4`, CRF 16) for the critic | capture.sh |
| `t60_trick_reel_telemetry.csv` | per-frame traversal telemetry (60 Hz, every row): `flip_prog`, `flip_t`, `flip_scale`, `flip_rate_dps`, `flip_shape(_legs)`, `body_pitch_deg`, `tuck_*`, `limb_z`, `px_*` | WebTravCharacter (`-WHShotDir`); rows of window k from window k's run (`tools/tricks/stitch_telemetry.py`) |
| `t60_trick_reel_pose.csv.gz` | rendered bone positions + head / chest / pelvis axes per frame (`-WHTrickPose`), r02 adds the catch-lean state (`catch_*`: window weight, predicted pitch / twist / sideways rest, swing-pose bank share, hand, predicted anchor) and the mesh / body / predicted-frame quaternions | WebTravFlips.cpp |
| `CHECK.txt` | `tools/tricks/tricks_check.py` on the two CSVs (every SPEC line + C, X, G1f, PEN, PIK) and ffprobe of every part and the local full file | `tools/tricks/finish_r02.sh` |
| `NUMBERS.md` | the SPEC lines with the measured numbers | |

## Capture settings

| | |
|---|---|
| output | 1920x1080, 60 fps, H.264, 13 Mbps target (`-b:v 13000k -maxrate 16250k`), parts of 8 s (<= 15 MB each) |
| internal resolution | 1920x1080 (`r.ScreenPercentage 100`, native) |
| time step | fixed 1/60 s (`-benchmark -fps=60 -dumpmovie`), offscreen `-game` (`Scripts/run_game.sh`), 0.8 s pre-roll cut |
| hero light | `-WHHeroFill=16000,36000` (the character's camera-side fill light, cd base / flip camera; default 5000 / 18000) |
| GPU | every engine run inside `_scratch/gpu/bin/gpu_slot.sh capture --label tricks` (background priority, frame-capped) |
