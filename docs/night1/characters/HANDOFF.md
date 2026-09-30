# P2 Characters: handoff after round 05

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203. Author of round 05b: Sonnet 5.5 (resumed the interrupted Opus 5.5 round; nothing was restarted).
Round-04 critic (blind, `critic/round-04-CRITIC.md`): hero model 4, hero animation 5, enemies 4, civilians 3, image quality 3; FAILS (avg 3.8). Biggest gaps: (1) CH18 seam cracks on civilians, (2) enemies as combatants (CH11 / CH12 / CH14), (3) suit quality. Round 05 worked on those three plus the secondaries. Evidence: `round-05/` (`CAPTURES.md`, `SPEC_CHECK.md`, `captures/`, `evidence/`). The round-05 blind critic pack is in `~/sm2-n1/_scratch/critic-P2-r05/` (not committed); its verdict goes to `critic/round-05-CRITIC.md`.

## Round 05: what changed

**1. CH18 (civilians): three levels, all in `tools/ue_char/eval/`, run by `prep_all.sh` / `export_citizens.sh`.**
The 18 shipped crowd citizens (`public/assets/city/npc`, 5000 triangles) are shredded garment shells (3000-4400 open boundary edges each: pockets, lapels, hems are separate overlapping pieces).
- *Weights* (`underlayer.py`): `smooth_weights` (abutting shells share weights over 14 mm) and **`skirt_weights` (new, 05b)**: every garment vertex below the hips that hangs free of the legs (farther than 12.5 cm from the nearest leg axis, or closer but with another layer under it: ray test 25 cm) gets a position-only rig (thigh L / R by side, `tanh(x / 8 cm)`, scaled by depth below the hip line up to 0.6, rest on the hips bone). Every panel at the same place has the same weights, so coat tails / skirts move as one piece instead of tearing into strips and flaps behind the trailing leg. `final_weights()` is the one entry point (Blender FBX export, hull skinning and the offline probes all call it).
- *Under-layer hull* (`underlayer.py`, appended to every citizen mesh): 2 iso-surfaces 4 mm and 12 mm under the cloth (numpy surface nets), each triangle coloured by the outermost cloth above it (one uv per triangle, same material). 05b changes: **`fill_small_holes`** (a patch of hull with no cloth above it, diagonal < 12 cm and enclosed by kept hull, is kept and its interior vertices re-placed on a harmonic membrane: pocket cut-outs / missing panels show cloth colour, not the street), **cross-group triangles dropped** (a triangle whose corners belong to two limb groups bridges a joint: it was the spiky skin / cloth webs at every armpit), **`prune_stretched`** (any hull triangle whose edge grows > 2.6 x + 6 mm in a sampled frame of the walk / idle clips is dropped).
- *Geometry* (`citizen_rig.py`, new 05b): **every garment triangle is expanded 3 mm per edge about its incentre and unwelded** (`CIT_EXPAND`, uv NOT scaled: growing the uv samples the atlas gutters = white speckles). Hairline gaps between the pack's shells close. Offline proxy on 9 dark walkers: slivers 31 -> 15 (garment), 17 -> 11 (with hull).
- *Measurement* (new): `Char_CrowdKey` (build step `mapkey`): the crowd map with street / facades unlit pure green, no fog / sky; `capture_r5.sh ... gK` shoots it at native 4K and `eval/key_holes.py` counts green pixels enclosed by people = see-through cracks in the real engine. The critic's `cracks.py` counts bright thin components inside dark-clothed people, which include hair highlights, fingers, necklaces: of its 37 hits in the final tracking still 7 are hair / face and 12 hand / arm skin (`eval/cracks_classify.py`). Use both, and look at the crops.
- Layout: 18 distinct citizens (`Char_Crowd` = two-way flow: 6 + 6 mid lane, 3 + 3 near lane 4.5 m from the tracking camera), gait phases seeded from `AnimOffset` (golden ratio, CH19: `eval/gait_phase.py`).

