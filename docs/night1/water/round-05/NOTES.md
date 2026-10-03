# Water round 05: contact foam, island reflections, sun colour

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/water`, merged with `origin/Opus-5.5-Loop-Night-1` at 44821e6d (traversal r26 / characters r17; C++ rebuilt with
`build_editor.sh`: OK). Part A (below) is Opus 5.5's interrupted round; part B is the resumed round (Sonnet 5.5 xhigh via Devin) and
supersedes every number in part A: the shader both used had the distance bug found in part B.
Every Unreal process ran inside a `gpu_slot.sh capture --label water` hold, one engine at a time, stopped with `stop_ue.sh` (drivers first); no
engine crashed. The Studio was shared with the look / terrain sessions (1-2 other engines, GPU 0-80 %).

## PART B: round 05b result (everything in this folder is ONE build: `build_water.py` blob 5e552fcd6edb)
4K stills are native 3840x2160 (`r.ScreenPercentage 100`, t = 16 s); the dollies are 1920x1080 (internal 100 %), fixed 60 fps step, clip = t 6-16 s
(600 frames), x264 CRF 23 (`river_low_dolly.mp4` 11.3 MB) / CRF 26 (`river_sun_dolly.mp4` 10.8 MB; CRF 20 and 23 were 25.9 / 16.8 MB). The five 1080p
stills (`*_1080.jpg`) are 1920x1080 at 100 % screen percentage, from the same build (holds G3 07:40-08:14 and G4 08:15-08:40, `SKIP_BUILD`). Numbers: `spec.json` / `spec.txt` (`python3 tools/water/water_spec.py all docs/night1/water/round-05`).

| check | target | r03 | r04 | r05 as Opus left it (legacy shader) | r05b FINAL |
|---|---|---|---|---|---|
| GATE seawall band >= 12 px (Y >= 180) on share of wall rows (crop) | >= 60 % | 0 | 0 | 96.5 % | **80.5 %** PASS (22.2 px mean, band Y 194) |
| GATE band present in every 4 fps dolly sample (>= 50 band px) | 100 % | | 0 | 100 % | **100 %** PASS (min 308 px at the end of the clip) |
| GATE XOR / OR of the band masks, every consecutive 4 fps pair | >= 0.20 | 0.03 | 0.0 | min 0.197, mean 0.375 | **min 0.483, mean 0.677** PASS (39 pairs) |
| GATE harbour_high bright contact line >= 3 px, share of island-seawall columns | >= 50 % | 0.6 | 0.7 | 0.6 | **72.6 %** PASS (median 4 px) |
| BLOCKER harbour_high water under the island vs open water (Y darker) | >= 15 | 32.0 | 18.8 | 21.4 | **28.0** PASS (streak spread 42.6; r03 44.0, r04 22.3) |
| BLOCKER river_low far-shore reflection | visible | yes | no | yes (but a flat white bar over the far quay) | **yes**; far-strip bright share 6.86 % (r03 4.16, legacy r05 13.3; guard <= 7.16) |
| BLOCKER harbour_sun_high p1 / R-B (crop) | <= 55 / <= 70 | | 52.7 / 100.0 | 51.7 / 98.8 | **52.7 PASS / 98.1 FAIL** (atmosphere: look piece, not chased) |
| HOLD harbour_high crop hp sd | >= 7.5 | 4.27 | 8.19 | 8.11 | 14.72 PASS (reference 9.3: possibly too busy, see next steps) |
| HOLD harbour_sun_high glints / path columns / median sparkle | 0.5 % / 50 % / 6 px | | 0.61 / 100 / 3 | 0.53 / 100 / 3 | **1.67 / 100 / 3** PASS |
| HOLD river_low near hp sd | >= 12 | 9.93 | 11.74 | 10.64 FAIL | **21.36** PASS |
| HOLD river_low near mean Y | <= 80 | 78.5 | 62.0 | 78.8 | **93.5 FAIL** (silver sky reflection; reference 58.6) |
| HOLD river_low_dolly autocorr 80 px (river_sun_dolly) | <= 0.10 | 0.053 (0.015) | 0.076 (0.024) | 0.064 | 0.076 PASS (max 0.151) (0.050) |
| HOLD S4 C14 | 5..35 | 17.9 | 22.0 | 15.0 | 15.5 PASS |
| HOLD river_sun sparkle width | >= 50 % | 37.8 | 50.5 | 38.4 FAIL | **65.1 %** PASS |
| Not scored since r03: river_low p1 <= 25 / p99.5 >= 150 / glints >= 1 % | | | | | 30.9 FAIL / 175 PASS / 8.2 % PASS |
| Perf (water <= 2.5 ms) | | | 2.51 | not measured | **not measured** (no attended Mac: HID idle 5.8 h; `gpu_slot perf` would exit 75). The near field now really runs, so expect it to cost more than r04's 2.5 ms: measure first thing |

## What was wrong (found with Dbg 10, hold D, evidence `iter/e_DBG10_*`, `iter/e_base_harbour_high_4k.jpg`)
`Dbg 10` on harbour_high showed the contact map and the pixel footprint reading correctly at the island tip (a CPU ray-cast of the camera onto
the map, `tools/water/r05/proj_contact.py`, puts the 2 m contour exactly on the rendered seawall edge: the map covers the tip as rendered), but the
column `dist / 2000 m` read >= 1 at every water row from 300 m to 1.5 km and `nearW` read 0. In the pixel shader `WPos` (the WorldPosition
node, "exclude all shader offsets") is the grid vertex position BEFORE the camera-following WPO, i.e. relative to the water actor at the
origin, not the pixel's world position. So `dist`, `V`, `down` and `nearW` were computed from (camera - that point): about |camera| from the
origin (777 m at river_low, 4.7 km at harbour_high), a horizontal view vector, `nearW` = 0 and `down` = 0, in every view, since round 02 (Dbg 10
river_low: nearW 0.00 under the camera before the fix, 0.999 after). That explains every open question of part A:
- the far contact line was multiplied by `1 - smoothstep(1750, 2500, dist)` = 0 at harbour_high (gate 3: 0.6 %), but not at river_low
  (|camera| = 777 m);
- the "near-field" foam branch never ran: the seawall band of part A was the FAR block (that is why `Dbg 4` / `Dbg 7` "lied": they read variables
  of a branch that never executed; r04's "no foam" was not the ternary and not the texture import either);
- the two-realization near field, the resolved wind chop (MicroK was never exercised), the from-above weighting of r04 (`down`) and
  everything using V (bend, glitter, grazing roughness) ran with a garbage view vector;
- r04's near-crop mean Y 62 came from `GrazeRough 0.42` applying to ALL water (garbage dist) and the legacy hp numbers from that matte floor.
**Fix**: `wp = float3(Lag.xy, -1.6)` (the pixel's world xy from the vertex interpolator, water plane z); `DistFix` 1 (0 = legacy, kept as a variant);
the far line's range gate uses the true distance in both modes. Legacy vs fixed at 1080p (hold E): river_low hp 7.3 -> 12.9 (4K 21.4),
river_sun sparkle width 38.2 -> 65.3 %, harbour_high hp 5.8 -> 14.8, harbour_high contact line 77.8 % (legacy + the gate fix) / 73.3 %.

## What else changed in `build_water.py` (all parameters of the material, defaults in PARAMS)
- `FarMaxM` 16 / `FarLowK` 0.7: the far contact line is capped in metres. Part A's `FarPx` footprints painted a 40 px flat white bar over the far
  quay at river level (bright share of the far strip 13.3 % vs r03 4.2 %); from 1.3 km up 16 m is ~5 px, enough for gate 3.
- Near foam is lace, not a sheet: `CovMax` 0.56 (coverage cap), `CBias` 1.6 (the map's zero contour lies 0.1-1.4 m land-side of the rendered
  waterline, so the zone must reach ~1.9 m), `PatFine` 1 (finer 0.4 m term, less 1.9 m clumping), `FoamTK` 28 (foam drift 0.1-0.2 m/s),
  `BreathK` 0.3 / `BreathW` 2.2 (the band's edge breathes with the swell), `LapDens` 0 (density does NOT follow the swell: with it, the band
  saturated into a solid sheet at the lap maxima, T = 7.0-7.7 s and 9.3-10 s, and the pairwise XOR / OR fell to 0.10-0.15).
- `BandPx` (screen-pixel cap of the band; default 0 = off): at 55 it removed the foam (map offset), kept as a documented dead end.
- `RCalm`, `LFa`, `LFb`, `GSpread`, `FarEmisK`, `MicroK` (now 1.0, was 2.0), `DistFix`: parameters used by the variants; not needed by the final.
- Dbg 10 (8 interleaved columns + calibration ramp) stays in the shader; decoder in `tools/water/r05/report_r05d.py`.

## Instruments added / changed (`tools/water/`)
- `water_spec.py foam`: the seawall edge line is now FIXED (`FOAM_EDGE_REF`, median of six per-frame fits; the per-frame `_wall_edge` fit
  moved 12-55 px with the water colour, r05 final per-frame fit would read 71.5 % instead of 80.5 %); the per-frame value is still printed.
  Part A's table used the per-frame fit (old r05 build: 96.5 % per-frame, 96.7 % fixed).
- `farshore.py` (river_low far-quay bright-bar guard, in `water_spec.py all`), `r05/selfshift.py` (single-still gate-2 proxy),
  `r05/static_pairs.py`, `r05/dolly_pairs.py` (per-pair XOR / OR), `r05/make_pack.py` (blind-critic pack), `r05/report_r05d.py`.
- The dolly gate was screened WITHOUT dollies: stills at the dolly positions 3 m / 7 m (`Water_View_RiverLow_P3/_P7`) at the dolly times
  (T = 7.5 / 9.5 s); `selfshift` of those stills tracked the dolly pairs (0.17 -> 0.11 at the saturated phase of the CovMax 0.9 build).

## Iteration log (holds; scratch `_scratch/water/r05{d..m}`, kept iteration stills in `iter/`)
D (04:34) Dbg 10 build -> found the bug. E (04:47) DistFix build: harbour_high gate 3 73 %, DF0 vs fixed, MicroK 0.5/1/2. F/F2 (05:18-05:44) 4K stills
of the four water views + ScatK / MicroK / CBias / CovMax variants (ScatK 0.02 made the water brighter, not darker: not used). G (05:48) CovMax 0.9:
gate 1 88.7 % but dolly min 0.107 (solid sheet). H-I (06:13-06:35) lace parameters, static screens. J-K (06:37-06:58) dolly-position stills;
BandPx dead end. L (07:02) CBias 1.6 / CovMax 0.66: dolly min 0.15 at the lap maxima. M (07:23) LapDens 0, CovMax 0.56: p3 @ 7.5 s proxy 0.76,
4K gate 1 67.5 % -> the final build. G3/G4 (07:40-08:40) the final captures. One engine hung 5 min at exit after its screenshot (hold M, C50_p3):
stopped with `stop_ue.sh` (drivers first, SIGTERM was enough); no crash, no SIGKILL.

## Honest failures, open items
- river_low near mean Y 93.5 (hold <= 80) and p1 30.9: bright silver sky reflection on the chop; ScatK did not darken it; reference is 58.6 / 14.
  Likely lever: sky / look piece, or more slope variance at 10-60 m with a darker environment.
- harbour_sun_high R-B 98.1 (<= 70): the atmosphere's in-scatter toward the 9 deg sun (part A; look piece).
- harbour_high is busier than the reference (hp 14.7 vs 9.3) and its from-above ripple texture is uniform; river_sun is a bright gold sheet
  (near-crop mean Y 145, 63 % of pixels Y >= 140; r03 148 / 53 %). The r03 "0 pale blobs" counter reads 1398 on any textured surface (it was a decal detector).
- The per-frame dolly row share (>= 6 px at 1080p) falls to 2 % late in the clip: the static edge line leaves the wall as the camera passes
  the pier corner; the band itself is present (>= 308 px) in all 40 samples.
- Not measured: perf; critic not run (builder never runs it).

---

# PART A: round 05 as Opus 5.5 left it (LEGACY shader: all numbers in this part were measured with the distance bug described in part B)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/water`, merged with `origin/Opus-5.5-Loop-Night-1` at de80d8ef (traversal C++ rebuilt with `build_editor.sh`: OK).
Every Unreal process ran inside `gpu_slot.sh capture` holds, one engine at a time (the lock's `slots` file read 4 during these holds; the
Studio was shared by 3-5 other Unreal processes, which made 1080p runs take 35 s in hold 1 and ~4 min in hold 2).

