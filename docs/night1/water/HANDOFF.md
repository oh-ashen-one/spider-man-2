# River water: handoff after round 06 (Claude Opus 5.5 high via Devin)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

Branch `night1/water` (pushed), worktree `~/sm2-n1/water`, scratch `/Users/midir/sm2-n1/_scratch/water/`. W owns `/Game/Water`,
`unreal/WebHomage/Scripts/build_water.py`, `docs/night1/water/`, `tools/water/`. No `.uasset` / `.umap` is committed (CONTENT.md), no LFS; no IP
copied. Integration (`Opus-5.5-Loop-Night-1`) carries water r03; r05 / r05b / r06 are not merged. Round 06 was the director's bounded last
round: if it does not merge, water stops here.

`round-06/` holds the final captures of ONE build (`build_water.py` blob 329f2d5fa61b), `round-06/NOTES.md` the full story (screening holds
A-G with numbers), `round-06/spec.json|txt` the measured numbers (`python3 tools/water/water_spec.py all docs/night1/water/round-06`, block
`-- r06 round targets`). The blind critic was NOT run by the builder; its pack is `/Users/midir/sm2-n1/_scratch/critic-W-r06/pack`
(pairs.json beside it).

## What round 06 changed (build_water.py; ShoreMask 0 restores r05b exactly)
- Contact mask: `cmask` = 1 within ShoreA 2 m .. ShoreB 14 m of walls / piers / piles (0.9 m/px contact map; outside its box the layout shore
  map, 10..40 m); `openW` = 1 - cmask within OpenD0 250 .. OpenD1 400 m of the camera (river-level views only: the harbour views and S4 are
  unchanged, measured).
- Open water (openW): chop not shaded (OpenChop 0), second realization off (OpenB 0), whitecaps off (OpenWC 0), GGX roughness floor
  OpenRgh 0.5. Within 2-14 m of walls / piers the r05b near field (chop, two realizations, sharp lobe, lace foam) is unchanged.
- The finding: the r05b "frost" was the sharp (<= 0.08) near-field lobe mirroring the bright horizon haze, not the chop; removing chop / B /
  whitecaps alone made river_low brighter. The legacy (DistFix 0) shader was darker only because its wrong distance put every pixel into the
  far-field roughness. Roughness on open water is what moves river_low near mean and the river_sun flanks / path.
- Open-water sun glints (OpenGlS, GlitPow, GlitSlK, GlitRgh, GlitE): picked from the full-detail normal; they stay sparse (~0.5 % of pixels)
  and did not move the sparkle width (all variants 26-35 %).
- Debug: `Dbg 11` mask colours, `Dbg 12` glint pick. Instruments: `water_spec.py` r06 block (`r06_low`, `r06_sun`; they reproduce the critic's
  r05 numbers exactly: 94.1 / 20.9 / 111.5 / 1.49 / 53.5 %), `tools/water/r06/screen.py` (1080p screening).

FINAL_TABLE_PLACEHOLDER

## Next steps (only if the owner / director reopens water)
1. River_sun sparkle width (gate e, native rule >= 50 %): r05b's 53.5 % was mostly the sky frost the director asked to remove (its left flank
   mean was 132). At 6 m height and a 9-degree sun, glints 10-25 degrees off the sun azimuth need facet tilts >= 30-58 degrees; the pow(N.H)
   pick could not produce 2 % of the rows per column. Options: a reconciled rule (e.g. Y >= 200 on >= 0.5 % of the rows, or sparkle counted
   within the sun path only), a higher river_sun camera, or a dedicated capillary glint layer with a much wider slope distribution in the
   near 30 m (would need its own believability check).
2. Perf: not measured since r04 (unattended rule). The near field (<= 150 m) now runs for real; the open water skips the chop and the second
   realization, the contact fetch is shared with the far line.
3. harbour_sun_high R-B 98 is the atmosphere's (look piece); harbour_high hp 14.6 is busier than the reference (9.3).
4. Foam drift (secondary): seawall band XOR / OR is in the flicker range (> 0.5); FoamTK 28 -> lower values would drift slower but risk gate b
   (>= 0.20 every pair). Screen with `tools/water/r05/selfshift.py` stills before a dolly.

## How to rebuild / re-capture (all headless; every Unreal process inside `gpu_slot.sh capture`)
```
S=/Users/midir/sm2-n1/_scratch/water
# inputs (CPU) only if missing: grid, noise, shore map, slope, chop, contact map (+ B copy)
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 python3 unreal/WebHomage/Scripts/build_water.py --steps inputs
SM2_WATER_SCR=$S python3 unreal/WebHomage/Scripts/build_water.py --steps contactb
python3 tools/water/r05/hlsl_check.py                 # offline DXC compile of the generated pixel shader: status 0x0
# screening hold (build with variants + 1080p stills; RD / VJ / SHOTS env, see the script):
RD=$S/r06x VJ=tools/water/r06/variantsG.json /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash tools/water/r06/holdA.sh
python3 tools/water/r06/screen.py $S/r06x/stills
# final hold(s): builds when $S/r06g/BUILT != git hash-object of build_water.py, then 4K stills, dollies, 1080p stills (re-runnable)
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash tools/water/r06/final_g.sh
bash tools/water/r06/post_r06.sh                      # crops, iter copies, dolly pairs, spec.json / spec.txt
python3 tools/water/r06/make_pack.py                  # blind-critic pack (pairs.json, same pixel size both sides, <= 2048 px)
```
Gotchas: `stop_ue.sh "/Users/midir/sm2-n1/water"` also kills any of YOUR shell loops whose command line contains the worktree path (it
killed a queued chain once): launch chained holds from a script under `_scratch/water/` that `cd`s inside. `kill -0 0` is always true (process
group): pass a real pid. Two screening runs stalled ~70 s on the first frame (variant shader), quit in the screenshot frame without writing it
and hung ~4 min at exit: `stop_ue.sh` cleared both with SIGTERM. Screening numbers vary +-3 Y run to run (animation phase / exposure).

## State at hand-off
- No engine of this worktree running; no chain scripts left. Scratch: holds `r06a`..`r06g2`, final `r06g`, captures `cap/`.
