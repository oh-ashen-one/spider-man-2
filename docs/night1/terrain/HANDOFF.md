# Terrain (piece E) — HANDOFF (round 06: captures + blind critic pack done; critic not run by the builder)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/terrain` (pushed; r05 merged into `Opus-5.5-Loop-Night-1`, r06 not merged), worktree `/Users/midir/sm2-n1/terrain`, scratch `/Users/midir/sm2-n1/_scratch/terrain` (r06 drivers / logs in `r06/`).
Owns `/Game/Terrain*`, `tools/export/{export_terrain.mjs,collect_terrain.js,gen_terrain_shaders.mjs}`, `tools/terrain/`, `unreal/WebHomage/Scripts/{build_terrain.py,terrain_materials.py}`,
`unreal/WebHomage/Shaders/Terrain/`, `docs/night1/terrain/`. Spec / shot list / cameras: `SPEC.md` (E12 = r06 targets), `SHOTLIST.md`, `shots.json`. Nothing of the builder's is running.

## Round 06 (2026-10-03 07:14-, Claude Opus 5.5 high via Devin): tree crowns cast sun shadows (every number: `round-06/README.md`)
Target (Opus director after the r05 critic [4,4,4,5,3]): the tree crowns cast sun shadows on the lawn and paving. Final content `/Game/TerrainR6` (full build 07:43 + incremental
`tex,mat,treecopies` / `mat` builds, last `mat` build 08:41); stills (`round-06/stills`, 9 views, 3840x2160 out, internal 1920x1080) and movies (`t5_avenue_to_park.mp4`,
`t4_lawn_sprint.mp4`, 1920x1080 native, hero hidden) from that same content. Measured (`tools/terrain/measure_r06.sh`, table in `round-06/README.md`):
(1) shadow pass proven and fixed (see below); (2) p4 trees: darkest lawn box 0.537 / 0.481 / 0.470 of the critic's lit lawn 105 (r05 frame, same tool: 0.70 / 0.66 / 0.51) — but
these three trees stand in the West Side skyline's shadow, so the darkening there is the baked canopy sky occlusion, not a cast sun shadow; a cast crown shadow in the p4 sunlit
strip reads 0.47 of the sunlit lawn (r05 0.89); (3) p6 esplanade tree shadows 0.89 / 1.02 — not met (city trees on city paving); (4) p10: 2 smooth sky-bordered patches > 30 px
remain (48 px SD 3.57, 32 px SD 3.37), the r05 ball and a second core ball are gone. Guards: crowns 20 / 24, median 12.53; E9c 46.3 px by the tool = a city building's stepped
roof (no crown segment > 40 px); p10 sigma-6 19.48 / 17.00, R / G 0.884. GPU ms: not measured (perf lock refused, exit 75, Mac unattended); capture-run GPU ms (contaminated) p1 189.6 / p10 101.5 / p4 123.6 (r05 163.5 / 92.9 / 105.5). Movies: t5 10.5 MB (crf 30), t4 13.7 MB (crf 32); the merged traversal flies t5 differently (28 % over the park). t4 shows 3 smooth dark ground patches > 100 px (canopy-occluded floor).
Blind critic pack (not judged by the builder): `/Users/midir/sm2-n1/_scratch/critic-E-r06/pack` (16 pairs; both sides of every pair the same pixel size), `pairs.json` beside it, key outside (`pack.key.json`).
One engine crash this round (the build commandlet on a re-run of the `map` step, 07:55); three stills holds were stopped on purpose with `stop_ue.sh` to fix the p10 patch.

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
1. **p10 smooth patches (r06 target 4)**: two remain — (172-219, 532-572) in the left tree line (luma 58) and a dark crown interior (1250-1275, 385-416, luma 35). Both are dark;
   the core speckle (`Foliage.ush`, core branch) scales with luma. Next: identify them (a VB_p10 city-only still is in `round-06/diag/base_p10_lawn_eye.jpg` if the last hold ran),
   then lift the core's shade or add speckle in absolute terms.
2. **p4 lawn under the skyline shadow**: no sun shadow can form where the 9 deg sun does not reach (most of the Great Lawn / p1 lawn). The look piece owns the rig; a higher sun or
   a different azimuth would put crown shadows on the open lawn. The terrain's levers left: canopy occlusion strength (`CANOPY_OCC`), lawn sky occlusion (`LAWN_SKYOCC`).
3. **p6 esplanade shadows (r06 target 3)**: city street trees on city paving; the paving material decides the shadow depth (the terrain lawn needed sky occlusion 0.25 to
   reach ~0.5): a city-piece item.
4. **Pond-bank 'olive eggs' in p3**: the reed clumps (`parkReeds`, `M_TerrainVC2`, olive tint) read as smooth khaki ovoids at 100-200 m; they need a blade texture / alpha, not
   the rock material (the rock material is grey and grained now).
5. Crown saturation median 0.646 (target 0.65); p4 aerial lawn box sigma-6 6.24 (<= 5 wanted): the canopy pools' edges sit in that box.
6. t4: three smooth dark ground patches > 100 px (0.75 / 3.5 / 4.25 s): the canopy-occluded woodland floor under the near trees reads near-black and flat; lighten
   `CANOPY_OCC` near the camera or give the woodland floor its own detail.
7. GPU: capture-run GPU ms rose (p1 189.6 / p10 101.5 / p4 123.6 against r05 163.5 / 92.9 / 105.5, contaminated runs): the Nanite shadow casters (4,771 card trees + L1 leaves) are
   the likely cost; an exclusive `gpu_slot perf` run is needed (refused while the Mac is unattended).

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
