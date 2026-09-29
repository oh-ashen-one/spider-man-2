# P2 Characters: handoff after round 04

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203.
Round-03 critic (blind, `round-03/CRITIC.md`): hero model 4, hero animation 3, enemies 3, civilians 2, image quality 4; FAILS. Biggest gap: the hero run (CH6 / CH7 / CH10). Round 04 worked on three gaps (hero run, enemy masks + lineup, civilians) plus the hand texture bleed. Evidence: `round-04/` (`CAPTURES.md`, `SPEC_CHECK.md`, `captures/`, `evidence/`).

## Round 04: what changed

**1. Hero run (browser + UE: `public/assets/spiderman.glb`).** `tools/ue_char/heroanim/hero_run_r4.py` (numpy, runs in python3 or `blender -b -P`) patches the GLB in place: every node, mesh, skin, texture and the other 78 clips stay byte-identical (checked: channels, mesh buffers, inverse binds and images equal), clip and bone names unchanged.
- `run`: 19/30 s -> 17/30 s (3.16 -> 3.53 steps/s at rate 1), world-space forward pitch added along spine / spine1 / spine2 (+4, +4, +3.5 deg; neck -3, head -3.5 so the gaze stays down-range), upper-arm swing x1.35 and forearm flex x1.15 about the cycle mean. Head-to-hip lean 12.3 -> 19.9 deg (min 19.5), hand fore-aft swing 61 -> 74 cm (`evidence/hero_clips_r4.json`, before: `hero_run_r3_before.json`).
- `runTakeoff` (NEW clip, additive): 16/30 s grounded anticipation crouch: the run contact pose gathers in 0.12 s into the `jump` clip's first pose with the hips lowered 17.2 cm so both feet stay on the ground, sinks 3 cm more until 0.25 s, then eases back toward the jump's start pose (never reached in the lineup: the actor leaves the ground at 0.25 s).
- Browser: `npm test` 15/15, `vite build` ok, headless load on port 5203 (`tools/ue_char/heroanim/browser_check.mjs`): no console errors, rig `run` = 0.5667 s. The browser does not use `runTakeoff` (its jump charge uses `jumpCrouch`, P3's animator); the browser's LOCO anchor for `run` is 8.5 m/s while the clip's feet move at 5.95 m/s, so the browser run slides (not P2's file).
- UE (`Source/WebHomage/Characters`): `UWHCharAnimInstance` has `Takeoff` + `TakeoffBlendIn` (0.07 s) and a `TakeoffTime` state; the crouch is held under the air blend for 0.12 s after lift-off so `jump` (same first pose) continues it; `FallAlpha` is reset on lift-off (a jump no longer starts on the skydive `fall` pose). `AWHCharLoopWalker`: `TakeoffTime`, `FirstHopDelay`, hops in Line mode, Line mode moves along the actor's yaw (180 = -X). Lineup ABP: `fall` = `fallCalm` (the old `fall` is a horizontal skydive: the round-03 "belly dive"), `takeoff` = `runTakeoff`; loco anchors are the clips' planted-foot speeds (walk 114, jog 310, run 570, sprint 899 cm/s; `tools/ue_char/heroanim/foot_speed.py`).
- Traversal (P3): clip names unchanged; `run` is shorter and leans more; `runTakeoff` is available for their jump start.

