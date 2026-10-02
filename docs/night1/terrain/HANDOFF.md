# Terrain (piece E) — HANDOFF (round 04 IN PROGRESS: lawn rebuilt, content built side by side as /Game/TerrainR4, capture hold queued)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/terrain` (pushed), worktree `/Users/midir/sm2-n1/terrain`, scratch `/Users/midir/sm2-n1/_scratch/terrain` (r04 notes in `r04/`), dev port 5209 (Vite, exports only; stopped).
Owns `/Game/Terrain*`, `tools/export/{export_terrain.mjs,collect_terrain.js,gen_terrain_shaders.mjs}`, `tools/terrain/`, `unreal/WebHomage/Scripts/{build_terrain.py,terrain_materials.py}`,
`unreal/WebHomage/Shaders/Terrain/`, `docs/night1/terrain/`. Spec / shot list / cameras: `SPEC.md` (E10 = r04), `SHOTLIST.md`, `shots.json`.

## Round 04 (2026-10-02, Sonnet 5.5): THE LAWN — state at the last push
Target (three critics, r3 verdict): replace the yellow star tufts by dense blade grass + 0.3-3 m lawn albedo detail, sat >= 0.70, E1 sigma-6 SD >= 8 on the critic crops + guard boxes, no flat quad > 100 px in t4,
t5 last 5 s over park ground at 25-40 m with sigma-3 SD >= 5, canopy guard for the never-rendered pass-2 hunks, GPU ms p1 / p10 within +5 % of r3 (161 / 92 ms), no axis below [4,4,4,4,3].
Done in committed scripts (CPU, verified offline: `tools/terrain/check_hlsl.py` 13 / 13): `tools/terrain/prep_lawn.py` (4 near blade-patch meshes of ~1150 blades / 2.3 m discs on a 1.5 m grid = 177 k instances, culled 18 m; 2 far patches of ~400 wider blades on a 2.6 m grid = 59 k, culled 60 m;
`lawn_detail.png` tileable RGBA noise; `blanket_weave.png`), `Shaders/Terrain/Lawn.ush` (lawn grade with blue 0.10 instead of 0.46, 0.3-16 m mottling / wear / clover / mowing stripes, clay vs grass mask), `terrain_materials.py`
(M_TerrainGrass = blade turf: two-sided foliage, root -> tip colour, wind, distance shrink; M_TerrainBlanket = gingham weave + fringed ends + fold normal; M_TerrainVC grain; path gravel grain), `build_terrain.py` (env `SM2_TERRAIN_ROOT`,
grass pools out of ray tracing, 2 cm lifted tilted blankets, grass scatter clears the blankets). A numpy simulation of the lawn detail predicted hp6 SD 10-12 at 0.07-0.15 m/px with amplitude 0.55 (`_scratch/terrain/r04/sim_detail.py`).
Content: `/Game/TerrainR4` (built by `SM2_TERRAIN_ROOT=/Game/TerrainR4 tools/terrain/run_build.sh`, 2-4 min nullrhi) — the HEAD content `/Game/Terrain` (pass-2 canopy, old tufts) is untouched for the GPU-ms baseline.
Capture: hold A (`round4.sh STAGE=A`, launcher `_scratch/terrain/r04/hold_A.sh`, log `_scratch/terrain/r04/holdA.log`) = safe warm-up + nine 4K stills + t5 route probes (12 candidates in `round-04/t5_candidates`, nullrhi, the best becomes the t5 movie) + t4 / t5 movies.
Then `tools/terrain/measure_r04.sh docs/night1/terrain/round-04`, then `make_pairs.py` + `abpack.py` (pack dir `/Users/midir/sm2-n1/_scratch/critic-E-r04/pack`).
If the pass-2 canopy gate fails (trees axis < 4, E9b FAIL, E9a < 5/24 or E9c > 47 px): reverse the pass-2 hunks: `git diff cdaa64a0 dfaf7f94 -- unreal/WebHomage/Scripts/build_terrain.py unreal/WebHomage/Scripts/terrain_materials.py unreal/WebHomage/Shaders/Terrain/Foliage.ush | git apply -R` (tested context may need hand merging),
rebuild, recapture the p1 / p10 / p9 / p4 stills.

