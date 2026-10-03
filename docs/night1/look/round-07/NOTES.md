# P4 Look / Sky, round 07: capture notes

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Round target: twilight dome continuity (SPEC L27, from `critic/round-06-CRITIC.md`, "Biggest gap"). Started by Opus 5.5 (holds A-H, table v0-v3), resumed by Sonnet 5.5 xhigh via Devin on 2026-10-02 20:35 (holds J-Q, tables v4-v10). Branch `night1/look`, not merged with `Opus-5.5-Loop-Night-1` this round.

## What was captured (all from the real game: `Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`; no crash, no OS dialog, one engine at a time)
- `stills/` (40 stills, **1920x1080 output, internal 100 % (`r.ScreenPercentage 100`, native)**): golden 18:24 S1-S8, night 22:00 S1-S8 + S4m, the L24 / L27 hours (S4 + S4w at 19:00 19:30 19:48 20:00 20:30, S4 + S4e at 06:30 07:00 07:30, S4 at 21:00 21:30), dawn mist 07:36 (S1 S4 S4e), clear 13:00 (S4 S8). Which hold / table each still comes from: `stills_source.json` (hold X = table v7 for most, hold Q3 = the committed table v10 for the verdict stills 19:30 S4 and 19:48-20:30, hold Y for S4 21:00 / 21:30). Settle rule: first pose of an hour 8-14 s after the hour change, next poses 5 s, at least 90 frames.
- `tod_lapse_S4.{mp4,json}`, `_sheet.jpg` (the L23b / L27f instrument): **960x540 output, internal 100 %**, 720 frames, stitched: 03:42-05:30 x4, 05:30-09:12 x16, 09:12-17:36 x4, 17:36-21:24 x16, 21:24-04:00 x4 (render sub-steps; fixed 1/60 s step; live pins `pp.AutoExposureSpeedUp/Down 40`; `segments[]` in the json, `reused_from_earlier_hold` = rendered in an earlier GPU hold of a table whose keys in that segment's hours are identical).
- `swing_tod_22.mp4`, `swing_tod_18h4.mp4` (P3 hero swing, **1920x1080, internal 100 %, fixed 1/60 s step**, 719 frames each, <= 15 MB) + hero-box luma json / telemetry csv / `.check.json`.
- Numbers: `TESTS_r07.md` (lapse, L27 dome table, L24 / L25 / L26, golden / night spec tables, clip numbers), `DOME_r07.*`, `TWILIGHT_r07.*`, `TESTS_tod.*`, `diag/holdM_verdict.md`, `diag/verdict_captures.md` (every capture of every verdict still).

## Machine conditions (context)
The GPU lock held 1-3 other agents' engines for most of the session (load average 4-16); a stills hold of 40 poses took 16 min, a 720-frame 1080p clip 27 min (the night clip's 719 frames), the dusk x16 lapse window 10-13 min. `gpu_slot` waits were 0 s. The lock's SIGTERM / SIGKILL at 2400 s never fired: chains check their budget before a step (`hold_lapse.sh`: per-segment run_game timeout 1700 s, not the 900 s default). One chain was stopped with `stop_ue.sh "/Users/midir/sm2-n1/look"` ("stopped cleanly") because its table file had been edited after it had read it.

## What changed in the look (details `diag/holdJ-P_findings.md`, table `Scripts/look_presets.json` built by `tools/perf_ue/sweeps/r07/make_v3.py --knobs diag/knobs_v10.json --bias-overrides lapse_bias_overrides.json`)
1. Fog directional inscattering cut hour by hour at twilight (the only knob that moves the far band toward the sun), haze colour x.4-.55 19:48-21:00.
2. Twilight tonemapper: shoulder x.4, slope x.88, white clip 0, red highlights x.8, saturation x.6 over 18:33-21:24 and 05:36-07:36 (ends on the last evening key, so 22:00 keeps the round-06 values exactly).
3. Sun cloud luminance 0 from 19:39 to 20:36 and 06:06 to 06:48; sky luminance factor x1.5 at 19:57-20:12, thinner clouds 19:54-20:24.
4. `fog.FogCutoffDistance` 0 only from 05:36 to 20:42 (round-07 start state: 0 on every key, which took S4 22:00 sky-far from +15.5 to -0.6).
5. Exposure: bias curve of the keys 18:27-18:45 made linear (the golden-to-dusk fall had a 3.1 Y frame step), one windowed x16 loop iteration per build (`lapse_loop_w.py`).

## Instrument facts
- `dome_check.py` reads rows 0-89 (sky) against box 450,192,1350,236 (far) of the 1920x1080 frame; B-R is mean(B) - mean(R) of rows 0-89; clipping counts any channel >= 250 in rows 0-150.
- Cloud noise: the same table renders a different volumetric cloud pattern in every capture; single stills move by about +-5 Y (sky-far) and +-0.3 % (clip). `diag/verdict_captures.md` lists every capture.
