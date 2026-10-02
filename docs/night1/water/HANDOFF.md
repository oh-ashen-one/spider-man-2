# River water: handoff, round 03 IN PROGRESS (Opus 5.5)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

## Round 03 status (live; the round-02 handoff follows below)
- Code done and pushed (`night1/water`): `build_water.py` r03 shader (resolved 0.15-0.5 m wind chop `T_WaterChop`, two scroll directions;
  near-field (<= 150 m) GGX roughness <= 0.08 with true texture gradients, no mip bias; streak / slick terms deleted; whitecap / contact foam
  faded to zero by 150 m; one spectrum realization + no chop / foam / contact-map lookup beyond 150 m; shore map resampled to 2048^2 so it
  mips; cream foam albedo). New params: MicroK, SpecK, RoughN. Defaults ChopK 2.4, MicroK 1.6, ScatK 0.06, SpecK 1.6, FarVarK 0.25.
- `tools/water/water_spec.py`: harbour crop (native-4K x0-2400 y1300-2100), pale blobs, sparkle width, PASS/FAIL table (`all`).
- `tools/water/perf_summary.py`: per-pass costs. FINDING: round 02's "SingleLayerWater 3.68 ms" was the CSV profiler's footer row (value 2160)
  inside the mean; the true r02 SLW pass was 0.80 ms (river_low) / 1.25 (river_sun) / 0.57 (S4) at TSR 67 %.
- `tools/water/emu_river_low.py`: CPU emulation used to choose the start params / variants (calibrated on the r02 frame, rough).
- GPU: ONE capture hold queued (`_scratch/water/r03/hold_r03.sh`: build + 1080p variants + autopick + final build + round-03 stills + dollies)
  and a perf chain (`r03/perf_chain.sh`, exclusive native-100 % perf after the hold). Logs: `_scratch/water/r03/hold.log`, `perf_chain.log`.