## Round 03 outcome (2026-10-02, Opus 5.5; details: `round-03/README.md`)
Target (Fable): canopy reads as leaves at every distance. Done in pass 1 (captured): 165-520 m band = leaf-card LOD1 from the browser's own trees.js `canopyGeometry` (LOD0 reproduced vertex for vertex as a check),
clump hull only >= 520 m with bump 3.0 / 0.5, crownfar dropped; **root cause of the black cards found and fixed**: Lumen HWRT puts every drawn primitive in the ray-tracing scene regardless of
`affect_dynamic_indirect_lighting` and never evaluates opacity masks, so all leaf pools were opaque shells (hull around every canopy) -> foliage pools `visible_in_ray_tracing = False`;
constant leaf emissive replaced by AO from exposure + shade / distance-weighted fill; water sublevel in the terrain maps (p6 / p7 / p8 now show the merged river); silhouette + dark-pocket tests.
| test (pass 1, `round-03/`) | result | r02 |
|---|---|---|
| E9a 24 crown crops >= 9 | **FAIL** 5 / 24, min 4.28, median 7.74 (far 11-12, mid 6.7-9.8, foreground 4.3-7.8) | 10 / 24, min 5.41 |
| E9b flat patch > 40 px incl. dark pockets (p1) | **PASS** 24.7 px, dark pockets 0.06 % | 126.8 px |
| E9c straight silhouette p10 | **FAIL** 47.2 px (one near leaf-spray quad edge) | 75.6 px (hull facets) |
| GPU ms (same hold, r02 built side by side) | p1 156-161 vs 164; p10 90-92 vs 89 | |
| E1 lawn | p10 7.43 / 6.34 (up), p9 2.63, p4 1.41 | |
Why E9a fell: the LOD1 cores read as smooth round puffs; with all foliage out of ray tracing nothing shades the lawn under the canopy, so foreground boxes that held black pockets now hold smooth lit lawn.
Blind critic pack (pass 1): `/Users/midir/sm2-n1/_scratch/critic-E-r03/pack` (16 pairs: 9 views vs refs, 5 progress pairs r02 vs r03 incl. both shore views, 2 movies; key outside), `pairs.json` beside it.

## NEXT (in this order)
1. Capture PASS 2 (content is already built from HEAD; no rebuild needed unless scripts change): `cd <worktree> && /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round3.sh`
   (detach it: `_scratch/terrain/r03/hold_r03.sh` under nohup). Before that, move pass-1 media aside (`_scratch/terrain/r03/pass1_media` already holds a copy) and delete `round-03/gpu_ms.txt` (it appends).
   Then `tools/terrain/measure_round.sh docs/night1/terrain/round-03`; keep whichever pass scores better; rebuild the pack (`SHORE_PROGRESS=1 python3 tools/terrain/make_pairs.py docs/night1/terrain/round-03 <pack>/pairs.json docs/night1/terrain/round-02` + `abpack.py`).
   **The warm-up has now been stopped twice by the health monitor (08:40, 10:38; the second one was my own 960x540 warm-up pinning the GPU).** `round3.sh` now caps 4K stills at 4 fps. Consider `WANT` without `warm`
   (pass `capture_round.sh <round> stills moves r2gpu`: the first still compiles shaders anyway) and watch `health.log` during the first launch; stop at once if it pins again.
2. If pass 2 still misses E9a: the foreground boxes are now lawn-under-canopy (need shade: the pass-2 proxy) and the near cards' leaf contrast; the mid band is the LOD1 core.
3. Deferred to r4 (Sonnet): aerial lawn E1 >= 8 and saturation >= 0.70, blade tufts instead of star sprites, pond-bank rocks, esplanade dressing; p6 water seam (lighter rectangle near the seawall, untraced).

