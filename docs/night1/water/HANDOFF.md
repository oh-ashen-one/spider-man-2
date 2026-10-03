# River water: handoff after round 05b (Sonnet 5.5 xhigh via Devin, resumed after Opus 5.5's interrupted round 05)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

Branch `night1/water`, worktree `~/sm2-n1/water`, scratch `/Users/midir/sm2-n1/_scratch/water/`. W owns `/Game/Water`,
`unreal/WebHomage/Scripts/build_water.py`, `docs/night1/water/`, `tools/water/`. No `.uasset` / `.umap` is committed; no IP is copied.
Merged with `origin/Opus-5.5-Loop-Night-1` at 44821e6d (traversal r26 / characters r17; C++ rebuilt with `build_editor.sh`: OK).
STATE: WORK IN PROGRESS (round 05b final capture not yet taken when this stub was written; the section "Round 05b result" is filled at the end).

## The one thing to know (found with Dbg 10, round 05b)
In the water pixel shader `WPos` is the grid vertex position BEFORE the camera-following WPO (relative to the actor at the origin), not the
pixel's world position. Since round 02 `dist`, `V`, `down`, `nearW` were computed from camera minus that point: |camera| from the origin
(777 m at river_low, 4.7 km at harbour_high), a horizontal V, `nearW` = 0 and `down` = 0 in every view. So the near field (two realizations,
resolved wind chop, near foam branch), the from-above logic of r04 and everything using V ran in "far mode" with a garbage view vector; the
seawall band of r05 was the far-line block; the far line was gated off at harbour_high (gate 3 at 0.6 %). Fixed: `wp = float3(Lag.xy, -1.6)`
(`DistFix` 1; 0 = the legacy behaviour, a variant). Everything in `round-05/` is the fixed shader; r03-r05 numbers belong to the legacy one.

Details, numbers and the iteration history: `round-05/NOTES.md`; instruments: `tools/water/water_spec.py all <round dir>`, `tools/water/farshore.py`,
`tools/water/r05/{selfshift,static_pairs,dolly_pairs,report_r05d}.py`.