## Holds
1. **Hold 1** (12:20:37-12:33:42, 785 s, 1080p only): build with 16 variants, `Dbg 9` (t 16 + 45 s), contact-texture candidates, reflection
   and colour variants. Stills + report: `iter/h1_*` (`iter/h1_report.json`).
2. **Hold 2** (12:36:07-12:57, stopped by me with `stop_ue.sh` after 2 stills): the build waited ~6 min for other agents' instances and
   then took 458 s; each 1080p run took ~4 min, so the planned variant pass + final set could not fit the 2400 s max hold (whose end is a
   SIGTERM / SIGKILL of the process group). Two stills were kept (`iter/h2_*`): enough to settle the colour question.
3. **Final hold A** (13:18:23-13:52:35, build a6a35140 of build_water.py; evidence kept in `_scratch/water/r05/finalA/`): build 9.5 min
   under load, river_low_4k, river_low_dolly (967 frames at ~1 frame/s), harbour_high_4k, river_low_1080; the rest skipped by the per-run
   deadline (the hold ended at 2052 s, never near the 2400 s kill). Results that changed the build:
   - seawall gate 1 PASS: band >= 12 px on 97.3 % of wall rows, mean 41.8 px, band luma 203 (`water_spec.py foam`).
   - gate 2 PASS by the critic's wording: band present in all 40 samples at 4 fps, XOR/OR mean 0.37, minimum over consecutive pairs 0.201;
     dolly autocorr(80 px) 0.064. (A per-frame row share against the still's wall line dips to 8 % late in the clip, where the moving
     camera brings the pier corner in: the band is continuous there, `iter` has the frame.)
   - river_low near crop HOLDS FAILED: hp sd 10.68 (>= 12), mean Y 80.1 (<= 80). By depth band the far rows of the crop lost structure
     (hp 14.9 -> 10.8, Y 66 -> 92): ShoreCalm also removed the r04 gains on 100-300 m river-level water. Fixed: the calm now applies seen
     from above or beyond 300-500 m only.
   - harbour_high far contact line FAILED: 0.6 % of seawall columns. Ray-casting the edge pixels: the map reads 3-11 m two pixels below the
     visible edge, the shore gate value is 41-82 m (it cut part of the band), and even where my CPU evaluation of the formula gives wf ~0.7
     nothing rendered. Rebuilt branch-free and without the shore gate.
   - harbour_high reflections: under-island 21.2 Y darker than open water, streak spread 36.2 (r03 44.0, r04 22.3), hp sd 8.22.
