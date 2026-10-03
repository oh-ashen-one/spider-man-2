# River water: handoff after round 05b (Sonnet 5.5 xhigh via Devin, resumed after Opus 5.5's interrupted round 05)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

Branch `night1/water` (pushed), worktree `~/sm2-n1/water`, scratch `/Users/midir/sm2-n1/_scratch/water/`. W owns `/Game/Water`,
`unreal/WebHomage/Scripts/build_water.py`, `docs/night1/water/`, `tools/water/`. No `.uasset` / `.umap` is committed (CONTENT.md), no LFS; no IP is
copied. Merged with `origin/Opus-5.5-Loop-Night-1` at 44821e6d (traversal r26 / characters r17; C++ rebuilt with `build_editor.sh`: OK).
`round-05/` holds the final captures of ONE build (`build_water.py` blob 5e552fcd6edb), `round-05/NOTES.md` the full story (part B = this round, part A = Opus's
interrupted round on the legacy shader), `round-05/spec.json|txt` the numbers. The blind critic was NOT run by the builder; its pack is
`/Users/midir/sm2-n1/_scratch/critic-W-r05/pack` (key beside it, not for the critic).

## The one thing to know (found with Dbg 10)
In the water pixel shader `WPos` is the grid vertex position BEFORE the camera-following WPO (relative to the actor at the origin), not the pixel's
world position. From round 02 to the Opus part of round 05 `dist`, `V`, `down`, `nearW` were computed from camera minus that point: |camera| from the
origin (777 m at river_low, 4.7 km at harbour_high), a horizontal V, `nearW` = 0, `down` = 0 in every view. The near field (two realizations,
resolved wind chop, near foam branch), the from-above logic of r04 and everything using V ran in "far mode" with a garbage view vector; the r05 seawall
band was really the far-line block, and the far line was gated off at harbour_high (gate 3: 0.6 %). Fixed with `wp = float3(Lag.xy, -1.6)` (`DistFix`
1; 0 = legacy, kept as a variant). All r03 / r04 / r05-Opus numbers belong to the legacy shader; do not compare them blindly with part B.

## Round 05b result (spec.txt; 4K native, dollies 1080p)
| check | target | r03 | r04 | r05 Opus (legacy) | r05b |
|---|---|---|---|---|---|
| GATE seawall band (crop) >= 12 px on share of wall rows | >= 60 % | 0 | 0 | 96.5 % | **80.5 %** |
| GATE band in every 4 fps dolly frame | 100 % | | 0 | 100 % | **100 %** |
| GATE XOR / OR every 4 fps pair (min / mean) | >= 0.20 | 0.03 | 0.0 | 0.197 / 0.375 | **0.483 / 0.677** |
| GATE harbour_high contact line >= 3 px, share of island columns | >= 50 % | 0.6 | 0.7 | 0.6 | **72.6 %** |
| BLOCKER under-island darker than open water | >= 15 Y | 32.0 | 18.8 | 21.4 | **28.0** |
| BLOCKER far-shore reflection | visible | yes | no | yes + white bar | **yes** (bar share 6.86 %, r03 4.16) |
| BLOCKER harbour_sun_high p1 / R-B | <= 55 / <= 70 | | 52.7 / 100 | 51.7 / 98.8 | **52.7 / 98.1 (R-B FAIL: atmosphere)** |
| HOLD river_low near hp sd / mean Y | >= 12 / <= 80 | 9.9 / 78.5 | 11.7 / 62.0 | 10.6 / 78.8 | **21.4 / 93.5 (mean Y FAIL)** |
| HOLD river_sun sparkle width | >= 50 % | 37.8 | 50.5 | 38.4 | **65.1 %** |
| HOLD harbour_sun_high glints / path / sparkle | 0.5 / 50 / 6 | | 0.61 / 100 / 3 | 0.53 / 100 / 3 | 1.67 / 100 / 3 |
| HOLD dolly autocorr 80 px; S4 C14 | <= 0.10; 5..35 | .053; 17.9 | .076; 22.0 | .064; 15.0 | .076; 15.5 |
Perf not measured (no attended Mac). The near field now actually runs: expect more than r04's 2.51 ms.

## Next steps (in order)
1. Perf, first thing on an attended Mac (`tools/water/capture_round.sh <round> perf`, `perf_summary.py`): the fixed shader executes the near block
   (second realization, chop, near foam, contact map) for every pixel within 150 m. If it is over 2.5 ms: `NEAR_M` 150 -> 100, drop the second
   realization of the 2.2 m layer, or the chop `lostC` terms; measure each.