## Round 02 outcome (history) (2026-10-02, details and numbers: `round-02/README.md`)
Target: trees / canopy at swing height (round-01 critic's biggest gap). Done: the browser's whole park-tree chain is ported with dithered per-pool distance bands (`Shaders/Terrain/Foliage.ush` + `M_TerrainLeaves / Bark / Cards / Clump / Crown`, 46 HISM pools, 47,710 instances), Nanite flag on the ez materials,
physically scaled ambient fill, lawn grade, brighter blankets, cameras p3 / p6 / p7 fixed, round-01 movies with the dev-suit emblem `git rm`ed, round-02 movies with the hero hidden.
| result of the final render (pass 3, `round-02/`) | |
|---|---|
| E8 crown crops (24 boxes, p1_south 4K, sigma 3) | **FAIL**: min 5.41, median 8.34, max 13.66, 10 / 24 >= 9 (far 10.3-13.7, mid 8.1-10.3, near-right 5.4-13.1, foreground 6.3-7.5) |
| E8 flat hull faces > 40 px | p10 PASS (12 px); p1 FAIL: 2 black shadow pockets (max 108 px, luma 25-37) |
| E1 lawn crops | round-1 boxes 3 of 4 lower (they contain tree parts); pure-lawn windows: p10 4.74 -> 5.32, aerial p9 2.81 -> 2.33, p4 1.52 -> 1.33 |
| lawn colour | met on pure-lawn windows (G/R 1.12-1.40, sat 0.58-0.64) |
| E2 / E3 / E7 | 89.9 % / 0 gaps / ground mode 803 of 803 frames |

Blind critic pack: `/Users/midir/sm2-n1/_scratch/critic-E-r02/pack` (key `pack.key.json` outside; `pairs.json`; 14 pairs). Not judged yet. Merge preconditions (no emblem movies, a reservoir-reference pair) are done; the Reservoir pair uses a park-water-basin frame because the private refs contain no Reservoir frame.

## Round-02 plan for round 3 (history: items 1a, 1b done in r03)
1. Judge the pack, then fix the one biggest gap. Likely candidates from my own look at the frames: (a) the far crowns (165-520 m) read as bumpy boulders (the browser's 4-lobe crown LOD with strong bump): smaller lobes / more of them, or leaf-card clusters, softer bump at < 300 m;
   (b) the ambient fill `Emis = c * 1800 * (0.4 + 0.6 expo)` in `terrain_materials.py` (M_TerrainLeaves, M_TerrainCards) is constant: close leaves in the sun go pale (`t4_lawn_sprint` 3 s): scale it down with distance < 10 m and by shade; the foreground canopy (SD 6-7) still lacks contrast and black pockets remain in the p1 foreground;
   (c) aerial lawn micro-detail (E1 1.3-2.8): tiled grass_nrm micro-normal + high-frequency albedo at < 1 m, bigger / brighter tufts; (d) pond-bank rocks are white lumps (p3); (e) the t5 perimeter ground at 13-15 s is the city's flat grey asphalt (city piece).
2. Re-measure with the same 24 crown boxes (`round-NN/crops.json`, `tools/terrain/crown_stats.py`) so numbers stay comparable; a round that changes framing must re-pick boxes with `tools/terrain/grid_overlay.py`.
3. Not built: pickets, wet bands, pond shallows, ballfield fences, Met-like museum (skipped on purpose), lamp night look, collision on rocks / esplanades; street trees island-wide belong to the island piece.

## GPU etiquette learned this round (read before enqueueing)
- The queue is slow (0.7-2 h per turn): rebuild the content BEFORE enqueueing (nullrhi, ~2-9 min, touch `_scratch/terrain/BUILDING` while it runs: `round2.sh` waits for it), enqueue early, never rebuild inside the hold, always `--timeout 28800`.
- `round2.sh` = warm-up (+ shader check: aborts the hold on `Failed to compile Material`) + 9 stills + 2 movies; env `ROUND_NAME` (output dir), `ONLY_IDS`, `PRIO_IDS` (empty = none), `BASE_IDS` (empty = no baselines), `HIDE_HERO=1` (movies). `capture_round.sh` is the engine of it.
- **The health monitor stopped my engine twice** (`WS-STARVED`: GPU 100 %, WindowServer CPU ~2 %, probe fail) at the first 4K still launch, both times while another engine was rendering. Do not lift a pause (it auto-lifts after 10 calm minutes); after a second stop kill your own hold scripts by PID so nothing relaunches, and resume only the missing shots.
- Never `pgrep -f` a pattern that appears in your own command line (it matched my wait loops); use bounded `until` loops, not sleep chains.

## Offline shader verification (saves GPU-lock turns; caught two real bugs this round)
- `python3 tools/terrain/check_hlsl.py`: every material body through DXC with UE's parameter types (**VectorParameter = float3**, TextureCoordinate = float2, ...). 12 / 12.
- `python3 tools/terrain/scw_check.py`: UE's own `ShaderCompileWorker` (CPU only) recompiles every dumped permutation under `unreal/WebHomage/Saved/ShaderDebugInfo/METAL_SM6/M_Terrain*` with the CURRENT `Foliage.ush` and the CURRENT Custom-node bodies of `terrain_materials.py` regenerated into the dumped wrapper
  (27 permutations: base pass, depth, shadow depth, Nanite HW / micropoly raster, Nanite base pass + Lumen card, ray tracing any-hit; new output pins are appended). Dumps exist only for permutations that failed once (the Saved dir of this worktree holds them). `SM2_FOLIAGE_SRC=<file>` tests a candidate `Foliage.ush` from scratch.
- Emissive units: the golden rig is physical (sun 44000 lux, EV 8.2-13): a sunlit albedo A radiates ~10000 A cd/m2; an emissive of 1 is invisible (pass 2 lost a render to that).

## What exists (all committed; Content is generated, never committed)
- `tools/export/export_terrain.mjs` + `collect_terrain.js`: headless-Chrome export of the TERRAIN kinds island-wide (park ground, lawns, ponds / Reservoir, furniture, rock outcrops, ez-tree prototypes + instances with autumn tints, the park-tree chain pools with their bands) -> `<scratch>/export` (~30 s).
- `tools/terrain/prep_terrain.py`: path / drive mask, grass tuft prototype + 527 k tufts, rock outcrops (Met-like museum dropped on purpose), `ParkData.ush`, leaf textures + the city leaf atlas, stats (E2). `tools/export/gen_terrain_shaders.mjs` -> `Shaders/Terrain/Park.ush`.
- `tools/terrain/shore_audit.py` (E3; granite bulkhead patch closes the browser coast's 12 gaps), `crop_manual.py` (E1), `crown_stats.py` (E8: crown crops sigma 3 + flat-face detector, lawn and sky excluded), `grid_overlay.py`, `measure_round.sh`, `make_pairs.py` + `tools/night1/abpack.py` (pack).
- `unreal/WebHomage/Scripts/build_terrain.py` (steps clean, tex, mat, mesh, foliage, trees, map, views; fail-soft): materials from `terrain_materials.py`; `/Game/Terrain/Terrain_Land` sublevel (ground tagged WHGround, tufts HISM x3 wind classes, props, 46 tree-chain HISM pools with a material instance per pool carrying `band = (near, far, 0)`),
  `City_Geo_T` (private copy of the city geometry level with the city's flat park ribbons / lawns / ez park trees hidden in game), `/Game/Terrain/Maps/Manhattan_Terrain`, still maps `V_<id>` / baseline `VB_<id>` from `shots.json`.

## Rebuild recipe (CPU steps need no slot; nullrhi commandlets are not renderers for the health monitor)
0. r03: after merging the integration branch run `unreal/WebHomage/Scripts/build_editor.sh`; water: `SM2_WATER_SCR=/Users/midir/sm2-n1/_scratch/terrain/water python3 unreal/WebHomage/Scripts/build_water.py --steps inputs,ue` BEFORE `run_build.sh` (the terrain maps add `/Game/Water/Maps/Water_River` when it exists).
1. `npx vite --port 5209 --host 127.0.0.1 --strictPort` (needs `npm ci`), `node tools/export/export_terrain.mjs`, `python3 tools/terrain/prep_terrain.py`, `node tools/export/gen_terrain_shaders.mjs`, `python3 tools/terrain/check_hlsl.py`, `python3 tools/terrain/scw_check.py`.
2. Base Manhattan content exists in this worktree's `unreal/WebHomage/Content` (round-01 recipe: `git show 77d0946:docs/night1/terrain/HANDOFF.md`).
3. `build_terrain.py` through the nullrhi commandlet: `tools/terrain/run_build.sh [steps]` (writes the job wrapper, touches `_scratch/terrain/BUILDING`, runs `UnrealEditor ... -run=pythonscript -unattended -nullrhi`; only when none of your engines is running).
4. Captures only through the lock: `ROUND_NAME=round-03 gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round2.sh`; then `tools/terrain/measure_round.sh`, `make_pairs.py`, `abpack.py`.
