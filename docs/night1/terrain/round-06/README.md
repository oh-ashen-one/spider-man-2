# Terrain round 06 — tree crowns cast sun shadows on the lawn

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Target (Opus director after the r05 critic [4,4,4,5,3], r05 merged): the tree crowns must cast sun shadows on the lawn and paving. Spec: `SPEC.md` E12.
Measured on the 4K stills of the final build; stills AND the t4 / t5 movies come from the SAME content (`/Game/TerrainR6`, final `mat` rebuild at 08:41, nothing rebuilt between the stills hold and the movies hold).
Numbers: `tools/terrain/measure_r06.sh docs/night1/terrain/round-06` (files beside this README).

## Captures
Real game (`-game`, offscreen), every launch through `gpu_slot.sh capture` (background priority) with `-notraceserver`.
- Stills `stills/*.jpg`: 3840x2160 output, **internal 1920x1080** (auto 50 % screen percentage, TSR 2x), 4 fps frame cap, shot at game 2 s after a 960x540 warm-up (as r04 / r05).
- Movies `t5_avenue_to_park.mp4`, `t4_lawn_sprint.mp4`: 1920x1080 output = **internal 1920x1080** (`r.ScreenPercentage 100`), fixed 1/60 s step, 12 fps wall cap, hero hidden, H.264 (sizes below).
- Intermediate holds (same content root, earlier material states; kept for the record): `test/` (build A: casters + lawn sky occlusion), `test2/` (+ canopy occlusion 0.4, non-Nanite L1 leaves),
  `s1_stopped/` (+ canopy 0.15, Nanite furniture; stopped by the builder after p10 / p4 to fix the p10 patch), `s2_stopped/`, `s3_stopped/` (two more p10-patch attempts), `test3/`
  (p10 test of the final materials), `diag/` (the shadow-pass diagnostic, `diag/NOTES.md`). Stops were deliberate (`stop_ue.sh`), not crashes.
- One engine crash this round: the nullrhi build commandlet asserted in `K2_AddLevelToWorld` while re-running the `map` step on an existing build (07:55); the next builds used the new
  `land` / `treecopies` steps and never re-ran `map`.

## Results (final build: stills and movies on the same content)
| target | wanted | measured | verdict |
|---|---|---|---|
| 1. do the leaf cards write shadow depth? | prove, fix the measured cause | yes: the card material casts like an opaque cube (lawn 0.82 vs 0.80) once the component casts; the cause was the component setup (non-Nanite + distance-field lighting off = no sun shadow, VSM or CSM) and a weak lawn sun share (full shadow 0.80). Fixed with hidden Nanite casters + lawn sky occlusion (`diag/NOTES.md`) | DONE |
| 2. p4 trees (3005,1100), (3040,1078), (2900,1060): darkest 15 px lawn box within 60 px on the anti-sun side / lit lawn | <= 0.6 each | box lumas 56.4, 50.5, 49.4 = **0.537, 0.481, 0.470** of the critic's lit-lawn value 105 (**0.521, 0.467, 0.456** of the lit box (2560,1080)-(2700,1150), median 108.3; `tree_boxes_p4.json`, preview `tree_boxes_p4_preview.jpg`). Same tool on the r05 frame: 73.9, 68.8, 53.9 = 0.70, 0.66, 0.51 of 105 (the r05 critic read 0.71, 0.62, 0.51); of its own lit box (127.7): 0.58, 0.54, 0.42 — the box test alone is lenient, the absolute box lumas fell 15-27 % | PASS as measured — see note |
| 3. p6: every esplanade tree shadow / paving | <= 0.6 | predicted crown-shadow bands of two isolated esplanade trees **0.894, 1.021** (`p6_shadow_ratio.json`) | FAIL (city-owned trees and paving, see note) |
| 4. p10: sky-bordered patch > 30 px with hp3 SD < 5 | none | **2** (48 px, SD 3.57, luma 58, left tree line; 32 px, SD 3.37, luma 35, a dark crown interior); the r05 'ball' (1139-1190, 237-280) and a second core ball (371-416, 546-591) are gone (`hull_p10.json`; same tool on r05: 3 patches, widest 52 px) | FAIL (2 left) |
| guard: p1 crown crops | >= 19 / 24 at sigma-3 >= 9, median >= 12 | **20 / 24, median 12.53**, min 6.94 (r05 19 / 24, 12.06) | PASS |
| guard: E9c longest straight crown silhouette, p10 | <= 42 px | tool 46.3 px; all three segments > 40 px (46.3 / 42.7 / 41.5) are the stepped roof of a city building at x 3530-3670, y 340-416 (`e9c_segments_building_roof.png`; r05: 40.3 px, the same roof); no crown segment > 40 px | PASS on crowns (tool number FAIL on the roof) |
| guard: p10 sigma-6 critic / guard box, R / G | >= 8, 0.85-0.95 | **19.48 / 17.00, R / G 0.884** | PASS |
| guard: critic prefers the new build in >= 3 / 5 r05-vs-r06 pairs; no axis below [4,4,4,5,3] | | for the critic (pack below) | — |
| if cheap: crown saturation median / foreground crowns | >= 0.65, 24 / 24 >= 9 | 0.646; 20 / 24 | not met |
| info: E1 aerial p4 critic box sigma-6 | <= 5 | 6.24 (r05 5.48): the box holds canopy-pool edges now | FAIL |

