# River water: handoff after round 04 (Opus 5.5)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

Branch `night1/water`, worktree `~/sm2-n1/water`, scratch `/Users/midir/sm2-n1/_scratch/water/`. W owns `/Game/Water`,
`unreal/WebHomage/Scripts/build_water.py`, `docs/night1/water/`, `tools/water/`. No `.uasset` / `.umap` is committed. No IP is copied:
the spectrum, chop and noise textures are generated, the distance maps are rasterised from the layout and the city export, and the rest is
code. The branch was NOT re-merged with `Opus-5.5-Loop-Night-1` this round: upstream has 19 newer commits, including traversal C++, which
would need `build_editor.sh`.

## Round 04 result (`round-04/NOTES.md`, `round-04/spec.json`)
| check | target | r03 | r04 |
|---|---|---|---|
| harbour_high crop hp sd / pale blobs | >= 10 / 0 | 4.27 / 2 | **8.19** / 188 (crest highlights) FAIL |
| harbour_sun_high glints / path columns / sparkle px | >= 0.5 % / >= 50 % / <= 6 | new | **0.61 % / 100 % / 3** PASS |
| seawall foam band (gate) | >= 12 px, >= 30 % rows, changing | 0 | **0 FAIL** |
| river_low hp sd / mean Y (hold) | >= 9.9 / <= 80 | 9.93 / 78.5 | **11.74 / 62.0** PASS |
| dolly autocorr low / sun (hold) | <= 0.10 | 0.053 / 0.015 | **0.076 / 0.024** PASS |
| S4 C14 (hold) | 5..35 | 17.9 | **22.0** PASS |
| river_sun sparkle width | >= 50 % | 37.8 | **50.5** PASS |
| perf at river_low (frame delta / SLW + depth prepass + Lumen refl delta) | <= 2.5 / <= 2.5 ms | -0.25 / 2.69 | `round-04/perf.json` (PERF_STATUS below) |

Blind critic pack: `/Users/midir/sm2-n1/_scratch/critic-W-r04/pack`, with `pack.key.json` beside it and `pairs.json`. 7 pairs: 4 against
references and 3 previous-vs-this (seawall foam crop, harbour_high, river_low dolly).

## What blocks the remaining targets (measured; details in NOTES)
1. **Foam (gate).** `Dbg 7` (`round-04/iter/h2_DBG7_river_low.jpg`) shows the in-engine contact-map distance at >= 4 m along the whole
   bulkhead, and the under-water ray at >= 4 m too. The CPU reads the same map as 0.6 to 1.9 m at those pixels: a ray-cast whose
   1 m x-crossings match `Dbg 8` exactly (`_scratch/water/r04/emu_contact.py`). Rewriting the map power-of-two and moving CBias did not
   change the in-engine value, so `T_WaterContact` is not sampled as the file says. The depth term cannot help here: the piles are
   vertical, but the bulkhead leans landward under the water.
   **Next:** one 1080p hold with a `Dbg 9` that outputs `tC` (and `tS`) at fixed UVs as emissive. Print the imported texture's size and
   format and its `compression_settings` / `mip_gen_settings` / `lod_group` / `never_stream` / `virtual_texture_streaming` in the build log.
   Suspect the import (Interchange) or the texture group first. Once cf > 0, CBias 0.8 should give a ~1-2 m band (CPU estimate).
2. **harbour_high hp sd plateau ~8.2.** LongK 2 to 3, MidK, FarRough 0.2 and ChopFar 800 / 1500 all land at 7.6 to 8.3. The sky it
   mirrors (19 to 60 deg up, sun behind) is nearly uniform. Haze lifts the far rows. The pale-blob rule now counts crest highlights (188, median 27 px),
   and every variant with more hp had more of them. This needs an orchestrator decision on the blob rule or the target (NOTES section
   "Far field").
3. **Dark specks** in the near field are dark reflections off steep chop facets. They are not foam, not N.L (the sun clamp did not remove
   them), and not fixed by BendK (0.7 / 1.0 give flat grey mirror patches). A look pass on the near-chop reflection is needed.
4. river_low p99.5 / glints and the S4 haze band are sky-ceiling items, routed to the look piece (round-04 reconciliation).

## How to rebuild (all headless; every Unreal process inside a gpu_slot hold)
```
S=/Users/midir/sm2-n1/_scratch/water
# 0. inputs (CPU): grid, noise, shore map, slope spectrum, chop, contact map (r04: crossings up to +2.3 m, written power-of-two)
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 python3 unreal/WebHomage/Scripts/build_water.py --steps inputs
# 1. one capture hold = build + iteration stills + decision gate + final build + stills + dollies (round 04 scripts, copy and edit):
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 14400 -- bash $S/r04/hold_r04b.sh
#    variants: $S/r04/variants2.json (SM2_WATER_VARIANTS); gate: write $S/r04/decide.json (final params) within 420 s of "GATE:" in the log
# 2. CPU post (foam crop, iteration jpgs, dolly size, spec.json):  bash $S/r04/post_r04.sh
# 3. perf (exclusive, native 100 %, 6 maps) after the capture hold:  bash $S/r04/perf_chain2.sh   (or capture_round.sh <round> perf)
python3 tools/water/water_spec.py all docs/night1/water/round-NN --json docs/night1/water/round-NN/spec.json
python3 tools/water/perf_summary.py $S/cap/perf_r04 native100 docs/night1/water/round-NN/perf.json
```
The Manhattan content in this worktree's `unreal/WebHomage/Content` (git-ignored) was built in round 03 by `$S/run_manhattan.py`. It
imports the integrator's `build_manhattan.py` and redirects SCR / EXPORT / TEX to `$S/manhattan/...` (export cloned from
`_scratch/showcase/manhattan/`). `build_water.py --steps ue` rebuilds only `/Game/Water` (~2.5 min commandlet).

## State at hand-off
- PERF_STATUS: the exclusive perf hold (`$S/r04/perf_chain2.sh`, pid in `r04/perf_chain2.pid`, log `r04/perf_chain2.log`) was queued
  at 10:12, 4th in the FIFO. When the log says `PERF CHAIN DONE`, `round-04/perf.json` and `perf_gpu.json` hold the numbers (gate field:
  `slw_depth_lumen_sum`). If it is still waiting and nobody owns it, it is safe to leave it: it only runs the 6 water perf maps.
- No engine of ours is running. Content: `/Game/Water` is built with the r04 defaults.
- Scratch: `r04/` (scripts, hold logs, `hold1_round/` = hold 1's full capture set, contact map of r03 in `r04/contact_r03/`),
  `iter/r04`, `iter/r04b` (full-res iteration PNGs), `cap/` (dolly PNG frames, ~6 GB; delete once the next round has its own).
