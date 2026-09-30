# P2 Characters: handoff after round 06

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203. Author of round 06: Sonnet 5.5.
Round-05 critic (blind, `critic/round-05-CRITIC.md`): hero model 4, hero animation 5, enemies 5, civilians 4, image quality 3; FAILS. Round-06 target set by the director: **garment integrity and the CH18 seam holes** (zero enclosed key pixels in torso / sleeve silhouettes, no vertex spikes on the olive coat, trousers and hoodie collar, no stretched fingers, proved with 3x crops).

## STATUS AT THE END OF ROUND 06 (read this first)

- **Root cause of every CH18 defect found and fixed in the content pipeline** (below). Verified OFFLINE (numpy proxy of the engine's skinning, same baked crowd matrices, 4 influences): spikes and cracks fall by 70-99 %. Evidence: `round-06/evidence/`.
- **Engine verification is NOT done in this round (see "Blocker")**: no UE launch was possible, so there are no fresh round-06 engine captures. `round-06/captures/` is empty on purpose; nothing in `round-06/` claims an engine result. Run the two commands under "Finish the round" first thing.
- Blocker: from 06:22 to at least 08:30 two `UnrealEditor` processes of other agents (pids 17555 / 17831, state `?E` = exiting, uninterruptible, both `kill -9`-ed mid-render) stayed stuck in the GPU driver. The GPU read 100 % (Renderer / Tiler 100 %) with no engine running, and `gpu_slot.sh` refuses every launch while an engine is stuck exiting (RULES.md, 23:08 kernel panic). Every piece's queue (city, combat, traversal, look, perf and this one) was frozen behind it. I did not bypass the lock and did not touch those processes. If they are still there when you read this, nobody can capture until they clear (a reboot is the owner's call).

## Round 06: what changed

**Root cause (corrects the round-05 diagnosis).** The pack's citizens (`public/assets/city/npc/citizens.bin`) were made by `tools/crowdfit/crowdfit.py` from the raw Tripo meshes (`~/sm2-assets/raw`, listed in `tools/crowdfit/manifest_citizens.json`). The raw meshes are clean: 6-7 k triangles, 100-215 open boundary edges, one 8192 px texture. crowdfit transfers skin weights **per glTF vertex**, and glTF splits vertices at every uv / normal seam, so the two halves of a seam got different weights and were **un-posed (exact inverse LBS) to different places**: the mesh left the pipeline as 3000-4400 open boundary edges of loose shells (round-05 notes). Cracks, sleeve tears, coat flaps, stretched fingers and the black-tee armpit hole are all that. (Round 05 blamed the engine ("weights do not reach the hijabi coat"): wrong. The offline proxy did reproduce the coat flap; it lives on the coat's left side (view yaw 270), which the round-05 probes never rendered.)

**Fix, all in `tools/ue_char/eval/`, run by `prep_all.sh` / `build_characters.py` prep (CPU only, no GPU):**
1. `refit.py NAME...`: repeats crowdfit (orient, pose fit, weight transfer, un-pose) on the raw mesh **with position-welded vertices**, so a seam stays closed; keeps every raw triangle (no decimation) and the raw texture at 2048 px (was a 1024 px atlas tile). Fits are cached (`$P2_SCRATCH/eval/refit/NAME_fit.json`, ~50 s each cold). Output `NAME.npz` + `NAME_tex.png`.
2. `weights_r6.py NAME...`: final weights on the welded vertices: `underlayer.smooth_weights` (touching shells move together), `underlayer.skirt_weights` (+ `opposite_leg_flags`: any triangle joining the left and right leg below the crotch is a coat / dress panel and gets the skirt rig), then **stretch relaxation** (any edge that grows by more than 30 % + 1 cm in a frame of the crowd's own walk / idle clips gets its weights pulled toward its neighbours', repeated until clean). Output `NAME_final.npz`.
3. `citizen_rig.py` / `citizens.py`: when `NAME_final.npz` exists the FBX exporter uses it (refit mesh, final weights, its own 2048 px texture, no expansion, no hull); otherwise (or with `CIT_SRC=legacy`) the round-05 path runs unchanged. **P6 compatibility:** the `SCR = _scr('eval')` line of `citizens.py` is untouched, `tools/life/citizens_fbx.py` still works, and it keeps building legacy citizens unless `P2_SCRATCH` points at a scratch that holds the refit files (run `refit.py` + `weights_r6.py` there first).
4. Cost: citizens are 6.0-6.5 k triangles (round 05: 5 k + 12-14 k hull triangles), 3 k welded vertices, one 2048 px texture each.

