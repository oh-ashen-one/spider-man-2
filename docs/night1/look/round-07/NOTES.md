# P4 Look / Sky, round 07: capture notes

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Round target: twilight dome continuity (SPEC L27, from `critic/round-06-CRITIC.md`). Model: Opus 5.5. Branch `night1/look` (not merged with `Opus-5.5-Loop-Night-1` this round).

## What was captured (all from the real game: `Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`)
- `stills/` (40 stills, 1920x1080 output, internal 100 % = native): ONE baked table per still, see `stills_source.json`:
  - **hold F** (the round's final build = the committed `Scripts/look_presets.json`): the L27 verdict stills (S4 + S4w at 19:00 19:30 19:48 20:00 20:30, S4 + S4e at 06:30 07:00), golden 18:24 S1-S8, night 22:00 S4 + S4m (24 stills).
  - **hold E** (the hold-D build: same table except the golden 18:24 bias (.95 vs .85), the twilight sun-cloud luminance (x.15 vs x.05-.12) and the 20:24 / 20:36 biases (-.15 EV)): night 22:00 S1-S3 S5-S8, 07:30 S4 + S4e, dawn mist 07:36 S1 S4 S4e, 21:00 / 21:30 S4, 13:00 S4 S8 (16 stills; none of these hours is evaluated from a changed key).
  - Settle rule: first pose of an hour 8 s (10 s golden, 14 s night) after the hour change, next poses 5 s, at least 90 frames.
- `swing_tod_22.mp4` / `swing_tod_18h4.mp4` (hold E, hold-D build; 1920x1080, internal 100 %, fixed 1/60 s step): the golden clip was re-encoded (libx264 crf 22) from 15.2 MB to 8.9 MB to stay under the 15 MB limit; the hero-box json was measured on the original frames. The golden clip has 334 frames (its capture ran into the hold budget on a loaded machine).
- `tod_lapse_S4.{mp4,json,_sheet.jpg}` (the L23b / L27f instrument, hold-F build): 960x540, internal 100 %, stitched: 03:42-05:30 x4, **05:30-09:12 x16**, 09:12-17:36 x4, **17:36-21:24 x16**, 21:24-04:00 x4 (the x16 twilight windows are wider than round 06's 05:30-08:12 / 18:24-21:24); segments rendered over holds F / H / I of the SAME build (`lapse_stitch.py --reuse`; `segments[].reused_from_earlier_hold`).
- Instruments: `tools/perf_ue/dome_check.py` (L27), `twilight_check.py`, `tod_tests.py`, `night_tests.py`, `clip_check.py`, `round7_report.py` -> `TESTS_r07.md`.

## Machine conditions (honest context)
The GPU lock ran up to 4-5 capture slots for most of the afternoon (`_scratch/gpu/slots` = 4 after the owner cleared DEMOTED at 11:31); the load average was 15-30 and our game got ~35 % of a core (`renice` 20 on all loop processes), so a rendered frame took ~0.6 s instead of ~0.09 s. Hold F's lapse could only render its first two segments; one engine (hold F's third lapse segment, which could not finish before the 2400 s hold limit) was stopped with `stop_ue.sh` (drivers first, SIGTERM, "stopped cleanly"). No crash, no OS dialog, PAUSED did not block any of these holds.

## Evidence of the holds (diag/)
`holdA_findings.md` (cutoff 0, black ceiling = cloud deck, sun-facing clamp), `holdB_findings.md` (min-EV clamp, v0 lapse windows), `holdC_findings.md` (v1: free meter, lapse 5.45 / 2.97), knobs v0 / v1 / v2 / v3_final, bias seeds, DOME / pivot tables, sheets.
