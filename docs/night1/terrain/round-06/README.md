# Terrain round 06 — tree crowns cast sun shadows on the lawn

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

(work in progress: numbers follow)

## What changed (committed scripts only; Content is generated, never committed)
1. Shadow-pass diagnostic (`diag/NOTES.md`): debug maps `D_shadow` / `D_shadow2` (`build_terrain.py` step `diag`). Result: the leaf-card material writes shadow depth as well as an
   opaque cube; the visible near-card pools cast nothing because no non-Nanite instanced component with `affect_distance_field_lighting` off casts a sun shadow here (VSM or CSM),
   and a full shadow on the r05 lawn reads only 0.79-0.80 of the sunlit lawn under the golden rig.
2. `build_terrain.py`: hidden Nanite shadow casters `ISM_shadowcards_<park|elm|conifer>` (Nanite copies `SM_trees_<kind>_near_nanite` of the near-card canopies, the real card
   material with `band.z = 1`, hidden in game + `cast_hidden_shadow`, out of Lumen / ray tracing / reflections); the visible near-card pools no longer flag cast_shadow; the r05
   non-Nanite crown shadow proxies are off by default.
3. `terrain_materials.py`: lawn sky occlusion `LAWN_SKYOCC` 0.25 (material AO: Lumen indirect / sky only) with `LAWN_SUNGAIN` 1.375 (sunlit lawn level kept); `M_TerrainCards` carries
   the Nanite usage flag; `M_TerrainRock` grey (90 % desaturated) with 11 cm / 3.7 cm grain.
4. `Foliage.ush`: the near-card core (0.27 of the lobes) is drawn only beyond 70-120 m (the smooth olive ball of p10); `band.z = 1` = shadow-caster mode (fixed coverage threshold,
   no LOD band, no edge-on fade).
5. Tools: `r06_checks.py` (p10 sky-bordered smooth patches, p4 tree lawn boxes, p6 ratios), `measure_r06.sh`, `diag_shadow_measure.py`, `make_pairs.py` pair-size normalisation, `round6.sh`.
