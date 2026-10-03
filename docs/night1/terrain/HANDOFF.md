# Terrain (piece E) — HANDOFF (round 06: captures + blind critic pack done; critic not run by the builder)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/terrain` (pushed; r05 merged into `Opus-5.5-Loop-Night-1`, r06 not merged), worktree `/Users/midir/sm2-n1/terrain`, scratch `/Users/midir/sm2-n1/_scratch/terrain` (r06 drivers / logs in `r06/`).
Owns `/Game/Terrain*`, `tools/export/{export_terrain.mjs,collect_terrain.js,gen_terrain_shaders.mjs}`, `tools/terrain/`, `unreal/WebHomage/Scripts/{build_terrain.py,terrain_materials.py}`,
`unreal/WebHomage/Shaders/Terrain/`, `docs/night1/terrain/`. Spec / shot list / cameras: `SPEC.md` (E12 = r06 targets), `SHOTLIST.md`, `shots.json`. Nothing of the builder's is running.

## Round 06 (2026-10-03 07:14-, Claude Opus 5.5 high via Devin): tree crowns cast sun shadows (every number: `round-06/README.md`)
STATUS_PLACEHOLDER

## Shadow-pass finding (r06 target 1, `round-06/diag/NOTES.md`)
- Debug maps `D_shadow` / `D_shadow2` (`build_terrain.py` step `diag`): the masked leaf-card material writes shadow depth as well as an opaque cube (lawn ratio 0.82 vs 0.80).
- Cause of "no crown shadow": every terrain pool / furniture mesh is non-Nanite with `affect_distance_field_lighting = False` (set since r01: 200 k distance-field instances pinned the GPU);
  in this project such a component casts no sun shadow at all (VSM or CSM; HISM, ISM or movable alike). With distance-field lighting on it casts (0.79); a Nanite HISM casts through
  the virtual shadow map with the flag off, also hidden in game with `cast_hidden_shadow` (0.81). The r05 crisp "trunk" lines were the Nanite ez L1 bark.
- Second cause: under the golden rig a full shadow on the r05 lawn read only 0.79-0.80 of the sunlit lawn (the 9 deg sun adds ~0.25 of the sky / bounce light).
- Third fact: most of the Great Lawn in p4 (and the p1 lawn) lies in the West Side skyline's shadow at the 9 deg / az 238 sun (the city-only baseline VB_p4 shows the same sunlit
  strip); no tree can cast a sun shadow there. The three p4 trees of the target stand in that shadow.

## Fixes in r06 (committed scripts; Content is generated, never committed)
- `build_terrain.py`: hidden Nanite shadow casters `ISM_shadowcards_<kind>` (Nanite copies `SM_trees_<kind>_near_nanite`, real card material, `band.z = 1`); the visible ez L1 leaves draw
  a non-Nanite copy (`*_l1_leaves_raster`, culled 46 m) and the Nanite L1 leaves stay as hidden casters (`ISM_l1caster_*`); furniture / edge meshes and the park lamp are Nanite
  (`NANITE_KINDS`) so benches / lamps / fences cast; step `treecopies` makes those copies / conversions in place; step `land` rebuilds `Terrain_Land` only (re-running `map` on an
  existing `Manhattan_Terrain` crashed the commandlet in `K2_AddLevelToWorld`); r05 crown shadow proxies off (`SM2_TERRAIN_SHADOW_PROXY=0`).
- `terrain_materials.py`: lawn sky occlusion `LAWN_SKYOCC` 0.25 with `LAWN_SUNGAIN` 1.375 (sunlit lawn level kept, full shadow ~0.5 in the debug map's terms); canopy sky
  occlusion `CANOPY_OCC` 0.15 from the pathmask alpha; `M_TerrainRock` grey with 11 / 3.7 cm grain; near ez leaves get leaf-scale detail within 35 m; Nanite usage on cards / VC.
- `tools/terrain/prep_canopy.py`: per-tree canopy coverage (crown footprint from the near-card GLB, 0.75-1.3 R) into the ALPHA of `<prep>/pathmask.png` — run it after
  `prep_terrain.py` and before the `tex` step.
- `Foliage.ush`: near-card core only beyond 70-120 m; `band.z = 1` shadow-caster mode; `tfLeafDetail`; clump shade 0.26-1.9.

## Open items, in order
OPEN_PLACEHOLDER

## Next-session recipe (everything idempotent)
- Offline first: `python3 tools/terrain/check_hlsl.py` (14 / 14). Prep chain (CPU): `export_terrain.mjs` -> `prep_terrain.py` -> `prep_lawn.py` -> `prep_canopy.py`.
- Content: `SM2_TERRAIN_ROOT=/Game/TerrainR6 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain -- tools/terrain/run_build.sh` (full ~13 min, nullrhi); after a
  material / texture / copy change only: `run_build.sh tex,mat,treecopies` (~2.5 min); after a pool change: add `land` (never `map` on an existing build).
- Captures: `docs/night1/terrain/round6.sh` (copy for round 07), detached from your own shell, never inside a hold: `STAGE=T` (warm + p4 p1 p10 -> `round-06/<TEST_NAME>`),
  `STAGE=S` (warm + nine stills), `STAGE=M` (t5 + t4, same content). Driver that chains build -> S -> M -> perf: `_scratch/terrain/r06/chain_F.sh`.
- Numbers: `tools/terrain/measure_r06.sh <round dir>` (needs `<round>/r06_boxes.json` with the p4 lit box and the p6 boxes); pack: `LAWN_PROGRESS=1 python3 tools/terrain/make_pairs.py
  <round dir> <critic dir>/pairs.json docs/night1/terrain/round-05` (normalises both sides of every still pair to 3840x2160), `abpack.py`, `tools/terrain/pack_small.py <pack>`.
- Safety: stop engines only with `stop_ue.sh /Users/midir/sm2-n1/terrain` (drivers in `_scratch/terrain` by PID); every launch passes `-notraceserver`; a commandlet crash leaves a
  `CrashReportClient` for `UE-WebHomage-pid-<your pid>`: stop that one by PID.

## Older rounds (history; numbers in `round-0N/README.md`)
- **r05 (Opus 5.5)**: crowns as lit leaf volumes (tfSummer, tfClumpShade, near cards to 520 m), critic [4,4,4,5,3], preferred 5/5; merged.
- **r04 (Sonnet 5.5)**: dense blade lawn, woven blankets, triplanar rock; critic [4,4,4,4,3]. **r03**: leaf-card LOD1, foliage out of ray tracing. **r02**: tree chain. **r01**: ground, ponds, shore.