**2. Enemies in a real fight.** `Char_Fight`: hero (`ABP_Hero_Fight`) in the middle of 6 enemies on a ring (r 2.65-3.0 m), each with its own clip sequence (`UWHCharAnimInstance::Sequence`); armed ones (bat, pipe, pistol) stand relaxed between swings, unarmed ones keep the boxing guard between punches / kicks / reactions. No clip raises an enemy head more than +8 deg (`evidence/head_pitch_clips.json`). Masks are cloth, not shrink-wrap (`people/mask.py`). Weapons are textured (`weapons/`).

**3. Hero suit (design and colours unchanged; UE only).** `hero_suit_r5.py` (smooth panel borders, raised thread normal, 2/2 twill detail normal, 2331 texels/m), `hero_lens_r5.py` (domed lenses).

**4. Secondary.** `runLeap` / `runLeapB` take-off + tuck clips (`hero_jump_r5.py`), `Char_Hero` = hero only (director `ManagedActors` / `ShowActors`), **05b: whole-body turntable (5.2 m, the 3.4 m version cut the legs off) and gameplay cameras (chase from behind at 5 m, toward the camera at 5.6 m: CH1 / CH2 were unproven)**, all movies with motion blur OFF (round 04 clips were smeared), hero 4K leap from a fixed-step 4K movie.

## Round 05 results

`round-05/SPEC_CHECK.md` (builder-measured numbers, CH1-CH19) and `round-05/CAPTURES.md` (what each file is). Known problems are the last section of SPEC_CHECK.