2. river_low mean Y 93.5 (hold <= 80, reference 58.6, p1 31 vs 14): silver sky reflection on the chop. ScatK 0.02 made it brighter (not darker); untested:
   ScatK 0.08, a darker horizon band in the look piece, more slope variance at 10-60 m.
3. harbour_high is busier than the reference (hp 14.7 vs 9.3) and the from-above ripple texture is uniform; LongK / MidK did not change it (variant LM1): look at
   `TopVarK`, the 6.7 m / 2.2 m layer gains for `down` > 0.5, `ChopFar`.
4. river_sun is a bright gold sheet (near-crop mean Y 145, 63 % of pixels >= 140; r03 148 / 53 %). MicroK 0.5 gave a more defined sun path and a wider
   sparkle (53-69 %) in the E/F stills but the same mean; the mean there is the sun, so judge it by the critic's "molten metal" wording, not by Y.
5. harbour_sun_high R-B 98 is the atmosphere's (look piece). Nothing in the water moves it (SunSpecK, SunTilt tried in part A).
6. Foam: the map's zero contour is 0.1-1.4 m land-side of the rendered waterline (0.9 m/px; CPU lookups are stair-stepped by ~0.38 m, probably the 2625 -> 4096 resize), which is why the
   zone is 1.9 m wide and lacy. A second contact map at ~0.15 m/px for a ~600 m box around the river_low seawall would let the band hug the wall.
   `BandPx` (screen-pixel cap) is implemented but needs that map to work.
7. The foam gate instrument uses a FIXED edge line (`FOAM_EDGE_REF` in water_spec.py); re-derive it only if the river_low camera or the seawall changes.

## How to rebuild / re-capture (all headless; every Unreal process inside `gpu_slot.sh capture`)
```
S=/Users/midir/sm2-n1/_scratch/water
# inputs (CPU) only if missing: grid, noise, shore map, slope, chop, contact map (+ B copy)
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 python3 unreal/WebHomage/Scripts/build_water.py --steps inputs
SM2_WATER_SCR=$S python3 unreal/WebHomage/Scripts/build_water.py --steps contactb
python3 tools/water/r05/hlsl_check.py                 # offline DXC compile of the generated pixel shader: status 0x0
# build + captures in holds of <= 2400 s (build 5-10 min; 4K still 1.5 min; river_low dolly 16 min; river_sun dolly 17 min):
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash $S/r05g/final_g.sh      # tools/water/r05/final_g.sh
SKIP_BUILD=1 ... same, for the next hold (touch $S/r05g/BUILT with the current `git hash-object` of build_water.py first)
bash tools/water/r05/post_r05b.sh                     # crops, iter copies, dolly pairs, spec.json/txt
python3 tools/water/r05/make_pack.py                  # blind-critic pack (pairs.json, same pixel size both sides, <= 2048 px)
```
Variants (no rebuild of the code): `SM2_WATER_VARIANTS='{"NAME": {"Param": value, "_views": ["river_low", "river_low_p3"]}}'` creates
`/Game/Water/Variants/Water_Var_NAME_<view>`; views are the keys of `views.json` plus `river_low_p3` / `river_low_p7` (dolly points 3 / 7 m).
Screening without dollies: `tools/water/r05/selfshift.py` on stills at p3 @ 7.5 s and p7 @ 9.5 s (`-shots 7.5`) predicts the dolly pairs (needs >= 0.35 at 1080p, k 16).
Do NOT run a hold while an engine of this worktree is stuck exiting; stop engines only with `stop_ue.sh "/Users/midir/sm2-n1/water"` after killing the driver scripts.

## State at hand-off
- Scripts of this round: `tools/water/r05/` (final_g.sh, hold{D..M}.sh + variants{D..M}.json, post_r05b.sh, make_pack.py, report_r05d.py, static_pairs.py,
  selfshift.py, dolly_pairs.py, proj_contact.py / proj_rl.py (CPU projection of the contact map onto a frame), hlsl_check.py + dxc_check.py); older r05 scripts stay.
- Studio load: 1-3 other engines all day; 1080p still 1.5-3 min, 4K 1.5-2 min, dolly ~1-1.5 frames/s.
- A 5 min engine hang at exit happened once (hold M): `stop_ue.sh` cleared it with SIGTERM.
