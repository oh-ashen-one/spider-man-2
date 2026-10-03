# P4 Look / Sky: handoff (round 09, Claude Opus 5.5 high via Devin, 2026-10-03)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

## Round 09 result - start here
Branch `night1/look`, worktree `~/sm2-n1/look`, pushed. Rounds 07 / 08 / 09 are NOT merged; integration (`Opus-5.5-Loop-Night-1`) still carries look round 03. This round merged `origin/Opus-5.5-Loop-Night-1` first (city r11 far-shore LOD facades, terrain r05, traversal r26, characters r17).
Target (Opus director after city r11): the S4 perch on the INTEGRATED Manhattan map under the fixed golden preset (`Look_Rig_golden`), 1080p, sky / aerial-perspective settings only; lines written down as SPEC **L29** (sky <= 205; far band 25-32 under the sky on BOTH boxes; T2, T4, C12, T1, C11, C14, C15) plus guards (golden S3 / S7 / S8 Y<25, round-03 floors, other hours unchanged).
Evidence in `round-09/`: `TESTS_r09.md` (every number; generator `tools/perf_ue/round9_report.py --round docs/night1/look/round-09`), `NOTES.md` (capture facts, build, preset table), `TESTS_tod.md`, `DOME_r09.md`, `TWILIGHT_r09.md`, `diag/` (15 live sweeps `sweep*.txt` + variants, `bakes.txt`, S4 PNGs), `stills/` (80 stills), `S4_perch_golden.mp4` (5 s, 1.3 MB), `perf/`. Blind critic pack `/Users/midir/sm2-n1/_scratch/critic-P4-r09/pack` (26 pairs, key `../pack.key.json`, pairs `../pairs.json`, generator `tools/perf_ue/sweeps/r09/make_pairs.py` + `abpack.py`; both sides 1920x1080 before abpack's 84 % crop -> 1613x907). The critic of this round has NOT been run by the builder.
All captures: real game (`run_game.sh -game`, offscreen, `gpu_slot.sh capture`), 1920x1080 output, internal 1920x1080 (`r.ScreenPercentage 100`).

### Measured (final bake; S4 frame = `/Game/Maps/Manhattan_View_S4`, t = 38 s, PNG `round-09/diag/png/view_s4_1_t038.png`)
| line (target) | before (round-08 golden, same city) | round 09 |
|---|---|---|
| sky (0,0,1650,80) mean Y (<= 205) | 192.5 | **183.1** |
| far (450,192,1350,236) - sky (-32..-25) | -26.5 | **-31.7** (margin 0.3; second session -31.7, fixed-step movie frames at 8 / 13 s -31.5 / -31.7) |
| (0,150,1300,215) - sky (-32..-25) | -22.0 | **-27.2** |
| T2 % above 204 in (0,150,1300,300) (<= 10) | 0.5 | **2.0** |
| T4 flat / bright blocks (<= 10 %), flat / all | 0 of 0, 0 % | **0 of 1, 0 %** |
| C12 far - sky B-R (+-10) | -5.9 | **+8.1** |
| T1 silhouette std A / B / C (>= 12 px) | 0 / 79 / 0 | **0 / 26.7 / 0.7 (FAIL on A and C)** |
| C11 lap ratio (>= 6), flat 8x8 % | 3.9, 16.4 | **9.0, 1.2** |
| C14 far - river (5..35) | 18.4 | **30.3** |
| C15 rms far / near (0.25..0.45) | 0.09 | **0.26** |
| same pose in the golden tour of `/Game/Maps/Manhattan` (hero pawn at the perch) | -26.5 / -22.0 | -28.7 / **-24.7** (critic box FAILS by 0.3) |
| golden S1-S8 on Manhattan, L1 / L5 pass | 3 / 8 | 3 / 8 (merged r03 on the r03 city: 5 / 8) |
| golden Y<25 S3 / S7 / S8 % (city r10 13.2 / 1.4 / 7.8) | 51.7 / 44.1 / 19.2 | **51.9 / 53.2 / 17.9** (FAIL; S7 +9 points: the S7 sun glow in the street haze is aerial perspective, S7 mean 60 -> 42) |
| fixed midday L2 mean / L7 B-R / clipped 0.00 | (unchanged inputs) | 7 / 8 (S7 71.1) / 8 / 8 / 7 / 8 (S7 0.03 %); r03 8 / 8, 8 / 8, 6 / 8 |
| fixed night L3 / L8 / L13 (S1 S5 S6 blobs) | (unchanged inputs) | 7 / 8 (S3 33.2) / 8 / 8 / 9, 14, **4**; r03 8 / 8, 8 / 8, 14 / 14 / 9 (4K) |
| ToD 18:24 golden L1 / 22:00 L3, L8, L13, L22a | (table unchanged) | 5 / 8 / 8 / 8, 8 / 8, 10-13-4, 2.69 % (r08: 5 / 8 critic count, 8 / 8, 8 / 8, 10-13-3, 2.83 %) |
| L25a moon (S4m 22:00) | | 78.2 px / 255 (the Y >= 200 blob includes the halo; r08 22.5 px) |
| L27 dome (12 verdict stills, 42 lines) | | 9 / 12 stills, 39 / 42: S4 20:00 a +8.1, S4w 20:00 b 25.6, S4w 20:30 d -13.7 (r08 10 / 12) |
| L23b lapse | | not re-run (key table unchanged, `tod_guard.py --check`: 71 / 71 keys equal; round-08 lapse 3.07 / 2.20) |
| perf | | see `round-09/perf/PERF.md` |

### What changed (only `presets.golden` sky / atmosphere / fog keys; `round-09/NOTES.md` has the table)
- aerial perspective distance scale 5 -> 2.5, sky-and-AP luminance factor 0.5 (new key, darker AP veil), sky luminance 0.925, height-fog contribution 0.8: the far shore gets its contrast back (C11 3.9 -> 9.0, C15 0.09 -> 0.26) and sits 27-32 Y under the sky.
- sky light 2.5 -> 5.7: lowering the sky luminance also lowered the real-time sky-light capture (S4 near city, canyons); the sky light keeps the city ambient (S4 near box 55 -> ~74 Y). Sweeps 5-6: without it the vertical far-band gradient (crit box - far box) is 11-13 Y; with it 4.5-6.
- volumetric fog extinction 0.5 -> 2.0 (within 360 m only): near haze that AP 2.5 no longer gives (S8 Y<25 24.6 -> 17.9; it did not bring the S7 glow back).
- Time of day unchanged: `tod.derived.golden_r08` (round-08 golden values) replaces every `golden` base in the tod section; `look_tod.ATM_DEFAULTS` has the new param at its engine default 1. Check: `python3 tools/perf_ue/sweeps/r09/tod_guard.py --check caaf7002`.

### Findings (sweeps `round-09/diag/sweep1..15.txt`)
1. On the integrated map the round-08 golden S4 sky is 192.5, not the city frame's 229 (the city r11 frame comes from the city's own test map: manual +2 EV, its own fog). The golden failures there were the critic box (-22), C11 and C15 (a 5x AP veil).
2. Far contrast needs less AP; with less AP the far band drops 40+ Y under the sky unless the sky luminance drops too. The sky band is mostly fog-on-sky + clouds: `SkyLuminanceFactor` moves it 10-50 Y per unit, `FogCutoffDistance` (any value 3-200 km) darkens the far band itself (-20 Y), fog max opacity / directional inscattering / ground fog / Mie anisotropy did not separate far band and sky.
3. The two far boxes differ by 4.5-6 Y whenever C15 >= 0.25 (lower rows = nearer shore, less veil; left = sun side): the 25..32 window leaves ~1.5 Y for the sky. The tour pose and the view map differ by ~1.3 Y on the far box, so no knob set put both frames inside both windows (`diag/bakes.txt`).
4. T1 definition A (first row with Y < 215) is 0 for any sky under 215 and cannot pass with L29a; definition C (Y < column sky - 12) is ~1 because the horizon fog band (rows 100-130) is > 12 Y darker than rows 0-60.
5. Every AP reduction removes the S7 street glow (S7 mean 60 -> 40-45) and raises S7 Y<25 by 4-12 points; the round-08 golden on this city already has S3 / S7 / S8 Y<25 52 / 44 / 19 % (round 03 on the round-03 city 12 / 10 / 14 %): the darkening comes with city r11.

### Not met / open
T1 (A 0, C 0.7); critic box on the tour frame (-24.7); near-black guard (S3 / S7 / S8 51.9 / 53.2 / 17.9 % vs 13.2 / 1.4 / 7.8; S7 worse than before); far-box margin 0.3 Y; L27 9 / 12 (was 10 / 12) and the moon blob 78 px with the table unchanged (city / cloud draw); midday S7 mean, night S3 mean and S6 blobs (city since r03); lapse not re-run.