- RESUMED 05:05 (Opus 5.5, fresh session after the 502): the queued hold (`gpu_slot` pid 81663, `hold_r03.sh`) and the perf chain
  (`perf_chain.sh` pid 84310, waits for the hold, then one exclusive perf hold) were still alive and were left running (no second hold).
  1080p iteration stills (base / V1 / V2 / V3) show the chop layer resolves, but the river_low range stays compressed (p1 ~43, p99.5 ~100-116):
  the sky the near water reflects is only ~114-121 Y (p99 137-163) in this look rig, so even a mirror tops out near 120 Y; ScatK 0.05-0.09
  moves p1 by < 5 Y (floor = Fresnel x sky + height fog over the water, not the body). Harbour hp sd 2.9 at 1080.
  If this session died: check `gpu_status.sh`; if neither runs, re-queue the same two commands (see the scripts' headers).


> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

Branch `night1/water` (from integration 914de97 + round-02 commits), worktree `~/sm2-n1/water`, scratch `/Users/midir/sm2-n1/_scratch/water/`.
Owned: `/Game/Water`, `unreal/WebHomage/Scripts/build_water.py`, `docs/night1/water/`, `tools/water/`. No `.uasset` / `.umap` committed;
no copied IP (generated spectrum / noise textures, distance maps rasterised from the browser layout polygons and the city export, code).
Blind critic pack: `/Users/midir/sm2-n1/_scratch/critic-W-r02/pack` (key: `pack.key.json` next to it; pairs: `pairs.json`).

## How to rebuild (all headless; every Unreal process inside a gpu_slot hold)
```
S=/Users/midir/sm2-n1/_scratch/water
# 0. inputs (CPU): water grid, noise, shore map, wind-sea slope spectrum, contact-distance map from the city export
SM2_WATER_SCR=$S SM2_WATER_EXPORT=<city export dir with manifest.json> python3 unreal/WebHomage/Scripts/build_water.py --steps inputs
# 1+2. one GPU hold: Manhattan content (if Content/ is empty) + water + optional iteration stills
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 14400 -- bash $S/hold1.sh
# 3. captures + perf (stills = 1080 + 4K of S4 / river_low / river_sun / harbour_high; movie = both dollies; perf = exclusive)
SM2_WATER_SCR=$S tools/water/capture_round.sh docs/night1/water/round-NN stills,movie water
GPU_SLOT_PERF_WAIT_TIMEOUT=14400 SM2_WATER_SCR=$S tools/water/capture_round.sh docs/night1/water/round-NN perf water
# 4. numbers
python3 tools/water/water_spec.py all docs/night1/water/round-NN --json docs/night1/water/round-NN/spec.json
```
Scratch helpers (not committed, recreate from this text if the scratch dir is gone):
- `run_manhattan.py`: imports the integrator's `build_manhattan.py` unchanged and overrides `SCR`/`EXPORT`/`TEX`/`CHAR_STAGE` to
  `$S/manhattan/...`, `UE` to `$S/bin/ue_locked.sh` (= `gpu_slot.sh capture --label water -- <UnrealEditor> "$@"`), `stage_characters` to a
  no-op (P2 inputs cloned once from `_scratch/showcase/manhattan/chars`), and `wait_slot` to count `pgrep -x UnrealEditor` only.
  The export (`$S/manhattan/export/midtown3x3`) and `tex/` were cloned (`cp -Rc`) from `_scratch/showcase/manhattan/` (prepped city r10 export).
  Run: `python3 $S/run_manhattan.py --steps city,traversal,characters,look,map` (~9 min of commandlets).
- `hold1.sh`: run_manhattan (unless `$S/hold1.skip_city` exists) + `build_water.py --steps ue` with `SM2_WATER_VARIANTS=$(cat variants.json)`
  + `iter_stills.sh` (aborts if the game log says `M_RiverWater ... Failed to compile Material`) + optional autopick / `hold3.sh`.
- `hold3.sh`: final `build_water.py --steps ue` with `SM2_WATER_PARAMS=$(cat final_params.json)` + capture_round stills + movie.

## What the water is now (round 02)
- Grid: camera-centred polar grid (0.1 m rings to 4 m, +2 %/ring to 81 km), WPO Gerstner (the browser's 12 waves), SLW material.
- Shading: 5 longest Gerstner waves analytically + **4 layers of a baked random-phase wind-sea slope spectrum** (`T_WaterSlope`, 1024^2,
  k^-4, 3..24 cycles/tile, 2 realizations, tiles 21 / 6.7 / 2.2 / 0.73 m, scrolled at their phase speed, mip bias +1, unresolved variance
  -> GGX roughness). Facets whose reflection would point below the horizon are bent up (`BendK`). Turbid body via SLW coefficients
  scaled by `ScatK`. Sun glitter facets as round 01.
- Foam: contact foam from `T_WaterContact` (distance to where the export's geometry crosses the water plane: island shore box
  -1204..1141 x -3689..3627 m, 0.89 m/px) + the old depth test; rare whitecaps; no streak foam.
- Material parameters (`PARAMS` in build_water.py, committed defaults = round-02 pick "E"): ChopK 2.6, ScatK 0.2, FarVarK 0.5, FoamK 1.8,
  BendK 0.3, GlitterK 1. Tuning variants: `SM2_WATER_VARIANTS='{"X": {"ChopK": 2.0, "_views": ["river_low"]}}'` -> `/Game/Water/Variants`.
- Coverage: every `/Game/Maps/Manhattan*` classic map gets the `Water_River` sublevel (P1's flat `WaterPlane` hidden, collision kept);
  `/Game/Maps/Manhattan_WP` (island piece's World Partition map), if present in the project, gets a non-spatially-loaded `RiverWater_WP`
  actor (untested here: this worktree has no WP map; the WP map's own flat WaterPlane must be hidden by whoever builds it if it is not
  loaded at build time; a warning says so). The contact map is built from whatever export `SM2_WATER_EXPORT` points at: point it at the
  island piece's full export once it exists to get contact foam island-wide.
- Views (`views.json`, `SHOTLIST.md`): S4 perch, river_low (round-01 framing, seawall + piles), **river_sun** (into the golden sun across the
  Hudson, 19 m off a pier head), **harbour_high** (260 m over the harbour), river_low / river_sun dollies.

## Round 02 numbers (`round-02/spec.json`, `round-02/NOTES.md`; 4K = native 3840x2160, r.ScreenPercentage 100)
| check (PLAN section 4 Water) | target | round 01 | round 02 |
|---|---|---|---|
| river_low near crop mean Y | <= 80 | 90.5 | **79.3** pass |
| river_low near crop high-pass sd | >= 12 | 4.5 | 8.5 FAIL |
| river_low near crop p99.5 | >= 150 | 117 | 122 FAIL |
| river_low near crop glint px (Y >= 140) | >= 1 % | 0 % | 0.11 % FAIL |
| river_sun near crop high-pass sd / p99.5 / glint | (same) | n/a | **27.3 / 249 / 44.9 %** pass; mean Y 137 FAIL |
| dolly autocorrelation at 80 px | <= 0.10 | 0.224 | **0.006** (river_low), 0.041 (river_sun) pass |
| C14 at S4 | 5..35 | 41.0 | **22.0** pass (look rig changed: far shore 151 vs 171) |
| piling / seawall contact foam | present | none | **present** (`crop_river_low_4k_seawall_foam.jpg`) |
| water GPU cost (frame delta vs flat plane, exclusive lock, 4K TSR 67 %) | <= 2.5 ms | -0.01 / +6.41 (noisy) | **+1.23** river_low / **+0.42** S4 / -0.31 river_sun pass |
| water GPU cost (sum of water passes) | <= 2.5 ms | 1.54 / 1.15 | 4.55 river_low / 0.97 S4 / 4.16 river_sun FAIL at near views |

Why river_low cannot get its glints: in that framing the golden sun (compass az 238, elev 9) is behind-left of the camera, so the only
highlights are sky reflections; the near water reaching Y >= 140 would need reflectance ~0.75 of a ~155 sky. Brighter water (variant G,
ChopK 1.6 ScatK 0.3) reached p99.5 144 / 0.7 % glints but mean Y 100. The into-the-sun view (`river_sun`) carries the glitter instead.

## Known issues / next
1. river_low near-crop high-pass sd 8.5 (< 12) and no glints with the sun behind; options: sharper roughness (VAR_K 1.2 -> 0.6: a
   `VarKP` material input was tried but that build did not compile, see 2), sky-reflection contrast from the look rig, or a framing change.
2. Material compile failures: rebuilding `M_RiverWater` in place made a material that failed to compile for Metal SM6 (default material
   in game). `build_water.py` now deletes `Content/Water` before every rebuild; after that every build compiled. The VarKP input was
   removed in the same fix, so which of the two caused it is not isolated.
3. river_sun near-crop mean Y 137 (glitter path + bright golden sky); foam at the seawall is close to white-clipped in the golden key.
4. Wind streaks still read as faint straight bright lines (halved this round).
5. Island-wide contact foam needs the island export (only the midtown3x3 export's coast meshes were used; they do cover the whole island
   shore at coast-mesh level, but piers outside the exported detail tiles may be missing).
6. Queue reality: one GPU hold takes ~1-2 h of waiting; batch everything (build + variants + captures) into one hold.

## PERF (round-02/perf.json, perf_gpu.json; NOTES.md has the table)
`GPU-LOCK: class=perf exclusive=yes util_before=0% util_after=0% util_during_avg=59.9% wait_s=7573.75 instances_before=0 instances_max=1 contaminated=false`.
End-to-end frame cost over the flat plane is inside budget, but the SingleLayerWater pass itself reads 3.6-3.7 ms at the near views (round 01
0.75): the next round should slim the pixel shader (fewer slope samples at distance, drop the second realization beyond ~150 m, cheaper
contact lookup) and re-measure.

## Next round (suggested order)
1. Critic verdict on `_scratch/critic-W-r02/pack` (7 pairs: river_sun vs into-the-sun ref, river_low vs pier ref, harbour_high vs aerial
   golden waterfront, S4 vs aerial river, previous-vs-this still + dolly, sun dolly).
2. river_low near-crop detail (hp sd 8.5 -> 12) without brightening: sharper GGX (lower VAR_K) on the resolved layers.
3. Slim the SLW pixel shader (see PERF).
4. Point SM2_WATER_EXPORT at the island export when it exists; check `/Game/Maps/Manhattan_WP` gets the water and its flat plane is hidden.
5. Foam tint (cream, lower albedo) so the seawall band does not clip in the golden key.

## State at hand-off
- Nothing running (no engine, no hold, no waiter). Content (Manhattan + /Game/Water, round-02 defaults) is built in this worktree's
  `unreal/WebHomage/Content` (git-ignored); Intermediate / DerivedDataCache kept for the next round (rebuild is ~10 min + queue).
- Scratch kept: `_scratch/water/manhattan` (export / tex / chars clones, ~1.4 GB), iteration stills, logs; dolly PNG frames deleted.
