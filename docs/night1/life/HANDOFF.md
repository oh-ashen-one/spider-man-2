# P6 City life: handoff after round 02 (traffic, crowd, signals; water not started)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe. See `DISCLAIMER.md`.

Branch `night1/life`, worktree `~/sm2-n1/life` (integration `Opus-5.5-Loop-Night-1` merged in at e0ada6c). UE MCP port 8776 (not used: everything is headless commandlets + `-game`), dev port 5207.
Owned: `/Game/Life`, `/Game/Tests/Life`, `unreal/WebHomage/Scripts/build_life.py`, `unreal/WebHomage/Scripts/life_data/`, `tools/life/`, `docs/night1/life/`, and (flagged for the integrator)
`unreal/WebHomage/Source/WebHomage/Life/` (new folder in the shared module: no Build.cs / .uproject / Config change was needed).
Scratch: `/Users/midir/sm2-n1/_scratch/life/` (capture frames, logs, venv with ultralytics for the detector). No `.uasset` / `.umap` is committed: `build_life.py` recreates everything.
Round 02 was interrupted once by the 23:08 kernel panic (the WIP was committed) and resumed; every engine launch of the resumed run went through `gpu_slot.sh` (waits of 10-25 minutes per run are normal while other pieces capture).

## The one thing the next builder should know first

Round 01's critic FAILED the piece on pedestrian density (2/10: 4 people in the street clip, twin heads, blank signal heads, no queue, no swing-height clip). Round 02 fixed exactly that and measured it with the SPEC detector, not with the engine probe (the round-01 probe counted tiny far figures that the detector never sees, so its "meets" was too generous). The blind critic pack for round 02 is `_scratch/critic-P6-r02/pack` (key outside it in `pack.key.json`). Wait for its verdict before starting anything new; the likely next gaps are listed under "Known gaps".

## What round 02 built (delta on round 01; round 01 systems are unchanged unless said)