4. **Final hold B** (14:18:41-14:52:53, 2052 s; build_water.py blob 703aa5250bd2 = commit 8f9d4279's script): build 6 min, the five 4K
   stills (native 3840x2160, `r.ScreenPercentage 100`, t = 16 s, 8 fps cap) and `river_low_dolly.mp4` (1920x1080 at 100 %, fixed 60 fps
   step, t 6-16 s, 600 frames, CRF 20, 13.1 MB). The files in this folder come from this hold. Dbg 10 (debug-only branch) was committed after it.
5. **Hold C** (queued at 14:53): `river_sun_dolly`, the 1080p stills from the same content (no rebuild), then a Dbg 10 build + still if time is left.

## Numbers (`spec.json`; `python3 tools/water/water_spec.py all docs/night1/water/round-05`, section `-- r05 round targets`)
| check | target | r03 | r04 | r05 |
|---|---|---|---|---|
| GATE seawall band >= 12 px, Y >= 180, share of wall rows | >= 60 % | 0 | 0 | **96.5 %** PASS (mean 41.3 px, band Y 202.5) |
| GATE band in every 4 fps dolly sample (>= 50 band px) | 100 % | | 0 | **100 %** (40 / 40) PASS |
| GATE band XOR / OR between consecutive 4 fps samples | >= 0.2 | 0.03 | 0.0 | **mean 0.375, min 0.197** (one pair 0.003 under) |
| GATE harbour_high contact line >= 3 px on the island seawall | >= 50 % of columns | 0.6 % | 0.7 % | **0.6 % FAIL** (see below) |
| BLOCKER harbour_high under-island vs open water | >= 15 Y darker | 32.0 | 18.8 | **21.4** PASS; streak spread 36.4 (r03 44.0, r04 22.3) |
| BLOCKER river_low far-shore reflection | visible | yes | no | **yes** (GrazeRough 0; compare `river_low_4k.jpg` rows 900-1500 with r03 / r04) |
| BLOCKER harbour_sun_high p1 / R-B (crop) | <= 55 / <= 70 | | 52.7 / 100.0 | **51.7** PASS / **98.8 FAIL** (atmosphere, see below) |
| HOLD harbour_high hp sd | >= 7.5 | 4.27 | 8.19 | **8.11** PASS |
| HOLD harbour_sun_high glints / path columns / median sparkle | 0.5 % / 50 % / 6 px | | 0.61 / 100 / 3 | **0.53 / 100 / 3** PASS |
| HOLD river_low near hp sd / mean Y | >= 12 / <= 80 | 9.93 / 78.5 | 11.74 / 62.0 | **10.64 FAIL** / 78.8 PASS |
| HOLD river_low_dolly autocorr 80 px | <= 0.10 | 0.053 | 0.076 | **0.064** PASS |
| HOLD S4 C14 | 5..35 | 17.9 | 22.0 | **15.0** PASS |
| HOLD river_sun sparkle width | >= 50 % | 37.8 | 50.5 | **38.4 FAIL** |

The two failed holds are the price of the reflection blocker, measured: river_low near hp is 10.68 with ShoreCalm at river level and 10.64
without it, so it is GrazeRough 0 (the far rows of the crop lost r04's rough-lobe contrast: hp 14.9 -> 10.8); river_sun's sparkle width is
back at r03's value (37.8 -> 38.4) with GrazeRough 0 and the far-field calm. Not separated this round: whether LongK 3 at river level (calm
off beyond 500 m) keeps the far-shore reflection and brings the sparkle width back.

## harbour_high contact line: still none
The far line renders at river level (the far pier across the basin in `river_low_4k.jpg` has a foam line, rows ~1080-1100), but not at the
island tip seen from 260 m. Both forms (branched and shore-gated in final hold A, branch-free and ungated in B) gave 0.6 %. A CPU ray-cast of
the edge pixels (camera from views.json) reads the map at 3-11 m two pixels below the edge and a footprint of ~2.7 m (band >= 16 m with
FarPx 6), which should give coverage ~0.7; so either the ray-cast does not match the engine camera there or the map does not hold the
tip's rendered seawall. `Dbg 10` (committed: contact distance, footprint and coverage as emissive columns, the Dbg 9 style that proved
reliable) answers which; hold C runs it if its time allows (`iter/h3_DBG10_harbour_high.jpg`).


