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
3. **Final hold** (`_scratch/water/r05/final.sh`, re-runnable, per-run deadline): build, then the round-05 set in priority order.

## Foam gate: diagnosis and fix
- **`Dbg 9` (hold 1) clears the import path.** Thermometer bands (`iter/h1_DBG9_river_low_00_t016.0.jpg`, identical at t 45 s) read in-engine:
  `T_WaterContact` 4096 x 8192, 1 mip; `Load()` at the texel the file reads 0 m = 0 m; `SampleLevel` at that UV = 0 m; at the open-water probe
  10 m off the wall 11.5 m (file 11.7 m). The half-res Interchange + NeverStream copy (B) and the legacy-factory copy (C) read the same
  (0.3 m / 11.5 m), `T_ShoreDist` reads 39 m at the probe. The build log's TEXINFO lines agree (TC_Grayscale, NoMipmaps, World group,
  sRGB off, no VT). So the texture, its size, format, mips and streaming were never the fault.
- **The r05 build renders the band.** Hold 1 `base_river_low` (CSel 0, CBias 0.8): band on 84 % of wall rows (1080p frame upscaled to
  the 4K crop geometry), band luma 200; C1 / C2 (B / C maps): 90 %; C1F (CBias 1.4, FoamK 2.8): 100 %, 57 px. The band widens with
  CBias, so the contact map drives it. r04's frames show none.
- **What changed between r04 and r05 in this path:** the map lookup. r04 sampled inside a ternary
  (`cond ? Texture2DSampleLevel(...) * cmax : cmax`); r05 samples in an `if / else` chain inside `[branch] if (all(cu > 0) && all(cu < 1))`.
  Nothing else in the near-foam code changed (CBias, FoamK, FoamNK, lap and pattern are identical). That is the most likely cause, but it
  is an inference: I did not rebuild the r04 form to prove it.
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
