# P4 Look / Sky: handoff (round 06, Sonnet 5.5; started 2026-10-01 20:50, resumed 2026-10-02 05:02)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

## Round 06 (resumed 2026-10-02 05:02 after the 502; Sonnet 5.5) - start here
State at 05:55: the committed `round-06/` holds the captures the first builder made at 04:42-04:57 (stills, lapse, two clips from the hold-4 table; numbers in `TESTS_r06.md`, `TWILIGHT_r06.md`, `TESTS_tod.md`). They FAIL most of the round target (table below). Hold 6A (05:19-05:51, evidence in `round-06/diag/hold6a_*`) found the instrument fix and the variant winners; hold 6B (queued, chain `tools/perf_ue/sweeps/r06/hold6b.sh`) builds the final table, runs the closed loop, rebuilds and re-captures everything into `round-06/`. If 6B has NOT run when you read this: the committed `look_presets.json` is still the hold-4 table, `$SM2_LOOK_SCRATCH/r06/final6/knobs_final.json` (copy: `round-06/diag/knobs_final_r06.json`) holds the 6B knobs; queue it with
`/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label look --timeout 21600 -- tools/perf_ue/sweeps/r06/hold6b.sh` (needs the C++ of this branch built: `unreal/WebHomage/Scripts/build_editor.sh`, editor / game closed; it takes 12 s). 6B = loop (2 sub-stepped lapses) -> make_v2 in place -> headless rebuild -> final lapse -> 40 stills -> 2 clips, ~35 min, a step is skipped when its budget is short; afterwards run `tools/perf_ue/round6_report.py --round docs/night1/look/round-06`, regenerate the pack (`/Users/midir/sm2-n1/_scratch/critic-P4-r06/make_pairs.py` then abpack) and commit.
### Findings of this resume (all measured, real game)
1. **Moon checker bug fixed** (`twilight_check.moon_disk`): a far speck replaced the disk, the report read 2.0 px for a 21.7 px disk (L25a was already passing: disk 21.7 px, peak Y 255 at 22:00 on S4m). L25b (sky high-pass std >= 3) was 2.06 in the hold-4 table; the hold-2 cloud pattern `cloudv.Layout_GlobalTexturePlacement [0, 30000, 0, 0]` reads 3.4 (Mv4) - it is in the 6B knobs. A night highlight roll-off (.8) lowers the high-pass to 2.31 and does NOT remove clipped pixels (hero box max 1922 px vs 2103): dropped. The hero box clipped pixels are lit windows (the suit reads red / blue in the frames); L15b as written (0 px in the box) is not reachable without darkening the windows.
2. **L23b: the round-05 / hold-4 "lag" is the engine's temporal lighting caches (~35 frames).** Hold 4's instrument (render settings `TimeSlice=0` + `r.VolumetricFog=0`) put a one-frame step at 18:58 (-12.8 Y) into the lapse. New instrument (`capture_tod_lapse.py --substeps 4`): the clock runs at 0.5 h/s (fixed 1/60 s step), every 4th frame is kept = the same 725-frame 2 h/s lapse with the caches settled between output frames, NO render setting changed, fog on. D0 (hold-4 table): max jump 6.56 (was 12.81), p99 4.61, 05:00-21:30 mean <= 104.9, clipped <= 5.40 % (06:52, the red sky). x2 (1 h/s) is not enough (D2: step 13.1 at 18:57, wash at 20:30). A one-frame step of ~6 Y remains at sun elevation ~3 deg (18:55) in every lapse (x1, x2, x4); candidates not yet tested: Lumen surface-cache direct-light refresh when the sun diffuse scale first leaves 1.0, cloud shadow map (`r.VolumetricCloud.ShadowMap 0`), night street lights unhide (`lights` key >= .02 at 18:25). The settled stills fall 5 Y per frame between 18:54 and 19:02 (truth is steep: `step_h*` stills in the hold-4 scratch).
3. **Twilight sky variants (hold 6A, settled stills):** the hold-4 factor [30, 6, 1.2] on SkyLuminanceFactor saturates the red channel (S4 clipped 3.7-5.6 % at 06:30, 07:00, 19:00, 19:30). Lower factors (W1 / W3) cut it to 1.5-4.8 %; denser twilight clouds (coverage .25, density .03: W4) cut S4 clipping to 0.4 % (06:30 / 07:00 / 19:30) and 1.2 % (19:00) without losing B-R <= -20 on the sun-facing stills at 06:30-07:30 and 19:00-19:30. At 20:00 the denser clouds turn the sun-facing sky band neutral (S4w B-R +8 against -20 for the hold-4 table), so the 6B table (W5) thins them out by 19:48 and keeps factor 30 from 20:12. **Still failing in every variant:** L24a at 20:00 (S4 sky band 10-11 Y against the far band 18 Y: the sky is the darkest thing in the frame between the sun and the moon; the far band is fog + early windows) and L24b at 20:30 (S4w B-R +1..+4; the factor does not reach the dark sky). Ideas: fog inscatter x0.5 at 19:48-20:12, moon lux from 20:00 only if the moon shadow switch is also moved, a faint warm airglow keyed by sun.Intensity at 20:12-20:36.
4. Golden black lift (`pp.ColorOffset` on the golden keys): .0012 -> Y<10 on 5 of 8 stills (base 3 of 8) with p5 <= 12 on 6 of 8; .0022 -> 5 of 8 but p5 <= 12 on 5 of 8; S7 (14.8 %) and S5 (9 %) stay over 8 %. 6B uses .0015. Dawn mist 4.0 at 07:36: S1 correlation 0.574 (<= 0.6; the hold-4 table 0.620).
5. Closed-loop tooling for L23b: `lapse_loop.py` (sub-stepped lapse -> `lapse_opt.design_target` = the curve closest to the measured one with |dY| <= 1.25 per frame, golden / night anchors, clip ceiling -> exposure bias of the 14 twilight keys), `make_v2.py --bias-overrides`, C++ `sun.RampLo / sun.RampHi` table params (the sun surface-light ramp, default -2.5 / 3.5 deg, the 6B table uses -4 / 8 = 65 game minutes; this is why the C++ must be rebuilt). Table knobs added to `make_v2.py`: `tw_fac_pts`, `tw_hl_r`, `tw_cloud`, `night_hl`, `cloud_offset`, `sun_ramp` (defaults reproduce the hold-4 table exactly: checked).
### Round-06 numbers of the committed captures (hold-4 table, instrument fix applied) - the baseline 6B must beat
L23b (old 2 h/s + cvars lapse) max 12.81 / p99 4.13 / clipped 5.36 %; D0 sub-stepped max 6.56 / p99 4.61 / clipped 5.40 %. L24a 8 of 9 hours (20:00 fails); L24b 8 of 9 (S4w 20:30 fails); L25a pass (21.7 px, 255), L25b 2.06 (fail); L26 0.620 (fail). Golden 18:24: L1 mean 61..100 on 7 of 8 (S3 57.2), Y<10 <= 8 % on 3 of 8, p5 <= 12 on 7 of 8, clipped <= 1.8 % on 8 of 8 (S7 2.12 <= 3.1), S4 99.7. Night 22:00: L3 8 of 8, L8 8 of 8, L22a 1.72 %, L13 blobs S1 / S5 / S6 = 9 / 13 / 4 (S6 fails). Hero (swing_tod_22): mean 58.0, 92 frames below 40, clipped px in the box 675 frames / max 2103.
### Files
`sweeps/r06/`: gen_plans_e.py (6A variants + plan), hold6a.sh (done), analyze_a.py, make_final_knobs.py (6B knobs), gen_plans_f.py (6B stills plan), hold6b.sh (6B chain), make_v2.py (table builder), final_r06.sh / hold4.sh (hold-4 chain, history). `capture_tod_lapse.py --substeps N`, `lapse_loop.py`, `lapse_opt.py`. Evidence: `round-06/diag/hold6a_analysis.md` (+ 3 contact sheets, D0 / D2 lapse jsons, N1 hero clip numbers).
GPU facts of this resume: a health-monitor auto-pause (05:22, my sub-stepped lapse + another agent's 4K capture at GPU 100 %, WindowServer 2 %) held every launch for 10 min; the max hold of 2400 s ends with SIGTERM + 10 s + SIGKILL, so no engine may be running at hold start + 2400 s (the chain scripts only start steps that fit the 2250 s budget).

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

