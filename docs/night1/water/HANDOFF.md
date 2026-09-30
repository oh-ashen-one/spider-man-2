# River water (A/B, Opus 5.5 build): handoff after round 01

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

Branch `night1/water-ab-opus`, worktree `~/sm2-n1/water-ab-opus` (base: integration `Opus-5.5-Loop-Night-1` at 80ef6cb). UE MCP port 8780 (not used:
everything is headless commandlets + offscreen `-game`). Owned: `/Game/Water`, `unreal/WebHomage/Scripts/build_water.py`, `docs/night1/water/`,
`tools/water/`. Scratch: `/Users/midir/sm2-n1/_scratch/water-ab-opus/`. No `.uasset` / `.umap` is committed; no copied IP (no textures or
meshes from upstream assets: the water uses only generated noise, a shore-distance map rasterised from the browser layout polygons, and code).

## How to build (editor closed)

```
# 1. the integrated city (unchanged build_manhattan.py; wrapper = private scratch dir + export dev port 5231 instead of C's 5208):
python3 /Users/midir/sm2-n1/_scratch/water-ab-opus/run_manhattan.py            # ~12 min of work (+ waiting while 3+ Unreal run)
# 2. water on top (inputs: numpy + opencv + node; ue: one -nullrhi commandlet, ~40 s):
SM2_WATER_SCR=/Users/midir/sm2-n1/_scratch/water-ab-opus python3 unreal/WebHomage/Scripts/build_water.py            # steps inputs,ue
# 3. captures / perf (every run wrapped in gpu_slot.sh; perf = exclusive lock):
SM2_WATER_SCR=... tools/water/capture_round.sh docs/night1/water/round-NN [warm|stills|movie|perf|all] water-ab-opus
```
`run_manhattan.py` imports `build_manhattan.py` as a module and only overrides `SCR`, `DEV_PORT` and the instance-wait poll (5 s instead of 60 s,
same "wait while 3+ Unreal instances" rule). It is not committed (scratch); its 15 lines are reproduced in `round-01/NOTES.md`.
Debug views: `SM2_WATER_DBG=1..5` at build time bakes a debug default into the material (1 Lagrangian coords, 2 normal, 3 roughness,
4 foam/contact/gust, 5 per-vertex hash), shown through the base colour.

## What exists