### Next (ranked)
1. Run the critic on `/Users/midir/sm2-n1/_scratch/critic-P4-r09/pack` (fresh, blind).
2. S7 glow and near-black: an S7-only lever is missing (the glow is Mie AP toward the sun); candidates not tried: higher `mie_scattering_scale` with lower AP distance, AP start depth, a golden local-exposure shadow lift (`pp.LocalExposureShadowContrastScale`, used in the ToD twilights) - it is post, not sky, so it needs the director's OK.
3. T1 C: remove the dark horizon fog band (rows 100-130) without `FogCutoffDistance` (e.g. second fog height offset / falloff, `fog.SkyAtmosphereAmbientContributionColorScale`).
4. Margin on the far box: sky light 5.7 -> 5.8 or sky luminance .90 (each moves far - sky by ~0.5 Y on the view frame).

### Commands (worktree root; every Unreal run through the lock)
- Manhattan build: `SM2_MANHATTAN_SCR=/Users/midir/sm2-n1/_scratch/look/manhattan gpu_slot.sh capture --label P4 --timeout 7200 -- python3 unreal/WebHomage/Scripts/build_manhattan.py --steps cpp,city_prep,city_extra,city,traversal,characters,look,map` (the city step alone took 2082 s; split across two holds: `--steps traversal,characters,look,map` after the first). City export on port 5205 by hand (NOTES.md).
- Live sweep: `python3 tools/perf_ue/sweeps/r09/gen_s4.py <v.json> '{"name": {"ap": 2.5, ...}}'`, then `python3 tools/perf_ue/capture_tour.py --round <dir> --presets golden --res 1920x1080 [--shots S4] --map /Game/Maps/Manhattan --variants <v.json> --settle 5 --first-settle 14 --work <dir>` (capture_tour wraps itself in `gpu_slot.sh capture`); numbers `tools/perf_ue/sweeps/r09/quick_s4.py <dir>` / `quick_all.py <dir>`.
- Apply + bake: `python3 tools/perf_ue/sweeps/r09/apply_golden.py '<knobs>'` (then re-run `tod_guard.py apply` ONLY if the golden_r08 block is missing; `--check` after every golden edit), `gpu_slot.sh capture --label P4 --timeout 7200 -- tools/perf_ue/sweeps/r09/hold_c.sh <out>` (golden rig + view S4 x2 + tour + 13 s movie; `NOMOVIE=1`), `hold_a.sh` (all rigs + golden + fixed presets), `hold_b.sh` (48 ToD stills + dome / r08 checks).
- Report + pack: `python3 tools/perf_ue/round9_report.py --round docs/night1/look/round-09`; `python3 tools/perf_ue/sweeps/r09/make_pairs.py <pairs.json> <norm>` + `abpack.py`.
- Perf: `gpu_slot.sh perf --label P4 --timeout 3600 --json <dir>/perf_gpu.json -- tools/perf_ue/sweeps/r09/perf_s4.sh <out>` (4K output, TSR 67 %).
GPU facts this round: queue waits 0-25 min per hold (island, tricks, water held 1-2 slots); one 9-min PAUSE (health monitor, WindowServer CPU 97 %) inside hold A; no engine crash.

# P4 Look / Sky: handoff (round 08, Claude Opus 5.5 high via Devin, 2026-10-03)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

