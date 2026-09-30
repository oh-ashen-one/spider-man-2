# P2 Characters: handoff after round 05

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203.
Round-04 critic (blind, `round-04/CRITIC.md`): hero model 4, hero animation 5, enemies 4, civilians 3, image quality 3; FAILS (avg 3.8). Biggest gaps: (1) CH18 seam cracks on civilians, (2) enemies as combatants (CH11 / CH12 / CH14), (3) suit quality. Round 05 worked on those three plus the secondaries (jump take-off, crowd flow, hero_jump retake, no second hero). Evidence: `round-05/` (`CAPTURES.md`, `SPEC_CHECK.md`, `captures/`, `evidence/`).

## Round 05: what changed

**1. CH18 cracks (civilians).** Root cause, measured: the 20 shipped crowd citizens (`public/assets/city/npc`, 5000 triangles) are shredded garment shells: 3000-4400 open boundary edges per mesh after welding by position (pockets, lapels, hems are separate overlapping pieces) and the LOD decimation moved the pieces independently, so 1-20 mm gaps (median 3 mm) show the background; welding by tolerance collapses the mesh before it closes them. Three mesh / weight level fixes (all in `tools/ue_char/eval/`, run by `prep_all.sh` and `citizen_rig.build`):
- `underlayer.smooth_weights`: skin weights are averaged across abutting shells (14 mm radius, sigma 6 mm, normal gate; the arm's inner side is excluded), so a sleeve no longer tears away from the torso at the armpit when the arm swings (the biggest cracks).
- `underlayer.py`: an under-layer hull appended to every citizen mesh: signed distance to the oriented garment (6 mm grid), iso-surfaces 4 mm and 12 mm under the cloth (numpy surface nets), triangles with no cloth 2 x depth + 12 mm above them dropped (webs), hull vertices that mix limb groups or belong to a hand dropped, each hull triangle coloured with the OUTERMOST cloth above it (uv of the first garment hit along its normal, one uv per triangle, same material, no extra slot). A crack now shows cloth colour, not the wall.
- `crack_probe.py` / `crack_render.py`: offline stand-ins (no GPU): posed single-sided orthographic coverage and a rendered row of walkers against a wall run through the critic's `cracks.py`. On 9 dark walkers x 1 pose each: wall-coloured slivers 35 (garment only) -> 22 (smoothed weights) -> 9 (weights + hull, purity 0.45, 2 layers). Numbers in the real 4K capture: `round-05/SPEC_CHECK.md`.
- Layout: 18 distinct citizens (6 more, none shares a face), `Char_Crowd` = two-way flow (6 + 6 mid lane, 3 + 3 near lane 4.5 m from the tracking camera), gait phases seeded from `AnimOffset` (golden ratio, CH19).

**2. Enemies in a real fight.** `Char_Fight`: hero (`ABP_Hero_Fight`: fightIdle -> punch1 -> punch2 -> kick -> ...) in the middle of 6 enemies on a ring (r 2.65-3.0 m), each with its own clip sequence (`UWHCharAnimInstance::Sequence`, cross-faded; `AnimOffset` shifts each actor's clock): armed ones (bat, pipe, pistol) stand relaxed with the weapon hanging (hero idle, head +6 deg) between swings, unarmed ones keep the boxing guard between punches / kicks / hit reactions. No clip used raises an enemy head more than +8 deg (`evidence/head_pitch_clips.json`; round 04 used `idleLook`, up to +39 deg). The grey-hoodie twin is gone; the Oxblood thug now also has a green mask.
- Masks (`people/mask.py`): `hang()` = cloth, not shrink-wrap (cloth radius = smoothed envelope of the head surface from up to 5 cm above, so lips, chin cleft and jowl creases vanish, the nose stays a soft tent; only the outermost shell is draped; the hem tapers back to the neck); `drop_cavity` + `fill_face_holes` (per-edge fans, UV-safe) close the mouth slit, nostril pits and the hood's neck hole; `fix_flips`, `cloth_normals` remove back-faced slivers and dark slit shading; the brute's hem stops at the chin (`bot_drop`).
- Weapons textured (`weapons/weapon_textures.py`, `add_weapon.py` part_uv): wood grain + scuffs, galvanised pipe with rust and scratches, wrapped grip, cloth tape, stippled polymer, mapped with real uvs into the atlas strip.

**3. Hero suit quality (design and colours unchanged; UE only).** `tools/ue_char/hero_suit_r5.py`: panel borders re-drawn smooth in 3D (the blue / red charts meet along a zig-zag; blue membership Gaussian-averaged over the surface, 7 mm), raised thread normal (web-line mask -> rounded height) + glossier crest roughness + foot occlusion, and a 2/2 twill detail normal (32 yarns per tile, 0.45 mm per yarn = tiling 122 from the mesh UV density 0.569 UV/m) replacing the 3 mm knit. `hero_lens_r5.py`: lens discs pushed out 7 mm into a dome (rim fixed), normals recomputed; `MI_Hero_Lens` darker base + roughness 0.05 so sky / sun show as highlights.

**4. Secondary.** `hero_jump_r5.py` adds `runLeap` / `runLeapB` (0.73 s: takeoff crouch -> open stride -> tuck -> reach, torso lean 22-39 deg, the mirrored clip leads with the other leg; alternating per jump: `UWHCharAnimInstance::JumpVariants`, `AirBlendIn`, `TakeoffHoldTime`, `bJumpHoldsThroughDescent`). `Char_Hero` = hero only (director `ManagedActors` / `ShowActors` hide every other actor per shot: no second hero), the leap shot frames the whole jump, the 4K leap still comes from a fixed-step 4K movie (deterministic timing).

## Round 05 results

See `round-05/SPEC_CHECK.md` (builder-measured) and `round-05/CAPTURES.md`.

## Commands

```
tools/ue_char/prep_all.sh                                   # every derived input (hero maps + lens, hulls, people + weapons, citizen FBX), no Unreal, no GPU
tools/ue_char/build_characters_headless.sh '{"steps":"clean,tex,mat,mesh,citizens,rename,abp,map,maps5"}'   # 45 s inside the GPU lock
unreal/WebHomage/Scripts/build_editor.sh                    # after C++ changes (if UnrealEditor.modules keeps the old dylib, point it at the new one by hand)
tools/ue_char/capture_r5.sh <out> [MOVIES "H F C"] [STILLS "gC gF gE gH"] [JUMP 1]   # offscreen, GPU lock, native 4K stills + 1080p60 movies + 4K leap
tools/ue_char/analyze_r5.sh <captures> <evidence>            # cracks.py / count.py / YOLO / head bob / lean / takeoff
python3 tools/ue_char/eval/crack_render.py OUT NAME:clip:frame ...   # offline see-through proxy; then critic_r04/cracks.py on the PNGs
python3 tools/ue_char/people/clay.py PREPARED.npz OUT.png --atlas ATLAS.png --yaws -40,0,40   # numpy head renders
python3 tools/ue_char/heroanim/skel_plot.py GLB OUT.png clip:t0,t1 ...                       # stick figures of clip poses
```

## File map (what P2 owns)

| Path | What |
|---|---|
| `tools/ue_char/eval/` | `underlayer.py`, `crack_probe.py`, `crack_render.py`, `citizen_rig.py` (weights + hull), `critic_r04/` (critic's `cracks.py`, `count.py`, `hero_track.py`), `video_checks.py` |
| `tools/ue_char/people/` | `prepare_person.py`, `mask.py` (hang / drop_cavity / fill_face_holes / fix_flips / cloth_normals), `clay.py` |
| `tools/ue_char/weapons/` | `make_weapons.py`, `add_weapon.py`, `weapon_textures.py` |
| `tools/ue_char/heroanim/` | `hero_run_r4.py`, `hero_jump_r5.py`, `skel_plot.py`, `measure_clip.py`, `foot_speed.py`, `browser_check.mjs` |
| `tools/ue_char/hero_suit_r5.py`, `hero_lens_r5.py` | suit maps, lens dome |
| `unreal/WebHomage/Source/WebHomage/Characters/` | sequence idle, jump variants, phase seed, director visibility |
| `unreal/WebHomage/Scripts/build_characters.py` | maps `Char_Hero`, `Char_Fight`, `Char_Crowd`, `Char_Lineup` (faces only now), ABPs, 18 citizens |
| `docs/night1/characters/round-05/` | `CAPTURES.md`, `SPEC_CHECK.md`, `captures/`, `evidence/` |

## Local-only binaries (nothing below is committed; all regenerable from `~/sm2-assets/raw` + the repo)

- `unreal/WebHomage/Content/{Characters,Tests/Characters}`; `art/night1/characters/**/*.png, *.fbx` (people atlases, citizen FBX with hulls, hero r5 maps, twill).
- `/Users/midir/sm2-n1/_scratch/characters/`: `ueimport/`, `r3/people`, `r3/fit`, `eval/hull` (hull npz), `eval/tiles`, `r4/yv` (ultralytics venv), `r5/` (previews, offline crack renders).
- `DerivedDataCache/`, `Intermediate/`, `dist/`, movie frame folders deleted at the end of the round.

## Gotchas (new this round; earlier lists in git history)

1. **`UnrealEditor.modules` can keep pointing at a deleted dylib** after `build_editor.sh` (link made `-0002`): edit the manifest by hand (it is the worktree's own file).
2. **`capture_r5.sh` must be executable** (a file written by an editor tool is not); `zsh` does not word-split `$VAR` (use `bash -c`).
3. **Citizens: cracks are geometry AND weights.** Test with `crack_render.py` before spending a UE run; hull layers deeper than 12 mm or a permissive purity make webs / shards next to the armpits and the coat hem at close range (the 3-layer hull made the first real 4K crowd worse than round 04: 40 slivers).
4. **Hull colour must come from the outermost cloth**, not the nearest vertex (a T-shirt sleeve over an arm showed skin).
5. **Masks: multi-shell neck.** A hoodie / vest collar sits outside the neck skin; displacing both tears the collar off the mask hem (only the outermost shell is draped now).
6. **Director clock drifts behind the automation clock** in real-time runs (about 1.5 s at 5 s): stills use shots of 6-8 s and combined runs; timing-critical stills (the leap) come from fixed-step movies.
7. Hero and thug clips share one skeleton: any hero clip can be an enemy sequence entry (`H:` prefix in `build_characters.py` `fights`).

## Known problems

See `round-05/SPEC_CHECK.md` (list at the end).

## No copied IP (owner rule)

Enemies and civilians: the owner's own Tripo generations and the browser game's own crowd; weapons are generic primitives with procedural wear, no lettering. The hero suit design is still the open brand flag (round-02 to round-04 critics): owner decision, unchanged this round (only fabric, thread relief, panel borders and lens were touched).
