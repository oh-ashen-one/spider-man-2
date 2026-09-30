# P6 water (blind A/B build, Sonnet 5.5): handoff after round 01

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

Branch `night1/water-ab-sonnet` (worktree `~/sm2-n1/water-ab-sonnet`, base = integration `Opus-5.5-Loop-Night-1` at a730d97). Owned: `/Game/Water`,
`unreal/WebHomage/Scripts/build_water.py`, `docs/night1/water/`. Scratch: `/Users/midir/sm2-n1/_scratch/water-sonnet/`. No `.uasset` / `.umap` is committed.

## Rebuild (editor closed, ~12 min from an empty `Content/`, then ~30 s per water iteration)

```
python3 unreal/WebHomage/Scripts/build_water.py                      # base, assets, water, views
python3 unreal/WebHomage/Scripts/build_water.py --steps water        # after a shader / tune change (material + maps only)
SM2_WATER_TUNE='{"body":[0.05,0.07,0.06],"dn_k":0.5}' python3 ...   # override any key of TUNE without editing the file
```
| step | what it does |
|---|---|
| `base` | `build_manhattan.py` steps `cpp, city_export, city_prep, city, look, map` (traversal / characters are skipped: the water does not need them) with this piece's scratch, vite port 5219 and every Unreal launch wrapped in `gpu_slot.sh capture` (a wrapper script replaces the UnrealEditor path inside the imported module) |
| `assets` | numpy / cv2 / PIL, no Unreal: `T_WaterNoise`, `T_WaterRipple` (seeded FFT noise), `T_WaterShore` / `T_WaterContact` (distance maps, see below), `WaterGrid.glb` (polar mesh) |
| `water` | one headless `-nullrhi` commandlet: imports the assets to `/Game/Water`, builds `M_WaterRiver` + `MPC_Water`, replaces the rendering of P1's `WaterPlane` in `City_Midtown_Geo`, builds the view maps |
| `views` | writes `docs/night1/water/views.json` (needs `assets` and the city export) |

Verified from a clean state on 2026-09-29 (base 617 s, water 27 s).

## What is in the level
- `/Game/Tests/City/City_Midtown_Geo` (P1's level, shared by every map) gets an actor `WaterSurface` (static mesh `SM_WaterGrid`, material `M_WaterRiver`, no collision, no shadow,
  excluded from the distance-field / Lumen scene and from ray tracing). P1's flat `WaterPlane` stays (it is tagged `WHGround` by P4 and is the floor the hero collides with) but no longer renders.
  Every map that streams `City_Midtown_Geo` (all `Manhattan*` maps included) shows the new water after `build_water.py --steps water`.
- `/Game/Water/Maps/Water_View_{Low,Dolly,LowWest,LowPoly,Low_Midday,LowWest_Midday,S4,S4_Off,Low_Off}`: view maps (city geo + golden or midday rig + the camera of `views.json`).
  `*_Off` maps carry a level sequence that sets `MPC_Water.Off = 1` (the wave surface moves 10^7 m up = culled): the "no water" baseline of the perf measurement.

## How it works
- **Surface.** One polar grid, 289 rings x 64..512 segments, 124 609 vertices / 248 704 triangles, radius 71.8 km (mesh radial step max(0.5 m, 2 % of r) out to ~1.5 km, ~12 % beyond; 2:1 angular
  refinement stitched without T-junctions). Its bounds are +-72 km around the origin, so it is never frustum-culled. The material's WPO moves every vertex to the camera
  (`cam.xy`) and displaces it with the browser's 12 Gerstner waves (`src/world/waves.js` SPEC, same constants: Lagrangian point, height `A sin`, horizontal `Q A cos`). The wave phase depends on the
  world lattice point only, so the surface does not slide when the camera moves. Each vertex carries its local grid spacing in UV0.x; a wave is faded out when spacing / wavelength > 0.18..0.3
  (same rule as `waveDisp`), so the far rings are flat by construction and there is no separate far plane and no horizon seam.
