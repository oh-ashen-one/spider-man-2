# LOOK-SPEC (P4 lighting, atmosphere, post) — fixed targets, measured from refs

> Homage fan game; not affiliated with Marvel, Sony or Insomniac. Refs private.
> Written 2026-09-29 by spec agent B. Instrument: `specs/tools/lum_by_tod.py` on every non-UI still (1920 px wide, INTER_AREA),
> luma Y = .2126R+.7152G+.0722B (8-bit sRGB), "clipped" = any channel ≥ 250, "near-black" = Y < 10. Per-still results: `specs/data/lum.json`.
> Stats are the spread across ref stills of one lighting group (p10–p90 of per-still values). Run the same script on our 1080p stills
> (captured at the documented game time, eye adaptation settled). `dn` refs are HDR tone-mapped to SDR by the uploader (source is PQ 10-bit).
> Perf (4K/60) moves to the perf piece F under the GPU lock; it is not a LOOK axis any more.

## 1. Exposure per time of day (L-A, L-E)
| id | preset | frame mean Y | Y<10 (near-black) | Y<25 | clipped | p99 Y | measured from |
|---|---|---|---|---|---|---|---|
| L1 | golden (Look_*_golden) | **61–100** (med 84) | **≤ 8 %** (med 1.0) | med 6 %, ≤ 27 % | **≤ 1.8 %** per frame, set median ≤ 0.3 % | 171–248 | 74 golden/sunset stills (nm, og, cp, gr) |
| L2 | midday overcast | **83–97** (med 91.5) | **≤ 0.05 %** | ≤ 3.8 % | **0.00 %** | 161–205 | 31 dn stills |
| L3 | night | **37–60** (nt p10–p90 37.5–53.3; incl. ts up to 80) | **≤ 1.0 %** (nt p90 0.66) | 25–45 % (nt med 37) | ≤ 1.7 % (nt p90), emissive only | 195–255 | 21 nt stills (+16 ts) |
| L4 | day/afternoon | 55–89 | ≤ 12.7 % | 10–28 % | ≤ 0.3 % | 170–220 | 24 stills |
| L5 | sun-facing golden view (S7-type) | 59–118 | ≤ 8.8 % | — | **≤ 0.7 %** | — | swing-avenue-sunset__nm_0654 .67 %, skyline-sunset-nm .00 %, sunset-swing-trailer .10 %, dive-sunset-og .02 %, sunset-river-og .07 %, rooftops-watertowers-golden .01 % |
Round-1 critic night targets (mean ≥ 35, ≤ 3 % < 10) are consistent with L3; L3 is the binding, stricter line.