## Commands

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters      # the default (unreal/WebHomage/Saved/P2Build) does not exist: EVERY tool needs this
tools/ue_char/prep_all.sh                                       # every derived input (hero maps + lens, hulls, people + weapons, citizen FBX), no Unreal, no GPU
tools/ue_char/build_characters_headless.sh '{"steps":"clean,tex,mat,mesh,citizens,rename,abp,map,maps5,mapkey"}'   # ~50 s in the GPU lock (+ queue wait)
unreal/WebHomage/Scripts/build_editor.sh                        # after C++ changes (if UnrealEditor.modules keeps the old dylib, point it at the new one by hand)
tools/ue_char/capture_r5.sh <out> [MOVIES "H G F C"] [STILLS "gH gF gC gE gK"] [JUMP 1]    # offscreen, GPU lock, native 4K stills + 1080p60 movies (blur off) + 4K leap; ONLY="gC1 gK1" limits still groups
tools/ue_char/analyze_r5.sh <captures> <evidence>               # cracks.py / count.py / YOLO / head bob / lean / takeoff / key holes / gait phase
python3 tools/ue_char/eval/key_holes.py KEY_4K.jpg OVERLAY.png # CH18 in the real engine
python3 tools/ue_char/eval/crack_render.py OUT NAME:clip:frame ... [--px-per-m 300]   # offline posed render (EXPAND=0.003 mimics the export); critic_r04/cracks.py on the PNGs
python3 tools/ue_char/eval/underlayer.py NAME ...               # hulls (HULL_STRETCH, HULL_HOLE_MAX, HULL_PURITY, SKIRT_* env knobs)
```
Scripts are bash: in zsh a `$VAR` list is not word-split (use `bash -c`).

## File map (what P2 owns)

| Path | What |
|---|---|
| `tools/ue_char/eval/` | `underlayer.py` (hull, skirt rig, weights), `citizen_rig.py` (export: expanded triangles, weights, hull), `crack_probe.py`, `crack_render.py`, `key_holes.py`, `gait_phase.py`, `critic_r04/` (critic's `cracks.py`, `count.py`), `video_checks.py`, `citizens.py` (FBX exporter; keeps a legacy `SCR` fallback line so P6's `tools/life/citizens_fbx.py` string substitution still matches) |
| `tools/ue_char/people/`, `weapons/`, `heroanim/`, `hero_suit_r5.py`, `hero_lens_r5.py` | enemies, weapons, hero clips / suit / lens |
| `tools/ue_char/capture_r5.sh`, `analyze_r5.sh`, `ue_wait.sh` | capture / analysis / launch wait (`ue_wait` counts real `UnrealEditor` processes only: `gpu_slot.py` wrappers of queued agents carry the engine path and starved it) |
| `unreal/WebHomage/Source/WebHomage/Characters/` | sequence idle, jump variants, phase seed, director visibility |
| `unreal/WebHomage/Scripts/build_characters.py` | maps `Char_Hero`, `Char_Fight`, `Char_Crowd`, `Char_CrowdKey`, `Char_Lineup`, ABPs, 18 citizens |
| `docs/night1/characters/round-05/` | `CAPTURES.md`, `SPEC_CHECK.md`, `captures/`, `evidence/` |

## Local-only binaries (nothing below is committed; all regenerable from `~/sm2-assets/raw` + the repo)

- `unreal/WebHomage/Content/{Characters,Tests/Characters}`; `art/night1/characters/**/*.png, *.fbx`.
- `/Users/midir/sm2-n1/_scratch/characters/`: `ueimport/`, `eval/hull` (hull npz), `eval/tiles`, `r4/yv` (ultralytics venv), `r5/` (previews, offline renders, capture dirs `cap3` old-content stills, `cap6`, `cap7`, `cap8`).
- `DerivedDataCache/`, `Intermediate/`, movie frame folders: deleted at the end of the round.

## Gotchas (new this round; earlier lists in git history)

1. **Never edit a shell script that a running bash is executing in place**: bash reads it incrementally, the run died with `syntax error near ;;` mid-batch. Write a temp file and `mv` it over (new inode; the running copy is unaffected).
2. **The GPU queue is the schedule.** Other agents' perf runs hold the exclusive lock for 10-20 min at a time; every UE launch of ours (build, movie, each still group) waits in the FIFO separately. Batch work into as few launches as possible; never re-plan around a single launch.
3. `build_characters.py` step `mapkey` duplicates `Char_Crowd` before keying it. The first version loaded the original, keyed it and saved the dirty original too (the "crowd" movie came out green). If `EAL.duplicate_asset` reports the destination exists, delete `Content/Tests/Characters/Char_CrowdKey.uasset` by hand (or use the `clean` step).
4. `cracks.py` (critic) counts hair highlights, fingers and necklaces as slivers on dark-clothed walkers: judge cracks on crops and on `key_holes.py`.
5. Coat / skirt tears are weights first: test in `crack_render.py` (it reproduces them) before spending a UE run. The skirt rig replaces the pack's per-vertex auto weights below the hips for free-hanging garment only; trousers keep theirs.
6. The 4K real-time still groups and the movies do not share a clock (director clock drifts ~1.5 s at 5 s): compare defects, not frames, between runs.
7. Earlier gotchas that still hold: `UnrealEditor.modules` can keep pointing at a deleted dylib after `build_editor.sh`; `capture_r5.sh` must be executable; hull colour must come from the outermost cloth; masks: only the outermost shell is draped; hero and thug clips share one skeleton.

## Next steps (ordered by what the round-04 critic will look at first)

1. **Find out why the citizen weights do not reach the engine geometry of the hijabi coat** (SPEC_CHECK problem 1): the flap / hem slits are pixel-identical before and after the skirt rig. Cheapest decisive test: export a debug FBX for `17_hijabi_student` with an exaggerated weighting (all vertices below y 0.9 at 100 % on `head`), rebuild (`steps: citizens,rename` is enough), shoot `Char_Crowd` shot 0 and see whether anything moves. Check the `BindPose Matrix generation acquired 2 different Matrices from FbxCluster vs FbxPose` warning (Blender FBX export of the armature: pose vs cluster matrices). A commandlet `AssetExportTask` of the imported mesh crashed once in nullrhi (`SkinnedMeshComponent.cpp:4987`); do not loop it.
2. Judge the 3 mm expansion by eye on the near-lane hands / trouser edges (thorns); `CIT_EXPAND=0` restores welded triangles.
3. Fight: more hero beats per 8 s window (SPEC_CHECK problem 5); crowd: more walkers near the camera if the critic still counts < 16 people.
4. Suit design flag and lens highlight (owner decision / material work).

## Known problems

See the end of `round-05/SPEC_CHECK.md`. The hero suit design (white spider on the chest, blue legs with red stripes) is still the open brand flag (round-02 to round-04 critics): owner decision, unchanged (only fabric, thread relief, panel borders, lens and framing were touched).

## No copied IP (owner rule)

Enemies and civilians: the owner's own Tripo generations and the browser game's own crowd; weapons are generic primitives with procedural wear, no lettering. No reference image or footage is committed.