## Round 08 result - start here
Branch `night1/look`, worktree `~/sm2-n1/look`, pushed (round 07 was NOT merged; integration still carries look round 03). Target (director after the round-07 critic): light the city under the twilight sky with SURFACE-ONLY light (sky light / fill, or local exposure) and keep the sky / far-band settings that pass L27. The pass lines are written down as SPEC **L28** (the critic's "Biggest gap" + secondary 1). Evidence in `round-08/`: `NOTES.md` (capture facts), `TESTS_r08.md` (every number), `L28_r08.md`, `DOME_r08.md`, `diag/` (sweeps A-D, baked checks, final-v4 numbers, loop, billboard crops, knob files). Blind critic pack `/Users/midir/sm2-n1/_scratch/critic-P4-r08/pack` (key `../pack.key.json`, pairs `../pairs.json`, 38 pairs: 17 against the private refs, 8 round 03 vs round 08, 13 round 07 vs round 08 incl. the lapse sheet; both sides of every pair the same pixel size, 1920x1080 for stills). The critic of this round has NOT been run by the builder.
All captures are real-game (`run_game.sh -game`, offscreen, `gpu_slot.sh capture`): stills / clips 1920x1080 internal 100 %, lapse 960x540 internal 100 %.

### Measured (final committed captures)
| line | round 07 (final) | round 08 (final stills `round-08/stills`, one session) |
|---|---|---|
| **L28a / L5** S4e 07:00 mean, Y<10, clipped | 27.9, 54.5 %, 0.01 % | **65.7, 0.00 %, 0.006 %** |
| **L28a / L5** S4e 07:30 | 39.1, 34.4 %, 0.00 % | **71.7, 0.00 %, 0.00 %** |
| **L28a / L5** S4w 19:00 | 48.0, 5.5 %, 0.00 % | **70.8, 0.00 %, 0.00 %** |
| **L28b** sky rows 0-89 HSV saturation (same three) | .49 / .44 / .55 | **.490 / .443 / .546** |
| **L28c** S4 20:30 sky B-R (>= 0) | -34.4 | **+6.6** |
| **L28d** sub-horizon disk on S4w 19:30-20:30 | 32-36 px at (1404, 387) | **0 blobs**; the round-07 disk box holds lit windows only (`diag/disk205_r07_vs_v3.png`) |
| L27a-e (dome_check, 12 verdict stills; 42 lines) | 12 / 12 stills, 42 / 42 | **10 / 12 stills, 40 / 42 lines**: S4e 06:30 8-row step **25.1** (b <= 25), S4w 20:30 sky B-R **-13.2** (d <= -20); S4 20:00 sky-far +16.8, S4w 20:00 step 23.6, S4w 19:30 clipped 0.05 %; L27e 46.1 >= 42.6. Second capture (`diag/second_capture`, other cloud draw): 9 / 12 (S4e 06:30 sky-far +9.3, S4w 19:30 clipped 1.72 %, S4w 20:30 -11.6) |
| L23b stitched lapse max jump / p99 / frames > 3 / > 1.5 | 2.58 / 2.07 / 0 / 33 | **3.07 / 2.20 / 1 / 37** (FAIL; dawn x16 segment 2.63, dusk x16 segment 3.07 at 19:06; max mean 98.2, clipped <= 0.16 %) |
| r03 midday floor (fixed midday preset map, mean / B-R) | (r03: 8 / 8, 8 / 8) | mean **7 / 8** (S7 75.4; r03 89.0, see cross-piece), B-R 8 / 8, clipped 0.00 % on 6 / 8 (r03 6 / 8). ToD 13:00 overcast: 5 / 8 |
| r03 night floor L3 / L8 / L13 | ToD 22:00: 8 / 8, 8 / 8, S6 4 blobs | ToD 22:00: **8 / 8, 8 / 8**, L13 S1 10 / S5 13 / **S6 3**; fixed night preset map: L3 7 / 8 (S3 33.9), L8 8 / 8, S6 4 blobs |
| r06-hold-C floors: L25a moon, golden L1, L22a | 30.8 px / 255, 7 / 8 (S4 97.7), 2.71 % | **22.5 px / 255, 7 / 8 (S3 46.2 out, S4 97.3), 2.83 %**; L26 0.436 (<= .6); L24a 8 / 9 (21:00 -13.4 as in round 07) |
| clips (box luma mean / frames < 40 / max clipped px in box) | 22:00: 58.0 / 91 / 2159 | 22:00: 55.7 / 108 / 2191; 19:00 (new): 96.5 / 0 / 86 |

Not met: L27 S4e 06:30 b (25.1) and S4w 20:30 d (-13.2); L23b max 3.07 / p99 2.20 (round 07 2.58 / 2.07); midday preset S7 mean; L13 S6; night clip hero box 108 frames < 40.

### What changed (sweeps `round-08/diag/sweepA..D.md`, baked checks `diag/check2`, `diag/check3`, `diag/final_v4`)
1. **Local exposure for the twilight city** (the structural fix; per-pixel post that lifts only regions darker than a shifted middle grey, so the sky band and most of the far band keep their values; AE histogram unchanged): new keyed params `pp.LocalExposureShadowContrastScale`, `pp.LocalExposureBlurredLuminanceBlend` (.2 on every key) and `pp.LocalExposureMiddleGreyBias` (defaults = off, in `look_tod.preset_params`). Shadow contrast 1 outside the twilights; dawn .8 05:36-06:00, .3 06:30, 0 06:54-07:36, 1 at 08:48; dusk 1 at 18:27, .55 18:45, .2 19:00, .5 19:30, .75 19:45, 1 at 20:03. Middle-grey bias -2 until 06:30, -1.25 06:54-09:30, -1 from 16:30. Sweeps B / D: bias -1.5 lifted S4e 07:00 by +32 Y and S4 by +8.6 (the most selective setting); a stronger sky light lowered the S4 sky through the metering (19:00 sky-far +10 -> -11) and the horizon fills at tens of lux did not register: neither is used.
2. **The sub-horizon "sun disk" was the horizon fill lights' specular glint on the river** (`fill.W`, 10 deg up, water roughness .06): the four fills are diffuse-only (`build_look.py`: `specular_scale` 0). Sweep B with the fills at 0 lux removed it; every baked capture since shows no disk (`diag/disk_fill0_sweepB.png`, `diag/disk205_r07_vs_v3.png`, `L28_r08.md`).
3. **Blue hour** (keys 20.4 / 20.6, ramps from 20.2 and to 21.0): SkyLuminanceFactor x[.37, .95, 1.85] and a warm fog directional-inscattering lobe toward the sun (.008, exponent 12) that starts at 4 km (`fog.DirectionalInscatteringStartDistance` 4e5 on the keys 20.2-21.0), so it warms the sky toward the sun and not the far band. Sweeps C / D: a stronger lobe or a nearer start turned the haze band toward the sun into an 8-row step (L27b 28-120) or lifted the far band (L27a < 0); with S4 >= 0 the sun-facing S4w 20:30 sky stays at -11..-17 B-R (L27d wants <= -20).
4. `sunc.CloudScatteredLuminanceScale` x.3 19:24-19:33 (aimed at the clipped cloud streaks on S4w 19:30; the check sessions showed the clipping does not follow this knob - the final session has 0.05 %).
5. C++ `AWHLookTimeOfDay`: `skyc.<property>` reaches the SkyLight component (the sweeps used `skyc.VolumetricScatteringIntensity`; not in the final table).
6. Lapse: one closed-loop iteration of the twilight exposure biases (`lapse_loop_w.py`, x16 windows, slope 1.1, max delta .6 EV; the keys 06:57-07:03, 07:27 and 18:57-19:03 held so the L28a stills keep their exposure). Holding keys left 0.3-0.4 EV steps next to them (dawn lapse segment max jump 9.25, `diag/lapse_seg1_untapered.json`): the final bias file tapers the loop deltas into the held keys (06:42-06:54, 07:06-07:09, 18:54, 19:06-19:15), and 19:54 / 20:12 are set by hand to -.28 / -.42 (the loop's +.07 / +.09 took the S4w 20:00 8-row step to 26.3). `round-08/lapse_bias_overrides.json`.
Table builder `tools/perf_ue/sweeps/r08/make_v4.py` (= round-07 `make_v3.py` + `knobs_v10.json` + the round-07 biases, byte-identical with an empty knob file, then the round-08 schedules); knob file `round-08/diag/knobs_r08.json` (generator `make_knobs.py`; history v1-v5 in `diag/`). `Scripts/look_presets.json` = `make_v4.py --knobs diag/knobs_r08.json --r07-bias round-08/lapse_bias_overrides.json` (checked byte for byte).

### Cross-piece (city-owned, NOT edited here) - brand read
- The rooftop wall mural of S3 (golden-rooftop pair) is the city's ORIGINAL replacement art for ad cell `ts_ads` P 27, `art_P27` "PLANT A TREE" in `tools/export/ip_original_art.py` (applied by `tools/export/ip_sanitize.py`). Its bottom line is `GREENER BLOCKS START HERE`. At native resolution on `round-08/stills/tod_S3_1920x1080_h18.4.jpg` (crop `diag/brand_S3_native.png`, x3 `diag/brand_S3_x3.png`) the parapet lamps hide "GREENER BL" and the tight word spacing joins the rest into `OCKS START HE...` / `OCKSTART`, which reads like the real studio name ROCKSTAR. It does not spell a real brand, but it evokes one in this view: P1 should change the line (e.g. `PLANT ONE ON YOUR STREET`) or widen the spacing. No other brand read in the round-08 stills (AMBROCHE as in rounds 05-07).
- Midday floor: the fixed midday preset map S7 reads 75.4 (round 03: 89.0) with identical P4 inputs (the midday preset has no fills; round 08 changed only time-of-day keys and the fills) - the S7 facades and glass are darker than in round 03 (city content since round 03).

### Honest caveats
- The volumetric cloud pattern differs between sessions of the same table: the L27 margins at S4e 06:30 (sky-far +9.3 / +18.0, 8-row step 12.4 / 25.1) and S4w 19:30 (rows 0-150 clipped 1.72 % / 0.05 %) move across the limits between captures (`diag/second_capture` vs `DOME_r08.md`); the round-07 committed stills had the same spread (round-07 `diag/verdict_captures.md`).
- Build bookkeeping (`round-08/NOTES.md`): the committed stills come from the bake before the final bias taper; the taper changed only bias keys whose Catmull-Rom neighbourhoods do not include a still hour, and a second capture of a taper build reads the same L28a values. The midday preset stills come from the v5 bake (identical midday inputs). The lapse x4 day / night segments are reused from the previous bake (identical keys there).
- Lapse: the L28a stills need the city lift at exactly 07:00 and 19:00; S4 (the lapse view) gets +9..16 Y there, so the twilight ramps of the lapse are steeper than in round 07. The first loop iteration with the still keys held created bias steps (dawn segment max 9.25); the tapered file still leaves the twilight segments above 3 Y per frame in places (see the measured table). The loop keys should not be held; the next round should either let the loop move the 07:00 / 19:00 biases and raise the local exposure to compensate, or widen the local-exposure ramps to >= 1.5 game hours.
- Blue hour vs L27d: with the sky factor that makes S4 20:30 blue, the sun-facing S4w 20:30 sky is -11..-17 B-R; the warm lobe that would take it under -20 needs a strength that turns the far haze band into an 8-row step (sweeps C / D).
- `sunc.CloudScatteredLuminanceScale` x.3 at 19:24-19:33 did not change the S4w 19:30 clipping in the check sessions (1.48 -> 1.40 %); the clipped streaks are lit by something else (sky luminance factor 9 / 3 / 1.1 at 19:30 is the next suspect).
- Night clip hero box 55.7 mean / 108 frames < 40 (round 07: 58.0 / 91): the fills are diffuse-only now and the hero lost their specular sheen; the night stills keep L3 / L8 8 / 8.
- Perf not measured (not the target; local exposure adds a bilateral grid pass).

### Next (ranked)
1. Run the critic on `/Users/midir/sm2-n1/_scratch/critic-P4-r08/pack` (fresh, blind).
2. Lapse L23b (max <= 3, p99 <= 1.5): one loop iteration WITHOUT held keys (`hold_loopw.sh`, `KEYS_H` = the round-07 list), then re-check L28a at 07:00 / 19:00; if they drop under 59, deepen the local exposure there (shadow contrast is already 0 at 06:54-07:36: lower the middle-grey bias to -1.0 at dawn, sweep D numbers) instead of holding biases.
3. S4w 20:30 L27d with the blue S4: a cloud-colour or haze-colour key only on the sun side is not available; test `fog.DirectionalInscatteringStartDistance` 6-8 km with a weaker lobe and exponent 20-30 (narrow), or accept the -11..-17 and ask the critic.
4. L27c S4w 19:30 cloud streaks and the S4e 06:30 margins: they depend on the cloud draw - repeated captures (`gen_plans_r08.py --set check`, 10 min) before a commit decision, report every capture.
5. City-owned: the `GREENER BLOCKS START HERE` line (cross-piece above), the midday S7 darkening since round 03.

### Commands (worktree root; every Unreal run through the lock)
- Table: `python3 tools/perf_ue/sweeps/r08/make_v4.py --knobs docs/night1/look/round-08/diag/knobs_r08.json --r07-bias docs/night1/look/round-08/lapse_bias_overrides.json --in-place`, bake `tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod` (inside `gpu_slot.sh capture`).
- Live-pin sweeps on the baked table: `tools/perf_ue/sweeps/r08/gen_sweep_c.py --out <dir> --name x --hours ... --variants '{json}'` (every group pins every round-08 param: an unkeyed pin stays on the volume after `wh.ToDClear`, found in sweep A), then `gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r07/hold_sweep.sh <plan> <dir>`; numbers `tools/perf_ue/sweeps/r08/quick.py <dir>`.
- Bake + stills: `[R07_BIAS=<bias json>] [MIDDAY=1] gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_build_stills.sh <knobs> <out> full|check` (check = 17 pass stills, ~15 min with the bake; full = 48 stills, ~30 min).
- Loop iteration: `KEYS_H=... SLOPE=1.1 MAXD=0.6 gpu_slot.sh capture ... -- tools/perf_ue/sweeps/r08/hold_loopw.sh <knobs> <bias in> <dir>` (~22 min; do NOT hold keys out of it without tapering, see caveats); lapse `tools/perf_ue/sweeps/r08/hold_lapse.sh` (`REUSE=1` keeps rendered segments); sequential final holds `final_chain.sh` / `final_chain2.sh` (started from the builder's shell; they wait on the previous hold's PID).
- Checks: `tools/perf_ue/r08_check.py --dir <stills>` (L28), `dome_check.py` (L27), `round8_report.py --round docs/night1/look/round-08` (TESTS_r08.md), pack `tools/perf_ue/sweeps/r08/make_pairs.py <pairs.json> <norm dir>` + `abpack.py`.
GPU facts this round: no wait for the lock (terrain, water, life held 1-2 slots); live-pin stills 16-30 s per pose; a 17-pose check 10 min + 4-5 min bake; 48 stills 21-25 min; loop iteration 22 min; stitched lapse > one 2400 s hold when all five segments render (REUSE across two holds).

# P4 Look / Sky: handoff (round 07 finished, 2026-10-03 03:40; started by Opus 5.5, resumed by Sonnet 5.5 xhigh via Devin 20:35)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

## Round 07 result - start here
Branch `night1/look`, worktree `~/sm2-n1/look`, pushed. Target: twilight dome continuity (SPEC L27, `critic/round-06-CRITIC.md` "Biggest gap"). Evidence in `round-07/` (`NOTES.md` capture facts and conditions, `TESTS_r07.md` all numbers, `stills_source.json`, `diag/`), blind critic pack `/Users/midir/sm2-n1/_scratch/critic-P4-r07/pack` (29 pairs: 14 against the private refs, 15 round 06 vs round 07; key `../pack.key.json`, `make_pairs.py` + `abpack.py`). The critic of this round has NOT been run by the builder.
All captures are real-game (`run_game.sh -game`, offscreen, `gpu_slot.sh capture`): stills / clips 1920x1080 internal 100 %, lapse 960x540 internal 100 %.
### Measured (final committed stills, table v10)
| line | start of the resume (hold F, committed by Opus) | final |
|---|---|---|
| L27 a-d on the 12 verdict stills (S4 + S4w 19:30 19:48 20:00 20:30, S4 + S4e 06:30 07:00) | 26 of 42 | **42 of 42** (`diag/final_verdict.md`; sky-far +14.3 .. +62.8, 8-row step <= 24.3, clip <= 0.22 %, facing B-R -32 .. -78) |
| L27e S4 20:30 vs 22:00 mean | 46.9 vs 40.7 | 46.6 vs 42.3 |
| L23b/L27f stitched lapse max jump / p99 / frames > 3 / > 1.5 | 4.79 / 2.79 / 7 / 48 | **2.58 / 2.07 / 0 / 33** (p99 <= 1.5 not met) ; max mean 98.2, clipped <= 0.14 % |
| L24a (S4 sky band above far band, 9 hours) | 7 of 9 (21:00 -11.2, 21:30 -1.3) | 8 of 9: 21:00 fails (-11.7; -12.9 in the previous capture), 20:00 +30.9 (round 06: 20:00 fails, 21:00 passes) |
| L10 night S4 22:00 sky-far (round 06 +15.5) | -6.7 | +16.5 (+15.0 / +20.8 in other captures) |
| L25a moon disk (S4m, Y >= 200 blob equivalent diameter; round 06 20.5 px) | 127 px (a blown halo, blob 12690 px) | 30.8 px, peak 255 |
| L25b sky high-pass std (S4m, >= 3) | - | 2.32 (fails; round 06 2.17) |
| L26 dawn S1 correlation (<= 0.6; round 06 0.597) | - | 0.54 |
| golden 18:24 (hold X stills) | - | L1 7 of 8 (S3 46.8 out), S4 97.7, S7 clipped 1.80 %, Y<10 4 of 8, p5 <= 12 6 of 8 (round-06 C: 7 / 98.6 / 2.05 / 5 / 6) |
| night 22:00 | - | L3 / L8 8 of 8, L22a 2.71 %, median 33.9, L13 blobs 10 / 13 / 4 |
| hero swing night clip (box luma; frame mean Y, B-R, clipped, L18 p50) | - | box mean 58.0, 91 of 718 frames < 40, clipped px max 2159 (round 06: 58.0 / 92 / 2103); frame 35.6 Y, B-R +3.5, 0.54 %, L18 .57 |
| hero swing golden clip | - | box mean 89.6, 24 of 718 frames < 40, clipped px max 11041; frame 57.9 Y, B-R -33.4, 0.33 %, L18 .74 |
Not met: L25b, the moon halo (ring Y at r=100 122-190 in single captures; round 06 160; critic wants <= 60), L24a 21:00, lapse p99 <= 1.5, golden Y<10 4 of 8 and S3 46.8, L13 S6 4 blobs, 13:00 midday cloud structure, golden sun disk / bloom core (critic secondary items 1, 2, 4: not worked this round).
### What changed (details `round-07/diag/holdJ-P_findings.md`, `SPEC.md` L27 "Round-07 design")
Fog directional inscattering cut per hour; haze colour x.4-.55 19:48-21:00; twilight tonemapper (shoulder x.4, slope x.88, white clip 0, red highlights x.8, saturation x.6) ramping in 18:33-19:00 and out by 21:24 / 05:36-07:36; sun cloud luminance 0 19:39-20:36 and 06:06-06:48; sky factor x1.5 19:57-20:12; thin clouds 19:54-20:24; `FogCutoffDistance` 0 only 05:36-20:42 (7e5 = unfogged sky at night: the round-07 start state had 0 on every key and lost the night depth cue); linear exposure bias 18:27-18:45; loop biases. Table builder `tools/perf_ue/sweeps/r07/make_v3.py` (new knobs `tw_mul`, `cutoff_sched`; `sun_cloud`, `tw_dir`, `tw_minev` ...), knob files `round-07/diag/knobs_v4..v10.json` (v10 = committed), bias file `round-07/lapse_bias_overrides.json`.
### Honest caveats
- Cloud noise: every capture of the same table draws a different volumetric cloud pattern (sky-far +-5 Y, clip +-0.3 %). `diag/verdict_captures.md` lists the 5 captures of every verdict still: S4w 19:30 clipped 0.35 % in two of four captures of the same hour (committed one 0.06 %), S4 20:00 sky-far 9.3 / 13.1 / 10.8 / 30.9 (the margin of the final table is larger: v10 lowered the 20:24-20:36 biases).
- Stills of other hours are from hold X (table v7) / hold Y (v8): `stills_source.json` says which; later tables changed only keys outside those hours (checked by diff of the key values).
- Segments 0 / 1 / 2 / 4 of the lapse come from earlier holds (tables v8 / v9) whose keys in those hours equal v10 (`segments[].reused_from_earlier_hold`); segment 3 (dusk) is from the final table.
- The perf was not measured (not this round's target); the twilight changes add no passes.
### Next (ranked)
1. Run the critic on `/Users/midir/sm2-n1/_scratch/critic-P4-r07/pack` (fresh session, blind). Expect the weakest items: moon halo, L25b, midday cloud structure, golden sun core.
2. Night sky: moon halo (ring Y at r=100 <= 60, `S4m`): bloom / lens flare / Mie / `moonc.*` single-capture pins did not separate from the cloud noise; needs repeated captures (`gen_sweep_*.py` + `/tmp`-style `moonq` ring analysis is in `diag/holdJ-P_findings.md` item 11) or a darker night Mie glow key.
3. L24a 21:00 (city lights lit far band vs afterglow sky: `pp.AutoExposureMinBrightness` / afterglow `atm.SkyLuminanceFactor` at 21:00), lapse p99 <= 1.5 (the dawn rise 07:50-08:10 is ~2.4 Y per frame, the dusk bump 20:14-20:20 2.5 Y: both from natural scene change, would need a second loop iteration with a smoother target `--slope 1.0`).
4. Golden: S3 46.8 (L1), Y<10 (S1 / S3 / S5 / S7), golden bias .85 vs .95 trade-off (hold E vs F).
### Commands (worktree root; every Unreal run through the lock)
`python3 tools/perf_ue/sweeps/r07/make_v3.py --knobs round-07/diag/knobs_v10.json --bias-overrides round-07/lapse_bias_overrides.json --in-place` writes the table; `tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod` bakes it; live-pin sweeps: `gen_sweep_*.py --out <dir>` then `gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r07/hold_sweep.sh <plan.json> <out>`; `hold_build_stills.sh <knobs> <bias> <plan> <out>` (bake + stills); `hold_d.sh loop|build,stills|lapse|clips` (HOLD_DIR, STILLS_SET) = the old chain; `hold_loopw.sh` (one loop iteration on chosen windows); `hold_lapse.sh` (`REUSE=1` to keep segments; per-segment timeout 1700 s); clips: `capture_looks.py --presets tod@22 --clips --no-stills --no-warmup --res 1920x1080 --timeout 2100`; `verdict.py <dome json>`; `round7_report.py --round docs/night1/look/round-07`.
GPU facts: no wait for the lock tonight (other agents held 1-2 slots); a loop iteration (dawn + dusk x16 windows) 21-24 min, a dusk-only window 13 min, 40 stills 16 min + 4 min build, lapse 5 segments 33 min, 720-frame 1080p clip 27 min.

# P4 Look / Sky: handoff (round 06, Sonnet 5.5; started 2026-10-01 20:50, resumed 2026-10-02 05:02)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

## Round 06 result (2026-10-02 08:50, Sonnet 5.5, resumed 05:02 after the API 502) - start here
Branch `night1/look`, worktree `~/sm2-n1/look`. All captures from the real game (`Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`), stills / clips 1920x1080 internal 100 %, lapse 960x540. Commits: a130c4b = hold 7 (B: x4 lapse, 40 stills, 2 clips), **d81f8f9 = hold 8 (C) = the round's final captures** (stitched lapse, 42 stills; the two swing clips are B's). `round-06/TESTS_r06.md` / `TESTS_tod.md` / `TWILIGHT_r06.md` have every number; critic pack of C: `/Users/midir/sm2-n1/_scratch/critic-P4-r06/pack` (14 pairs, `make_pairs.py` + `abpack.py`).
### What the round measured (hold 4 = the state at the 502 | B | C)
| line | hold 4 | B | C |
|---|---|---|---|
| L23b max jump / p99 / clipped / mean | 12.81 / 4.13 / 5.36 % / 107.9 (x1 + render cvars) | 5.75 / 3.48 / 1.94 % / 105.4 (x4) | 8.10 / 3.21 / 2.42 % / 114.3 (x4 + x16 stitched: the faithful instrument) |
| L24a (S4 sky band over far band, 9 hours) | 8 of 9 (20:00) | 8 of 9 (20:00) | 8 of 9 (20:00: 13.8 Y sky over 38.1 Y far; 19:48 also fails) |
| L24b (sun-facing B-R <= -20) | 8 of 9 (20:30) | 8 of 9 | 8 of 9 (S4w 20:30 +4.4) |
| L25a moon disk >= 12 px, Y >= 200 | pass (checker bug read 2.0) | 21.2 px / 255 | 20.5 px / 255 |
| L25b sky high-pass std >= 3 | 2.06 | 2.11 | 2.17 (fail; the cloud offset does not reach the baked rig, finding 7) |
| L26 S1 07:36 vs 18:24 correlation <= 0.6 | 0.620 | 0.602 | 0.597 |
| golden 18:24 L1 mean 61..100 on >= 7 of 8, S4 <= 100 | 7 of 8, 99.7 | 6 of 8 (S4 100.7) | 7 of 8 (S3 59.0), S4 98.6 |
| golden Y<10 <= 8 % (merge bar 8 of 8) | 3 of 8 | 5 of 8 | 5 of 8 (S3 8.6, S5 9.1, S7 11.7) |
| golden p5 <= 12 on >= 6 of 8 / clipped <= 1.8 % on 7 of 8 | 7 of 8 / 8 of 8 | 6 of 8 / 7 of 8 | 6 of 8 / 7 of 8 (S7 2.05 <= 3.1) |
| night 22:00 L3, L8 | 8 of 8, 8 of 8 | same | same |
| night L13 blobs S1 / S5 / S6, L14 S1 / S5 / S6, L22a | 9 / 13 / 4, -, 1.72 % | 9 / 13 / 3, -, 2.47 % | 9 / 12 / 4 (S6 fails), L14 S1 + S5 pass (S6 p90 72), L22a 1.99 % |
| hero swing_tod_22 box: mean / frames < 40 / clipped px | 58.0 / 92 / 675 frames, max 2103 | 58.2 / 91 / 676, 2104 | (same clip) |
The round target ("sky lit and legible at every hour, no exposure excursions") is NOT met: L23b fails in every variant (the remaining excursions are two rig cliffs, below), L24a 20:00 and L24b 20:30 fail, L25b fails. What improved: the clipped red sky (5.4 % -> 1.9-2.4 %), the black hole at 19:48-20:30 (S4 stills 15 -> 32 Y at 20:00 in C), the dawn ramp (jumps > 3 in the faithful x16 dawn window: 9 -> 2), the pack's twilight stills (amber instead of blood red), L26, golden S4 <= 100, three instrument bugs.
### Next (ranked) - hold 9 (D) is prepared and NOT run (it waited behind 3 other holds for > 1.5 h, so I stopped its queue entry at 08:43; nothing of mine is running)
1. **Run D**: `mkdir -p $SM2_LOOK_SCRATCH/r06/final6d && cp docs/night1/look/round-06/diag/knobs_d_r06.json $SM2_LOOK_SCRATCH/r06/final6d/knobs_d.json` (or regenerate: `python3 tools/perf_ue/sweeps/r06/make_knobs_d.py --knobs-c $SM2_LOOK_SCRATCH/r06/final6c/knobs_c.json --overrides $SM2_LOOK_SCRATCH/r06/final6c/loop/bias_overrides.json --out .../final6d/knobs_d.json`), make sure the C++ is built (`unreal/WebHomage/Scripts/build_editor.sh`, editor / game closed, 12 s; the source has `sun.SurfaceGain`), then `/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label look --timeout 21600 -- tools/perf_ue/sweeps/r06/hold6d.sh` (~35 min: windowed x16 loop 3 iterations -> table in place -> headless rebuild -> stitched lapse -> 46 stills incl. the baked-vs-runtime night stills `h22b` / `rt_h22` / `rt0_h22`). D = C + the CLIFF FIX (finding 5) + finer keys at the cliffs + the dawn biases of C. It rewrites `look_presets.json`, the stills and the lapse of `round-06/`; C is committed (`git checkout d81f8f9 -- unreal/WebHomage/Scripts/look_presets.json docs/night1/look/round-06` restores it). Then `tools/perf_ue/round6_report.py --round docs/night1/look/round-06`, regenerate the pack, commit.
2. Baked vs runtime key table (finding 7): the night stills `rt_h22` (table loaded at run time) are blue and foggy (Y 105) while the baked ones are dark (Y 44): the table text is identical. Read D's `h22b` / `rt_h22` / `rt0_h22` stills (rt0 = the same table with the cloud offset zeroed): if rt0 looks like the baked one the baked rig ignores `cloudv.Layout_GlobalTexturePlacement` (L25b then needs the cloud pattern fixed in `Apply` / `Bind`), if rt0 is still foggy something else differs (hour history, fog / sky caches).
3. L24a 20:00 / L24b 20:30 (the sky is the darkest thing between the sun and the moon; the far band is fog + early windows), L13 / L14 on S6 (night street lamps), golden Y<10 (S5 / S7), L15b (the bbox contains lit windows).
### Findings of this resume (all measured, real game)
1. **Moon checker bug fixed** (`twilight_check.moon_disk`): a far speck replaced the disk, the report read 2.0 px for a 21.7 px disk (L25a was already passing). A night highlight roll-off .8 does not remove clipped pixels (hero box max 1922 vs 2103 px: they are lit windows; the suit reads red / blue) and only lowers the sky high-pass: dropped. L15b as written (0 clipped px in the hero bbox) is not reachable without darkening the windows.
2. **The round-05 / hold-4 lapse lag is the engine's temporal lighting caches (~12-35 rendered frames).** Hold 4's instrument (render settings `TimeSlice=0` + `r.VolumetricFog=0` at 2 h/s) put a one-frame step of 12.8 Y at 18:58 into the lapse and switched the volumetric fog off. `capture_tod_lapse.py --substeps N` runs the clock at 2/N h/s (fixed 1/60 s step) and keeps every N-th frame: no render setting changed, fog on. x2 is not enough (D2: step 13.1, wash at 20:30), x4 removes the wash but reads 54.6 / 39.7 / 42.2 Y at 19:48 / 20:00 / 20:30 against 15.0 / 14.9 / 22.0 for settled stills; x16 reads 17.8 / 18.1 / 19.2 (the truth). The final lapse is stitched from x4 (day, night) and x16 (twilights) segments (`lapse_stitch.py`), each starting 0.3 h early.
3. Twilight variants (hold 6A, settled stills): the hold-4 factor [30, 6, 1.2] saturates the red channel (S4 clipped 3.7-5.6 % at 06:30, 07:00, 19:00, 19:30); lower factors cut it to 1.5-4.8 %, denser twilight clouds (coverage .25, density .03) to 0.4-1.2 % without losing L24b at 06:30-07:30 and 19:00-19:30; at 20:00 the denser clouds turn the sun-facing sky neutral, so they thin out by 19:48. Golden black lift `pp.ColorOffset` .0012 -> Y<10 on 5 of 8 stills (p5 <= 12 on 6 of 8), .0022 -> p5 <= 12 on only 5 of 8: C uses .0015. Dawn mist 4.5 -> L26 0.597.
4. **Dawn bumps are rig steps** (fixed in C, 9 -> 2 frames > 3 in the x16 dawn window): the keys at 07:00 / 07:12 / 07:24 are mixes of different bases and zigzag in fog colour, height falloff, start distance, sun temperature, sky light, contrast and the exposure window; C puts them on the line between 06:48 and 07:36, makes the sun lux ramp geometric (it went x4.5 between 06:15 and 06:30) and lets the city lights fade later (`make_final_knobs.py --dawn-smooth`).
5. **The dusk / dawn brightness cliffs are the tail of the sun surface-light ramp** (found in C's x16 windows: -8 Y per frame at 19:40, mirror +5 at 06:35): at 19:40 the sun still has 22500 lux for the sky and the clouds, a surface scale of 0.001 still puts ~20 lux of UNSHADOWED sun on every surface (shadows are off below 0.02), ten times the twilight ambient, until the ramp ends. No bias loop can cancel it (the cliff is in the scene). Fix prepared in D: C++ table param `sun.SurfaceGain` (default 1) multiplies the surface scale; `make_knobs_d.py` keys it so the effective surface lux decays by ~x3 per 6 game minutes (33880 at 18:48, 5357 at 19:12, 274 at 19:24, 2 at 19:30, 0 from 19:33; mirror at dawn). Untested.
6. C's windowed loop (`lapse_loop_w.py`, x16 windows, spline least squares on the 15 + 15 twilight keys, DP target `lapse_opt.design_target`) converged in the dawn and dusk descent but could not cancel the cliffs; its exposure raises at 19:39-20:00 (+1.8 EV) brighten the far band (L24a 20:00 38 Y) and blow out the sun-facing S4w at 19:48-20:00 (clipped 8.9 %); D restarts the dusk biases.
7. **Baked vs runtime key table**: `cloudv.Layout_GlobalTexturePlacement [0, 30000, 0, 0]` changed the 22:00 cloud pattern when the table was loaded with `wh.ToDLoad` (hold 6A sweep N1: moon blob 132 px) but not in the baked rig (S4m identical to the hold-4 still); hold 8's `rt_h22` night stills (loaded at run time at the END of the session after the day groups) are blue / foggy (Y 105 vs 44). Same text, same params; unexplained (see Next 2).
### Files
`tools/perf_ue/`: `capture_tod_lapse.py` (`--substeps`, `--drop-first-hours`, `--trim-end`), `lapse_stitch.py`, `lapse_loop.py` (whole-day loop, spline least squares), `lapse_loop_w.py` (twilight windows at x16), `lapse_opt.py` (`design_target`: slope-limited DP target with pinned anchors, clip ceiling, asymmetric raise penalty), `twilight_check.py` (moon fix), `round6_report.py`. `sweeps/r06/`: `make_v2.py` (table builder; knobs `tw_fac_pts`, `tw_hl_r`, `tw_cloud`, `night_hl`, `cloud_offset`, `tw_fog_scale`, `tw_sun_lux`, `sun_ramp`, `surface_gain`, `lights_dawn`, `extra_keys`; defaults reproduce the hold-4 table), `gen_plans_e.py` + `hold6a.sh` + `analyze_a.py` (hold 6A variants), `make_final_knobs.py` (`--dawn-smooth` = C), `make_knobs_d.py`, `gen_plans_f.py` (final stills plan), `hold6b.sh` / `hold6c.sh` / `hold6d.sh` (chains B / C / D), `final_r06.sh` / `hold4.sh` (hold-4 history). C++ `WHLookTimeOfDay.cpp`: `sun.RampLo` / `sun.RampHi` (-4 / 8 in the table), `sun.SurfaceGain`. Evidence of every hold: `round-06/diag/` (`hold6a_analysis.md`, contact sheets, D0 / D2 lapse jsons, `knobs_final_r06.json`, `knobs_d_r06.json`).
GPU facts: the lock waited 54 min (hold 6A), 48 min (B), 65 min (C); a health-monitor auto-pause (05:22, my x4 lapse + another agent's 4K capture, WindowServer 2 %) held every launch for 10 min and its auto-lift needs 10 calm minutes; a hold ends with SIGTERM + 10 s + SIGKILL at 2400 s, so the chains only start steps that fit their 2250 s budget and never leave an engine running at the limit; a queued placeholder (`sweeps/r06/hold2.sh` + `$SM2_LOOK_SCRATCH/r06/NEXT_HOLD`) keeps the place in the FIFO while the chain is being finished.

# P4 Look / Sky: handoff (round 05, Opus 5.5; resumed 2026-10-01 17:06 after the 15:41 owner pause)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

## Round 05 result (2026-10-01 20:25, Opus 5.5) - start here
Fresh captures, all from the real game (`Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`), 1920x1080 output, internal 100 % (`r.ScreenPercentage 100`):
- `round-05/stills/tod_S<1-8>_1920x1080_h<hour>.jpg`: ONE session of `Look_Midtown_tod` visiting the 8 shot poses at 7.6, 13 (clear), 13w1 (`wh.Weather 1` overcast), 18.4 (golden), 19.8 (blue hour), 22 (night). Numbers: `round-05/TESTS_tod.md` (`tod_tests.py`).
- `round-05/tod_lapse_S4.mp4` (+ `.json`, `_sheet.jpg`): 24 h from the S4 perch at 2 h/s, fixed 1/60 s step, 724 frames. `round-05/swing_tod_18h4.mp4`, `swing_tod_22.mp4` (+ `.check.json` from `clip_check.py`): P3 hero swing clips on the ToD map.
- Critic pack: `/Users/midir/sm2-n1/_scratch/critic-P4-r05/pack` (13 pairs, key in `pack.key.json`, made by `make_pairs.py` + `abpack.py`; 11 ref pairs + 2 progress pairs vs round 03).

Measured (final tour, `TESTS_tod.md`):
- Golden 18.4: means 56..117 (L1 61..100 on 6/8: S3 56, S4 117), clipped <= 1.0 % except **S7 3.5 %** (L5 0.7), B-R -57..-26 (L6 mostly in), **far band S4 19.4 Y under the sky (PLAN 15-32: PASS), dBR +11.1 (+-10: 1.1 over)**, L21 p5 4.1..31.9, p95/p5 5.9..52.1, sat .41..58.
- Night 22: L3 7/8 (S1 62.3 = first pose after the hour switch, see below), L8 B-R -8..+10 pass; far band -8.4 (was +47 at the start of the session; sweep G reached -21.5 with the same fog), **L22 S4 window points 1.73 % (FAIL, sweep G 3.09 %)**, median 28.7 (pass).
- Overcast 13w1: L2 4/8 (means 66..98), clipped <= .03 %; far band -6.3 (fail). Clear 13: means 70..100, clipped up to 2.2 % (S3), far band -9.4 / dBR -12.9 (fail). Dawn 7.6: 5/8 golden lines.
- Lapse (L23b <= 3 Y per frame): **FAIL, max 14.3 Y, p99 7.8**: the mean runs to ~200 at 6.6-8 h and 19.6-21.4 h. Cause: eye adaptation lags the 2 h/s clock (it brightens while exposure is still set for the darker hour; at dusk the city emissive ramps x11 at the same time) and the dense night fog lit by the twilight sky ambient (white wash in the sheet).
  Follow-up written but NOT run (cancelled at 20:42 while 5th in the GPU queue so nothing is left running; run it first next session: `/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label look --timeout 7200 -- $SM2_LOOK_SCRATCH/r05/final4.sh`; a copy is committed as `tools/perf_ue/sweeps/r05/final4.sh`): lapse with `pp.AutoExposureSpeedUp/Down 40` pinned (`--cmds`, a time-lapse camera re-meters every frame), 22 h / 19.8 h re-captured with 8 s settle into `$SM2_LOOK_SCRATCH/r05/settle`, and a diagnostic lapse without fog sky-ambient.
- Clips: golden mean Y 73.5 (31.7..93.6), clipped .77 %, L18 edge/centre p50 .76; night mean 39.4, B-R +2.0, L18 p50 .58. **Night clip: the hero renders white-hot (blown) on the ToD map** (round-02 night map hero was fine, same hero-light preset): not diagnosed yet. `hero_luma` = 0 frames measured (no hero pixel box in the telemetry on this map).

What changed this session (all committed): C++ sun diffuse/specular ramp under the horizon; stepped `fog.FogCutoffDistance`; presets night fog (800 m, .08, max .98, 7 km cutoff), golden white temp 6400 + saturation, day exposure -0.8, blue-hour sun 5000 + lighter fog; `tod_tests.py` abs symlinks; lapse `--cmds`.

## Next (ranked)
1. Night 22 S4 points 3.09 % -> 1.73 % between sweep G and the final tour with the same fog values: find the difference (the final tour ran under the new 45 fps capture cap in `run_game.sh`, fewer frames per settle; S1 at 62 says the first night pose was not settled) - compare `settle/` stills from final4.
2. L23b: exposure speed for the lapse (final4), then soften the dusk emissive ramp (`lights` / `mpc.EmissiveScale` keys) and the blue/night fog sky ambient (`fog.SkyAtmosphereAmbientContributionColorScale` key at night) so the 19.5-21 h wash goes.
3. Blue hour 19.8 still looks sunlit (twilight glow through the sky light): try `sky.Intensity` lower in the blue key, sun 5000 -> 1500.
4. Night hero white-hot on the ToD map (hero lights / exposure); golden S7 clipping 3.5 %, S4 mean 117, golden dBR +11.
5. Day / overcast far band (6-10 Y under the sky; needs 15-32).

## Sweeps of round 05
- Runner `tools/perf_ue/sweeps/run_r05.py --plan sweeps/r05/plan_<x>.json --out <dir>` (one session, `exec wh.ToDClear` before each group; params that are NOT keyed are sticky - e.g. a pinned `fog.FogCutoffDistance` leaked into sweep G's golden group). Results `round-05/sweeps/<X>_TESTS.md`.
- A..D (earlier today): ToD first pass, golden key/fill, night windows (nB), overcast (oA), clouds per hour (CD); T1 = first full tour after the rebuild; E = night fog / overcast + day aerial / moon; F = blue hour, golden white temp, day exposure; G = blue-hour light diagnosis (`sun.Intensity 0` is the only pin that darkens it) + fog cutoff.
- `unreal/WebHomage/Scripts/run_game.sh` carries an UNCOMMITTED orchestrator safety edit (18:12, frame caps 45 / 30 fps for non-perf captures): not P4's file, leave it.
- Left on disk: `unreal/WebHomage/{DerivedDataCache,Intermediate}` kept (this piece is active; deleting them costs a full shader recompile). Scratch: `/Users/midir/sm2-n1/_scratch/look/r05/` (sweep stills A..G, tour work dirs).
- Queue reality tonight: a capture hold waited 30-60 min (7-8 holders ahead); a waiter times out after 3600 s by default -> use `gpu_slot.sh capture --label look --timeout 7200 -- <one chain script>` and put several steps in one hold (inner gpu_slot calls pass through as nested; max hold 2400 s).

# (older) P4 Look, lighting, post: handoff (round 03; round 04)

## Round 04 in progress (2026-10-01, Opus 5.5) - resume here
- Target (critic round 03): golden S1-S8 1080p p5 Y <= 12, p95/p5 >= 16, HSV sat >= .44, L1 holding (S4 down), S1/S5/S6 sunlit/shaded facade pair ratio >= 3; night S4 window points >= 3 %, city median Y <= 42 (L21 / L22 in SPEC.md).
- Done: merged integration (perf preset perf60_hwl2 = `tools/perf_ue/perf_preset_ini.py` writes untracked Config/Mac/MacEngine.ini; P1 canyon shade fill = MPC_City ShadeFill), clouds 20 km in all presets, tour commands `! sun <elev> <az>` and `! mpc <path> <name> <v>`,
  headless `tools/perf_ue/rebuild_city.sh prep|ue`, sweeps `sweeps/gen_g7.py` (sun geometry, fill), `sweeps/gen_n7.py` (night windows), budgeted hold driver `sweeps/run_r04b.sh S|F|C`.
- Order: `gpu_slot.sh capture --label look -- tools/perf_ue/rebuild_city.sh ue` -> `... run_r04b.sh S` (sweeps -> `$SCR/eval7/stills`, rank with sweep_report.py / key_fill_check.py / night_city_check.py) -> edit look_presets.json golden/night -> `run_r04b.sh F` (stills) -> `run_r04b.sh C` (clips) -> round_tests.py -> critic pack.


> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Branch `night1/look`, worktree `~/sm2-n1/look`, UE MCP 8774, dev port 5205. Owns `/Game/Look`, `/Game/Tests/Look`, `tools/perf_ue/`, `Scripts/build_look.py`, `Scripts/look_presets.json`, `Scripts/look_ts_screens.json`,
`Source/WebHomage/Look/`, `docs/night1/look/`. Nothing in `Content/` is committed: scripts rebuild everything (`tools/perf_ue/rebuild_look.sh`).
Numbers of the round: `round-03/TESTS.md` (spec tables, 1080p and 4K, clips), `round-03/NOTES.md` (capture facts), `round-03/notes.json`. Targets: `docs/night1/look/SPEC.md` (LOOK-SPEC L1..L20). Shot list: `SHOTLIST.md`.

## State (end of round 03)
- Round-02 critic (`critic/round-02-CRITIC.md`): FAILS 4.3 avg. Ranked gaps: (1) build a real overcast midday, (2) far-field shading (far city takes the sky tint, 15..32 Y under the sky, no purple proxies / white shore band),
  (3) make night a night (B-R within +-13, bottom-third p10 15..30 / p90 >= 100). Round 03 addressed all three with preset v2 (below) and rebuilt the tooling so a look can be tuned live and measured in minutes.
- **Presets v2** (`Scripts/look_presets.json`, rebuilt by `rebuild_look.sh rigs[,night]`):
  - *midday* = overcast late morning (LOOK-SPEC L2): grey Rayleigh (`rayleigh_scattering` [.5,.5,.5], scale .03) so the sky is neutral, Mie .15 / anisotropy .6 haze, aerial-perspective distance 4, sky luminance factor 1.5, fog takes 3.5x
    sky ambient, sun 26000 lux with a 5 deg source angle (soft, no disk), sky light 2.3, **exposure = histogram average metering (low 10 % / high 90 %) with bias -0.7**, `film_white_clip` 0, shoulder .2, highlights gain .9, black lift .008.
  - *golden* = 9 deg sun behind the avenue ends, warm Mie haze (`mie_scattering` [1, .72, .45], scale .03, anisotropy .7, aerial distance 5) so the far shore takes the sky's orange, white temp 7800 K, cool sky-fill in the shadows,
    `film_white_clip` 0, shoulder .2, highlights gain .8. Exposure stays 70 % / 98 % histogram, bias .95.
  - *night* = dark facade masses with lit windows: moon 16 lux, sky light 2.5, city-glow fills x.85, Rayleigh tint [.3,.4,.7], fog density .012 (far shore 15..32 Y under the sky), white temp 6000 K, black lift (.0064, .008, .0144),
    exposure bias -.25; 634 lamps (spot 14000 cd, **cone 60 / 25 deg** = pools big enough for L14 p90), halo 120 cd, storefront spill 4000 cd, stand-in car heads 2000 cd.
  - Screens of the Times-Square-like district (`M_LookScreen`, `mat_screen`): every LED quad gets an emissive abstract content quad, built per (palette colour, aspect bin) so a 40 m tall panel becomes a stack of ad-like cells
    (gradient + soft blob + bars standing in for text lines + LED dot grid + rare flash). Pure maths, no text / logo / imagery (`IP_EXCLUSIONS.md`).
- **Tools** (all `tools/perf_ue/`, README lists them): `capture_tour.py` (one game session per preset and resolution visits the 8 shot poses through `Source/WebHomage/Look/WHLookTour.*`; `--variants <json>` = live look sweeps),
  `sweep_report.py` (ranks sweep variants against the spec), `look_spec_check.py` (spec numbers per still), `round_tests.py` (writes `round-NN/TESTS.md`), `clip_check.py` (clip numbers incl. L18), `capture_looks.py --clips --no-stills --no-warmup` (swing clips).

## Measured (round-03/TESTS.md; luma Y = .2126R + .7152G + .0722B of the 8-bit sRGB, stills resized to 1920 wide)
All numbers below are from the 3840x2160 native stills (native internal resolution, `r.ScreenPercentage 100`) unless noted; midday / golden 1920x1080 native stills agree within 1 Y (there are no night 1080p stills in round 03: the night preset was fine-tuned after the first 1080p pass, so only the final 4K set is kept). Round 02 for comparison: `round-02/TESTS.md`.
- **Midday (L2 overcast)**: frame means 85.2..94.5 on all eight views (band 83..97; round 02: 1 of 8 in band, means 62..91), near-black 0.00 % everywhere (limit 0.05 %; round 02 up to 7.3 %), B-R -12.0..+2.9 (band -19..+8),
  clipped 0.00 % on six views and 0.04 % on S3 and S7 (limit 0.00 %; round 02 up to 1.24 %). S4 far field: far shore 18.4 Y under the sky with B-R +0.2 from the sky (L10 -32..-15 / +-10 pass), horizon 9.1 Y above the sky (L11 >= +3 pass),
  far shore 9.5 Y above the river (P1 C14 pass). L17 glass p10 26..98 (>= 20 pass).
- **Golden (L1 / L5)**: means 74.8..110.0, seven of eight in 61..100 (S4 110.0 is sky-dominated), near-black 0.00 %, clipped <= 0.66 % except **S7 3.10 %** (L5 <= 0.7 %; round 02 2.58 %), B-R -19.6..-51.1 (band -55..-20; S3 -19.6 is 0.4 out; round 02 S2 / S4 were -66.7 / -57.1).
  S4 far field: far shore 26.3 Y under the sky (pass) but its B-R is +18.4 from the sky's (limit +-10) and it is 2.1 Y darker than the river (C14 wants +5..+35). L17: S8 right glass p10 16.6 (< 20).
- **Night (L3)**: means 39.4..58.1 (band 37..60), near-black 0.00 %, clipped 0.01..1.04 % (limit 1.7), **B-R -11.8..+5.9 on all eight (L8 +-13; round 02 S4 / S8 +26.9 / +19.8)**, S4 far shore 18.2 Y under the sky, B-R -7.8 from the sky (L10 pass),
  L13 lit blobs 14 / 14 / 9 on S1 / S5 / S6 (>= 5), L14 bottom-third p10 26.6 / 17.6 / 24.6 (15..30) and p90 167 / 133 / 119 (>= 100; round 02 S6 p90 94). The round-1 pools test (`night_tests.py`, peak >= 120, valley <= 40) gives S1 3 (target 4: the wider lamp cones merge neighbouring pools), S6 4.
- **Clips** (`swing_<preset>.mp4`, 1920x1080, 60 fps, 719 frames, internal 100 % of output, fixed 1/60 s step so they say nothing about real-time fps): midday (14.7 MB): hero pixel-box luma min 45.2 / p5 57.4 / mean 100.8 (frames below 40: 0 of 718). Frame numbers of every clip (mean Y, B-R, near-black, clipped, L18): `round-03/TESTS.md`. **Not captured this round: golden, night** (the GPU slot lock refused every launch for over an hour behind two UnrealEditor processes of other agents stuck exiting in the driver, pids 17555 / 17831; nothing was launched around the lock). Run `capture_looks.py --clips --no-stills --no-warmup --presets golden,night` first thing next round.


## Commands (from the worktree root; UE 5.8.3 at /Users/Shared/Epic Games/UE_5.8; scratch root env `SM2_LOOK_SCRATCH`, default `/Users/midir/sm2-n1/_scratch/look`)
```
unreal/WebHomage/Scripts/build_editor.sh                      # C++ (Traversal, Characters, Look), editor closed
tools/perf_ue/rebuild_city.sh                                 # city export + import (10-30 min), ends with the box / look rebuild
tools/perf_ue/rebuild_look.sh [geo,rigs,night,maps] [midday,golden,night]     # headless -nullrhi, editor closed (1-2 min; goes through the GPU slot, so it can wait 20+ min behind perf runs)
tools/perf_ue/capture_tour.py --round docs/night1/look/round-NN --presets midday,golden,night --res 1920x1080 --timeout 6000 --work $SM2_LOOK_SCRATCH/tour   # stills (one session per preset)
tools/perf_ue/capture_tour.py --round <scratch dir> --presets midday --res 1920x1080 --variants <json> --timeout 6000 --work <dir>                         # live look sweep
tools/perf_ue/sweep_report.py --dir <scratch dir>/stills --preset midday
tools/perf_ue/capture_looks.py --round docs/night1/look/round-NN --presets midday,golden,night --clips --no-stills --no-warmup        # swing clips (fixed 1/60 s step)
tools/perf_ue/round_tests.py --round docs/night1/look/round-NN       # TESTS.md
tools/perf_ue/run_perf.py --out <dir> --map /Game/Tests/Look/Look_Midtown_night --configs tsr50 --fixed-step    # GPU lock 'perf' (exclusive)
```
Live sweep format: `{"variants": {"name": ["exec showflag.fog 1", "set SkyAtmosphere - MieScatteringScale 0.03", "post AutoExposureBias 0.7", ...]}}`; `set <ActorLabel[*]> <ComponentClassSubstring|-> <Property> <text value>`, `post <CamelCaseProperty> <text>`.
Generators of the round's sweeps: `tools/perf_ue/sweeps/` (README there); the sweep stills of round 03 stay in `/Users/midir/sm2-n1/_scratch/look/eval/` (not committed).

## Gotchas learned this round
- **Live-sweep state is sticky**: a `set` / `post` line stays in force for every later variant of the session. Every variant must set every property that any variant of the file changes (an early golden sweep measured
  metering leaked from a previous variant). `gen_*` helpers set all keys each time.
- **Auto exposure decides the frame means.** `auto_exposure_low_percent` / `high_percent` choose the histogram window. 70 / 98 (bright-region metering, the default in `build_look.py`) makes sky-dominated frames darker and canyon frames
  brighter; 10 / 90 (average) equalises the eight shots' means (midday S1..S8 all 85..94). A sky-only change (sky luminance factor) is cancelled by the exposure when the sky is metered, so it does little for S4 / S7.
- Overcast is made from: neutral Rayleigh colour (blue Rayleigh = blue sky), sun disk 0 with a 5 deg angle, strong sky light, Mie haze for the bright horizon, fog picking up sky ambient (x3.5). Sun lux is what keeps S3 / S7 (sunlit rooftop / cross street) from going dark under average metering (26000).
- `film_white_clip` 0 + `color_gain_highlights` < 1 + shoulder .2 is what takes midday clipping to ~0 (`clipped` = any channel >= 250 counts, the midday limit is 0.00 %).
- Night: wide lamp cones (60 / 25 deg) are what make the bottom third of street views bright enough (p90 >= 100) without lifting the whole frame; more lamp power only raises the mean. Fog density 0.012 sets L10 (far shore under the sky).
- `Scripts/run_game.sh` (shared, not P4's) SIGKILLs the game at its `-timeout`. Always pass a large `-timeout` (the tools do: 5000 / 6000 / 7000); stop a hung game with `stop_ue.sh "<pattern that cannot match your own shell>"`, never `kill -9`.
- GPU queue: the slot lock is FIFO and the perf piece's exclusive runs (10..30 min each) block every capture behind them; a session that takes 1 min to run can wait 20..40 min. Plan sweeps as few, rich sessions (8..12 variants each).
- `unreal.Color` positional order is (B, G, R, A); use keywords. Atmosphere `ground_albedo` still positional (unchanged since round 01).

## Start of next round
- First: the two missing swing clips (`capture_looks.py --clips --no-stills --no-warmup --presets golden,night`), then `round_tests.py`; check `pgrep -fl UnrealEditor` / `ps -Ao pid,stat,command | grep '?E'` for engines stuck exiting before queueing anything.
- `unreal/WebHomage/{DerivedDataCache,Intermediate}` were deleted at the end of round 03 (idle rule): `build_editor.sh` recompiles the C++ and the first game run recompiles shaders (slow once).
- Merge `Opus-5.5-Loop-Night-1` first (city / traversal keep moving), `build_editor.sh` (editor closed), `rebuild_city.sh` if the city changed (it ends with the look rebuild), then `capture_tour.py` for the three presets.

## Open issues / next gap (facts, not self-assessment)
1. **Golden S7** (looking down a cross street toward the sun): 3.1 % of the pixels are clipped (the warm sky column at the end of the street; L5 wants <= 0.7 %). `film_white_clip` 0 / highlights gain .8 / shoulder .2 fix every other golden view (<= 0.66 %) but not this one;
   Mie scale 0.015 gives 1.9 % but breaks the far-shore tint (L10 B-R +26.8). Golden S4 mean 110 has the same root: sky-dominated frame under bright-region metering, sky-only changes (sky luminance factor) are cancelled by the exposure.
   Next idea: a different metering window for golden (a sweep showed 10 / 90 makes S3 / S7 too dark, so try 40 / 95 with a stronger sun) or a sun-aligned exposure compensation.
2. Golden S4 / L10 B-R (+18.4) and C14 (river brighter than the far shore): the river reflects the bright orange sky; sky luminance factor .65 / .65 / .65 brings L10 B-R to +11.8 but reddens S4 to -58 (past L6 -55); .65 / .70 / .85 gives +10.3 but S3 B-R -16.
3. Midday: S3 / S7 clipped 0.04 % (2000 px each; the limit is 0.005 %); a highlights gain of .8 would close it but takes S4 (85.2) under the 83 line; the overcast sky is a flat grey (the cloud deck `MI_LookClouds_midday` renders as a smooth dome): a textured deck (coverage / density MI variants, swapped live with
   `! set Clouds - Material /Game/Look/<mi>`) is the next visual step for S4 / S8 / the swing clip's sky.
4. Night: stand-in traffic is still boxes (P6 owns real traffic), tree foliage is bright green under the lamps (P1 material; the post grade cannot desaturate one hue), the LED content is procedural (abstract, by design).
5. **Perf was not run this round.** Night lamps now have 60 deg cones (46 before), storefront / head-light intensities doubled: the `Lights` pass grows; perf piece F should re-profile `Look_Midtown_night` (`run_perf.py`, GPU lock `perf`). Round 02 numbers (`round-02/PERF.md`) are for the old rig.
6. L18 (motion blur while swinging): `clip_check.py` measures edge / centre sharpness as mean |Laplacian| ratio; the critic's instrument was not available. Round 02 clips measure p50 .59 / .59 / .41 (midday / golden / night) with it, round 03 midday .78 (outside .20..+.65): content dependent;
   `motion_blur_amount` is 0.5 in every preset, raise it (0.7) if the critic flags it.
7. No runtime time-of-day blend (three fixed presets), no depth of field, no lens dirt, no sun shafts other than the volumetric fog.

