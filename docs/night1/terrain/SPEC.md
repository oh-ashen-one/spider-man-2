# TERRAIN-SPEC (piece E: parks, shorelines, ground at swing height) — fixed, measurable targets

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`. Reference footage stays private
> (`~/spiderman-learnings`); nothing from it enters this fork.

Source of the lines: `docs/night1/director/PLAN-firstpass.md` §4 "Terrain" and `OWNER-PRIORITIES.md` (first-pass item 3: "beautiful terrain: ground, parks,
shorelines, what you see from above"). All numbers are on the real game (`-game`, offscreen, through the GPU lock); internal resolution is stated next to every one.

| id | target | checker / evidence | note |
|---|---|---|---|
| E1 | **Park crop detail**: high-pass standard deviation (luma 0-255, Gaussian sigma 6 px high-pass on a 512 x 512 crop of pure park land) >= 8 on every park crop of the 4K stills | `tools/terrain/crop_stats.py` | crops are cut by pixel box from `round-NN/crops.json` (grass only: no sky, no building, no water); the browser reference crops are measured the same way for comparison |
| E2 | **Grass / meadow cover**: share of OPEN park land (park rectangle minus the 5 water bodies, the park paths + drives, and the museum lot) that carries the grass / meadow / woodland-floor ground cover (ground shader + tuft scatter) >= 90 % | `tools/terrain/prep_terrain.py` -> `round-NN/stats.json` (`grass_cover_of_open_land_pct`) + `tools/terrain/cover_topdown.py` on a top-down capture | **definition note**: 12.5 % of the park rectangle is path / drive by the browser design (82,320 m2 of 658,090 m2 land), so a literal "of all park land incl. paths" reading can never exceed ~87.5 %; both numbers are reported (`grass_cover_of_all_park_land_pct`). The bank / rock cut-outs of the browser mask (2 m around ponds, 125 schist outcrops) are legitimately not grass |
| E3 | **Shoreline continuous**: along the whole island shoreline (LAND_POLY, 342 vertices) no gap > 5 m without a shore element (seawall / bulkhead / esplanade edge / pier) | `tools/terrain/shore_audit.py` on the exported coast geometry (`round-NN/shore_audit.json`); in-engine shore-walk capture as evidence | |
| E4 | **Ground reads from swing height**: park lawns, paths, ponds, the Reservoir and shore edges are visible, textured and lit (not the flat land colour) from 30-120 m; ground C2 lines of the city spec hold | blind A/B vs the matching reference + `docs/night1/city/SPEC.md` C2 | |
| E5 | **Axes >= 6** (blind critic): lawn / ground cover, paths + water edges, shoreline, trees / canopy mass, overall "beautiful terrain" read | critic verdict `docs/night1/terrain/critic/round-NN-CRITIC.md` | |
| E6 | **Everything rebuilt by committed scripts** (no Content committed, no LFS): `tools/export/export_terrain.mjs` -> `tools/terrain/prep_terrain.py` -> `tools/export/gen_terrain_shaders.mjs` -> `Scripts/build_terrain.py` | `docs/night1/terrain/HANDOFF.md` rebuild recipe | |
| E7 | **Collision**: the park lawns, lawns on the coast and pond surfaces collide (tag `WHGround`, never hold a web); the hero runs the park without falling through | hero run capture + telemetry | |

Not in round 1 (said plainly): street trees island-wide (the island piece's per-tile export), pickets / wet bands / pier sheds (exported, not yet built), the Met-like museum
(skipped on purpose: real-building copy), night look of lamps / globes, ball-field fences' alpha cards.