**2. Enemies.** `tools/ue_char/people/prepare_person.py` + new `mask.py`, `tools/ue_char/weapons/`.
- Masks are now the head surface itself: the lower face / neck is subdivided once (red-green, no T-junctions), draped radially onto the convex hull of the front of the head (cloth spans nose -> cheeks and chin -> collar; up to 5-8 cm over the neck hollow), plus 3.5 mm thickness and small folds; the cloth is painted by 3D position (feathered edge, stitched rolled hem, weave, fold shading, no print) with the ears excluded by geometry. Nothing can clip or poke through: there is no second surface. Tie band round the back only on short hair (thug, brute); long hair (hood, tee, beard) ends behind the ears. `round-04/evidence/enemy_heads_ortho.jpg`.
- Texture fixes: UV-island seams blended by 3D position (`mask.seam_blend`, 0.8-0.97 M border texels per person); brute beanie + cuff get a knit rib and a soft 2-texel edge (was a flat stair-stepped band); remaining red / green plaid texels on sleeves, cuffs and collar cleared (0.40 M texels); tee chest print and left-chest logo removed (beard).
- Three more raw Tripo people (owner's `~/sm2-assets/raw`): `hood` (human+figure: black hoodie, cargo pants, white shades), `tee` (adult+male: black tee + the raw Tripo cap fitted on the head, procedural twill, hair pulled inside the crown), `beard` (human+character (3): black tee, chains). Tint variants (same mesh, other atlas): thug `Oxblood` jacket, hood `Grey` hoodie. All five go through the same skinfit (`--weld --spatial-smooth`), chamfer rms 3.9-5.4 cm.
- Weapons (`make_weapons.py`, Blender headless, generic shapes, no brand): bat (84 cm, taped handle), steel pipe with elbow fitting, pistol (polymer frame, steel slide). `add_weapon.py` puts one in the right hand, rigid on `hand.R` (handle parallel to the knuckle line, long weapons tilted 58 deg so they hang down-back), solid-colour tiles in the reserved right 512 columns of the atlas strip; one primitive / one material stays. Meshes: `SK_Street_{Thug,Brute,Hood,Tee,Beard}` + `SK_Street_Thug_Bat`, `_Thug_Pistol`, `_Brute_Pipe`, `_Hood_Pistol`, `_Tee_Bat`, `_Beard_Pipe`.
- Lineup: 7 enemies standing in two staggered rows on the north sidewalk (idle `thugIdle`, pistol holders `thugGunAim` via `ABP_Street_GunAim`), lane walkers now carry weapons (thug bat, brute pipe) and walk at their clips' foot speeds (walkStreet 114, walkBrute 110 cm/s; round 03 used 160 / 143 = 40 % foot slide).

**3. Civilians.** Root cause of three rounds of "gliding in a frozen pose": the citizen FBX takes land as `SK_Citizen(_)Armature_<take>`, the rename kept `Armature_`, so `ABP_Citizen_Lineup` loaded `None` for every clip and the citizens were drawn in the bind pose. Fixed in `rename_anims`. Then:
- 12 distinct crowd people (`CITIZENS`; none shares a raw person with an enemy, graphic tees left out), each with its own walk style (walk / walkF / walkBrisk / walkStroll / walkOld, `CIT_WALK`), one AnimBP per style (`ABP_Citizen_<style>`).
- The shipped in-place walks move the stance ankle non-uniformly (5-6 cm slide per plant at any constant speed): `tools/ue_char/eval/crowd_gait.py` re-times the keys so the planted ankle moves at constant speed; `citizen_rig.build` keys the FBX actions at those times. Slide per plant at each style's natural speed: 0.9-2.9 cm (`evidence/crowd_gait.json`); walkers move at exactly those speeds (`CIT_SPEED`).
- UV-seam duplicate weights welded in `citizen_rig.build` (the white seam streaks).
- Layout: south sidewalk, 8 walking +X and 4 walking -X, start positions spread (gait phases differ), a mesh-less tracker at 1.1 m/s for the side-tracking camera; the AI suits are parked at x -3500 and no hero-suit mesh is near the civilian or enemy cameras.

**4. Hero hand (UE only, if cheap).** `tools/ue_char/hero_hand_fix.py`: texels covered only by hand / finger triangles that are white are inpainted from the red glove (OpenCV Telea); texels shared with other triangles (chest emblem) untouched -> `art/night1/characters/hero/tex/suit_basecolor_r4.png`, used by the build. Browser texture unchanged. Lens specular / curvature: not done.

RESULTS_PLACEHOLDER

## Commands

```
# UE content (wipes + rebuilds /Game/Characters and /Game/Tests/Characters; 'prep' builds people, weapons, hand fix; waits while 3+ Unreal instances run)
tools/ue_char/build_characters_headless.sh
unreal/WebHomage/Scripts/build_editor.sh                        # after C++ changes (takeoff / Line yaw this round)
# hero clips (in place on public/assets/spiderman.glb; refuses to run twice)
python3 tools/ue_char/heroanim/hero_run_r4.py [--src GLB --out GLB]
python3 tools/ue_char/heroanim/measure_clip.py GLB run jog sprint   # steps/s, lean, arm swing
python3 tools/ue_char/heroanim/foot_speed.py GLB run [--speed 5.7]  # natural speed + slide per plant
blender -b -P tools/ue_char/heroanim/preview_clip.py -- GLB OUT run:34,runTakeoff:32
node tools/ue_char/heroanim/browser_check.mjs                       # headless load (port 5203), wrap in gpu_slot.sh capture
# enemies
tools/ue_char/people/build_people.sh [--force]                  # prepare (5 people + tints) -> skinfit (cached on SHA) -> weapons -> walks -> GLBs + PNGs
python3 tools/ue_char/people/prepare_person.py thug|brute|hood|tee|beard
# civilians
tools/ue_char/eval/export_citizens.sh NAME...                   # FBX with all 5 walk styles (time-warped) + welded weights
python3 tools/ue_char/eval/crowd_gait.py [--json OUT]           # natural speeds + slide before / after the warp
# captures (offscreen, GPU lock, every launch waits for < 3 Unreal instances)
tools/ue_char/capture_lineup.sh <out>                           # ONE 91 s 1080p60 -movie run -> clips + stills
tools/ue_char/capture_4k_stills.sh <out>                        # native 4K stills (r.ScreenPercentage 100), 6 groups
<venv>/bin/python tools/ue_char/eval/video_checks.py hero_run|takeoff|people ...   # opencv + ultralytics (YOLO11x, specs weights)
```

## File map (what P2 owns)

| Path | What |
|---|---|
| `tools/ue_char/heroanim/` | `ganim.py` (glTF anim I/O + FK), `hero_run_r4.py`, `measure_clip.py`, `foot_speed.py`, `preview_clip.py`, `browser_check.mjs` |
| `tools/ue_char/people/` | `prepare_person.py` (CFG for 5 people, tints, cap, weapon tiles), `mask.py`, `build_people.sh`, round-03 tools |
| `tools/ue_char/weapons/` | `make_weapons.py` (Blender), `add_weapon.py` |
| `tools/ue_char/eval/` | `citizens.py`, `citizen_rig.py` (weld + warped keys), `crowd_gait.py`, `video_checks.py` |
| `tools/ue_char/hero_hand_fix.py` | UE hero base colour hand inpaint |
| `unreal/WebHomage/Source/WebHomage/Characters/` | takeoff, Line yaw + hops |
| `unreal/WebHomage/Scripts/build_characters.py` | people / tints / armed meshes, citizens x12, ABPs (takeoff, per-walk-style, GunAim), round-04 lineup map and 18 shots |
| `docs/night1/characters/round-04/` | `CAPTURES.md`, `SPEC_CHECK.md`, `captures/`, `evidence/` (own renders and JSON only) |

## Local-only binaries (nothing below is committed; all regenerable from `~/sm2-assets/raw` + the repo)

- `unreal/WebHomage/Content/{Characters,Tests/Characters}`; `art/night1/characters/**/*.png, *.fbx` (people atlases incl. tints, citizens FBX + PNG, hero `suit_basecolor_r4.png`).
- `/Users/midir/sm2-n1/_scratch/characters/`: `ueimport/` (stripped GLBs), `r3/people`, `r3/fit` (skinfit outputs + `.sha` cache, `walks.glb`), `r3/weapons`, `r4/` (previews, venv `yv` with ultralytics, YOLO weights copy).
- `DerivedDataCache/`, `Intermediate/`, `dist/` deleted at the end of the round.

## Gotchas (new this round; rounds 01-03 list still applies, see git history of this file)

1. **Check the imported asset names before blaming animation.** `load()` of a missing asset returns `None` and the AnimInstance silently drops the sample; the citizens stood in the bind pose for three rounds because of a rename prefix.
2. **In-place clips are not constant-speed.** Measure the planted-foot speed (`foot_speed.py`, `crowd_gait.py`) and set the loco anchor / walker speed to it; the browser LOCO anchors (1.6 / 4.5 / 8.5 / 14 m/s) are 30-60 % above the clips' foot speeds.
3. **glTF export from Blender is Y-up**: a weapon authored along Blender +Y comes out along glTF -Z (`add_weapon.py` converts back).
4. **Tripo atlases can reuse texels for two surfaces** (hair shells at the back of the head): painting by 3D position then paints the other surface too. Keep painted regions on the face / short hair.
5. **Auto landmarks** (`mask.auto_landmarks`, nose = most forward centre-line point) fail on people with sunglasses: `hood` has measured numbers.
6. Blender headless `render` prints `unregister_class ... _RNAMeta` on exit: harmless.

## Known problems

KNOWN_PLACEHOLDER

## No copied IP (owner rule)

Enemies and civilians come from the owner's own Tripo generations. Removed this round: the beard person's chest print and a left-chest logo with lettering (`clear_graphic`); the raw cap's texture is NOT used (procedural twill), so no badge can come along. Weapons are generic primitives (no brand, no lettering). Graphic-tee citizens (07, 11) are left out of the crowd. The hero suit design is still the open brand flag (round-02 and round-03 critics): owner decision.
