# P6 City life: handoff after round 01 (traffic + crowd; water not started)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

Branch `night1/life`, worktree `~/sm2-n1/life` (base: integration `Opus-5.5-Loop-Night-1` at e1632c7). UE MCP port 8776 (not used: everything is headless commandlets + `-game`), dev port 5207.
Owned: `/Game/Life`, `/Game/Tests/Life`, `unreal/WebHomage/Scripts/build_life.py`, `unreal/WebHomage/Scripts/life_data/`, `tools/life/`, `docs/night1/life/`, and (new, flagged for the integrator)
`unreal/WebHomage/Source/WebHomage/Life/` (a new folder in the shared module: no Build.cs / .uproject / Config change was needed, the module root is already an include root).
Scratch: `/Users/midir/sm2-n1/_scratch/life/`. No `.uasset` / `.umap` is committed: `build_life.py` recreates everything.

## What round 01 built

| system | what it is |
|---|---|
| Traffic (`AWHLifeTraffic`) | Port of the browser sim (`src/world/npc/roads.js` + `traffic.js`) on the exported Midtown road graph: 179 lane links, 253 junction connectors with pairwise conflicts, the 40 s signal cycle of `props.js` (avenue 22 s green / 3 s amber, street 11 s green / 2 s amber), IDM car following (per-driver headway / accel), turn speed caps, left turns yield to oncoming, box reservation by connector conflicts (no car enters a junction whose exit is full), cars removed at region exits and spawned at entries up to the browser density (31 / 44 / 20 / 41 cars per km of lane for avenue / street / wide street / Broadway). 15 vehicle types x 3 LODs (the browser's Blender models, 5.5k / 1.1k / 160 tris), one `UInstancedStaticMeshComponent` per type with per-instance custom data (linear paint colour, brake-light state). About 650-710 moving instances + 1200 static parked ones. |
| Parked cars / curb taxis | Port of `parkedFor` (curb lane spots, double-parked trucks, pulled-over taxis (chance raised 0.16 -> 0.42), buses at stops), spots blocked by P1 curb props and junction paths are dropped. `life_data/parked.txt`, static ISM instances. |
| Crowd (`AWHLifeCrowd`) | Pedestrian graph exported from the browser layout (135 sidewalk corners, 113 sidewalk edges, 71 crosswalks, every point validated against `streetsAt`). About 1450 walkers are simulated analytically (acceleration-limited speed, smooth heading, wait at crosswalks for the walk signal on the same clock as the traffic); only the ~280 within 190 m of the camera own a `USkeletalMeshComponent` (pool of 8 per look x 60 looks = 20 citizen models x 3 outfits). Each live walker plays P2's citizen walk cycle through `UWHCharAnimInstance` at its exact ground speed (`ForcedSpeed`), starts at a random gait phase (pre-roll 0.2-2 s), and identical looks on screen are re-assigned (farther one only, >= 30 m). The outfit variants (`tools/life/citizen_variants.py`) recolour clothes / bags / hats of each citizen's atlas tile (hue +120 / +240 deg outside skin, red and brown), the mesh is shared. |
| Materials | `M_LifeVehicle`: port of `partmat.js` / `vehicles.js` (part id in UV1.x, atlas UV0, baked AO in vertex colour, taxi topper ad tiles picked per instance from the CLEAN tiles, glass over the interior cards, brake lights from custom data, night lamps from `MPC_City NightK`). `M_LifeCitizen` + 20 instances. |
| Test maps | `/Game/Tests/Life/Life_Midtown` (playable, default game mode, PlayerStart on the avenue), `Life_View_S1`, `Life_View_S2` (P1 shot cameras from `city_shots.json`), `Life_Street_Clip` (a walking camera through the avenue's curb channel). All four = sublevels `City_Midtown_Geo` (P1, patched by P4) + `Look_Rig_golden` (P4) + `Life_Actors` (traffic, crowd, probe). |
| Probe (`AWHLifeProbe`) | Logs `WH_LIFE_FRAME` (vehicles / people in the camera frustum, size- and occlusion-tested), `WH_LIFE_FOOT` (planted-stance ankle displacement of the 14 nearest walkers), sim ms. `tools/life/analyze_feet.py` computes the gait-phase spread from the CSV. |

## How to build (editor closed)

```
python3 tools/life/build_deps.py            # pieces this one stands on: cpp, P1 export + city build (2 passes), P4 look (~4 min; own vite :5207, scratch _scratch/life/manhattan)
python3 unreal/WebHomage/Scripts/build_life.py            # prep (vehicle GLBs + IP-clean atlas, lanes / parked / walk data, 20 citizen FBX via P2's exporter in Blender), cpp, content (~50 s), map (~20 s)
python3 unreal/WebHomage/Scripts/build_life.py --steps content,map      # any subset, always in this order
tools/life/build_cpp.sh                     # C++ only (also repairs the stale UnrealEditor.modules manifest, see Gotchas)
docs/night1/life/capture_round.sh docs/night1/life/round-NN [warm|stills|clip|perf]     # every run under gpu_slot.sh
```
`build_life.py` needs `/Game/Tests/City/City_Midtown_Geo`, `/Game/Look/Rigs/Look_Rig_golden` and `/Game/City/Materials/MPC_City` (P1 / P4). The commandlets wait while the number of running Unreal
processes is >= the cap in `_scratch/gpu/slots` (they are `-nullrhi`, no GPU).

## Integration into `/Game/Maps/Manhattan` (integrator)

Add the sublevel `/Game/Tests/Life/Life_Actors` (always loaded) to `Manhattan*` in `build_manhattan.py`'s `add_sublevels`, after the city and the rig. Nothing else: the actors carry their data (lane text, parked list, walk graph, mesh and anim references) as properties, use the same city export coordinates, and follow the player camera for the crowd. The hero does not affect traffic yet.
The C++ under `Source/WebHomage/Life/` must be merged with the branch (new folder, no shared file touched). Command line switches for A/B runs: `-WHLifeOff`, `-WHTrafficOff`, `-WHCrowdOff`, `-WHLifeStats=<seconds>`.

## File map

| Path | What |
|---|---|
| `unreal/WebHomage/Source/WebHomage/Life/` | `WHLifeTraffic`, `WHLifeCrowd`, `WHLifeCamRig`, `WHLifeProbe` |
| `unreal/WebHomage/Scripts/build_life.py` | orchestrator + in-Unreal content / map builder |
| `unreal/WebHomage/Scripts/life_data/` | `lanes.txt` (nodes, links, connectors, conflicts), `parked.txt`, `walk.txt` (generated by `tools/life/export_lanes.mjs` from the browser road code; committed so the build does not need node) |
| `tools/life/` | `export_lanes.mjs`, `prep_vehicles.py` (GLB split + sanitised atlas), `citizens_fbx.py` (P2's exporter redirected), `citizen_variants.py` (2 outfit recolours per citizen), `build_deps.py`, `build_cpp.sh`, `ip_check.py`, `analyze_feet.py`, `spec_table.py` |
| `docs/night1/life/` | this file, `IP_EXCLUSIONS.md`, `capture_round.sh`, `round-01/` (stills, clip, probe logs, perf, spec table, notes) |


## Round 01 results (evidence: `round-01/`)

Spec table `round-01/SPEC_TABLE.md` (probe counts, not YOLO: see its header). Summary at 4K, S1 / S2 cameras, median over 4 reports:

| id | target | measured | |
|---|---|---|---|
| C4 cars (S1) | 5-19, median ~11 | 9 vehicles >= 44 px (8-12); 21.5 incl. small far ones >= 22 px | in range at 44 px |
| C4 people (S1) | 6-32, median ~24 | 15 (12-19) at >= 28 px, 12 (9-13) at >= 56 px | in range, median low |
| S1 parked cars incl. taxis | >= 5 | 12 parked, 1 taxi among them (moving taxis 2-4) | meets |
| C6 vehicles (S2) | median 14-22 | 14 (10-16) at >= 22 px | low edge |
| CH16 people | 8-25 | 15 (12-19) | meets |
| CH17 >= 6 models, no twins | 6 / 0 | 15 looks in frame (12-19), 0 identical looks in all 4 reports of each run | meets in these runs (twins can still appear briefly) |
| CH17 feet | 0 sliding walkers | ankle displacement in planted stances (14 nearest walkers): median 15.7 cm (4K) / 21.7 cm (1080p), 2.2 % / 3.6 % of stances > 45 cm, per-walker medians 12-21 cm | no continuous glide; ankle bone only, not toe-level |
| CH19 gait phases | spread >= 0.2 cycle, >= 6 walkers | 14 walkers, mean pairwise 0.264, max 0.49 cycle | meets |
| C4 traffic lights | >= 1 | P1 heads present, NOT driven | gap |

Instance counts: about 650-710 moving vehicle instances (of which 30-50 % stopped at lights), 1197 parked (140 taxis), 1458 simulated walkers of which about 290 live (skeletal) near the camera; 15 vehicle meshes x 3 LODs, 60 looks.
Sim cost (CPU, game thread): traffic 0.06 ms + instance push 0.08-0.12 ms, crowd 0.17-0.45 ms.

GPU-locked perf (`round-01/PERF_TABLE.md`, exclusive runs, S1 view, NATIVE internal resolution, GPU 0-2 % before each run):

| | frame ms (avg) | GPU ms (avg) | life vs off |
|---|---|---|---|
| 1080p, life off | 22.70 | 20.48 | |
| 1080p, life ON, ray-tracing visible (first build) | 38.77 | 34.74 | +16.1 frame / +14.3 GPU: too expensive |
| 1080p, life ON (default now) | 23.59 | 22.62 | +0.9 frame / +2.1 GPU |
| 4K, life off (run 2; run 1 was 64.43 / 61.72) | 55.38 | 52.64 | |
| 4K, life ON (default now) | 58.09 | 54.64 | +2.7 frame / +2.0 GPU |

The whole cost was the ray-tracing scene (`r.RayTracing=True` + Lumen HWRT): moving ISM instances and skinned meshes force TLAS / BLAS updates every frame. `bVisibleInRayTracing = false` (default on both actors) removes it; the cars and walkers then do not appear in Lumen reflections / GI (they still get direct light, shadows and screen-space effects). Shadows from the life actors cost nothing measurable (24.3 vs 23.6 ms with them off). Crowd only: +1.4 ms frame (CPU, 290 skeletal components), traffic only: about 0. The scene without life is 20 ms GPU at native 1080p, so the 60 fps budget is P4's problem, not P6's.

## Known gaps / next (round 02 candidates)

1. Water (`/Game/Water`): not started (P1 has the far-field water material; boats, waterfront, wakes are in the browser `water.js` / `waterfx/` / `boats.js`).
2. Drive the P1 signal heads from the life clock (`AWHLifeTraffic::GetSignalClock`); crosswalk "walk" lights.
3. People avoid P1 street props (the export has the prop positions), yield to / are yielded to by cars at crosswalks, react to the hero (scatter, look up); cars brake / honk for the hero (browser `playerObstacle`).
4. More than 20 citizen meshes (P2 pipeline) or per-look normal / detail variation; the seam-crack skinning issue of the crowd rig noted in P2's handoff was not re-checked here.
5. Night: headlights / taillights / lit windows through `MPC_City NightK` are wired but not captured (round 01 is golden hour only); the taxi topper and bus screens glow at night.
6. Lane changes, parked-car pull-outs, buses at stops, bicycles, the Broadway diagonals beyond the 2 short links in the region.
7. Perf: instance culling per LOD distance, VSM caching flags for the parked instances, skeletal LODs / URO for the crowd.
8. Integration: add `Life_Actors` to the Manhattan maps (see above); the map keeps the default game mode.

## Gotchas learned

1. **Stale module manifest**: while other agents' editors of this engine run, UBT links `libUnrealEditor-WebHomage-000N.dylib` but sometimes leaves `UnrealEditor.modules` on the old name; the commandlet then dies with "game module WebHomage could not be found". `tools/life/build_cpp.sh` re-points the manifest to the newest dylib.
2. **`Texture2DSample` in a Custom node needs its sampler**: `tAtlas` + `tAtlasSampler`; usage flag `used_with_instanced_static_meshes` must be set on the material asset (a commandlet cannot add it at runtime).
3. **Hidden ISM instances**: park freed instances at (0, 0, -50 m) with scale 0.001. At z = -10 km the distance-field object upload logs "Found precision loss while converting matrix to GPU format" (ensure) every frame.
4. **Interchange glTF**: no materials in the vehicle GLB -> one empty slot per mesh; LODs are separate GLBs merged with `StaticMeshEditorSubsystem.set_lod_from_static_mesh` (needs `Module Load StaticMeshEditor` in a commandlet); UV channels must stay full precision (atlas UV0 and the part id in UV1).
5. **Citizen FBX**: the first import defines the skeleton, the others reuse it; the imported clips are named `Armature_walk` etc. (flatten with the last `_` token).
6. **zsh**: an unquoted `$NAMES` does not word-split and an unmatched glob aborts the command line; the scripts here use Python for lists.
7. **Blender headless**: `--factory-startup`, otherwise the owner's BlenderMCP add-on loads.
8. **Editing a bash script while it runs** shifts the read offset (the capture driver printed `fsize: command not found` after an edit): stop the run first.