| system | round 02 change |
|---|---|
| Crowd (`AWHLifeCrowd`) | **Camera-centred population**: 1461 walkers exist inside a 130 m disc around the camera (`PerKmAvenue 1300`, `PerKmStreet 860` walkers per km of sidewalk edge, was 950 / 640 over the whole block); walkers that fall behind are recycled to the far edge of the disc out of view, a camera jump repopulates. Only walkers inside the view cone (+30 deg) or within 22 m get a skeletal mesh (about 500-550 live at the S1 camera, pool of 6 per look x 100 looks = 600 components). **Sidewalk bands** (`AvenueBandMin/Max`, `StreetBandMin/Max`): people walk on the building side of the curb strip where P1 puts trees / lamps / bins. Personal space around a street-level camera (walkers step around it). **Looks**: 20 citizens x 5 = 100 looks (`tools/life/citizen_variants.py`: clothes hue, hair / beard colour through the head masks of `citizen_headmask.py`, skin tone, and the pink head coverings of citizens 17 / 20 recoloured per variant). The look is chosen at assignment: not worn by a live walker within 45 m (weight 1000) / 90 m (100), a different citizen mesh than walkers within 30 m where possible; identical looks on screen are swapped for the farther walker (never nearer than 30 m). |
| Signals (`AWHLifeTraffic::BuildSignals`) | `life_data/signals.txt` (37 P1 masts / posts, `tools/life/export_signals.py`) -> 246 lens instances: flat emissive discs (engine cylinder mesh, `M_LifeSignal`) drawn over P1's unlit heads, red / amber / green from the shared 40 s clock. The crowd waits at crosswalks on the same clock. |
| Traffic | density 2.3 x browser (`SM2_LIFE_DENSITY`), queue at the lights with per-driver reaction time after green (`ReactionMin/Max`), buses / tour buses 7 % of the avenue curb lane, `CameraClearM` (a street-level camera is never inside a car: cars whose body is within 1.8 m of it are not drawn), `-WHLifeClearAhead=<m>` (fixed shots: no moving car in a corridor ahead of the camera; the S1 stills use 12 m because the S1 camera stands in a lane and a box truck arrived on its frame at t = 28 s in the first capture). |
| Test maps | new `Life_Swing_Clip` (30 m over the avenue centre line, 25 m/s), `Life_Signal_Clip` (fixed camera 7.5 m up, queue at the street-160 signal, `-WHLifeSignalPhase`), `Life_Street_Clip` (walking camera, 1.8 m eye). `AWHLifeCamRig` holds 2.5 s at the start pose (Lumen / TSR / exposure warm-up) and `capture_round.sh` trims those frames, so frame 0 of every clip is lit (round 01's frame 0 was dark, luma 27). |
| Probe | `WH_LIFE_SAMPLE` lines: unoccluded vehicles / people in frame, distinct and repeated looks (30 m / 60 m), lane motion, queue on a link (`-WHLifeQueue=`), junction-box stops, foot log window (`-WHLifeFoot=from:to`). |
| Tools | `tools/life/detect_counts.py` (the SPEC instrument: YOLO11x-seg, conf 0.35, imgsz 1920, person + vehicle classes, on stills and clips, 0.5 s sampling; needs `_scratch/life/venv` and `_scratch/city/yolo/yolo11x-seg.pt`; run with `--device cpu` when the GPU is busy), `spec_table.py` (SPEC_TABLE.md from detector.json + probe lines), `clip_strip.py` (contact strip + frame-0 luma), `perf_table.py`. |

## How to build and capture (editor closed)

```
python3 tools/life/build_deps.py                      # only if P1 / P4 content is missing (cpp, P1 export + city build, P4 look; ~4 min)
python3 unreal/WebHomage/Scripts/build_life.py        # prep + cpp + content (~60 s) + map (~20 s); or --steps content,map
tools/life/build_cpp.sh                               # C++ only (repairs the stale UnrealEditor.modules manifest)
python3 tools/life/citizen_variants.py $SM2_LIFE_CIT/fbx   # only when the variant recolours change (PIL, no Blender); then --steps content,map
docs/night1/life/capture_round.sh docs/night1/life/round-NN [warm stills clips clip_street clip_swing clip_signal detect perf]     # every run under gpu_slot.sh
VIEWS=S1 docs/night1/life/capture_round.sh docs/night1/life/round-NN stills clip_street          # subsets; VIEWS limits the stills to a view
docs/night1/life/perf_variants.sh <round dir> 3840x2160 off:-WHLifeOff on:                        # exclusive GPU-locked runs, r.ScreenPercentage 67
```
Detector, tables (CPU, no GPU lock needed): `python tools/life/detect_counts.py --device cpu --json <round>/detector.json <stills> <clips>`, `python3 tools/life/analyze_feet.py <round>/feet_clip.csv --json <round>/feet_analysis.json`, `python3 tools/life/spec_table.py <round>`.
Command line switches: `-WHLifeOff`, `-WHTrafficOff`, `-WHCrowdOff`, `-WHLifeStats=<s>`, `-WHLifeSample=from:to:step`, `-WHLifeClearParked=x0:z0:x1:z1`, `-WHLifeClearAhead=<m>`, `-WHLifeSignalPhase=<s>`, `-WHLifeQueue=<link,link>`, `-WHLifeFoot=from:to`.

## Integration into `/Game/Maps/Manhattan` (integrator)

Add the sublevel `/Game/Tests/Life/Life_Actors` (always loaded) to `Manhattan*` in `build_manhattan.py`'s `add_sublevels`, after the city and the rig. The actors carry their data as properties, use the P1 export coordinates and follow the player camera for the crowd (the population is camera-centred, so the cost is bounded wherever the hero goes). The C++ under `Source/WebHomage/Life/` must be merged with the branch (new folder, no shared file touched). The hero does not yet affect traffic or the crowd.

## File map

| Path | What |
|---|---|
| `unreal/WebHomage/Source/WebHomage/Life/` | `WHLifeTraffic`, `WHLifeCrowd`, `WHLifeCamRig`, `WHLifeProbe` |
| `unreal/WebHomage/Scripts/build_life.py` | orchestrator + in-Unreal content / map builder (actor properties are set here; see gotcha 1) |
| `unreal/WebHomage/Scripts/life_data/` | `lanes.txt`, `parked.txt`, `walk.txt`, `signals.txt` (generated by `tools/life/export_lanes.mjs` / `export_signals.py`, committed so the build does not need node) |
| `tools/life/` | build / export / analysis tools (see above) |
| `docs/night1/life/` | this file, `SHOTLIST.md`, `IP_EXCLUSIONS.md`, `capture_round.sh`, `perf_variants.sh`, `round-01/`, `round-02/` |

## Round 02 results (evidence: `round-02/`; SPEC instrument = detector; internal resolution native, `r.ScreenPercentage 100`, 1080p and 3840x2160 output)

Detector numbers (`round-02/SPEC_TABLE.md`, `detector.txt`). References measured with the same detector: sidewalk still 28 people, avenue-hero-taxis 6 people / 10 vehicles, midtown-high 1 / 27, intersection-high 39 / 24, street-npcs clip median 8 people, swing-avenue-traffic clip median 14 vehicles (p90 24).

| id | target | round 01 | round 02 |
|---|---|---|---|
| People, S1 street view (5 stills t = 12-28 s) | >= 16 median (critic); SPEC 6-32, ~24 | 4-6 | **27** (24-30); published stills 30 / 30 |
| People, street clip (18 s, 36 samples) | >= 16 median (critic); SPEC 8-25 | 4 (p10 0, p90 6) | **19** (p10 17, p90 22) |
| Vehicles, S1 | 5-19, ~11 | 5-9 | 11 (10-11) |
| Vehicles, swing clip (10 s, 30 m over the avenue, 25 m/s) | >= 14 (critic); ref 14 | none supplied | **17** (p10 12, p90 21) |
| Vehicles, S2 still series (5 times) | 14-22 | 13 (1080p) / 7 (4K) | 13 (12-19), published stills 14 / 16: **at the low edge** |
| Signal queue (`probe_signal.txt`) | queue of >= 3 stops at red, pulls away on green, nobody stopped in the box | signals unlit, no queue | 3 cars in each southbound lane stand at the line (front 0.7-0.8 m), red until clip t = 7 s, first car moves at 8 s, front car crosses the line at 9 s; junction-box stops 0 |
| Lit signal heads | >= 1 | blank | 246 lenses lit from the clock (`signal_clip_1080p60.mp4`, S1 far mast) |
| Twin looks (`probe_*.txt`) | no repeated head in a frame | twin bearded head in S1 4K | 100 looks; a twin pair within 30 m in 8 of 41 S1 samples (max 2 pairs), 0 of 36 street-clip samples, 0 of 25 signal-clip samples; more than 100 people within 60 m still repeat looks beyond 60 m |
| Gait phases (14 walkers, street clip) | mean pairwise phase spread >= 0.2 cycle | 0.264 | 0.262 (max 0.487, R 0.121) |
| Feet (planted-stance ankle displacement, 14 nearest, 60 fps movie for the clip) | no continuous glide | clip median 33.1 cm, 20.8 % > 45 cm | clip median 33.5 cm, **9.0 % > 45 cm** (p95 47.6); S1 4K 20.7 cm (1.3 %), S1 1080p 30.4 cm (6.4 %). The ~20-25 cm heel-toe roll is the floor; ankle bone only |
| Clip frame 0 lit | luma ~76 | 27 | 82 / 98 / 89 (street / swing / signal) |
| IP text check | 0 hits | 0 | 0 (`round-02/ip_check.txt`) |

Sim cost (CPU, game thread): traffic 0.0-0.25 ms + instance push 0.1 ms, crowd 0.2-0.7 ms (1463 walkers, 470-550 live).

GPU-locked perf: PERF_PLACEHOLDER

## Known gaps / next (round 03 candidates)

1. **Water** (`/Game/Water`): not started (P1 has the far-field water material; boats, waterfront, wakes are in the browser `water.js` / `waterfx/` / `boats.js`). The water A/B pieces are separate worktrees.
2. The near 12 m ahead of the S1 camera is empty by construction (`-WHLifeClearAhead`); a real hero standing in a lane needs cars that brake / honk for the hero (browser `playerObstacle`), people that step aside and look up.
3. Vehicle mesh quality (blobby minivan, flat oversized windshield on the van, fuzzy white convertible atlas): the browser's low-poly models; needs Blender remodelling of the 3-4 worst types. More body types (bicycles, motorbikes, delivery scooters).
4. S2 vehicle count is at the low edge (median 13 in the still series; the 10 s swing clip is 17). `SM2_LIFE_DENSITY` 2.3 -> 2.6 would lift it but also S1 and the perf cost (re-measure).
5. Pink / magenta / lime accents in the crowd are the hue-shifted clothes of dark citizens; a fifth of the atlas could use a desaturated palette. Crowd is still 20 meshes (P2 pipeline for more).
6. Foot planting is measured on the ankle bone only; toe-level and IK planting are not done. Seam-crack skinning of the crowd rig (P2 note) not re-checked.
7. Night (headlights / taillights / lit windows through `MPC_City NightK` are wired, not captured), lane changes, parked-car pull-outs, buses at stops, the Broadway diagonals beyond 2 short links.
8. The ray-tracing switch (`bVisibleInRayTracing = false`, round 01) means cars / walkers are absent from Lumen HWRT reflections / GI; revisit when P4 decides the final RT settings.
9. In the S1 view a soft green-white glow smear hangs over the road centre (also in the round-01 stills, before any signal lens existed) and a green tint sits on a P1 litter bin: neither comes from the life actors; report to P1 / P4.

## Gotchas learned

Round 01 gotchas 1-8 still hold (stale module manifest -> `tools/life/build_cpp.sh`; `Texture2DSample` needs its sampler + `used_with_instanced_static_meshes`; hidden ISM instances park at z = -50 m, scale 0.001; Interchange glTF has no materials / LODs are separate GLBs; citizen FBX first import defines the skeleton; zsh does not word-split an unquoted `$NAMES`; Blender `--factory-startup`; do not edit a bash script while it runs). New:

1. **Actor properties equal to the C++ default are not saved in the map.** `build_life.py` sets `per_km_avenue` etc. explicitly, but a value equal to the class default at save time is not serialised, so changing a C++ default silently changes every already-built map. Keep the script's values and the header defaults identical (round 02: 1300 / 860, `num_variants` 5, `pool_per_model` 6) and rebuild the map when they change.
2. **`build_life.py` waited on a wrong process count**: `pgrep -f 'MacOS/UnrealEditor( |$)'` also matches the queued `gpu_slot.py` wrappers of other agents (their argv carries the path). It now counts `pgrep -x UnrealEditor` (real engines).
3. **`pgrep -f` / `pkill -f` patterns match your own shell** when the pattern text is in the command line (a background `until pgrep -f "build_life.py"` wait loop matched itself and ran until its 10 minute limit). Use a bracket pattern `[b]uild_life`, or poll a log line.
4. **A queued `gpu_slot.sh` job can be cancelled safely while it is still `wait phase=queue`** (kill your driver script first, then its `gpu_slot.py` wrapper; no engine exists yet). Never do that once `run child_pid=` is logged: let the run finish or use `stop_ue.sh`.
5. **The signal queue depends on the pre-roll**: `-WHLifeSignalPhase` changes the whole 75 s warm-up trajectory, not just the light phase. Phase 30.5 leaves 3 cars in each southbound lane at the line (clip t = 0), phase 33.5 left a single car in one lane. Re-check `probe_signal.txt` after touching the phase, the pre-roll, the density or the seed.
6. **The foot log at 60 fps (`-movie`) reads about 10 cm higher than the real-time stills** because the heel-toe roll is sampled densely; compare clip to clip and still to still.
7. **The spec's 84 % centre crop in `abpack.py`** removes people at the frame edges (the crowd is on the left in the street clip): measure the clip after `crop=iw*0.84:ih*0.84` before claiming a margin (round 02: median 18 after the crop vs 19 before).
8. Queue waits: each `gpu_slot` capture waited 10-25 minutes behind other pieces' runs; a full round of captures took about 2-3 hours of wall clock. Batch everything that changes the build into one rebuild before capturing.
