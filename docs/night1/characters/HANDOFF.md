# P2 Characters: handoff after round 03

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203.
Round-02 critic (blind): hero model 5, hero animation 4, enemies 2, civilians 3, image quality 4; FAILS. Its single biggest gap was the thug and brute: prototype-grade (low-poly, mitten hands, sticker eyes, block shoes; the brute the same mass as the thug, hunched). Round 03 rebuilt both. Everything not listed under "Round 03" is unchanged from round 02.

## Round 03: street thug and street brute

**Sources (owner's assets, never committed).** `~/sm2-assets/raw/leather+jacket+man+3d+model.glb` (thug: grey-haired man, hooded leather jacket over a zip hoodie, jeans, boots) and `~/sm2-assets/raw/human+character+3d+model.glb` (brute: stocky bearded man, puffer vest over plaid shirt, work boots, beanie). Raw Tripo: 6.4k / 7.1k tris, one 8192^2 baked base-colour map, modelled faces with eyes, ears and hair, five-finger hands, folds in the cloth. The raw meshes face +X with the arms along Z; the pipeline rotates them into the game frame (faces +Z, +X = left).
The old `thug.glb` / `public/assets/enemies/brute_basecolor.webp` are untouched, so **the browser build is unchanged** (UE-only round; `npm test` 15/15 and `vite build` re-run at the end).

**Pipeline** (`tools/ue_char/people/`, run by the UE build's `prep` step through `build_people.sh`; about 2 min the first time, cached on the SHA of the prepared mesh afterwards):
1. `prepare_person.py thug|brute`: rotate + scale to the hero's height; rasterise the UV layout into a per-texel 3D position map so every texture edit is placed by body position; **replace the atlas gaps by nearest-island colour** (the raw atlas is thousands of islands with blurry gaps, which read as dark dashes / sparkles at seams); dress:
   - thug: ornamental belt buckle and key-chain metal (invented metalwork with pseudo-lettering) painted plain dark steel;
   - brute: orange pom-pom beanie to charcoal knit (pom-pom vertices pulled onto the fitted dome sphere, so no hole), red-green plaid to one worn brown-grey flannel tone, head and neck shrunk by 1/girth so the head keeps natural proportions after the actor is widened;
   - both: a **modelled bandana** (2,016 tris): a shell ray-cast from the head axis onto the real head surface, 8.5 mm off the skin (so it follows nose, cheeks, jaw and collar), with cloth folds, a rolled top edge and a tie strap behind the ears, on its own 4096x512 texture strip (plain dark navy / maroon with a faint dot print, no lettering). Eyes, forehead, ears and hair are untouched;
   - one primitive, one material, one 4096^2 atlas (raw atlas squeezed to 4096x3584 + bandana strip). 8,380 / 8,427 tris.
2. `tools/skinfit/skinfit.py` (extended, suits unchanged because both flags default off): pose-fit the hero mesh to the person, transfer weights from it, un-pose. New: `--weld` shares weights between coincident (UV-seam duplicate) vertices; without it every texture seam opened into a hairline crack as soon as the pose changed (in UE: thin see-through lines along seams; this is the "white seam cracks and sparkles" family of the round-02 critic's image-quality note); `--spatial-smooth 0.035` averages weights over 3D neighbours that face the same way, ACROSS mesh layers (jacket over hoodie, vest over shirt), so layers do not poke through each other. Chamfer rms before/after: thug 10.99 -> 4.85 cm, brute 7.84 -> 5.46 cm. The mesh sits on the game's exact 58-joint skeleton, so **all 79 hero clips and the 13 thug clips play on it**.
3. `make_walk.py`: the hero `walk` is a stalking, bent-knee cycle (knee flexion mean 46 deg, stance mean 40 deg, hips 6-9 cm below standing height). `walkStreet` raises the hips 5.5 cm and re-solves both legs with analytic two-bone IK to the ORIGINAL ankle positions and orientations (stance knee flexion mean 9 deg, max ankle displacement vs the hero walk 9.6 mm: no foot sliding). `walkBrute` raises 4.5 cm, adds a 3.2 cm weight shift over the stance foot with 3 deg opposite torso roll and a 1.125x slower cadence (36 frames, 1.2 s; UE imports on the 1/30 s grid only). `evidence/walk_gait_report.json`.
4. UE (`build_characters.py`): `/Game/Characters/People` = `SK_Street_Thug`, `SK_Street_Brute` (hero skeleton), `MI_Street_*` (M_Char_Suit master, no ORM, roughness 0.78, cloth 0.16), `A_Street_walkStreet` / `A_Street_walkBrute`, `ABP_Street_Thug` / `ABP_Street_Brute` (children of `UWHCharAnimInstance`, the walk swapped for the new clips at their natural speeds 160 / 142.2 cm/s).

**Sizes** (`tools/ue_char/people/measure_build.py`, rest pose, lineup actor scale applied; brute actor = 1.08 height x 1.32 X/Y girth, `people.json`): shoulder width thug 0.68 m, brute 0.93 m = **1.36x** (A-pose deltoid to deltoid); torso width 1.61x; chest depth 1.51x; hip width 1.60x; height 1.76 m vs 1.93 m (1.10x). `evidence/size_measure.json`, `evidence/thug_brute_front_compare.jpg` (front view at one scale with the shoulder lines).

**Lineup map** (`/Game/Tests/Characters/Char_Lineup`, now 75 s / 16 shots): shots 11-15 are new, on a straight lane at x = 3000 (`AWHCharLoopWalker` new `Line` mode + `RestartLine()`, `FWHShot.RestartWalkers` so each clip starts with the walkers in the same place): 11 thug + brute side-tracking together at 4.2 m (FOV 64), 12 thug at 3 m (FOV 62), 13 brute at 3 m (FOV 66), 14 thug face close-up, 15 brute face close-up. The mask-map / region-mask test of round 02 is off by default (`mask_map`); the old brute paint tools stay for the browser.

**Captures** (`round-03/CAPTURES.md`): one 75 s 1080p60 `-movie` run cut into clips; 4K stills rendered at NATIVE 3840x2160 (`-exec "r.ScreenPercentage 100"`; the round-02 critic noticed the round-02 "4K" stills were 1080p internal, upscaled).

## Commands

```
# UE content (wipes + rebuilds /Game/Characters and /Game/Tests/Characters; 'prep' builds the people; waits while 3+ Unreal instances run)
tools/ue_char/build_characters_headless.sh
unreal/WebHomage/Scripts/build_editor.sh                       # after C++ changes (Line mode, RestartLine, director RestartWalkers this round)
# the people alone
tools/ue_char/people/build_people.sh [--force]                 # prepare -> skinfit (cached) -> walks -> stripped GLBs + PNG atlases
python3 tools/ue_char/people/prepare_person.py thug|brute      # ~8 s; outputs in _scratch/characters/r3/people
python3 tools/ue_char/people/ortho.py PREPARED.glb out.png --view side|front|back --y0 1.40 --y1 1.82 --tex 4096   # metric textured view (no GPU)
blender -b -P tools/ue_char/people/preview_fit.py -- FIT.glb OUT --clips walk,walkStreet --frames 2,8,14,20 --extra fit/walks.glb
python3 tools/ue_char/people/measure_build.py [--out json]      # size ratios;  compare_front.py OUT.png = front view at one scale
# captures (offscreen, every launch waits for < 3 Unreal instances)
tools/ue_char/capture_lineup.sh <out>                           # ONE 75 s 1080p60 -movie run -> clips + stills
tools/ue_char/capture_4k_stills.sh <out>                        # native 4K stills + perf json
# round-02 tools (browser brute, 4K skin/white test): tools/ue_char/brute/*
# live editor (own instance, MCP :8772, python mailbox): tools/ue_char/launch_editor.sh ; pkill -9 -f "[c]haracters/unreal/WebHomage/WebHomage.uproject"
```

## File map (what P2 owns)

| Path | What |
|---|---|
| `tools/ue_char/people/` | `prepare_person.py`, `build_people.sh`, `make_walk.py`, `gltfio.py`, `ortho.py`, `preview_fit.py`, `measure_build.py`, `compare_front.py`, `inspect_raw.py`, `people.json` (brute scale/girth shared by the scripts) |
| `tools/skinfit/skinfit.py` | `--weld`, `--spatial-smooth` added (default off) |
| `unreal/WebHomage/Source/WebHomage/Characters/` | walker `Line` mode, `RestartLine()`, director `RestartWalkers` |
| `unreal/WebHomage/Scripts/build_characters.py` | People folder, `MI_Street_*`, `ABP_Street_*`, walk import, lane walkers, shots 11-15, `brute_scale/brute_girth` from `people.json` |
| `docs/night1/characters/round-03/` | `CAPTURES.md`, `captures/`, `evidence/` (own renders and JSON only; no reference images) |

## Local-only binaries (MANIFEST)

Nothing below is committed. Everything is regenerable from `~/sm2-assets/raw` (owner's, must exist) and the repo.
- `unreal/WebHomage/Content/{Characters,Tests/Characters}`; `art/night1/characters/**/*.png, *.fbx` (incl. `people/*_basecolor.png`, 4096^2).
- `/Users/midir/sm2-n1/_scratch/characters/`: `ueimport/` (stripped GLBs incl. `SK_Street_*.glb`, `SK_Street_Walks.glb`), `r3/people` (prepared meshes + atlases), `r3/fit` (skinfit outputs, `.sha` cache).
- `DerivedDataCache/`, `Intermediate/`, `dist/` deleted at the end of the round.

## Gotchas

Rounds 01-02 (still true): UE rejects `EXT_texture_webp`; Interchange scripting needs `AssetImportTask` + `InterchangePipelineStackOverride`; material sampler types must match the texture (masks texture = Masks sampler); `unreal.LightingChannels` needs `set_editor_property`; the build's `spawn()` takes `rot = (yaw, pitch, roll)`; use `pkill -f "[c]haracters/..."`; movie mode is brighter than real-time stills; every Unreal launch `-RenderOffScreen -NoSound` and waits while 3+ instances run.

Round 03:
1. **Seam-duplicate vertices must share weights.** A skinned mesh whose UV-seam duplicates got different weights looks fine in the bind pose and cracks open in motion (see-through hairlines along every texture seam). `skinfit.py --weld`. Suspect any Tripo-derived skin (the citizens, the AI suits) that shows thin light lines when animated.
2. **Layered garments interpenetrate** unless weights are smoothed across layers (`--spatial-smooth`).
3. **Interchange imports animations on the 1/30 s grid only**: a clip length that is not a whole number of frames fails with "not compatible with import frame-rate 30 fps" and the second clip of a GLB is silently dropped (only the first `..._Anim` asset appears). Resample to k/30 s.
4. **Blender 5.x slotted actions**: after `arm.animation_data.action = act` also set `arm.animation_data.action_slot = act.slots[0]`, or the pose stays in the bind pose.
5. **Head landmarks for the bandana are per character** (`CFG` in `prepare_person.py`: eye, nose, ear-lobe, chin heights measured on the normalised mesh with `ortho.py`). A new person needs new numbers; the mask top must sit about 1.5 cm under the eye centre.
6. **Skin and beard hues overlap the plaid red**: recolours need geometry (position) guards (`keep_skin`), not hue alone.
7. **The lineup stage renders sRGB albedo about 3x brighter** than the texture (round 02), so real photographic albedo looks right and stylised dark palettes look washed; the 4-light enemy fill on lighting channel 1 stays.
8. `pkill -f` and `rm -rf`: only inside this worktree or `_scratch/characters/` (owner hard limit 2026-09-29); the teardown at the end of the round uses a `case` check on the variable first.

## Against `docs/night1/characters/SPEC.md` (Opus-5.5-Loop-Night-1; lines that apply to enemies)

| line | target | thug / brute now |
|---|---|---|
| CH3 texel density (>= 680 texels/m) | 4K clothing | 1,949 (thug) and 1,947 (brute, mesh space) texels/m from a 4096^2 atlas; about 1,500 after the brute's actor scale. `evidence/texel_density.json` |
| CH11 5-7 enemies in frame | fight framing | NOT met: the lineup shows 2 enemy characters (thug, brute). Open |
| CH12 enemy screen height 0.16-0.60 | fight stills | pair shot (4.2 m, FOV 64): thug 0.59, brute 0.65 of frame height (camera geometry, not measured on pixels); the 3 m clips are close shots by design (0.85 / 0.94). Brute is above the line in the pair shot |
| CH13 >= 5 outfit silhouettes, >= 2 weapon types among 7 thugs | variety | NOT met: 2 outfits, no weapons. Open (next: `CFG` entries + raw people 06 / 05 / 07, a bat and a pistol prop) |
| CH14 modelled eyes/faces, five-finger hands, cloth folds, real shoes | side by side with thugs-close / thug-closeup | done in the meshes (`round-03/captures/*_face.mp4`, `*_4k.jpg`); the comparison is the critic's |
| CH15 brute bulk | design choice | shoulder width 1.36x, torso 1.61x, chest depth 1.51x, hips 1.60x, height 1.10x |
| CH18 zero seam cracks / sparkle pixels at native 4K | rule | cause fixed (weld); checked by eye on the 11 native-4K stills and the 3 m clips, no per-pixel crack detector was run on these two meshes (round 02's mask test does not apply: the new meshes have no region-mask map) |
| CH9 foot slide <= 3 cm | engineering | the walk clips keep every ankle within 9.6 mm of the hero walk's, and the walkers move at each clip's natural speed (160 / 142.2 cm/s), so no slide by construction; not measured with engine telemetry |
| CH6, CH7, CH10 | run cadence, sprint lean, pose pops | not touched (hero run unchanged; jog / run / sprint on the street people are the hero clips; blends not exercised) |

## No copied IP (owner rule)

The two people come from the owner's own Tripo generations; nothing on them is taken from a reference game. Checked on the 4096^2 atlases at reduced scale and on the native-4K stills: no readable lettering or logo on the jacket, vest, shirt, jeans, boots or bandana; the two pieces of invented ornamental metalwork on the thug (belt buckle with engraved pattern, key-chain with pseudo-lettering) were painted over with plain dark steel; the bandana print is a generic dot/ring lattice made by `prepare_person.py`. Small details (zip-pull faces, label stitching, boot-sole tread) were not inspected texel by texel. The hero's suit design is a separate open brand flag (see Known problems).

## Known problems

- **Thug / brute:** the meshes are 8.4k tris with 5-finger hands but low-detail fingers; faces are photo-textured (no facial animation, eyes do not move); the Tripo texture carries baked lighting (a soft AO-like shading, sun-side cloth does not darken); hair and beanie are cloth-shaded (no strand or knit shader); the bandana has geometric folds but no normal map. The walk is one clip (`walkStreet` / `walkBrute`) with no start/stop, turns, or run variants: jog/run/sprint and the 13 thug fight clips are the hero/thug ones, played on new proportions (the brute's arms/hands are scaled with the actor, so punches reach further and may clip the wider torso). Only ONE thug variant (browser has three colour variants; UE lineup shows one).
- **Brute palette:** muted; a charcoal beanie, brown-grey flannel sleeves, black vest, maroon bandana. The plaid check is intentionally flattened. Face is hidden behind the bandana below the eyes.
- **Hero:** unchanged; the round-02 critic's open items stand (coarse weave, flat lenses, thin web lines, upright jog, dive-to-run snap). **Brand flag from the round-02 critic:** the hero's white emblem, wrist cuffs and red leg stripes read as a near-copy of a studio suit design and should be redesigned.
- **Civilians:** unchanged; they still stand or glide in the lineup and carry the white seam cracks (same skinning cause as gotcha 1: re-weld their weights; their rig is the 18-bone crowd rig, `crowdfit`).
- **Perf:** no valid number; the GPU is shared. The native 4K stills run is reported in `round-03/CAPTURES.md` with the utilisation measured just before it.

## Round 04 should look at

1. The next critic's single biggest gap. Likely: civilians (real walk cycles, weld the crowd weights, six or more distinct people, seams at native 4K), then the hero suit read and run, then a second and third thug variant on the same pipeline (`CFG` entries + raw people 06 hoodie/cargo, 05 black tee), and thug clips retargeted for the taller/wider brute.
2. Apply `--weld` + `--spatial-smooth` to the five AI suits and to the citizen fit and rebuild their maps.
3. Brute/thug hands: a glove or a hand-mesh swap for crisper fingers; a normal map for the bandana; soften baked lighting.