## Foam gate: diagnosis and fix
- **`Dbg 9` (hold 1) clears the import path.** Thermometer bands (`iter/h1_DBG9_river_low_00_t016.0.jpg`, identical at t 45 s) read in-engine:
  `T_WaterContact` 4096 x 8192, 1 mip; `Load()` at the texel the file reads 0 m = 0 m; `SampleLevel` at that UV = 0 m; at the open-water probe
  10 m off the wall 11.5 m (file 11.7 m). The half-res Interchange + NeverStream copy (B) and the legacy-factory copy (C) read the same
  (0.3 m / 11.5 m), `T_ShoreDist` reads 39 m at the probe. The build log's TEXINFO lines agree (TC_Grayscale, NoMipmaps, World group,
  sRGB off, no VT). So the texture, its size, format, mips and streaming were never the fault.
- **The r05 build renders the band.** Hold 1 `base_river_low` (CSel 0, CBias 0.8): band on 84 % of wall rows (1080p frame upscaled to
  the 4K crop geometry), band luma 200; C1 / C2 (B / C maps): 90 %; C1F (CBias 1.4, FoamK 2.8): 100 %, 57 px. The band widens with
  CBias, so the contact map drives it. r04's frames show none.
- **What changed between r04 and r05 in this path** (`git diff 01f89b51 HEAD -- unreal/WebHomage/Scripts/build_water.py`): (1) the map
  lookup: r04 sampled inside a ternary (`cond ? Texture2DSampleLevel(...) * cmax : cmax`), r05 in an `if / else` chain inside
  `[branch] if (all(cu > 0) && all(cu < 1))`; (2) the texture import now calls `post_edit_change()` on every texture before saving. CBias,
  FoamK, FoamNK, lap and the pattern are unchanged. Which of the two fixed it is NOT isolated (no rebuild of the r04 form was spent on it).
