# Water round 06: contact mask (the near-field sparkle stays at walls and piers), rough open water, open-water sun glints

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/water` on top of the r05b state (DistFix 1 kept). Builder: Claude Opus 5.5 high via Devin. Every Unreal process ran inside a
`gpu_slot.sh capture --label water` hold, one engine of this worktree at a time; engines were stopped only with `stop_ue.sh` (driver scripts
first). No engine crashed. Two screening stills ended in a ~4 min hang at exit (engine quit in the same frame as the screenshot request after a
long first-frame stall, no png written); both were cleared with `stop_ue.sh` (SIGTERM, "stopped cleanly"). The Studio was shared with the
terrain / look / city / island sessions (1-2 other engines). Perf was not run (unattended rule; not this round's gate).

## Round 06 result (everything in this folder is ONE build: `build_water.py` blob dc84a75a5005, commit bfb35c5b)
4K stills are native 3840x2160 (`r.ScreenPercentage 100`, internal = output resolution, t = 16 s, 8 fps cap); the dollies are 1920x1080 at
100 % screen percentage, fixed 60 fps step, clip = t 6-16 s (600 frames), x264 CRF 23 (`river_low_dolly.mp4` 10.4 MB, `river_sun_dolly.mp4`
14.5 MB; CRF 20 gave 16.0 / 22.4 MB). The five `*_1080.jpg` are 1920x1080 at 100 % from the same build. Final holds: 12:44-13:19 (build,
4K stills, river_low dolly, four 1080p stills) and 13:23-13:44 (`SKIP_BUILD`: river_sun dolly, river_sun_1080). Numbers: `spec.json` /
`spec.txt` (`python3 tools/water/water_spec.py all docs/night1/water/round-06`, block `-- r06 round targets`; the r06 crops reproduce the
critic's r05 numbers exactly on the r05 frames: 94.1 / 20.9 / 111.5 / 1.49 / 53.5 %).

| check | target | r03 (merged) | r05b | r06 |
|---|---|---|---|---|
| PASS river_low near crop x0-1800 y1200-2160 mean Y | <= 80 | 76.4 | 94.1 | **75.4 PASS** |
| PASS river_sun flanks (x200-700, x2600-3100; y1000-2160) mean Y | <= 85 | 82.8 | 111.5 | **80.2 PASS** (94.3 / 66.0) |
| PASS river_sun sun path / flanks (400 px band) | >= 2.2 | 2.41 | 1.49 | **2.60 PASS** (200 px band 2.65) |
| GATE a seawall band >= 12 px on share of wall rows | >= 60 % | 0 | 80.5 | **70.1 % PASS** (18.6 px mean, band Y 192) |
| GATE b dolly band present every 4 fps frame | 100 % | | 100 | **100 % PASS** |
| GATE b dolly XOR / OR every pair (min / mean) | >= 0.20 | 0.03 | 0.483 / 0.677 | **0.477 / 0.664 PASS** |
| GATE b river_low_dolly autocorr 80 px | <= 0.10 | 0.053 | 0.076 | **0.109 FAIL** (max 0.169; river_sun_dolly 0.034) |
| GATE c harbour_high contact line >= 3 px, share of island columns | >= 50 % | 0.6 | 72.6 | **73.0 % PASS** |
| GATE d under-island darker than open water | >= 15 Y | 32.0 | 28.0 | **27.9 PASS** |
| GATE d far-shore reflection (far strip bright share guard <= 7.16 %) | visible | yes | 6.86 % | **visible; 4.71 % PASS** (reflection hp 13.5) |
| GATE e river_low near hp sd (native crop / pack crop) | >= 12 | 10.1 | 20.9 / 21.4 | **18.25 / 19.03 PASS** |
| GATE e river_sun sparkle width (native rule / pack rule) | >= 50 % | 31.6 / 37.8 | 53.5 / 65.1 | **36.9 / 42.5 % FAIL** |
| harbour_sun_high p1 / R-B (R-B is the atmosphere's, not chased) | <= 55 | | 52.7 / 98.1 | 52.1 / 98.0 |
| harbour_sun_high glints / path columns / median sparkle | | | 1.67 / 100 / 3 | 1.73 / 100 / 3 |
| harbour_high crop hp sd | | 4.27 | 14.72 | 14.69 |
| S4 C14 | 5..35 | 17.9 | 15.5 | 15.5 |
| Perf | | | not measured | not measured (unattended; `gpu_slot perf` exits 75) |

**Two pass lines fail: the river_low dolly autocorrelation (0.109 > 0.10) and the river_sun sparkle width (36.9 % < 50 %).** Both come with
the rough open water that brings river_low / river_sun into range: a rough lobe removes the fine sky speckle that carried r05b's low
autocorrelation and most of its Y >= 200 columns (r05b left flank mean 132). Static-still screening of the autocorrelation
(`tools/water/r06/still_ac.py`, 0.046 on the final 4K still, 0.073 mean of four 1080p shots) did not predict the dolly value (0.109); the
per-second dolly values are 0.04-0.15 and highest in the first 2 s at the river_low point (r05b there: 0.11). The harbour views and S4 are
unchanged against r05b (openW = 0 beyond 400 m; numbers above).
The critic guards (colour, believability, reflections, foam, motion, preference over r03 in >= 4 of 7 pairs) are for the blind critic; the
pack is `/Users/midir/sm2-n1/_scratch/critic-W-r06/pack` (13 pairs: 6 ours vs reference, 7 r03-merged vs r06; both sides of every pair the
same pixel size, <= 2048 px; key beside the pack, not for the critic).


## What changed in `build_water.py` (material parameters, defaults in PARAMS; ShoreMask 0 = r05b)
- **Contact mask** (`cmask`, `openW`): inside the contact box the 0.9 m/px contact map (distance to geometry crossing the water line:
  seawalls, bulkheads, pier piles, bridge piers) gives cmask = 1 - smoothstep(ShoreA 2 m, ShoreB 14 m, d); outside the box the 8 m/px layout
  shore map, 10-40 m (it reads ~28 m at the built river_low seawall, so it is only the fallback). Fade-out ends at 14 m (contact map) / 40 m
  (shore map). openW = (1 - cmask) within OpenD0..OpenD1 (250..400 m) of the camera: the swing-height views (harbour_high,
  harbour_sun_high: nearest water ~430 m) and the S4 perch keep r05b's shading (measured below). The contact-map fetch is shared with the far
  contact line (one fetch per pixel, as before).
- On open water (openW = 1) the final keeps the resolved chop and the second realization shaded (OpenChop 1, OpenB 1; both were 0 in final
  attempt 1, see below), drops the whitecap flecks (OpenWC 0) and puts a GGX roughness floor **OpenRgh 0.4** under it: the sharp-lobe
  sparkle (r05b's frost) is left only within 2-14 m of walls / piers, where the r05b near field (chop, two realizations, sharp lobe <= 0.08,
  lace foam) is unchanged.
- **Open-water sun glints** (OpenGlS, GlitPow, GlitSlK): a pixel whose full-detail normal (shaded slope + the unshaded open-water chop x
  GlitSlK) lies near the sun half-vector (pow(N.H, GlitPow)) is drawn as a sharp facet on the half-vector (roughness 0.06). Off on north-facing
  views (mirror direction more than 60 deg from the sun).
- Also added (variants, not used by the final unless listed): OpenSl (spectrum-layer gain on open water), OpenBend (BendK share on open water),
  OpenGlit / OpenGSp (gain / facet spread of the r03 noise glitter on open water). `Dbg 11` = the mask as unlit colour (R cmask, G openW, B nearW;
  `iter/a_DBG11_rl.jpg`, `iter/a_DBG11_rs.jpg`).

## Screening (1080p stills at t = 16 s, `tools/water/r06/screen.py`; 1080p is upscaled to 4K before the crops, so hp reads ~0.75 x native
and the near mean ~4 Y above native)
What frosted the open water was not the chop: removing the chop, the second realization and the whitecaps from open water made river_low
brighter (101.1 vs 97.8 for ShoreMask 0), and a flatter open water (OpenSl 0.6) brighter still (107.6). The bright frost is the sharp
(<= 0.08) GGX lobe mirroring the bright horizon haze / golden sky at grazing angles. The legacy shader (DistFix 0) was darker because its garbage
distance pushed every pixel into the far-field roughness (~0.3); with DistFix 1 the near field (<= 150 m) is a sharp mirror. Roughness on open
water is the lever:

| variant (hold) | river_low near mean / hp (1080p) | river_sun flanks / path400 ratio / sparkle native (1080p) |
|---|---|---|
| OFF = r05b (A) | 97.8 / 15.6 | 116.3 / 1.38 / 56.1 % |
| mask, chop + B + whitecaps off (A) | 101.1 / 16.7 | 117.7 / 1.38 / 57.3 % |
| + OpenSl 0.6 (A) | 107.6 / 16.1 | |
| + OpenRgh 0.2 (A) | 96.9 / 16.0 | 107.9 / 1.69 / 45.5 % |
| DistFix 0 legacy (B) | 92.0 / 9.6 | 88.8 / 2.15 / 34.3 % |
| + OpenRgh 0.3 (B) | 89.0 / 15.2 | 94.1 / 2.07 / 34.3 % |
| + OpenRgh 0.3, OpenBend 0 (B) | 90.7 / 14.5 | 94.0 / 1.99 / 34.3 % |
| + OpenBend 0 only (B) | 103.7 / 15.2 | 117.7 / 1.38 / 56.6 % |
| + OpenRgh 0.4 (B) | 81.3 / 14.0 | 82.3 / 2.37 / 29.5 % |
| + OpenRgh 0.4, glints GlitPow 3000 (C) | 83.1 / 14.2 | 82.2 / 2.41 / 30.9 % |
| + OpenRgh 0.4, chop + B shaded (C) | 78.3 / 13.1 | 81.8 / 2.36 / 30.3 % |
| + OpenRgh 0.45 (D) | 77.3 / 13.3 | |
| + OpenRgh 0.5 (C / D) | 74.5 / 12.6 | 73.1 / 2.66 / 30.0 % |
| glint variants on OpenRgh 0.4 (C / D: GlitPow 1000-10000, OpenGlS 4, GlitSlK 2-4, OpenGSp 3) | | 81-83 / 2.35-2.69 / 26.0-34.5 % |

The sparkle width (native rule: >= 2 % of the water rows at Y >= 200 per column) of r05b came mostly from that same frost (r05b's left flank
mean 132). Sun glints from 9-deg sun at 6 m height need facet tilts of 35 deg or more 10-25 deg off the sun azimuth, so the pow(N.H) glint
pick stayed at 26-35 % of the columns up to GlitPow 1000. Holds E-G on OpenRgh 0.5 (1080p):

| variant (hold) | river_sun flanks / path400 ratio / sparkle native |
|---|---|
| GlitPow 150, GlitSlK 3 (E, F base) | 75.1 / 2.57 / 29.6 %; 75.0 / 2.58 / 30.5 % |
| GlitPow 80 / 300 / 60 (E, F) | 76.6 / 2.55 / 31.3 %; 73.5 / 2.63 / 29.1 %; 75.9 / 2.63 / 31.7 % |
| glint lobe GlitRgh 0.06 / 0.015 (F; default 0.025) | 74.5 / 2.60 / 29.6 %; 75.2 / 2.55 / 28.1 % |
| glint emission GlitE 20 / 80 / 300 (G) | 74.4 / 2.61 / 29.4 %; 74.7 / 2.60 / 29.9 %; 73.9 / 2.69 / 30.8 % |
| GlitE 80 + GlitPow 60 / + GlitSlK 4.5 (G) | 76.4 / 2.61 / 32.8 %; 76.2 / 2.51 / 28.0 % |

`Dbg 12` (`iter/g_DBG12_rs.jpg`) shows the pick firing across the whole width in the near rows, but at pow(N.H, GlitPow/4) only ~2.5 % of the
water pixels exceed 0.5, so the GlitPow pick is ~0.5 %: about 2-3 pixels per 1080p column, below the rule's 2 % of the rows. Nothing tried in
the glint path moved the sparkle width above 33 %; the final keeps the sparse pick (OpenGlS 1, GlitPow 150, GlitSlK 3, GlitRgh 0.025) and
GlitE 0. River_low is north-facing (the pick is gated off), so none of this touches it.

### Final attempt 1 (hold-G build, blob 329f2d5fa61b: OpenRgh 0.5, OpenChop 0, OpenB 0) - rejected by the dolly
4K native, final hold 1 (11:47-12:11): river_low near mean 72.9 / hp 17.42 (pack 17.82), far-strip bright share 4.84 %; river_sun flanks 73.7
(84.4 / 62.9), path400 ratio 2.57, sparkle 29.9 % native (34.9 % pack); seawall band 64.6 % of rows; harbour_high contact line 73.1 %,
under-island 27.6 Y; harbour_sun_high glints 1.72 %, p1 52.3; S4 C14 15.4; river_low_dolly XOR / OR min 0.475 / mean 0.663 but
**autocorr(80 px) 0.115 (gate <= 0.10; r05b 0.076)**: with the open-water detail neither shaded nor sharp, the long-wave pattern dominates
the high-passed dolly crop. These files are kept in scratch (`_scratch/water/r06g/attempt1/`), not in this folder. A single-still version
of the dolly instrument (`tools/water/r06/still_ac.py`) reads 0.099-0.115 on the OpenRgh 0.5 stills and 0.046-0.058 when the open-water
chop and second realization are shaded (R3B0C, CB): hold H screens OpenRgh 0.4 / 0.45 / 0.5 with OpenChop 1, OpenB 1 (shots at 8-16 s).

| hold H (OpenChop 1, OpenB 1; 1080p) | river_low near mean / hp | still ac80 (mean of 4 shots, 8-16 s) | river_sun flanks / path400 ratio / sparkle native |
|---|---|---|---|
| OpenRgh 0.5 | 72.3 / 12.2 | 0.099 | 73.7 / 2.64 / 32.7 % |
| OpenRgh 0.45 | 75.3 / 12.7 | 0.084 | 77.1 / 2.63 / 36.1 % |
| OpenRgh 0.4 | 76.1 / 12.6 | 0.073 | 81.4 / 2.46 / 32.1 % |

Shading the open-water chop / second realization does not lower the autocorrelation at OpenRgh 0.5; the roughness itself does (a uniform
rough lobe smears the horizon reflection into row-coherent bands). Hold I tried patchy roughness (RghVar: the floor x 1 +- RghVar x 4-30 m
noise) on OpenRgh 0.45: still ac80 0.196 (RghVar 0.5) / 0.197 (0.9) against 0.087 without, and river_low brighter (82.7 / 80.0 vs 73.7):
the patches are themselves 80-px-coherent structure. Dropped (RghVar 0 stays in the shader as a parameter). Hold I was cut by an
auto-PAUSE of the health monitor at 12:28 (WindowServer CPU 95 %, not this hold's engine: it was building headless); the stills were taken
after the auto-lift (12:39) with SKIP_BUILD.

**Final defaults** (build_water.py blob dc84a75a5005, commit bfb35c5b): OpenRgh 0.4 with OpenChop 1, OpenB 1 (the open water keeps its
resolved chop and second realization under the rough floor), ShoreMask 1, ShoreA 2, ShoreB 14, ShoreSA 10, ShoreSB 40, OpenD0 250,
OpenD1 400, OpenSl 1, OpenWC 0, OpenGlit 1, OpenBend 1, OpenGlS 1, GlitPow 150, OpenGSp 1, GlitSlK 3, GlitRgh 0.025, GlitE 0, GlitT 0.4,
RghVar 0. Everything else as r05b. Chosen over 0.45 for the dolly autocorrelation margin (still ac80 0.073 vs 0.084), at the cost of the
river_sun flank margin (81.4 vs 77.1 at 1080p, target <= 85).
