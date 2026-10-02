# Terrain (piece E) — HANDOFF (round 02 done: captures, measurements, critic pack; E8 numeric target NOT met)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/terrain` (pushed), worktree `/Users/midir/sm2-n1/terrain`, scratch `/Users/midir/sm2-n1/_scratch/terrain`, dev port 5209 (Vite, exports only; stopped).
Owns `/Game/Terrain`, `tools/export/{export_terrain.mjs,collect_terrain.js,gen_terrain_shaders.mjs}`, `tools/terrain/`, `unreal/WebHomage/Scripts/{build_terrain.py,terrain_materials.py}`,
`unreal/WebHomage/Shaders/Terrain/`, `docs/night1/terrain/`. Spec / shot list / cameras: `SPEC.md` (E8 added), `SHOTLIST.md`, `shots.json` (p3 / p6 / p7 cameras changed in round 02).
Nothing of this piece is running (no engine, no Vite, no queued ticket). Content (`/Game/Terrain`) in this worktree is built from the committed scripts (pass-3 state); it is never committed.

## Round 02 outcome (2026-10-02, details and numbers: `round-02/README.md`)
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

## NEXT (round 3), in this order
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

## Rebuild recipe (CPU steps need no slot)
1. `npx vite --port 5209 --host 127.0.0.1 --strictPort` (needs `npm ci`), `node tools/export/export_terrain.mjs`, `python3 tools/terrain/prep_terrain.py`, `node tools/export/gen_terrain_shaders.mjs`, `python3 tools/terrain/check_hlsl.py`, `python3 tools/terrain/scw_check.py`.
2. Base Manhattan content exists in this worktree's `unreal/WebHomage/Content` (round-01 recipe: `git show 77d0946:docs/night1/terrain/HANDOFF.md`).
3. `build_terrain.py` through the nullrhi commandlet: `tools/terrain/run_build.sh [steps]` (writes the job wrapper, touches `_scratch/terrain/BUILDING`, runs `UnrealEditor ... -run=pythonscript -unattended -nullrhi`; only when none of your engines is running).
4. Captures only through the lock: `ROUND_NAME=round-03 gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round2.sh`; then `tools/terrain/measure_round.sh`, `make_pairs.py`, `abpack.py`.