- **Per pixel** (`hlsl_pixel()` in `build_water.py`, a port of `water.js river()` / `waterShade()`): analytic Gerstner slope of the 12 waves with the browser's footprint filter (waves smaller than the pixel
  move into roughness: `varU`), four ripple normal layers at 2.6 x 7.5 / 4.4 x 12 / 9 / 21 m tile scales (crests across the wind, drifting downwind; the texture band is 2..12 cycles per tile, a finer band read as per-pixel noise because Lumen's reflection of the cloudy sky then flickers from pixel to pixel), wind / gust / slick / streak fields, the shorter waves
  (< 9 m) ride a low-frequency domain warp (breaks the interference contours the plain sine sum draws), GGX roughness from Cox-Munk unresolved slope + variance, a reflect-vector clamp
  (a facet that would reflect the view ray into the water reflects the sky: without it Lumen traces downward into nothing and the river goes dark and blotchy at grazing angles).
  Output = Default Lit: world normal, roughness, base colour, `Specular 0.25` (F0 0.02, water). Fresnel, the sun's GGX glint (glitter path), sky + skyline reflections and the shadowing all come from the
  engine: Lumen reflections (hardware RT on, as the project sets it) and the directional light. No planar reflection, no SSR: Lumen traces the real city (a flat glossy test surface reflects the warehouse,
  piers and the far skyline with the correct perspective: `round-01/debug/flat_glossy_mirror_west_1080.jpg`, an earlier build with debug mode 2 = flat normal, roughness 0.08, black body), so its cost is the project's Lumen cost and is included in the measurement below.
- **Colour / absorption.** Base colour = albedo of a turbid, silty medium (`TUNE.body`, green-grey), lit by sun + sky light; near the walls (distance map < 90 m) the river bed shows through
  (Beer-Lambert, sigma_t ~0.5 / m, depth 1.2 m at the wall to 12 m mid-channel) and the water turns browner and lighter; mid-channel it is slightly bluer; a wet-contact line darkens the last decimetres.
- **Shore / pier foam.** `T_WaterContact`: signed distance (+-16 m, 2 m/px, 8 bit) baked from the real waterline: the coast meshes of the city export (esplanade fill, seawalls, riprap, platforms) and the bridge
  piers, clipped at the water plane, rasterised at 0.5 m/px, plus the layout polygons. `layout.LAND_POLY` alone is NOT the waterline: `waterfront.js` builds the esplanade / bump-outs up to ~25 m outward of it.
  The foam is the browser's contact foam (band width from noise + a lapping pulse). `T_WaterShore` (8 m/px, 400 m) drives the silt tint. Whitecaps on the steepest crests in the gusts.
- **No tiling.** The waves are analytic sums (no repeat over the island); the noise fields are sampled at 620 / 230 / 34 m scales with anisotropic wind-aligned coordinates and the ripple layers at four scales and
  orientations; footprint fades remove the detail with distance. No repeat was visible in the captures.

## Cost
River_low (water ~30 % of the frame) costs **1.86 ms GPU** and the S4 perch (water ~12 %) **0.35 ms** at 3840x2160 output, TSR 67 % (2573x1447 internal), exclusive lock, valid runs, final assets (budget 2.5 ms).
Other pairs: river_low 1.96 ms (one run contaminated by a foreign capture), 2.63 ms (one run holds a 300 ms hitch; the median-frame delta of the same pair is 2.11 ms); superseded look v0: 1.38 / 1.73 ms. Full tables: `round-01/NOTES.md`, `round-01/perf.json`.
The water cost includes the Lumen reflection / GI work of the water pixels (they vanish in the baseline), i.e. any glossy opaque water pays it. The vertex work (125 k vertices x 12 waves) and the pixel shader are small next to it.
No per-pass breakdown was taken: if the budget gets tight, the levers are the Lumen reflection quality on the water (roughness > 0.4 is not traced) and the ripple layer count.

## Known limits / next
- **TSR velocity.** The vertices follow the camera, so the engine's per-vertex velocity of the surface equals the camera motion, not the motion of the water. Static or slow cameras are fine; fast swings may
  soften near water. Fix options: a `Previous Frame Switch` that feeds the current camera to the previous-frame WPO, or a snapped lattice.
- `C14` (river 5-35 luma below the far shore at S4) is not met: river Y 126.3, far shore Y 172.1 (= 45.8). The river band at S4 is dominated by the height fog: a nearly calm mirror surface only reaches Y 130.5, the old P1 plane
  measures Y 132.1 (40.4) on the same view. The far shore is itself above CITY-SPEC C13 (Y sky + 12.6, target sky - 35..-25): P1 far-city / P4 fog, not the water.
- No boats / wakes, splash ripple sim, spray, underwater view, or river bed: the browser's `waterfx/*` and `setBoats` are not ported (P6 life owns them). The contact map has no piers that only exist as browser runtime solids
  (only the coast meshes and `bridgeStone` are in the export).
- The lens flare and ghost hexagons in the low-sun views (`river_low_west`) come from P4's rig (bloom lens flare), not from the water.
- `r.Lumen.*` are project defaults; nothing in `Config/` was changed. `MPC_Water.Off` is only for the perf baseline maps.
- Mesh distance-field generation cannot be disabled from Python on the mesh asset (property not exposed); the component is excluded from DF lighting instead. The engine logs one handled ensure
  ("precision loss while converting matrix", `UpdateDistanceFieldObjectBuffers`) that the old 60 km plane already caused in every city capture.
- Hero swimming / water gameplay height: `waves.js` `waveHeight()` is not exposed to gameplay; the surface height is `WATER_Y (-1.6 m) + Gerstner height` on the same constants (`WAVES` in `build_water.py`).

## Capture scripts
`docs/night1/water/scripts/`: `cap.sh <name> <map> <res> [run_game args]` (one capture through the GPU lock), `stills.sh name=map ...` (4K + 1080p jpgs into `round-01`), `dolly.sh` (movie; then trim frames 180..779 with ffmpeg as in NOTES),
`perf.sh name=map ...` (exclusive perf runs, sidecars into `round-01/perf_runs`). They hard-code this piece's scratch and worktree paths.

## Files
`unreal/WebHomage/Scripts/build_water.py` (everything), `docs/night1/water/views.json`, `docs/night1/water/round-01/*` (captures, `perf.json`, `NOTES.md`, `frame_stats.json`, `farfield_S4.json`), `docs/night1/water/IP_EXCLUSIONS.md`.
