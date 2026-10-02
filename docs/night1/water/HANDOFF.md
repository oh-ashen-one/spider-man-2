# River water: handoff after round 05 (Opus 5.5)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

Branch `night1/water`, worktree `~/sm2-n1/water`, scratch `/Users/midir/sm2-n1/_scratch/water/`. W owns `/Game/Water`,
`unreal/WebHomage/Scripts/build_water.py`, `docs/night1/water/`, `tools/water/`. No `.uasset` / `.umap` is committed; no IP is copied (generated
textures, maps rasterised from the layout and the city export, code). Merged with `origin/Opus-5.5-Loop-Night-1` at de80d8ef this round
(traversal C++ rebuilt with `build_editor.sh`: OK).

## Round 05 result (`round-05/NOTES.md`, `round-05/spec.json`; critic pack `/Users/midir/sm2-n1/_scratch/critic-W-r05/pack`, key beside it)
| check | target | r04 | r05 |
|---|---|---|---|
| GATE seawall band (crop) | >= 12 px on >= 60 % of wall rows | 0 | **96.5 %** PASS (41 px, Y 202) |
| GATE band in every 4 fps dolly sample / XOR-OR change | 100 % / >= 0.2 | 0 / 0.0 | **100 %** / mean **0.375**, min pair 0.197 |
| GATE harbour_high contact line on the island seawall | >= 3 px, >= 50 % of columns | 0.7 % | **0.6 % FAIL** |
| BLOCKER under-island darker than open water / far-shore reflection | >= 15 Y / visible | 18.8 / no | **21.4 / yes** PASS |
| BLOCKER harbour_sun_high p1 / R-B | <= 55 / <= 70 | 52.7 / 100 | **51.7 / 98.8** (R-B FAIL: atmosphere) |
| HOLDS harbour_sun_high glints / path / sparkle; S4 C14; dolly autocorr; harbour hp | | | PASS (0.53 % / 100 % / 3 px; 15.0; 0.064; 8.11) |
| HOLD river_low near hp sd | >= 12 | 11.74 | **10.64 FAIL** (cost of GrazeRough 0, measured) |
| HOLD river_sun sparkle width | >= 50 % | 50.5 | **38.4 FAIL** (back at r03's 37.8) |

## What was learned (evidence in NOTES)
1. **The contact texture was never the bug.** `Dbg 9` (fixed-UV emissive thermometers) read `T_WaterContact` in-engine as 4096x8192, 1 mip,
   0 m at the 0 m texel, 11.5 m at the open probe. The r05 build renders the band; r04's did not. Differences in that path: an `if/else`
   lookup inside `[branch]` instead of a ternary, and `post_edit_change()` on the textures. Not isolated which one.
2. **Debug views Dbg 4 / Dbg 7 are unreliable for values computed inside the foam branches** (they show the initial values where the beauty
   frame has foam). Use Dbg 9-style blocks that compute their own values (Dbg 9, Dbg 10).
3. **SLW's reflection ignores the Specular input**, and a 0.2 normal lean did not move harbour_sun_high's colour either: its brass (R-B ~100)
   is the atmosphere's forward in-scatter toward the 9 deg sun. Route to the look / sky piece or reconcile the target.
4. **GrazeRough 0 restores the far-shore reflection but costs river_low near hp (11.7 -> 10.6)**; ShoreCalm (far-field gains fade near land,
   seen from above or beyond 300-500 m) restores the island streaks (36 vs r04 22) without touching the near crop.

## Next steps (in order)
1. Far contact line at the island tip: read `round-05/iter/h3_DBG10_harbour_high.jpg` if hold C produced it (columns: contact distance / 32 m,
   footprint / 8 m, coverage). If contact reads > ~15 m at the visible edge, the city export's tip geometry and the rendered seawall differ:
   rebuild the contact map from the export the rendered Manhattan uses, or add the island's seawall polyline from the layout as a second source.
2. river_sun sparkle / river_low hp: try the calm only from above (`down`), i.e. LongK 3 again at river level beyond 500 m, and check that
   the far-shore reflection survives (r04 lost it with LongK 3 + GrazeRough 0.42 together; not separated yet).
3. Gate 2 minimum: one pair at 0.197. A slightly faster foam pattern scroll (the `pat` / `fn` time terms) would lift the minimum.
4. The seawall band is a wide, even cream strip (41 px at 4K); if the critic calls it flat, narrow CBias (0.8 -> 0.5) and break the pattern.
5. Perf: not measured this round (needs an attended Mac: `gpu_slot perf` exits 75 otherwise). GrazeRough 0 will cost Lumen-reflection time
   at river level (r04 measured 0.24 ms saved by it).

## How to rebuild (all headless; every Unreal process inside a gpu_slot hold)
```
S=/Users/midir/sm2-n1/_scratch/water
# 0. inputs (CPU): grid, noise, shore map, slope spectrum, chop, contact map (r04: crossings up to +2.3 m, written power-of-two)
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 python3 unreal/WebHomage/Scripts/build_water.py --steps inputs
SM2_WATER_SCR=$S python3 unreal/WebHomage/Scripts/build_water.py --steps contactb   # r05: half-res contact map B/C (Dbg 9 / CSel)
python3 tools/water/r05/hlsl_check.py                       # offline compile of the generated shader: status 0x0
# 1. final capture hold (re-runnable; touch $S/r05/READY3 first):
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 21600 -- bash $S/r05/final_gate.sh
# 2. CPU post (foam crop, iteration jpgs, dolly size, spec.json):  bash $S/r05/post_r05.sh
# 3. perf (exclusive, attended Mac only): tools/water/capture_round.sh <round> perf
python3 tools/water/water_spec.py all docs/night1/water/round-NN --json docs/night1/water/round-NN/spec.json
python3 tools/water/perf_summary.py $S/cap/perf_r04 native100 docs/night1/water/round-NN/perf.json
```
The Manhattan content in this worktree's `unreal/WebHomage/Content` (git-ignored) was built in round 03 by `$S/run_manhattan.py`. It
imports the integrator's `build_manhattan.py` and redirects SCR / EXPORT / TEX to `$S/manhattan/...` (export cloned from
`_scratch/showcase/manhattan/`). `build_water.py --steps ue` rebuilds only `/Game/Water` (~2.5 min commandlet).

## State at hand-off
- Scripts of this round: `tools/water/r05/` (copies of the scratch ones in `_scratch/water/r05/`): `final.sh` (re-runnable final capture:
  builds once per build_water.py hash, captures what is missing or older than the build, per-run deadline below the lock's 2400 s kill),
  `holdC.sh` (remaining captures with SKIP_BUILD, then the Dbg 10 build + still), `hold1.sh` (Dbg 9 + variants), `post_r05.sh` (CPU post +
  spec.json), `report_r05a.py`, `hlsl_check.py` + `dxc_check.py` (offline DXC compile of the generated WaterPS; run before any hold).
- Gate scripts `*_gate.sh` only run when `_scratch/water/r05/READY*` exists, so a queued place can be held while the script is finished.
- The Studio was shared by 3-5 Unreal processes all afternoon (the lock's slots file read 4): 1080p runs took 35 s to 4 min, 4K stills ~2 min,
  a 1080p dolly ~17 min (~1 frame/s), builds 6-10 min. Plan holds for that.
