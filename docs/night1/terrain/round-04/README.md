# Terrain round 04 — the lawn: captures and measurements

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Target (round-03 critic, three critics' consistent demand): replace the yellow star-sprite tufts by dense blade-clump grass, give the lawn albedo detail at 0.3-3 m scales without losing saturation,
fix the picnic blankets (flat tints, white at 9.75 s / maroon at 11.25 s), and re-plot `t5_avenue_to_park` so its last 5 s cross park ground at 25-40 m.
PASS list: `SPEC.md` E10 (a) E1 sigma-6 SD >= 8 on the critic crops + guard boxes, (b) saturation >= 0.70, (c) no flat quad > 100 px in t4 at 4 fps, (d) t5 last 5 s over the park at 25-40 m with sigma-3 SD >= 5,
(e) the pass-2 canopy guard, (f) GPU ms within +5 % of r3, (g) no axis below r3.

RESULT_PLACEHOLDER

## Build (all in committed scripts; Content is generated, never committed)
1. `tools/terrain/prep_lawn.py` (run at the end of `prep_terrain.py`): 4 near blade patches (a 2.3 m disc of ~1,150 blades: 26 clumps of 30-44 blades with outward lean + 200 loose blades, 3 triangles per blade, unit height,
   vertex colour R = height along the blade / G = blade random / B = clump random) scattered on a 1.5 m jittered grid over the browser's grass density / height mask (177 k instances, culled at 18 m, the blades shrink to the ground
   between 12 and 17.5 m so nothing pops); 2 far patches (~400 wider, taller blades) on a 2.6 m grid (59 k instances, culled at 60 m, they grow in between 6 and 13 m so there are no tall tufts at the hero's feet, shrink out between 42 and 58 m).
   Patches keep 0.45 m clear of paths / drives and clear of the 401 picnic blankets. Textures: `lawn_detail.png` (1024^2 tileable RGBA: clump luminance, wear field, clover field, grain) and `blanket_weave.png` (256^2 gingham weave, 0.24 m tile).
2. `Shaders/Terrain/Lawn.ush` (hand-written; `Park.ush` stays the generated browser ground): lawn grade (0.54, 1.22, 0.10) instead of (0.54, 1.20, 0.46) — the reference lawn's display blue is 16 / 255 against our 55 —,
   three-scale albedo mottling (1.15 / 4.7 / 16.3 m tiles, mip-filtered so it fades with distance), wear / dirt patches, clover patches, crisp 4.4 m mowing stripes, a clay-vs-grass mask (infield clay is no longer graded green);
   `M_TerrainPark` also gets gravel / asphalt grain on the paths and drives.
3. `terrain_materials.py`: `M_TerrainGrass` = blade turf (two-sided foliage with subsurface, dark root -> saturated yellow-green tip, per-blade and per-clump colour, yellow clumps, rare straw blade, wind at the tips, distance shrink),
   `M_TerrainBlanket` (gingham weave, fringed comb ends in a masked opacity, world-space wrinkle normal; six palettes), `M_TerrainVC / VC2` (furniture) get a world-space wood / paint grain.
4. `build_terrain.py`: grass pools are out of Lumen's ray-tracing scene and cast no shadows (r03: HWRT treats every drawn primitive as visible to indirect rays); blankets lie 2 cm over the lawn with a hair of tilt;
   env `SM2_TERRAIN_ROOT` (the r04 content is built side by side as `/Game/TerrainR4` while `/Game/Terrain` keeps the HEAD content for the GPU-ms baseline); the foliage step is re-runnable.
5. t5 route: `tools/terrain/t5_cands.py` writes 11 candidate scripts (`t5_candidates/`), the hold probes each headless (`-nullrhi`, telemetry only) and `tools/terrain/t5_score.py` ranks them by the share of the last 5 s spent over
   the park rectangle at 25-40 m; the best becomes `scripts/t5_avenue_to_park.json`.
Offline checks: `check_hlsl.py` 13 / 13 (DXC with UE's parameter types); a numpy simulation of the lawn detail (`_scratch/terrain/r04/sim_detail.py`) predicted hp sigma-6 SD 10-12 at 0.07-0.15 m/px and hp sigma-3 SD 8-9 at 0.06-0.35 m/px;
a Cycles CPU preview of the blade patches at eye height set the final blade density (the first 650-blade 1.9 m discs left ~45 % of the ground bare).

## Reference measurements (same tool, `tools/terrain/lawn_stats.py`; `ref_lawn_native.txt`, `ref_lawn_x2.txt`)
| frame | box | hp sigma-6 SD | mean HSV saturation | mean luma |
|---|---|---|---|---|
| centralpark-meadow-skyline (1080p native) | 512 x 400 lawn L / R | 10.08 / 10.20 | 0.840 / 0.817 | 79.8 / 78.2 |
| same, put on the 4K output grid (x2 Lanczos) | 512 x 400 / 460 | 5.73 / 7.35 / 8.61 | 0.822 / 0.808 / 0.855 | 82 / 86 / 75 |
| centralpark-aerial-ballfields (1080p native) | 400 x 300 / 400 x 200 | 3.84 / 2.79 | 0.893 / 0.879 | 114.6 / 90.7 |
| same, x2 | 512 x 400 | 2.25 / 1.43 | 0.894 / 0.887 | 120 / 98 |
| ours r03 (4K output, internal 1080p) | critic p4 / critic p10 / guards p10 p4 p9 | 4.40 / 7.95 / 6.34 / 1.41 / 2.63 | 0.582 / 0.541 / 0.609 / 0.639 / 0.649 | 142 / 104 / 95 / 105 / 83 |
Reading: the reference's own aerial lawn is smooth (hp sigma-6 SD 1.4-3.8), so the aerial >= 8 asked by the brief is above what the reference shows; at ground level the reference reaches 10 (native) / 5.7-8.6 (x2).
