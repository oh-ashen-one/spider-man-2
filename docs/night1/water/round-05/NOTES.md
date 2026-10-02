# Water round 05: contact foam (gate), island reflections, sun colour (Opus 5.5)

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
The far line renders at river level (the far pier across the basin in `river_low_4k.jpg` has a foam line, rows ~1030-1060), but not at the
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