- **The debug views lie for this term.** `Dbg 7` (hold 1, `iter/h1_DBG7C1_river_low.jpg`) still shows the defaults (contact 32 m,
  ray 99 m, cf 0) at the same wall pixels where the non-debug build renders the band; `Dbg 4` on harbour_high shows no wf either. The r04
  conclusion "the in-engine map reads >= 4 m" came from this view. Do not use Dbg 4 / 7 for the contact term; Dbg 9 (fixed-UV
  emissive thermometers) and the beauty frames are reliable.
- **Far contact line (gate 3, new).** Foam stopped at NEAR_M (150 m), and the island seawall is ~1 km from `harbour_high`. r05 adds a
  far line: the same map within 80 m of land on the shore map, out to `FoamFar` 2500 m, no sub-metre pattern, breathing with the swell.
  Hold 1 measured it at 0.3 % of seawall columns: a 1-2 m band is under 1 px there. The band now spans at least `FarPx` (6) pixel footprints.

## Reflections (merge-blocker)
- `GrazeRough` back to 0 (r04's 0.42 grazing floor blurred the far-shore reflection at river level; perf is not this round's gate).
- `ShoreCalm`: the r04 far-field gains (LongK 3, MidK 2) fade out within ShoreCalm m of land, so sheltered water along the island mirrors it.
  Hold 1, harbour_high at 1080p: island-streak spread (100-px column means, x 1000-2800) SC0 29.6, SC150 31.9, SC300 36.6, SC380 38.7,
  L2 (LongK 2) 38.7 (4K: r03 44.0, r04 22.3); under-island vs open water 22-24 Y darker in all (>= 15). hp sd 7.2-7.3 at 1080p.
  ShoreCalm 380 is the default.

## Sun colour (merge-blocker): not movable from the water material
- `SunSpecK` (F0 x 0.6 / 0.4 / 0.25 on sun-facing swing-height water) left harbour_sun_high's colour identical (crop R-B 100.1 / 100.1 /
  99.9, p1 54.5); only the glints dimmed (0.53 -> 0.37 %). SLW's reflection does not follow the Specular input.
- `SunTilt` 0.2 (shading normal leaning toward the camera, so the mirror ray climbs out of the grazing Fresnel peak): R-B 100.0 vs 99.7 at 0
  (hold 2). A 0.2 lean should have cut the reflected sky sharply, so the brass is not the water's reflection: it is the atmosphere's
  forward in-scatter over 1-3 km toward a 9 deg sun (the far rows are the most orange: upper band R-B 113). Both levers were removed.
  This needs the look / sky piece (fog / aerial-perspective colour toward the sun) or a reconciled target; the crop p1 (53-55) is at the
  limit already.