**Offline gate (no GPU), same code for both meshes, 18 citizens x (own walk clip + idle) x 8 views, 700 px/m (= native 4K near lane):** `eval_r6.py` (crack = enclosed background component thinner than 7 px whose rim is one limb group and that is not the tip of a natural gap; spikes = triangle edge growth over the crowd clips):

| | round 05 (pack LOD0 + hull + 3 mm expansion) | round 06 (refit) |
|---|---|---|
| cracks (components / px) | 1035 / 42551 | **244 / 13362** (mostly silhouette-edge slivers and ankle rings of 1-3 px) |
| triangles growing > 5 cm in a walk | 2134 | **13** |
| triangles growing > 10 cm | 915 | **0** |
| worst edge growth | 51.5 cm | **5.6 cm** |
| triangles per citizen | 15.7-19.8 k | 5.8-6.5 k |

`round-06/evidence/offline_before_after_proxy.jpg` (coat, hand, armpit, both meshes at the same pose), `offline_citizens_montage_*.jpg`, `offline_ch18_*_eval.json`. These are proxy renders (single-sided ortho raster, flat texel per triangle), NOT engine images; the engine baseline for the same regions is `round-06/evidence/keyreport_round05/` (`key_report.py` on the round-05 key stills: 47 / 31 / 47 / 31 interior holes, the critic's armpit hole is component #6 of crowd_key_a).

**Thug hoodie collar (thug_face_4k): not changed.** Measured on the fitted thug in its own walk (`tools/ue_char/people/thug_probe.py`: hero skeleton FK from `make_walk.build` + the skinfit weights): collar-zone edge growth <= 0.9 cm, no long / thin triangles, no stretched uv. Textured offline views from the front show a clean leather jacket over a hoodie. The dark shapes in the round-05 crop are therefore hood-interior / mask-hem shadow and neck skin + stubble under the mask hem, not stretched geometry. If a critic still calls them shards: lift the lineup `EnemyFill` (0.8 lux, channel 1) or add contact-shadow softening; decide with a 3x crop of the new `thug_face_4k`.

## Finish the round (one build launch + capture groups, all through the GPU lock)

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters
tools/ue_char/prep_all.sh                       # CPU: everything derived (refit + weights + FBX for the 18 citizens are already done in the scratch)
nohup bash tools/ue_char/build_characters_headless.sh '{"steps":"clean,tex,mat,mesh,citizens,rename,abp,map,maps5,mapkey"}' > $P2_SCRATCH/r6/logs/build1.txt &   # ~50 s + queue
tools/ue_char/run_r6_captures.sh $P2_SCRATCH/r6/cap "K C S E H F"                      # K key stills, C crowd movie, S crowd 4K stills, E enemy faces, H hero, F fight (most important first)
python3 tools/ue_char/eval/key_report.py $P2_SCRATCH/r6/cap/crowd_key_*_4k.jpg --out docs/night1/characters/round-06/evidence/keyreport_round06
python3 tools/ue_char/eval/crops_r6.py $P2_SCRATCH/r6/cap docs/night1/characters/round-06/captures/crops_3x --r5 docs/night1/characters/round-05/captures
```
A queued build (pid of `build_characters_headless.sh` in `$P2_SCRATCH/r6/logs/build1.txt`) and a watcher (`$P2_SCRATCH/r6/chain.sh`) were left waiting in the GPU FIFO by this session and are stopped at the end of it (a queued wrapper is not an engine; nothing of ours holds a slot). Expected in-engine result to confirm: `key_report.py` interior holes far below the round-05 47 / 31 / 47 / 31 with none inside a torso or sleeve; the olive coat one piece without the knee flap; fingers five separate wedges; 2048 px texture sharper than round 05. If holes remain, look at them first with `eval_r6.py --imgs` (offline, minutes) before another engine run.

## Commands

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters      # the default (unreal/WebHomage/Saved/P2Build) does not exist: EVERY tool needs this
tools/ue_char/prep_all.sh                                       # every derived input (hero maps + lens, hulls, people + weapons, refit citizens + weights + FBX), no Unreal, no GPU
python3 tools/ue_char/eval/refit.py NAME [NAME ...]              # raw Tripo -> welded rest-pose mesh + weights + 2048 px texture (cached fit)
python3 tools/ue_char/eval/weights_r6.py NAME [NAME ...]         # final weights (STRETCH_REL / STRETCH_ABS / SKIRT_TOPO / SKIRTW / SMOOTHW knobs)
python3 tools/ue_char/eval/eval_r6.py [--legacy] [--imgs DIR] NAME ...   # offline CH18 gate (minutes, no GPU); --legacy = round-05 geometry
python3 tools/ue_char/eval/key_report.py KEY.jpg ... --out DIR   # CH18 in the engine: enclosed key components + 3x crops
bash tools/ue_char/eval/export_citizens.sh NAME ...              # Blender FBX (uses the refit files when present; CIT_SRC=legacy forces the old path)
tools/ue_char/build_characters_headless.sh '{"steps":"clean,tex,mat,mesh,citizens,rename,abp,map,maps5,mapkey"}'   # ~50 s in the GPU lock (+ queue wait)
tools/ue_char/run_r6_captures.sh <out> "K C S E H F"             # capture groups, one capture_r5.sh call each; frame folders removed after cutting
tools/ue_char/capture_r5.sh <out> [MOVIES "H G F C"] [STILLS "gH gF gC gE gK"] [JUMP 1]    # the underlying capture script (ONLY="gC1 gK1" limits still groups)
tools/ue_char/analyze_r5.sh <captures> <evidence>               # cracks.py / count.py / YOLO / head bob / lean / takeoff / key holes / gait phase (needs $P2_SCRATCH/r4/yv)
unreal/WebHomage/Scripts/build_editor.sh                        # after C++ changes (if UnrealEditor.modules keeps the old dylib, point it at the new one by hand)
```
Scripts are bash: in zsh a `$VAR` list is not word-split (use `bash -c` or a script file). Stop an engine only with `/Users/midir/sm2-n1/_scratch/gpu/bin/stop_ue.sh "<worktree abs path>"`.

## File map (what P2 owns)

| Path | What |
|---|---|
| `tools/ue_char/eval/` | **round 06:** `refit.py`, `weights_r6.py`, `cit_proxy.py` (offline engine stand-in: LBS, ortho raster, key holes, spikes), `eval_r6.py`, `key_report.py`, `crops_r6.py`. Round 05 (legacy path, still used as fallback): `underlayer.py` (weights, skirt rig, hull), `citizen_rig.py` (exporter), `crack_probe.py`, `crack_render.py`, `key_holes.py`, `gait_phase.py`, `critic_r04/`, `video_checks.py`, `citizens.py` (FBX exporter; keeps the `SCR = _scr('eval')` line P6's `tools/life/citizens_fbx.py` substitutes) |
| `tools/ue_char/people/`, `weapons/`, `heroanim/`, `hero_suit_r5.py`, `hero_lens_r5.py` | enemies, weapons, hero clips / suit / lens (unchanged this round) |
| `tools/ue_char/capture_r5.sh`, `run_r6_captures.sh`, `analyze_r5.sh`, `ue_wait.sh` | capture / analysis / launch wait (`ue_wait` counts real `UnrealEditor` processes only) |
| `unreal/WebHomage/Source/WebHomage/Characters/` | sequence idle, jump variants, phase seed, director visibility (unchanged) |
| `unreal/WebHomage/Scripts/build_characters.py` | maps `Char_Hero`, `Char_Fight`, `Char_Crowd`, `Char_CrowdKey`, `Char_Lineup`, ABPs, 18 citizens; prep step now also runs refit + weights |
| `docs/night1/characters/round-06/` | `evidence/` (offline gate, before / after proxy, engine baseline key reports); `captures/` empty until the engine runs |

## Local-only binaries (nothing below is committed; all regenerable from `~/sm2-assets/raw` + the repo)

- `unreal/WebHomage/Content/{Characters,Tests/Characters}`; `art/night1/characters/**/*.png, *.fbx` (citizen FBX + 2048 px basecolors already regenerated from the refit, `git ignore`d).
- `/Users/midir/sm2-n1/_scratch/characters/`: `ueimport/`, `eval/refit` (NAME.npz, NAME_final.npz, NAME_fit.json, NAME_tex.png), `eval/hull`, `eval/tiles`, `r4/yv` (ultralytics venv), `r5/`, `r6/` (offline proxy renders, eval runs, logs, `cap/` for the captures).
- `DerivedDataCache/`, `Intermediate/`, movie frame folders: deleted at the end of a round (none were created this round: no engine launched).

## Gotchas

1. **Render every side.** The offline probes of round 05 viewed the citizens from one side only and declared the coat coherent; the flap was on the other side. `eval_r6.py` uses 8 yaws per frame.
2. **Weld before you weight, weld before you un-pose.** glTF vertices are split at uv / normal seams; anything per-vertex (weights, un-pose, smoothing) must run on position-welded vertices and be copied back (`refit.py`, `weights_r6.py`).
3. A crack metric must not count the air between an arm and the torso, the tip of a wedge, finger gaps or hair (`cit_proxy.classify_holes`: rim in one limb group and not attached to a wide gap). `key_holes.py` (engine) counts them all: read its crops; `key_report.py` separates silhouette slivers (edge distance <= 3 px) from interior holes.
4. Never edit a shell script that a running bash is executing in place (bash reads it incrementally): write a temp file and `mv` it over.
5. The GPU queue is the schedule: every UE launch waits in the FIFO separately; a stuck-exiting engine of anyone freezes the whole queue. `run_game.sh` `kill -9`s its engine on `-timeout`: always pass a generous timeout (capture_r5.sh does: 3000 / 3600 s) and stop engines with `stop_ue.sh`.
6. `build_characters.py` step `mapkey` duplicates `Char_Crowd` before keying it (it deletes an existing `Char_CrowdKey` first). `clean` wipes `Content/Characters` and `Content/Tests/Characters` on disk: it needs every art input present (they are, in `art/` and the scratch).
7. The 4K real-time still groups and the movies do not share a clock (director clock drifts ~1.5 s at 5 s): compare defects, not frames, between runs.
8. Earlier gotchas that still hold: `UnrealEditor.modules` can keep pointing at a deleted dylib after `build_editor.sh`; `capture_r5.sh` must be executable; masks: only the outermost shell is draped; hero and thug clips share one skeleton.

## Next steps (in order)

1. Finish the round (commands above), then judge the crops: coat, hand, armpit, trousers, collar (`crops_r6.py` puts round 05 and round 06 side by side).
2. If interior key holes remain: they are small ankle / cuff rings and 1-3 px slivers offline; cap them with a bridge strip between facing boundary loops (`tools/ue_char/eval/boundary_loops.py` lists the welded boundary loops: shoe collar / trouser cuff) rather than the old hull.
3. Refit the 2 citizens not in the crowd (`07_black_graphic_tee`, `11_graphic_tee_bonnet`) only if P6 wants them (the manifest has them).
4. Secondary (round-05 critic): original suit design (IP), one closed lens rim, crowd avoidance + arms hanging at 5-10 deg, fight hit reactions / knockdowns, masks with drape (no lip read). None was touched in round 06.

## Known problems

- Engine verification of round 06 pending (blocker above).
- The hero suit design (white spider on the chest, blue legs with red stripes) is still the open brand flag: owner decision, unchanged.
- Hijabi coat: a few hem edges still grow up to 5.4 cm in a stride, and the jeans can show through the coat hem at full stride (the coat follows the thighs at 60 %).
- Citizens are low-poly (6 k triangles): fingers are five faceted wedges, arms are 10-12 sided tubes; smooth normals hide most of it, the silhouettes do not.
- Performance is not measured (no engine; shared GPU otherwise).

## No copied IP (owner rule)

Enemies and civilians: the owner's own Tripo generations (`~/sm2-assets/raw`) and the browser game's own crowd rig; weapons are generic primitives with procedural wear, no lettering. No reference image or footage is committed.