Note on target 2: the three trees stand in the West Side skyline's shadow — at the rig's 9 deg / az 238 sun the Great Lawn is sunlit only in one strip (also in the
city-only baseline, r05 `diag/cmp_vb.jpg`), so no sun shadow can form beside them. What passes the box test there is the baked canopy sky occlusion (`CANOPY_OCC`, the lawn under
and beside a crown sees ~0.15 of the sky), not a cast sun shadow. Where the sun does reach the lawn, the crowns now cast: inside the p4 sunlit strip, box (3030,1525)-(3075,1555)
reads **0.47** of the strip's sunlit lawn (p90 160.2) in r06 against **0.89** in r05 (`strip_shadow.txt`).
Note on target 3: the p6 esplanade trees are the city piece's street trees and the paving is the city's; the terrain owns neither (their crowns do shadow the facades).
GPU ms: GPU_PLACEHOLDER
Movies: MOVIES_PLACEHOLDER


## What changed (committed scripts only; Content is generated, never committed)
1. Shadow-pass diagnostic (`diag/NOTES.md`): debug maps `D_shadow` / `D_shadow2` (`build_terrain.py` step `diag`). The leaf-card material writes shadow depth as well as an opaque
   cube; the visible near-card pools cast nothing because no non-Nanite instanced component with `affect_distance_field_lighting` off casts a sun shadow here (VSM or CSM); a full
   shadow on the r05 lawn reads only 0.79-0.80 of the sunlit lawn under the golden rig.
2. `build_terrain.py`: hidden Nanite shadow casters `ISM_shadowcards_<park|elm|conifer>` (Nanite copies of the near-card canopies, real card material with `band.z = 1`, hidden in game +
   `cast_hidden_shadow`, out of Lumen / ray tracing / reflections); visible ez L1 leaves = a non-Nanite copy (culled 46 m), the Nanite L1 leaves = hidden casters `ISM_l1caster_*`;
   furniture / edge meshes and the park lamp are Nanite (`NANITE_KINDS`: benches, lamps, posts, fences, copings cast); steps `treecopies` (copies / Nanite conversion in place) and
   `land` (Terrain_Land only); the r05 non-Nanite crown shadow proxies off by default.
3. `terrain_materials.py`: lawn sky occlusion `LAWN_SKYOCC` 0.25 with `LAWN_SUNGAIN` 1.375 (the sunlit lawn keeps its r05 level); canopy sky occlusion `CANOPY_OCC` 0.15 from the
   pathmask alpha; `M_TerrainRock` grey (90 % desaturated) with 11 / 3.7 cm grain; ez leaves: leaf-detail sample + world grain within 35-110 m; Nanite usage on cards / VC materials.
4. `tools/terrain/prep_canopy.py`: per-tree canopy coverage (crown footprint from the near-card GLB extent x instance scale, 0.75-1.3 R) baked into the alpha of `pathmask.png`.
5. `Foliage.ush`: near-card core only beyond 70-120 m, with 11 / 29 cm leaf-mass speckle; `band.z = 1` shadow-caster mode; `tfLeafDetail`, `tfLeafGrain`; clump shade 0.26-1.9.
6. Tools: `r06_checks.py` (p10 sky-bordered smooth patches, p4 tree lawn boxes, p6 ratios), `measure_r06.sh`, `diag_shadow_measure.py`, `make_pairs.py` pair-size normalisation, `round6.sh`.
