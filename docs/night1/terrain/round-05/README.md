# Terrain round 05 — crowns as lit leaf volumes (and the lawn shadows they should cast)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Target (Opus director after the r04 critic [4,4,4,4,3]; r04 not merged, the integration still has r03): make the tree crowns read as lit leaf volumes that cast shadows on the lawn.
Measured on the 4K stills; stills AND the t4 / t5 movies are from the SAME build (content `/Game/TerrainR5`, mat build 4 of 04:40; nothing rebuilt between the stills hold and the movies hold).
Spec: `SPEC.md` E1 (reconciled this round) and E11. Numbers: `tools/terrain/measure_r05.sh docs/night1/terrain/round-05` + `tools/terrain/tree_shadow_auto.py` (files beside this README).

## Captures
Real game (`-game`, offscreen), every launch through `gpu_slot.sh capture` (background priority), every launch with `-notraceserver`.
- Stills `stills/*.jpg`: 3840x2160 output, **internal 1920x1080** (auto 50 % screen percentage, TSR 2x), 4 fps frame cap, shot at game 2 s after a 960x540 warm-up (same as r04).
- Movies `t5_avenue_to_park.mp4`, `t4_lawn_sprint.mp4`: 1920x1080 output = **internal 1920x1080** (`r.ScreenPercentage 100`), fixed 1/60 s step, 12 fps wall cap, hero hidden, H.264 (crf in the log), telemetry beside them.
- Intermediate holds: `test/` (build 1), `test2/` (build 2), `build3/` (4 stills of build 3, the hold was stopped by me with `stop_ue.sh` to rebuild), `diag/` (lawn-shadow diagnostics, see `diag/NOTES.md`).

## Results (final build)
RESULTS_TABLE

## What changed (all in committed scripts; Content is generated, never committed)
1. `Shaders/Terrain/Foliage.ush`: `tfSummer` regrades the browser's per-tree autumn tints (hue 22-68 deg, brown .. olive) to a yellow-green .. leaf-green pair with the same luminance (per-tree variety kept);
   `tfClumpShade` world-space light / shade clumps (0.15-1.1 m octaves, x0.28-1.8) on the leaf cards beyond 25 m with yellower sunlit clumps; edge-on cards fade by their geometric facing
   (the p10 'saucer' streaks); 2.5 % dry leaves (r04 7 %); distant cards (+35 % beyond 450 m) and the >= 520 m hull (+50 %) gain albedo saturation against the golden haze; the cards use a fixed
   coverage threshold in the shadow pass.
2. `build_terrain.py`: the near leaf-card canopy (`trees-*-near`, 220-240 cards around a 0.27 core) is drawn out to 520 m (`NEAR_FAR`); the LOD1 pool (18-24 cards around a 0.85 solid core,
   the 'hull balls' of p10 and the smooth olive mid band of p1) is not built; bark tint 0.2 / 0.175 / 0.15 (was 0.33 / 0.29 / 0.25).
3. `terrain_materials.py`: `M_TerrainBark` vertical furrows / ridges / grain / lichen (triplanar on the two horizontal axes); blades R x1.53 (p10 R / G); lawn grade R 0.8; turf normal bent
   toward the sun (`Lawn.ush lwTurfNormal`, tilt 0.85; albedo x0.55); pond Specular 0.25 (water F0 0.02: the p3 Lake mirrored the pale sky as white blobs); greyer schist; FILL 650.
4. `Shaders/Terrain/Lawn.ush`: aerial fade of the lawn detail (`fa` = smoothstep 90-200 m: mottling / wear / clover x0.05, the base photo's own variation divided out, Park.ush's mid-scale
   patches compressed toward the nominal meadow luminance, softer stripe edges); the eye-level lawn is unchanged.
5. Tools: `measure_r05.sh`, `tree_shadow_auto.py` (shadow position predicted from the rig's sun and the crown heights, projected with the shot camera), `shadow_ratio.py` (hand boxes),
   crown saturation in `crown_stats.py`; `round5.sh` hold driver; `-notraceserver` in `capture_round.sh` / `run_build.sh`.

## Lawn shadows (target 4): not reached — what was found
See `diag/NOTES.md`. Our lawn shows no crown shadow in any build of this round, with VSM or CSM, while the city's own flat land in the city-only baseline VB_p4 shows long tree shadows.
Material AO + albedo gain (test 1) and a sun-facing turf normal (test 2 on) changed the lawn's colour / brightness but no crown shadow appeared. Open hypotheses for the next round, in order:
(a) the leaf pools are out of the ray-tracing scene (r03 fix for the black Lumen shells): if the sun's shadows are ray traced anywhere in this project's path (MegaLights / RT shadows), they cast nothing;
the city's trees (in the RT scene) do. Test: one still with `r.MegaLights.EnableForProject 0` / `r.RayTracing.Shadows 0`, and one with the near-card pool `visible_in_ray_tracing = True`.
(b) the non-Nanite VSM path (`[VSM] Non-Nanite Marking Job Queue overflow` in every terrain log). (c) a debug cube on the lawn to separate casting from receiving.