| asset | what |
|---|---|
| `SM_WaterGrid` (`/Game/Water/Meshes/SM_WaterGrid/StaticMeshes/`) | polar grid, 384 segments x 541 rings: 0.1 m rings to 4 m, then +2 % per ring to 81 km; 207 745 verts / 415 104 tris (mesh description) |
| `M_RiverWater` | Single Layer Water. **Vertex**: the grid follows the camera through WPO (`Cam.xy`), the 12 Gerstner waves of `src/world/waves.js` (same L / A / dir / q / phase, Q = q / (k A N)), each faded out when shorter than ~4 local grid spacings (waves.js `waveDisp` rule). **Pixel**: analytic slopes of the same 12 waves + 12 capillary waves (0.06-0.52 m), footprint-filtered (resolved -> normal, unresolved -> slope variance -> GGX roughness, Cox-Munk); wind gust / slick / streak fields from a 512^2 tileable noise at 140-1100 m scales and the 8 m/px shore-distance map (sheltered slicks, siltier water within ~100 m of land); contact foam from `SceneDepthWithoutWater` (distance under the surface along the view ray, lapping pulse, cell pattern), sparse whitecaps on steep crests in gusts, streak foam; sun glitter = sparse facets whose normal is tilted onto the sun half-vector with a smoother micro-roughness, so the engine's shadowed GGX sun specular lights them; turbid optics via SLW scattering (0.07, 0.09, 0.078) / absorption (0.50, 0.34, 0.56) per metre, phase g 0.55, F0 0.02 |
| `Water_River` (map) | the water actor (no shadow casting, not in the Lumen scene / DF / ray tracing / reflection captures, no collision) |
| Manhattan maps | `Water_River` added always-loaded to `/Game/Maps/Manhattan`, `_Midday`, `_Night`, `_View_S1/S2/S4`; P1's flat `WaterPlane` in `City_Midtown_Geo` hidden, collision kept (traversal floor, `WHGround`) |
| view / perf maps | `Water_View_RiverLow` (+`_Midday`, `_Dolly`), `Water_View_S4_Midday`, `Water_Perf_S4` (= Manhattan_View_S4 camera), `Water_Perf_RiverLow_Base` / `Water_Perf_S4_Base` (same views with P1's previous flat `M_CityWater` plane instead) |

Reflections: Lumen reflections (the project's `r.ReflectionMethod=1`, HWRT on) on the SLW surface, SSR fallback inside Lumen; no planar reflection
(a second scene render of the Manhattan geometry costs far more than the 2.5 ms budget; Lumen already pays for the tracing of the city's glass).
Horizon: the grid reaches 81 km; beyond ~40 km the exponential height fog + aerial perspective of the look rig cover it; far water is rough
(filtered variance) and reflects the averaged horizon sky.

## Views (docs/night1/water/views.json)
- `S4_perch_skyline`: city_shots.json S4 (same camera as `/Game/Maps/Manhattan_View_S4`), golden rig.
- `river_low`: UE (-76320, -12800, 440) cm, yaw -88.282, pitch -3, hFOV 90, golden rig. The brief's "layout west shoreline" `shoreX(-128)`
  = -744.16 m is the landward promenade line in the UE build (the camera stood on the esplanade); waterfront.js builds the seawall edge
  at -763.2 m there, so the camera is 4.8 m outboard of that edge (derivation text in views.json).
- `river_low_dolly`: InterpToMovement, 2 m/s along the view yaw, at the river_low point at t = 6 s; clip = t 6..16 s.
  UE 5.8 InterpToMovement rotates every control point by the actor rotation (relative or absolute, `InterpToMovementComponent.cpp:280`);
  the build un-rotates the offsets, otherwise the dolly sinks (pitch) and turns west.

## Round 01 numbers (details: round-01/NOTES.md, perf.json)
- GPU, 3840x2160 TSR 67 % (2573x1447), exclusive lock (perf_valid): passes attributable to the water (SingleLayerWater + its depth prepass +
  LumenReflections delta + Basepass delta) 1.54 ms at river_low, 1.15 ms at S4. Whole-frame GPU avg delta vs the flat-water baseline:
  -0.01 ms (river_low), +6.41 ms (S4; that run had 45 hitch frames and rising 5-s blocks); S4 repeat (contaminated by a foreign capture): +0.88 ms.
- CITY-SPEC C14 at S4: 40.9 (4K) / 41.1 (1080); P1 flat-water baseline 48.3.

## Known issues / next
1. C14 at S4 (far shore minus river luma, target 5..35) measures ~41 with this water (baseline flat water: 48). The spec's river box at S4 is
   1-2.5 km out and dominated by the golden rig's height fog; body / roughness changes moved it by < 2 luma. Look-rig fog is P4's.
2. Emissive output does not reach the screen on this SLW material (tested with a debug emissive of up to 3000 cd/m2); glitter was moved into
   normal / roughness. Not root-caused.
3. `StaticMesh.get_num_vertices(0)` in the `-nullrhi` commandlet reports 254 verts for the grid while its mesh description has 207 745;
   a per-vertex-hash debug render shows dense interpolation, so the rendered mesh looks complete; not root-caused.
4. The river_low frame is dominated by the pier deck on the right and a cross pier ~120 m ahead (the built Hudson River Park piers);
   open-river views need a different yaw / position.
5. No boats / wakes, splash ripples, spray or underwater view yet (browser water has them); contact foam only appears where geometry
   crosses the water line (piles, seawall faces), not along deck edges that stand on piles above the surface.
6. Midday / night rigs only checked at midday (extra stills); night not captured.
