# r06 shadow-pass diagnostic (do the leaf cards write the sun's shadow depth?)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Question (r05 open item 1, Opus director r06 target 1): why no tree crown shadow reads on our lawn. Method: two debug maps built by the committed script
(`build_terrain.py` step `diag`, `SM2_TERRAIN_ROOT=/Game/TerrainR5b`): the golden rig sublevel (`Look_Rig_golden`: sun 9 deg, az 238, sky light x8) + a 900 m plane with the real
lawn material `M_TerrainLawn` + a row of casters 35 m apart, perpendicular to the sun's ground shadow direction, seen top-down from 450 m (1920x1080 native, `r.ScreenPercentage 100`,
real `-game` offscreen through the GPU lock, frames at 20 s; driver `diag.sh`). Measured with `tools/terrain/diag_shadow_measure.py`: darkest 15 px running box along each slot's
shadow band / median lit lawn of the same span 40-60 px above and below. A ratio of 0.92-0.96 is the lawn's own stripe noise = no shadow.

| slot | caster | VSM (default) | CSM (`r.Shadow.Virtual.Enable 0`) |
|---|---|---|---|
| D_shadow -4 | opaque 8 m engine cube, StaticMeshActor | **0.80** | **0.79** |
| -3 | near-card mesh, HISM, opaque two-sided material, pool flags | 0.875 (contact smudge at the row, no cast shadow) | 0.87 (same) |
| -2 | near-card mesh, HISM, masked two-sided material (Op = 1), pool flags | 0.85 (same) | 0.87 (same) |
| -1 | near-card mesh, HISM, the real `MI_Pool_trees_park_near`, pool flags (r05 state) | 0.94 | 0.93 |
| 0 | same, in ray tracing, only `affect_distance_field_lighting` off | 0.94 | 0.96 |
| 1 | near-card mesh + real material as one StaticMeshActor | **0.82** | **0.82** |
| 2 | ez park0 L1 leaves + bark, Nanite HISM, pool flags | **0.85** | 0.94 (Nanite: no CSM) |
| 3 | r05 hidden crown shadow proxy (non-Nanite HISM, cast hidden shadow) | 0.94 | 0.96 |
| D_shadow2 -4 | opaque cube, StaticMeshActor | **0.79** | |
| -3 | near cards, HISM, real material, **no flags changed** (distance-field lighting on) | **0.79** | |
| -2 | near cards, ISM (not hierarchical), real material, pool flags | 0.94 | |
| -1 / 0 | near cards, HISM, pool flags, mobility movable / static | 0.96 / 0.92 | |
| 1 | **Nanite copy** of the near cards, HISM, real material, pool flags | **0.82** | |
| 2 | Nanite copy, **hidden in game + cast hidden shadow** | **0.81** | |
| 3 | engine cube in a HISM with the pool flags (opaque default material) | 0.92 | |

Findings (frames: `diag1_vsm_crop.png`, `diag1_csm_crop.png`, `diag2_vsm_crop.png`; numbers: `diag*_*.json`):
1. The blend mode / masked coverage is NOT the cause: the real masked leaf-card material casts as well as an opaque cube (0.82 vs 0.80) once the component casts at all.
2. The cause is the component setup: a non-Nanite instanced component (HISM or ISM, static or movable, any material, even the opaque engine cube) with the pool flags
   casts no sun shadow, with VSM or CSM. The same mesh with distance-field lighting left on casts (0.79): in this project the non-Nanite casters' sun shadows on our ground come
   through the distance-field shadow path, and `affect_distance_field_lighting = False` (set on every terrain pool since r01, because 200 k distance-field instances pinned the GPU)
   removes them. Nanite HISMs write the virtual shadow map regardless of that flag, also when hidden in game with `cast_hidden_shadow`.
   This also explains r05: the hidden crown proxies (non-Nanite) and the CSM test showed nothing; the crisp trunk lines were the Nanite ez L1 bark.
3. Even a full opaque shadow reads only 0.79-0.82 of the sunlit lawn under the golden rig: the 9 deg sun adds S = 0.25 K to the sky / bounce light K on this lawn although its
   turf normal already leans toward the sun. A 0.6 shadow target needs the lawn's sky share lowered, not only a caster.

Fix taken in r06 (committed scripts): hidden Nanite copies of every near-card canopy (`ISM_shadowcards_<kind>`, real card material, `band.z = 1` = fixed coverage threshold,
no LOD band, out of Lumen / ray tracing / reflections; the visible non-Nanite pools stay as they were and no longer flag cast_shadow), and the lawn's material AO (sky / Lumen
indirect only) at 0.25 with the albedo gain raised so the sunlit lawn keeps its r05 level (`terrain_materials.py LAWN_SKYOCC / LAWN_SUNGAIN`): a full shadow is then ~0.5.
The r05 crown shadow proxies are off by default (`SM2_TERRAIN_SHADOW_PROXY=0`). Distance-field lighting was not re-enabled on the pools (r01 GPU starvation).
