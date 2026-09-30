# P2 Characters: handoff after round 07

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203. Author of round 07: Sonnet 5.5.
Round-06 critic (blind, `critic/round-06-CRITIC.md`): hero model 4, hero animation 5, enemies 5, civilians 4, image quality 4; FAILS on the crowd. **Round-07 target (director):** walker avoidance (capsule radius >= 0.35 m), fix the key see-through, re-capture `crowd_key_c_4k` / `crowd_key_a_4k`: zero pixels G>R+40 inside a garment, no two walker masks overlapping across `crowd_tracking` at 60 fps, no detached polygon > 4 px, close the 3 ankle-cuff gaps, prove with 3x crops.

## STATUS AT THE END OF ROUND 07 (read this first)

- **Everything is committed and pushed** (last commit on `night1/characters`: "P2 characters r07 ..."). Nothing is running, nothing is queued; no engine of mine is alive. `Content/Characters`, `Content/Tests/Characters` are local rebuilt copies (no `.uasset` / `.umap` committed). Worktree `Intermediate/` is 831 MB (kept: rebuilding it costs ~3 min), `DerivedDataCache/` 0 B. Scratch: `/Users/midir/sm2-n1/_scratch/characters/` (frame folders removed).
- **Results, all measured in the real game (numbers: `round-07/SPEC_CHECK.md`, provenance: `round-07/CAPTURES.md`):**
  - 3D separation from the engine's own telemetry: smallest centre distance **130.0 cm over all 899 frames** of the `-movie` run the crowd clips are cut from (0 frames below 0.70 m). The same walkers on the round-06 (colliding) lanes: **avoidance off = 10 cm, 470/899 frames below 0.70 m; avoidance on = 80.4 cm, 0 frames.**
  - Key: `G>R+40` citizen pixels in the four stencil-keyed stills **181-185 px (1-px fringe) in three, 1,737 px (a teal tank top) in `_wide`; 0 green-dominant; 0 detached polygons** (round 06: 210-309k px, because the green-street key tinted every garment). The enclosed-gap census (46 components) is all air between limbs / walkers, no hole through cloth.
  - **Not claimed:** "no two silhouettes ever touch on screen". A side-on two-way flow at this density always has depth occlusion: median 4 touching silhouette pairs per frame in the tracking shot (id movie). The 3D intersection is 0.
- **Critic pack is built:** `/Users/midir/sm2-n1/_scratch/critic-P2-r07/pack` (19 pairs, key outside at `pack.key.json`, pairs in `round-07/critic_pairs.json`): the standard reference pairs + round 06 vs round 07 (crowd clip, still, key a / c, avoidance demo vs the round-06 clip, four 3x-crop pairs). The verdict goes to `round-07/CRITIC.md` and `critic/round-07-CRITIC.md` (not written yet).

## What changed in round 07 (the four findings worth knowing)

1. **Avoidance in C++** (`Source/WebHomage/Characters/WHCharLoopWalker.*`): `bAvoid`, `AvoidRadius` 40 cm; the whole group is stepped once per frame by the first walker that ticks (order independent, fixed sort by actor name); each walker picks the sideways offset (5 cm grid, +-260 cm, right-hand bias) that keeps its capsule clear of everybody's predicted capsules at 0 / .5 / 1 / 1.5 / 2 s, rate limit min(55 cm/s, 0.47 x speed), then a hard 2R + 0.5 cm relaxation. `-WHWalkerLog=<csv>` writes frame, time, label, x, y, yaw, offset, min pair distance for every walker every frame; `-WHNoAvoid` = baseline. `tools/ue_char/crowd/avoid_sim.py` is an offline copy of the same algorithm (reproduces the engine telemetry to 0.01 cm); `layout_search.py` searches lane layouts (`MID7` / `NEAR7` in `build_characters.py`: >= 130 cm for 2 s beyond both shots, near lane one way). `Char_CrowdAvoid` (step `mapavoid`, needs `maps5`) = the round-06 lanes with avoidance on.
2. **The key was the bug, not the meshes.** Round 05/06 painted the street green; Lumen bounce + the sky capture tinted every garment ("key-green jeans" = solid jeans). `Char_CrowdKey` (step `mapkey`) is now `Char_Crowd` with custom-depth stencil on the citizens and a post-process material `M_PP_Key` **before bloom with the material's own stencil test == 0** (UE 5.8 cannot read custom stencil after tonemapping: smeared 90 px border, no key). Bloom / vignette are off in that map. `Char_CrowdID` + `M_PP_KeyID` = per-walker id colours (`evidence/stencil_ids.json`). Needs `r.CustomDepth 3` (capture_r5.sh `gK` / `gI` pass it). Key stills are PNG (JPEG bleeds the key into edges).
3. **Stage bug: the mid lane stood 15 cm inside the pavement** (sidewalk box 30 cm thick centred on z = 0). Mid-lane walkers now spawn at z = 15 cm. This was the real cause of the "ankle-cuff gaps" (the floor plane slicing through the foot); the offline mesh checks could not reproduce them, which gave it away. Custom stencil ignores scene occlusion (a buried foot keeps its stencil): do not trust a stencil mask for occluded geometry.
4. Ankle skin gradient across the ankle joint (`weights_r6.py` `ankle_blend`); an inner "liner" sleeve was tried and dropped (it never became visible offline).