### L21 golden key / fill contrast (added round 04, from the round-03 critic verdict `critic/round-03-CRITIC.md`, "Biggest gap")
| id | preset | target (golden S1–S8 at 1080p, per still) | measured from |
|---|---|---|---|
| L21a | golden | **p5 Y ≤ 12** (deep shade reaches ref depth) | critic pass on the golden refs: 8–11 |
| L21b | golden | **p95/p5 ≥ 16** | refs 18–26 |
| L21c | golden | **mean HSV saturation ≥ 0.44** (S = (max−min)/max of the 8-bit RGB per pixel, frame mean) | round-03 stills 0.28–0.43 |
| L21d | golden S1, S5, S6 | a **sunlit / shaded facade pair with mean-luma ratio ≥ 3** (boxes in `facade_pairs.json`) | critic pass |
L1 keeps binding next to L21 (mean 61–100, Y<10 ≤ 8 %, clipped ≤ 1.8 %). Checker: `tools/perf_ue/key_fill_check.py` (same formulas as the critic's instrument; reproduces the round-03 numbers p5 17.6–39.6, p95/p5 4.6–11.3, saturation 0.28–0.43).

### L22 night skyline (added round 04, from the round-03 critic verdict, secondary 1)
| id | preset / view | target | measured from |
|---|---|---|---|
| L22a | night S4 | **window points >= 3 % of the frame** (Y >= 120 and Y - median9x9(Y) >= 35, 1920-wide frame) | critic: round 03 0.96 %, reference 4.38 % (this instrument reads 1.10 % on round 03) |
| L22b | night S4 | **city median Y <= 42** (and frame mean <= 42: the critic's round-03 "58" equals this instrument's frame mean 58.1, median 51.9) | reference 37 |
Checker: `tools/perf_ue/night_city_check.py`. L3 (night means 37..60 on every view) keeps binding.

### L23 continuous time of day (added round 05, director PLAN-firstpass §4 Sky)
| id | target | instrument |
|---|---|---|
| L23a | ONE map, `wh.TimeOfDay` 0–24 continuous: sun and moon move on their arcs, sky / atmosphere / fog / clouds / exposure / city lights follow the hour; the three preset maps stay buildable but are not needed for play | `/Game/Tests/Look/Look_Midtown_tod` (rig `Look_Rig_tod`, C++ `AWHLookTimeOfDay`) |
| L23b | no steps: in a 24 h time-lapse at 2 h per second (fixed 1/60 s step, 724 frames from 04:00 on the S4 perch) the frame-to-frame change of the frame mean Y stays **≤ 3 Y** (p99 ≤ 1.5 Y); from 05:00 to 21:30 the frame mean is **≤ 130** and clipped (any channel ≥ 250) **≤ 1.8 %** per frame. **Instrument condition (round 06):** the lapse compresses an hour into half a second, so (1) the eye adaptation is metered per frame: `pp.AutoExposureSpeedUp` and `pp.AutoExposureSpeedDown` are pinned to 40 for the capture only (live `wh.ToDSet` pins written into `<name>.json` as `instrument_condition`; the game keeps 6 / 3), and (2) the engine's temporal lighting caches (Lumen diffuse GI, real-time sky light capture, volumetric fog history: ~35 frames = 0.6 game hour at 2 h/s) are given time to settle between output frames by **sub-stepping the render**: `capture_tod_lapse.py --substeps 4` runs the clock at 0.5 h/s with the fixed 1/60 s step and keeps every 4th frame, so the 725 output frames are the same 2 h/s lapse (2 game minutes per output frame); no render setting is changed and the fog stays on (`substeps`, `rendered_frames`, `clock_rate_rendered_h_per_s` are written into the json). **x4 is still not the settled truth in the twilights** (hold 7: the x4 lapse reads 54.6 / 39.7 / 42.2 Y at 19:48 / 20:00 / 20:30 against 15.0 / 14.9 / 22.0 for settled S4 stills; from 21:00 on they agree): the final lapse is therefore STITCHED (`tools/perf_ue/lapse_stitch.py`, 720 frames): the twilights 05:30-08:12 and 18:24-21:24 at x16 (clock 0.125 h/s, the caches lag under one output frame; a x16 window measures 17.8 / 18.1 / 19.2 Y at 19:48 / 20:00 / 20:12, the settled stills 15), the day and the night at x4; each segment renders 0.3 h early and drops those frames (`segments`, `instrument_condition` in the json). Evidence (`round-06/diag/`): without sub-stepping the lag washes the frame out at 20:30 (mean 216 against 43 for a settled still); the first round-06 attempt, render settings `r.SkyLight.RealTimeReflectionCapture.TimeSlice=0` + `r.VolumetricFog=0` at 2 h/s (`wh.ToDLapseCvars`, still in the C++), removed the wash but put a one-frame step of 12.8 Y at 18:58 into the lapse and switched the volumetric fog off; x2 (1 h/s) still washes at 20:30 (D2). The rig steps (fog cutoff, dusk emissive ramp, moon shadow switch, sun surface ramp) each spread over >= 20 game minutes; the sun surface-light ramp limits are table params (`sun.RampLo` / `sun.RampHi`, deg) | `tools/perf_ue/capture_tod_lapse.py` (`<name>.json`: `frame_to_frame_mean_y_jump`, `checks_L23b`, per-frame hour / mean / B-R / clipped) |
| L23c | clouds visible at every hour (day, golden, night: a volumetric cloud layer lit by the sun or the moon), stars and a moon disk at night | stills of the round's hour tour + lapse contact sheet (critic) |
| L23d | the golden hour of the time of day passes L1 / L5 / L6 / L10 / L21; its night passes L3 / L8 / L13 / L14 / L22; `wh.Weather 1` at 13:00 passes L2 (overcast: 0 crisp shadows, 0.00 % clipped) | `look_spec_check.py`, `key_fill_check.py`, `night_city_check.py`, `tools/export/s4_far_check.py` (C12 / C13 far band) on the tour stills |

### L24 twilight sky stills (added round 06, from the round-05 critic verdict `critic/round-05-CRITIC.md`, "Biggest gap")
Stills settled **≥ 8 s after each hour change** (run_r06.py: first pose of an hour 8 s, then 5 s; ≥ 90 frames). Instrument: `tools/perf_ue/twilight_check.py`.
| id | target | note |
|---|---|---|
| L24a | S4 at 06:30, 07:00, 07:30, 19:00, 19:30, 20:00, 20:30, 21:00, 21:30: sky band (rows 0-89 of the 1080-high frame) **brighter** than the far-city band (far-shore box 450,192,1350,236) | sign of L10 (L10 itself wants 15..32 under the sky at the golden hour) |
| L24b | at 06:30-07:30 and 19:00-20:30 the sky band of the still that **faces the sun** has **B-R ≤ -20** | after 20:30 the sky may be neutral / blue (L8 ±13 at 22:00 stands: no warm-glow demand past 20:30). Facing stills: S4e (perch turned to compass azimuth 60, dawn) and S4w (azimuth 250, dusk), `tools/perf_ue/sky_poses.json`; S7 faces west and is also reported |
| L24c | sun surface light is 0 below -2.5 deg and the moon's surface light is keyed in only after 20:00 (both logged 0 at 19:48): no sunlit tower tops under a black sky | `wh.ToDDump` / WH_TOD log |
| L26 | dawn has its own look: S1 luma Pearson correlation (480x270) of 07:36 against 18:24 **≤ 0.6** (round 05: 0.85; dawn vs noon 0.37) | `twilight_check.py` (S1 stills at hours 6-8.5 against the 18.4 still) |
### L27 twilight dome continuity (added round 07, from the round-06 critic verdict `critic/round-06-CRITIC.md`, "Biggest gap"; supersedes the sign rule of L24a and the open-ended L24b at these hours)
Settled stills (>= 8 s after the hour change) S4 and S4w at 19:30, 19:48, 20:00, 20:30 and S4 and S4e at 06:30, 07:00. Instrument: `tools/perf_ue/dome_check.py` (1920x1080).
| id | target | note |
|---|---|---|
| L27a | sky band (rows 0-89) **>= 10 Y above** the far band (box 450,192,1350,236) | rows 0-89 of the perch poses are 2-5.5 deg above the horizon (pitch -17.9, fov 75): the horizon glow strip |
| L27b | **no 8-row step > 25 Y** of the row-mean luma in rows 100-300 | the height fog must meet the sky continuously: `fog.FogCutoffDistance` 0 on every key (the fog applies to the sky pixels), no cutoff switch at any key; the worst 240-px column band is reported as a diagnostic |
| L27c | rows 0-150 **clipped (any channel >= 250) <= 0.3 %** | the round-06 twilight clouds clipped red ("lava streaks") |
| L27d | sun-facing sky band (S4w dusk, S4e dawn) **B-R within -90 .. -20** | r05's warm floor plus r06's saturation ceiling: -247 is clipped red, not warmth |
| L27e | S4 frame mean at 20:30 **>= its 22:00 mean** | no dark pit between the blue hour and the night |
| L27f | the L23b lapse (stitched x4 / x16): max frame-to-frame jump **<= 3 Y, p99 <= 1.5**; the sun's surface light decays **geometrically over >= 20 game minutes** (round 07: x3.3 per 6 min from 18:33 to 0.5 lux at 19:30, 0 from 19:33; dawn mirrored 06:30-07:27; `sun.SurfaceGain` keys every 3 game minutes, `tools/perf_ue/sweeps/r07/make_v3.py`) while the sky dome carries the exposure; L24c is then met by a lit dome, not a hard sun cut | the C++ applies the surface scale with a 1 % relative threshold (round 06: an absolute 1e-3 = 40 lux steps) and keeps the sun's shadows while it puts > 0.5 lux on the surfaces |
Floors (no regression vs round-06 hold C): L25a moon >= 20.5 px / peak 255, night L3 / L8 8 of 8, L26 <= 0.6, golden L1 7 of 8 with S4 <= 100, L22a >= 1.99 %.
Round-07 design that meets L27a-e (`diag/knobs_v8.json`, builder `tools/perf_ue/sweeps/r07/make_v3.py`, findings `round-07/diag/holdJ-P_findings.md`): (1) the fog's DIRECTIONAL inscattering (the fake sun glow in the haze, the only knob that moves the far band toward the sun) is cut hour by hour (x.005 at 19:30, x.07 at 19:48, x.03 at 20:00; dawn x.03 at 06:30, x.02 at 07:00) and the fog's haze colour is x.4-.55 from 19:48 to 21:00, so the city behind the skyline is darker than the sky above it; (2) the tonemapper is flattened over the twilight window (`pp.FilmShoulder` x.4, `pp.FilmSlope` x.88, `pp.FilmWhiteClip` 0, red highlights gain x.8, `pp.ColorSaturation` x.6): the lit cloud streaks no longer reach 250 and the sky B-R falls into -20..-90; (3) the sun's cloud luminance is 0 from 19:39 to 20:36 and from 06:06 to 06:48 (the Earth's shadow covers a 9 km cloud deck beyond ~3 deg of sun depression); (4) `fog.FogCutoffDistance` is 0 only from 05:36 to 20:42 and 7e5 (unfogged sky, the round-06 night) from 20:54 to 04:54, because a fogged night sky took S4 22:00 sky-far from +15.5 to -0.6; the twilight tonemapper ramps end on the last evening key (21:24) so 22:00 keeps the round-06 values.
### L25 night sky (added round 06)
| id | target | note |
|---|---|---|
| L25a | 22:00: moon disk **≥ 12 px** (equivalent diameter of the connected Y ≥ 200 blob at the moon's predicted pixel) with **peak Y ≥ 200** | the standard S4 pose faces north-west and the 22:00 moon (elevation 38, grid azimuth 118) is behind the camera, so the moon is measured on **S4m** (same perch turned to the moon, pitch +12, fov 90). Moon source angle enlarged (`moonc.LightSourceAngle`) when the real 0.52 deg disk is under 12 px. (Checker fix 2026-10-02: the blob selection let a far speck replace the disk, 2.0 px was read for a 21.7 px disk) |
| L25b | moonlit cloud, sky **high-pass std ≥ 3** (Y - gaussian(Y, 6) over rows 0-250 of S4m, moon disk ±70 px excluded; also reported with it) | round 05: 1.27 on S4 22:00, reference `perch-moon` 3.98 |
| L15b | swing_tod_22: hero pixel box (P3 `-WHTravMask` telemetry box) has **0 pixels with any channel ≥ 250 in every frame** and mean Y ≥ 40 (L15) | `night_tests.hero_stats` (`L15b_*` fields), hero lights keyed by hour (`hero`). Round-06 note: the box is the hero's pixel bounding box, so lit windows inside it count (the suit reads red / blue in the frames; a night highlight roll-off .8 only moved the max from 2103 to 1922 px); a hero-mask-only count needs the per-frame mask, which the telemetry does not keep |

## 2. Colour by time of day (L-A)
| id | target (frame mean B−R, 8-bit) | measured from (median [p10, p90]) |
|---|---|---|
| L6 | golden warm: **−55 … −20** | og −52 [−78, −31], nm −26 [−38, −17], cp −45 [−82, −31], gr −34 [−46, −8] |
| L7 | midday overcast near neutral: **−19 … +8** | dn −6.5 [−19, +8] |
| L8 | night near neutral: **−13 … +13** (blue sky/moon, warm lamps balance out) | nt 0.0 [−13, +13] |

## 3. Atmosphere and depth (L-C) — shared with CITY-SPEC C11–C15
| id | target | measured from (`haze_regions.py`) |
|---|---|---|
| L9 | RMS contrast falls with distance: far/near ratio **0.25–0.45**, monotonic near → mid → far → horizon | skyline-perch-nm .654 → .447 → .182 → .074; skyline-perch-dn .310 → .194 → .125 |
| L10 | Far band luma **15–32 below the sky band**; far band takes the sky tint (B−R within ±10 of sky) | dn far city −15.7, far shore −26.6 (B−R 15.7/15.4 vs sky 15.6); nm horizon −13.9, far shore −32.0 (−46 vs −37) |
| L11 | Midday sky: horizon band **≥ zenith band** (+3 … +5 Y) | skyline-perch-dn 134.8 vs 131.4; skyline-overcast-dn 172.9 vs 168.6. (Golden varies: gr +56, nm −10 → no golden rule) |
| L12 | Saturation drops with distance (golden): HSV S near .66 → mid .55 → far .44 → horizon .35 | skyline-perch-nm |

## 4. Night street lighting (L-F)
| id | target | measured from |
|---|---|---|
| L13 | Street-level night view: **≥ 5 lit blobs** in the bottom half (Gaussian σ = 12 px at 1080p, Y ≥ 100, area ≥ 400 px); ref median 9 | night-street-2 7, night-street-level 9, night-street-car 12, hero-idle-crosswalk-night 9, landing-crosswalk-night 3; swing-night-canyon 21 |
| L14 | Bottom third: **p90 Y ≥ 100** (pools) and **p10 Y 15–30** (dark between pools, not black) | p90: 106/143/132/131/138; p10: 17.2/21.9/20.4/26.4/19.9 |
| L15 | Hero readable at night: hero-mask mean Y ≥ 40 | round-1 critic line; ref hero-mask luma not measured in this pass (keep as provisional) |
| L16 | Lamp spacing along the street | **unmeasurable in metres from refs**; critic's "every 25–30 m" stays a guideline |

## 5. Reflections and post (L-D, L-E)
| id | target | measured from |
|---|---|---|
| L17 | No pure-black glass panel in daylight: glass-mask p10 Y ≥ 20 | rule from r1 defect; glass-only ref crops not isolated in this pass |
| L18 | Motion blur while swinging: edge/centre sharpness p50 0.20–0.65 (= TRAVERSAL T20), hero sharper than ring (T21) | swing clips, see TRAVERSAL-SPEC §4 |
| L19 | Vignette, bloom radius, lens ghosts | **unmeasurable from refs** (corner/centre luma ratio p10–p90 0.55–1.74 across 168 stills: content-dominated). Rule: no sourceless lens ghost (r1 defect) |
| L20 | Banding/aliasing | judged at native 4K crops; no numeric ref line |
Checkers: `look_lum_check.py` (= lum_by_tod.py on our stills, per preset; L1–L8), `farfield_check.py` (shared with P1; L9–L12, depth + sky masks),
`night_pool_check.py` (L13–L14 blob counter above, same σ/threshold), glass-stencil capture for L17.

## 6. Axis → spec lines
| axis | lines |
|---|---|
| L-A Sun / sky / time of day | L1, L2, L4, L5, L6, L7, L11 |
| L-B GI & shadows | L1–L3 near-black columns, L14 p10 (shadowed side lifted, never crushed) |
| L-C Atmosphere & depth | L9, L10, L12 |
| L-D Reflections & materials | L17 (+ side-by-side vs wallrun-glass-*, webwings-bridge-night) |
| L-E Post & exposure | L1–L5 clipped columns, L18, L19 rule |
| L-F Night look | L3, L8, L13, L14, L15 |
Critic rules: score against these lines; ADD observed gaps with file@coords; do not contradict a line unless `lum_by_tod.py` /
`haze_regions.py` run on the ref shows the ref violates it. Night used to hide missing city detail is judged as if lit.
