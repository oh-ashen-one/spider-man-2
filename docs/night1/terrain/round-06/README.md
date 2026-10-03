# Terrain round 06 — tree crowns cast sun shadows on the lawn

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Target (Opus director after the r05 critic [4,4,4,5,3], r05 merged): the tree crowns must cast sun shadows on the lawn and paving. Spec: `SPEC.md` E12.
Measured on the 4K stills of the final build; stills AND the t4 / t5 movies come from the SAME content (`/Game/TerrainR6`, final `mat` rebuild at RESULTS_BUILD_TIME, nothing rebuilt between the stills hold and the movies hold).
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

RESULTS_PLACEHOLDER

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