## Commands

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters      # EVERY tool needs this
tools/ue_char/prep_all.sh                                       # derived inputs incl. refit citizens + weights + FBX (no Unreal)
tools/ue_char/build_characters_headless.sh '{"steps":"clean,tex,mat,mesh,citizens,rename,abp,map,maps5,mapkey,mapavoid"}'   # full rebuild ~70 s in the lock; '{"steps":"maps5,mapavoid,mapkey"}' = maps only (deletes the old key / id umaps first)
unreal/WebHomage/Scripts/build_editor.sh                        # after C++ changes (20-30 s)
tools/ue_char/run_r7_captures.sh <out> "T K I C A D S E H F"   # T telemetry (nullrhi) K key stills I id stills C crowd movie A avoidance demo D id movie S crowd stills E faces H hero F fight
tools/ue_char/crowd/key_movie.sh <out> [quit_s]                 # 4K fixed-step key frames (pick a frame by number; frame numbers line up with the id movie)
tools/ue_char/trim_clips_r7.sh <captures>                       # warm-up trim of the first clip of each run
tools/ue_char/analyze_r7.sh <captures> <evidence>               # telemetry / key / spikes / id overlap / YOLO (CPU)
tools/ue_char/assemble_r7.sh <captures> <evidence>              # copy into docs/night1/characters/round-07
python3 tools/ue_char/crowd/telemetry_check.py CSV --out DIR    # separation per frame
python3 tools/ue_char/eval/key_check_r7.py STILL.png ... --out DIR ; key_components_r7.py (montages) ; crops_r7.py (3x crops)
python3 tools/ue_char/make_pairs_r7.py <r07 captures> <r06 captures> <crops> <pairs.json>; python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py <pack> <pairs.json>
```
Scripts are bash: in zsh a `$VAR` list is not word-split (use `bash -c` or a script file). Stop an engine only with `/Users/midir/sm2-n1/_scratch/gpu/bin/stop_ue.sh "<worktree abs path>"`; count engines with `pgrep -x UnrealEditor`. macOS has no `timeout`; the tool shell blocks `sleep` > ~30 s (use an until-loop).

## File map (what P2 owns)

| Path | What |
|---|---|
| `tools/ue_char/crowd/` | **round 07:** `avoid_sim.py`, `layout_search.py`, `telemetry_check.py`, `run_telemetry.sh`, `id_movie.sh`, `id_overlap.py`, `key_movie.sh` |
| `tools/ue_char/eval/` | **round 07:** `key_check_r7.py`, `key_components_r7.py`, `crops_r7.py`, `ankle_gap.py`, `ankle_sliver.py`, `island_drift.py`; round 06: `refit.py`, `weights_r6.py` (+ ankle), `eval_r6.py`, `cit_proxy.py`, `key_report.py`, `spike_key.py`, `leap_track.py`, ... |
| `tools/ue_char/` | `run_r7_captures.sh`, `capture_r5.sh` (gK / gI / A), `analyze_r7.sh`, `assemble_r7.sh`, `trim_clips_r7.sh`, `make_pairs_r7.py`, `build_characters_headless.sh`, `ue_wait.sh` |
| `unreal/WebHomage/Source/WebHomage/Characters/` | walker (avoidance + telemetry), sequence idle, jump variants, phase seed, director visibility |
| `unreal/WebHomage/Scripts/build_characters.py` | maps `Char_Hero`, `Char_Fight`, `Char_Crowd` (`crowd_map()`), `Char_CrowdAvoid`, `Char_CrowdKey`, `Char_CrowdID`, `Char_Lineup`, ABPs, 18 citizens |
| `docs/night1/characters/round-07/` | `captures/` (clips, stills, `crops_3x/`), `evidence/`, `CAPTURES.md`, `SPEC_CHECK.md`, `critic_pairs.json` |

## Gotchas (new in round 07; the older ones below still hold)

1. **PP materials and stencil:** custom stencil is unreadable after tonemapping; use `enable_stencil_test` + `BL_SCENE_COLOR_BEFORE_BLOOM`. Python enum names differ from C++ (`unreal.BlendableLocation.BL_SCENE_COLOR_BEFORE_BLOOM`, `MaterialStencilCompare.MSC_EQUAL`): the build script discovers them by substring and logs the list.
2. The build pipeline (`... | grep | tail`) can hang after the commandlet exits when another agent's UnrealTraceServer inherits the pipe; the files are already saved: check `characters_build.log` for "Char_CrowdID saved" and kill your own pipeline by PID (never by pattern).
3. `DuplicateAsset` cannot overwrite an existing map inside the commandlet: `build_characters_headless.sh` now removes the old key / id umaps first. Two `new_level` calls in one second collided on the temp name: fixed with a counter.
4. **Never edit a shell script a running bash is executing** (I had to restart a driver because of it), and never `pkill -f` a generic name (see the incidents).
5. Real-time stills and `-movie` runs do not share a clock (IoU of the same still in two real-time runs 0.64-0.84); pick stills from a fixed-step movie by frame number when it matters.
6. The queue: other agents' exclusive perf runs held the GPU lock up to 20 min per launch; batch launches (each capture group is one or two).
7. Earlier gotchas still hold: render every side, weld before weighting, a key-still hole count is not a crack count, movies start with low mips for ~0.4 s (trim), `UnrealEditor.modules` can point at a deleted dylib after `build_editor.sh`, masks drape only the outermost shell, hero and thug clips share one skeleton.

## Incidents to disclose (nothing left running)

- While replacing a waiting build I ran `pkill -f "ue_wai[t].sh"`, which matches EVERY agent's `ue_wait.sh`: if another agent's queued `ue_wait.sh` was polling at that moment, that poll was killed (its `gpu_slot.sh` launch still enforces the cap; nothing crashed that I saw). Afterwards I only used explicit PIDs.
- Another agent's UnrealEditor run auto-spawned `UnrealTraceServer` (TCP 1981 / 1989 listeners) during my builds: the editor does this by itself; I never launched it or Insights; no system dialog appeared.
- Two of my own queued `gpu_slot.py` wrappers (waiting, no engine child) were SIGTERM / SIGINT-ed after I cancelled their runs; no engine of mine was ever killed.

## Next steps (in order)

1. Read the blind critic's verdict on the round-07 pack (`round-07/CRITIC.md`); write `critic/round-07-CRITIC.md`.
2. If the critic still counts screen-space masks: the layout search with a heavy overlap weight (`layout_search.py --dmin 8.5 --ovw 5 --flip`) halves the touching pairs at the price of density (8.5 people); decide with the director, it cannot reach zero.
3. Secondary (round-06 critic): original suit design (IP; owner decision), one closed lens rim, fight hit reactions / knockdowns, masks with drape, hood-interior shadow wedge, arms hanging ~30 deg out, the coat walker's rear foot flicking to knee height, crowd density >= 16 (needs more than 18 distinct citizens: twins are forbidden by CH17).
4. Refit the 2 citizens not in the crowd (`07_black_graphic_tee`, `11_graphic_tee_bonnet`) only if P6 wants them.

## Known problems

- Screen-space contact between walkers (median 4 pairs per frame); the near lane is a one-way stream (up to 4 people within 1.5 m).
- The hero suit design (white spider on the chest, blue legs with red stripes) is still the open brand flag: owner decision, unchanged.
- Citizens are low-poly (6 k triangles): faceted fingers, 10-12-sided arm tubes; the kurta man's kicked-up rear leg shows a crumpled trouser tube.
- Hijabi coat: a few hem edges grow up to 5.4 cm in a stride.
- Performance is not measured (shared GPU, contaminated capture slots).

## No copied IP (owner rule)

Enemies and civilians: the owner's own Tripo generations (`~/sm2-assets/raw`) and the browser game's own crowd rig; weapons are generic primitives with procedural wear, no lettering. No reference image or footage is committed (the critic pack lives in `_scratch`, references stay in the private `~/spiderman-learnings`).
