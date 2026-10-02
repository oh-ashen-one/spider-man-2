# P3 Traversal + camera — handoff (after round 22)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

**Status (round 23 RESUMED 05:05, 2026-10-02, Opus 5.5, after the 04:40 API 502):** hold 1 (`round-23/tools/probe1_check_ba60f84.txt`) showed the
ba60f84 build PASSES V23 a/b/c on both windows (w2 bbox windows 85/85, c 67/67) but Z23 FAILED (w2 zip flew up the 300 m tower, no perch by 7.2 s:
nothing in front of the facade-facing wall camera within 58 m) and c's torso was 28-35 deg off wall-up (c climbs a 33 deg diagonal).
Fixes committed after ba60f84: `WallZipFarRange` 90 (second zip search off a wall, any direction but through the facade, run direction preferred)
and `WallVertMaxDeg` 10 (a vertical-dominant run keeps its run line within 10 deg of wall-up). Hold 2 queued 05:10 (`_scratch/traversal/r23/hold2.sh`,
log `hold2.log`; copy `round-23/tools/hold2.sh`): probes -> if fail, -WHTravTune variants and the first passing one becomes the compiled default
(header sed + rebuild) -> captures of all 11 clips (guard 1950 s) -> leftovers `LEFT` run by hold3 (queued when hold2 starts).**
Round 22 critic FAILED TARGET (7/6/6/6/6/7, `critic/round-22-CRITIC.md`, mergeable: no axis below r21): biggest gap = the VERTICAL wall run
"slides frozen, legs together, bbox_w .082-.088 for 1.5 s". Director r23 target: fix the excursion, not the cadence -- recovery toe >= .25 m off the
face with the knee .35-.50 m at mid-swing, stance foot on the face, contacts alternate <= .18 s, torso 5-20 deg off wall-up, hips <= .45 m; pass the
r22 critic tests verbatim on w2 1.0-2.8 s AND c 2.65-4.15 s (foot_sep_run_m crosses < .15 / > .35 >= 4/s; bbox_w changes >= 25 % in every 0.4 s
window; legs apart in >= 6/10 frames at 12 fps); gates: r22 side-run numbers on w2, SSw=28 compiled, all 11 clips on compiled defaults from one build,
T22 c pitch, f1/f4/a bit-identical, w2 E-zip perches <= 2 s after fire, w1 / x2 recaptured (w1 on a lit face if a route reaches one).
r23 changes (A/B at run time): vertical sprint `-WHGaitTune=VKick=0` restores r22 exactly (VSw, VTr, VKt, VTrack, VKneeLat, VHip, VRoll, VArmOut,
VArmUp, VArmK: see the comment block in `Anim/WebTravAnimInstance.cpp`); `SSw` default 28; wall-zip far-top fallback `-WHTravTune=WallZipFarUp=0`
restores r22 (a facade top > 110 m up is only the fallback; the nearest roof edge first); telemetry `hip_wall_m`, `ankle_sep_3d_m`.
Checker: `python3 docs/night1/traversal/r23_checks.py <dir> [--sheets <dir>]` (on round-22 it reproduces the critic: bbox_w windows 1/85, Z23 FAIL).
Older history: r21 handoff `git show 5f1970b:docs/night1/traversal/HANDOFF.md`, r20 `git show aa5b205:...`, r19 `git show 9f28ab2:...`, r01-18 `git show 047a342:...`.

Owned paths: `unreal/WebHomage/Source/WebHomage/Traversal/**`, `/Game/Traversal`, `/Game/Tests/Traversal`, `unreal/WebHomage/Scripts/build_traversal.py`,
`docs/night1/traversal/**`. Branch `night1/traversal`, worktree `~/sm2-n1/traversal`. Integration `origin/Opus-5.5-Loop-Night-1` merged at the r22 start
(fast-forward; it carries the orchestrator's run_game.sh frame cap that sat uncommitted here -- byte-identical, nothing lost). GPU: every engine run
through `/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh`; `PAUSED` = no launches; stop with `stop_ue.sh "<worktree>"`, never kill -9.

## 0. Round 22 -- what changed (A/B at run time)
| # | Item | Fix (file) | A/B flag (r21 values) |
|---|---|---|---|
| 1 | Side run = plank / slither | `WallSideUpright`: upright runner side-on to the facade -- body up = wall-up leaned `WallSideLeanDeg` 14 fwd along the run line and `WallSideOutDeg` 16 out from the wall, chest along the run line, root `WallSideFootOff` .36 m (feet ~.1 m off the face, hips ~.36 m); `W.SideUpK` blends it in (12/s) / out (8/s) (`WebTraversalComponent.cpp` Orient) | `-WHTravTune=WallSideUpright=0` |
| 2 | Run line diagonal for 0.5 s (torso "above the run line" only ~40 deg) | a sideways stick on the wall sheds the climb speed at `WallSideClimbDamp` 10/s (r21 3/s) (`StepWall`) | `-WHTravTune=WallSideClimbDamp=3` |
| 3 | Legs / arms for the upright run | `FWebTravAnimFrame::SideUpW`, `WallZ`: legs stride along the run line under the hips (touchdown .45 / toe-off .50 leg lengths, smootherstep recovery, heel tuck .55, stance reach .95), knees forward; sprint arm pump contralateral, elbows back; shoulders counter-rotate about the body axis (`Anim/WebTravAnimInstance.cpp`). Recovery toe off the face: default 14 cm, **captures used `-WHGaitTune=SSw=28`** (14 cm left one foot within .08 m of the face, 2 touchdowns only) -- make 28 the default next round | `-WHGaitTune=STd=,STo=,STuck=,SSw=,SReach=,SArm=` |
| 4 | Characters critic: idle -> run 1-frame weight pop | ground locomotion weights (idle/walk/jog/run/sprint) move <= 1/0.18 s per s (`GroundW`; the node's first frame snaps; moving phase rate = r21) | `-WHGaitTune=GBlend=0.02` |
| 5 | Telemetry | `torso_wallup_deg` (3D hips->head vs wall-up), `chest_run_deg`, `side_up_k`, `ankle_sep_plane_m` | -- |
| 6 | Sunlit route | w2 on the west face of the 284 m tower at x -229.4 (y -57..-41, z ~64): sun yaw -178 elev 8, the hinterland west of x -256 shadows every low west face (the city collision region is x -256..512, y -512..256 -- the heightmap's y < -512 "towers" have NO collision); this face clears it above ~48 m. Jump from the west avenue onto the face (0.95 s), vertical wall run, sideways sprint 2.85-3.98 s, E 4.0 s. The fin at y -40 ends the run. Script `scripts/city/w2_wallrun_side_zip.json` (variant t2_h, `round-22/tools/`) | r21 route: `git show 5f1970b:docs/night1/traversal/scripts/city/w2_wallrun_side_zip.json` (captured as `w2_r21route`) |

**Measured (`round-22/R22_CHECK.txt`, checker `python3 docs/night1/traversal/r22_checks.py <round> --sheets <dir> --prev docs/night1/traversal/round-21`; on round-21 it reproduces the critic):**
| Test | r21 | r22 |
|---|---|---|
| B22 box h >= w, w1 + w2 side frames | 58/86 (w2 13/41) | **114/114** (w2 69/69, h/w med 1.93; w1 45/45) |
| L22 facade luma (12 fps side frames) | w2 15-22, w1 15-27 | **w2 94-142 (14/14 >= 45)**; w1 15-29 (r21 route, not moved) |
| hero_occl (mullion) max on side frames | w2 .29 | **w2 .02** (w1 .18) |
| F22 w2 3.1-3.85 s @12 fps legs apart (along-run >= .3 m) | 4/10 | **9/10** (in-plane 10/10) |
| torso <= 30 deg off wall-up / >= 60 deg above run line / chest-to-run | -- / 0 % (med 28) / -- | w2 100 % (med 19.9) / 97 % (med 78) / med 4 deg |
| along-run ankle sep peak, share >= .3 m | .58, 49 % | w2 .87, 76 % |
| touchdowns, longest gap | 4, .183 s | w2 8, **.167 s** |
| c vertical run (limbs, touchdown gaps, 15 deg) | .30 m, med .150 / .383, 82 % | identical (c differs from r21 only in its roof-run ground rows 5.9-7.0 s = the ground blend) |
| f1 / f4 / a telemetry vs r21 | -- | **bit-identical** (145 columns, 0 cells) |
Sheets: `round-22/sheets/w2_wallrun_side_zip_3.1-3.9_12fps.png` (sunlit, upright stride, glass reflections), `w1_wallrun_tall_zip_side_12fps.png`.
w1 / x2 / w2_r21route were captured in hold A with the first r22 build (no `WallSideClimbDamp`, SSw 14): their side runs climb diagonally (above-run-line
med 38-42 deg) and w1 / w2_r21route have 1-2 long touchdown gaps (.30-.32 s). w1 is still on the shadowed r21 route (the t1 tower probes never reached the lit band).

## 1. Architecture map (Source/WebHomage/Traversal)

| File / class | What it does |
|---|---|
| `WebTravTypes.h` | `FWebTravInput` (held + edge flags: move, look, swing, jump, sprint, zip, drop, quick, trick), `FWebTravAnim` (C1 anim contract, see §2), `FWebTravEvent`, `FWebTravStrand` (web strand state). |
| `WebTravWorld.*` `FWebTravWorld` | World queries in METRES: `Raycast` (line trace, WorldStatic/Dynamic, ignores the pawn), `GroundHeight` (downward trace + terrain boxes tagged `WHGround`), `PushOutCapsule` (overlap + `ComputePenetration`, horizontal MTD), `SphereSweep`/`SphereOverlaps` (camera), `Near` (24 m XY grid of building AABBs), `Inside`. |
| `WebTravAnchors.*` `FWebTravAnchors` | Port of anchors.js (face candidates around a desired point ahead/up, 30-40 m band over the street, raycast confirm, `OnModel` probe, low zip-point fallback, cone rays) + zippoints.js (roof edge / corner / water-tower points from boxes, screen-centre targeting with hysteresis). No tree anchors. |
| `WebTraversalComponent.*` `UWebTraversalComponent` | Port of traversal.js: 120 Hz substeps; modes ground/air/swing/wall/zip/perch; kin moves vault/cornerWrap/wallHop; jump charge, landing tiers, glide, dive, corridor, facade avoid, side peel, rope wrap/reanchor, pump/climb assist/first-arc motor, drag, release boosts, momentum chain, tricks (TRICK_DEF, boost at snap), wall run/zip/corner/hop, zip bezier with speed profile, perch, point/anchor launch, web dash, quick boost. Writes `Anim` (C1), `Events`, `Strands[2]`. Browser function order kept. |
| `WebTravCamera.*` `FWebTravCamera` | Yaw auto-recenter + FOV/kick/punch/shake/roll/motion-blur from camera.js; composition replaced in round 03/05 by `ComposeChase` (see §3); round 16: `ChooseFlipView` + the held trick camera blended onto the chase in polar coordinates (§3 "Round 16"). Outputs `CamPos` (m), `CamRot`, `OutVFov` (VERTICAL deg), `MotionBlur`, `HeroDist`, `bCamInGeometry`. |
| `WebTravCharacter.*` `AWebTravCharacter` (+ `AWebTravGameMode`) | Pawn: Enhanced Input built at runtime (RMB/R2 swing, Space/A jump, Shift/R2 sprint, E/MMB/Y/L2+R2 zip, C/Ctrl/B drop, Q/L1 quick, F/X trick, WASD/LS, mouse/RS look). Tick: input (live or script) → camera look → traversal → events→camera → camera → actor + FollowCamera (absolute; vertical→horizontal FOV) → figure root (BodyQ + trick spin + air sway) → anim drive → webs → telemetry. Hero mesh `SetupHeroMesh` (axis correction from ref pose), placeholder block figure fallback, web strands = 2×12 cylinder segments (min ~1.6 px width, retract on release, culled within 3 m of lens), hero pixel-mask capture (telemetry only). |
| `WebTravFlips.*` (round 11) | Pure flip-program module: `EWebFlipShape` (Tuck, Pike, Layout, Swan, Pencil, Straddle, Throne, Twist, Reach -> clips `flip<Shape>`), programs `backDouble`, `frontPikeSwan`, `corkscrew`, `backSingle`, `wallFront` (segments of shape + duration + twist), `WebFlips::Sample(P, t)` -> pitch / twist / rate + upper-body shape blend (sampled `FlipLead` 0.04 s ahead) and legs blend (`FlipLag` 0.07 s behind). Used by the traversal (durations), the character (root rotation) and the anim instance (shapes). |
| `WebTravScript.*` `UWebTravScript` | GameInstance subsystem: `-WHTravScript=<json>` playback, `-WHTravCsv`, `-WHTravSeed`; mini JSON parser (the Json module is not a direct Build.cs dependency — Build.cs is integrator-owned). |
| `Anim/WebTravAnimInstance.*` `UWebTravAnimInstance` + `FWebTravAnimProxy` | No AnimBP: game thread picks a node from C1 (ground loco blend walk/jog/run/sprint by speed; land_*; swing 3-way low/bottom/high + L variants + corner bank; zip_*; perch_*; wall crawl/run/side/corner/zip; air cycle timelines; trick_*), crossfades with browser TRANS times; proxy `Evaluate` samples/blends `UAnimSequence`s, spine bank, web-arm aim (upper arm → anchor, elbow eased straight). Clips from `/Game/Traversal/HeroDev/<clip>`. Round 06: wall-run node = the `sprint` clip at 1.8-2.6 steps/s by wall speed (own phase `WallRunPhase`); `topOut` node = `releaseFlip` (T x 0.72, held at 0.78 s + 0.45 `fallCalm`); `land_landTopOut` = `perchLand` from 0.12 s; trick→air blend 0.22 s. |

**Hero asset paths are data (round 10, Manhattan issue P3-1):** `AWebTravCharacter` properties `HeroMeshPath`, `HeroLensMeshPath` (empty =
no separate lens mesh), `HeroClipRoot`, `HeroClipPrefix` (clip asset = `<root>/<prefix><browser clip name>`), `UPROPERTY(Config)` under
`[/Script/WebHomage.WebTravCharacter]` in the Game ini, overridable by a Blueprint subclass / placed actor and by the command line
`-WHHeroMesh= -WHHeroLens=none -WHHeroClips= -WHHeroClipPrefix=`. Defaults = the HeroDev proxy. P2 hero:
`-WHHeroMesh=/Game/Characters/Hero/SK_Hero.SK_Hero -WHHeroLens=none -WHHeroClips=/Game/Characters/Hero/Anims -WHHeroClipPrefix=A_Hero_`
(not captured this round; hero_swap_check.json says all 58 bones match by name).

Content (`build_traversal.py`, idempotent, commandlet): materials `/Game/Traversal/Materials/{M_TravFacade, M_TravGround, M_TravColor}`
(custom HLSL), map `/Game/Tests/Traversal/Trav_Canyon` (1.6 km avenue, 98 m blocks, 80-300 m towers, 40 % podium+setback, row 2,
water towers; seed 20260929; game-mode override `WebTravGameMode`; layout → `docs/night1/traversal/trav_canyon_layout.json`),
hero `/Game/Traversal/HeroDev` from `public/assets/spiderman.glb` (webp → png via `sips` into `Saved/HeroDev.glb`, Interchange import,
clips renamed to their exact names; mesh `/Game/Traversal/HeroDev/HeroDev/SkeletalMeshes/SpiderMan`, `Lenses`).

## 2. C1 anim struct (`FWebTravAnim`, positions cm, velocity cm/s)
`Mode` (Ground/Air/Swing/Zip/Perch/Wall/Land), `FromMode`, `Sub` (browser sub names), `T`, `ModeT`, `Speed` (m/s), `Velocity`,
`bGrounded`, `JumpCharge`, `Swing{Phase -1..1, Bank, Tension, Anchor, bRightHand, RopeLengthCm, Angle, Kick, Chain}`,
`Zip{Target, T, Phase fire|flight|catch, bWebs, Pitch, Dir, bDash}`, `Wall{Normal, Move, bFast, Phase, RunK}`,
`Perch{Point, Normal, Kind, Impact}`, `LandingSeverity`, `Trick`, `TrickSide`, `TrickDur`, `bDive`, `bGlide`, `FacingDeg`,
`BodyQ`, `RootPos` (feet), `StepOffset`, `bQuickActive/QuickT/bQuickRightHand`. Read via `AWebTravCharacter::GetTravAnim()`.
Round 06 sub names: air `topOut` (wall-run reached the top), land `landTopOut` (its crouch landing; `IsLand` includes it).

Round 19 additions: `WebTravWorld` boxes-only filter (`Allowed`, `AllowedComps`, `LastGroundSrc`); `WebTravAnchors::bHighFix`;
`UWebTraversalComponent::NearestZip`, `LastZipWhy`, `FlipRng`; `WebTravFlips` variants (`MakeVariant`, `FindBase`, per-program `Lead/Lag/Ver/Scale`);
`FWebTravAnimFrame` wall gait / swing shaping / tuck fields; `FWebTravAnimWall::Point/Up`; character `PollLiveInput`, `WatchInput`, `InputTestTick`.

## 4. Commands
Round 10: everything runs in the integrated lit city `/Game/Maps/Manhattan` (golden), built IN THIS WORKTREE by piece C's
`Scripts/build_manhattan.py` (unchanged) with this piece's scratch: city export from our own vite on :5204
(`node tools/export/export_city.mjs --url http://127.0.0.1:5204/ --out $S/export/midtown3x3 --profile $S/chrome-profile`, then
manifest `5204/` -> `5202/`), then `SM2_MANHATTAN_SCR=$S SM2_MANHATTAN_PRESETS=golden python3 unreal/WebHomage/Scripts/build_manhattan.py
--steps city_prep,city,traversal,characters,look,map` with `S=/Users/midir/sm2-n1/_scratch/traversal/manhattan` (~10 min of commandlets;
`_scratch/traversal/manhattan/run_rest.py <steps>` runs the same with a tighter slot wait: `pgrep -x UnrealEditor`, 5 s polls — the
`pgrep -f` pattern also counted python wrappers and the build waited 70 min). All -nullrhi commandlets; still waits while 3+ run.
`capture_round.sh` / `probe.sh` default to `/Game/Maps/Manhattan` and the `scripts/city/` scripts; `rhythm_check.py` (T1-T4, T7
engine side; heights = feet over the street) and `spec_cam_check.py` (`AVENUE_YAW=90`: the Manhattan avenue runs north-south).
```
docs/night1/traversal/build_p3.sh   # rm WebHomage dylibs + UnrealEditor.modules, then Scripts/build_editor.sh
# (F1's wrapper alone can leave UnrealEditor.modules pointing at a deleted hot-reload dylib -> "Incompatible or missing module")
UnrealEditor <abs uproject> -run=pythonscript -script=<abs>/Scripts/build_traversal.py -unattended -nullrhi   # content, ~40 s
docs/night1/traversal/capture_round.sh docs/night1/traversal/round-NN [seq ...]   # 1080p60 movies + 4K stills + telemetry
Scripts/run_game.sh <out> -map /Game/Tests/Traversal/Trav_Canyon -res 1920x1080 -quit 16 -name r -- -nullrhi -benchmark -fps=60 \
   -WHTravScript=<abs json>                          # fast headless telemetry probe (no pixels: px_* need a real render)
python3 docs/night1/traversal/px_check.py  <telemetry.csv> <label> [tmax]   # hero pixel height (≥160 px share), anchor on screen at attach
python3 docs/night1/traversal/anim_check.py <telemetry.csv> <label>   # T-pose frames, 6 fps air silhouettes, repeated cycles
python3 docs/night1/traversal/cam_check.py  <telemetry.csv> <label>   # model bbox, in frame, cam-hero distance, cam in geometry, pitch
python3 docs/night1/traversal/drop_test.py  <telemetry.csv> [--skip-first]   # release->low point drop ≥15 m, arcs differ
python3 docs/night1/traversal/cadence_check.py <telemetry.csv> <label> [12]   # attaches, swing s, web-less gaps, drop, rope on screen, body vs rope
python3 docs/night1/traversal/facade_check.py <telemetry.csv> <label> t0:t1 ...   # rendered: wall_frac <= 0.30, hero never occluded, facade distances
python3 docs/night1/traversal/spec_cam_check.py <telemetry.csv> <label> [t0 t1]   # TRAVERSAL-SPEC T8-T14, T16, T19 (rendered)
# spec video instruments (venv: uv venv specv --python 3.12; uv pip install opencv-python-headless numpy scipy):
#   python ~/sm2-n1/_scratch/director/specs/tools/vp_cam.py <mp4> <out prefix> 6 ; .../nearflow.py 8 <mp4>
python3 docs/night1/traversal/flip_check.py <telemetry.csv> <label>   # round 11: FLIPS_SPEC F1-F5, F7-F11 per trick (rendered body axis, px height)
python3 docs/night1/traversal/sky_check.py <round dir> <clip> ...   # TC-I (round 16): POOLED over the clips, >= 35 % of 10 fps trick samples with ring >= 50 % sky (40 px ring around the hero mask bbox) AND hero h >= .15; (r12-r15: >= 70 % per clip)
python3 docs/night1/traversal/apex_check.py <telemetry.csv> <label>   # round 12: per flip program: height over the solver's tallest roof, release -> start, flip camera view, next web
python3 docs/night1/traversal/flow_check.py <telemetry.csv> <label> [--video <mp4>]   # round 13: critic r12 test -- release->shape <= .25 s, reach->attach <= .3 s, T4 <= 3.1 s, T2 <= 3.3 s, per-frame camera <= 3 deg / 4 deg / 1.2 m, flip-camera blend-out >= .4 s, backDouble <= 2 shapes, hero V (video)
GPU_OUTER=1 docs/night1/traversal/capture_round.sh ...   # round 12: inside ONE outer `gpu_slot.sh capture --label traversal -- <batch script>` hold (max 40 min): no per-run queueing
python3 docs/night1/traversal/wall_check.py <telemetry.csv> <label>   # wall-run: limb phases @6 fps, head>hips, steps/s, px in frame through top-out
python3 docs/night1/traversal/roof_check.py <telemetry.csv> <label>   # round 17: per flip -- apex hips vs the lower roofline within 30 m (city/heightmap_5m.csv.gz), share of rows >= roofline + 3, flipcam_k at flip_t .35, view_sun min, side / tier
python3 docs/night1/traversal/trickcam_check.py <telemetry.csv> <label> [--video <mp4>]   # round 16 v2: TRICK_CAMERA_SPEC tests TC-A..TC-K (WIN = program + 0.5 s, HOLD = program rows with flipcam_k >= .9; TC-C on the rendered hero mask, TC-H suit-mask luma from the video, TC2 fallbacks listed); `python3 docs/night1/traversal/tc_table.py <round dir>` = clip x test table
python3 docs/night1/traversal/suncam_check.py <telemetry.csv> <label> [--video <mp4>]   # round 15: critic r14 test -- U1 pitch <= 10 up, U2 trick <= 8 up, S1 trick view >= 100 deg from the sun, T11 median 4-12 down, L1 hero-box luma >= 245 <= 5 %, L1h suit-mask variant (unreliable when the hero is fully white), per-flip height over the roofline
python3 _scratch/traversal/r14/sidesky.py <ns|ew> <h over street> x0,x1,y0,y1 [step]   # round 14 (scratch): offline side-view ring-sky potential from the r12 heightmap (where a side-on flip can have sky behind it)
python3 _scratch/traversal/r14/flipsim14.py <variants.py>   # round 14 (scratch): offline flip rate model with segment ease (same integration as WebTravFlips)
python3 docs/night1/traversal/scripts/bake_keys.py <auto.json> <telemetry.csv> <out.json> <name>  # rule → plain timed keys
python3 docs/night1/traversal/make_shotlist.py <round dir> "round NN" <commit>   # neutral SHOTLIST.md
```
After an interruption / reboot re-run only what is missing: `capture_round.sh <round> <seq>` (movie + 4K stills of that sequence, plus the warm-up render unless `SKIP_WARM=1` — keep it after a reboot / DDC wipe; the replay
is deterministic, so a re-run reproduces the telemetry exactly). `Scripts/run_game.sh -timeout N` ends with `kill -9` of the engine when N wall seconds
pass (integrator-owned file, breaks the RULES no-SIGKILL law): keep `-timeout` well above the real run length (capture_round.sh uses 2400-3000 s) and
stop a stuck run with `stop_ue.sh "<worktree>"`. `spec_check_round.sh <round dir>` writes SPEC_CHECK.txt (its YOLO step uses `device='mps'`: wrap it in
`gpu_slot.sh capture --label traversal --`; reuse the cached `_scratch/traversal/specwork/<label>/*_dets.json` when re-running).
capture_round.sh renders an unrecorded 960x540 warm-up pass first (shader compile after a DDC wipe) and runs every sequence with a 0.8 s pre-roll that is trimmed.
Tuning without a rebuild: `-WHTravTune=MaxArcRope=30,PendingVz=5` (any float UPROPERTY of the traversal component).
RULES: never a 4th Unreal instance (capture_round.sh waits; probe loops should `pgrep -f 'MacOS/UnrealEditor( |$)'` first).
Telemetry (round 06 adds `head_hip_dz`, `limb_z`; round 07 `body_rope_deg`, `web_on`; round 08 `wall_frac`, `hero_occl` from a full-scene depth capture) quirk: `anim_*`, `pose_sig`, `head_hip_dz`, `limb_z`, `pcm_*`, `px_*` are sampled at the start of the next frame (mesh evaluates / camera
manager caches / capture renders after the actor tick); the checkers shift them one row. Stop only your own processes:
`pkill -9 -f "/Users/midir/sm2-n1/traversal/unreal/WebHomage/WebHomage.uproject"`.

## 5. Script format (`docs/night1/traversal/scripts/*.json`, metres, UE axes, yaw deg)
```
{ "name": "...", "seed": 1234,
  "spawn": { "pos": [x,y,z], "yaw": 0, "camPitch": 0.12, "vel": [vx,vy,vz] },
  "keys": [ { "t": 0.0, "move": [0,1], "heading": 0, "swing": true, "jump": false, "sprint": false, "zip": false,
              "drop": false, "quick": false, "trick": false, "look": [yawDegPerS, pitchDownDegPerS], "flip": "backDouble,corkscrew",
              "autoChain": true, "releasePhase": 0.95, "gap": 0.3, "repressVz": 0.0, "trickEvery": 2 } ] }
```
Round 17: top-level `"tune": "Name=V,..."` (traversal float UPROPERTYs, as `-WHTravTune`) and `"camTune": "Name=V,..."` (camera doubles, as `-WHCamTune`) apply at BeginPlay before the command line (the f-series carry `ArcLowMin=14,ArcDropShallow=8,ArcDropDeep=12,WallClearance=9`).
Keys hold until the next key; omitted fields keep their value. `heading` = stick set each frame to that world yaw relative to the
camera (`"heading": false` clears). `autoChain` = release when swing phase > releasePhase while rising (or at the forward apex),
re-press after `gap` once vz ≤ repressVz; `trickEvery` N presses trick on every Nth release. Round 07: the release also
needs the swing to have come down first (vz < -3 m/s); a/d rule = releasePhase 0.7, gap 0.15, repressVz 99, trickEvery 3. `*_auto.json` = rule form; the
capture scripts `a_swing_chain`, `d_sprint_jump_first_swing` are baked (bit-identical replay verified); `b`, `c` are hand-timed
(zip timings depend on camera pose — re-verify b/c after any camera change). Sequences: a (spawn 22 m, first press 0.4 s, 15.6 s),
b (spawn 58 m, swing → release+trick 3.2 s → dive → zip 4.8 s → perch), c (street → wall-run up B04_N0 podium → roof → camera
turn → zip to roof edge → perch; round 06: the turn key looks UP, `look [-150, -10]`, or the zip finds no target), d (street sprint → charged jump → first swing → chain, 12 s).
Round 11: f1/f2/f3 (swing from 30 m at x 250, sky launch = jump + trick at 1.4 s with `flip` forced, web re-pressed 0.28 s before the program's
end, then autoChain without tricks), f4 (a-style chain, `trickEvery` 1, `skyEvery` 2, `skyTricks` 1, program list cycled). `capture_round.sh`
knows them; `NO_STILLS=1` skips the 4K stills run, `SKIP_WARM=1` the warm-up (the shared GPU queue is ~2-10 min per acquisition).
Round 12: f1/f2/f3 = west avenue x -250 from y 170 / 180 / 190 heading south (yaw 90, 28 m, 24 m/s), autoChain from 0.4 s with `skyEvery` 1
(a release is a sky launch only where `SkyPeakNeeded` clears the roofs; the first reachable one is the 2nd release at y ~210), `flip` forced;
f4 = same avenue from y 120, 13 s, `skyEvery` 1 (one launch fits in 13 s); f5 = r11's f1 stretch (x 250 north) under the same rule (no launch).
The GPU queue was 4-30 min per acquisition this round: batch several runs in one hold (`GPU_OUTER=1`, `_scratch/traversal/r12/cap_batch2.sh`).
Round 13: f1_flow_backDouble / f2_flow_pikeSwan / f3_flow_corkscrew = west avenue x -250 from y 170/180/190 heading south, autoChain from
0.4 s, `trickEvery` 2, `skyEvery` 0, `flip` forced; f4_chain_flips = same avenue from y 120, 13 s, `trickEvery` 1 (programs cycled);
f5_canyon_backDouble = Midtown x 250 north, `trickEvery` 2; a / d = the chain with `trickEvery` 3 (unforced: programs cycle); b = release +
trick at 1.4 s (frontPikeSwan), drop 3.05-3.3 s, zip 3.35 s. The r12 `f*_sky_*` scripts are deleted (sky launches are off).
Never `pkill -f` a pattern that can match your own gpu_slot / batch processes (round 13 killed its own capture batch with `[c]ap_batch.sh f[14]_`):
kill by PID.

## 6. Known issues / open (after round 22)
- **w1 not on the sunlit tower** (director asked w1 AND w2): probes t1_a / t1_b (jump at the tower face, vertical run, E at 3.6 s) stayed below the lit band
  (z < 50); try spawning at z ~50 (podium top is 32-33 m, x -234..-228) or a later E. Recapture w1 + x2 with the final build and `SSw=28`.
- Side-run camera on corners: the first tower attempt (t2_c, spawn y -61) hit the recessed core face (x -224.4) in the notch and wrapped the corner --
  the wall camera swung 90 deg and lost the hero (hero_occl 1.0, cx -0.22). Keep side runs >= 4 m from face ends; the camera is frozen (TC-A..K).
- The tower face is reached by a jump from the avenue, not a swing (no swing anchor put the hero on a lit face in the 18 route probes; the swing routes
  south of y -512 hit faces with no collision or south faces). A swing entry needs anchors near x -250, y -60..-30 at z >= 50.
- G22 cannot be measured from telemetry (`anim_weight` = total clip weight); no shot-list clip has a standing start.
- Carried: x2 post-cancel camera whip (cx .17, 2.5 m); T7 roofline altitude; web on 55 % of a (T3 45 %); tuck wrist-shin .34-.45 m; repeated glide pose
  (a 4.25 / 10.25 / 14 s); s1 sun flare; leaves over the hands (a 12 s); "POP TH… SUMM…" billboard (P4).

## 7. Critic history (summary; full table in `git show 047a342:docs/night1/traversal/HANDOFF.md` §7)
| Round | Scores (swing/camera/web/moves/body, flips) | Biggest gap |
|---|---|---|
| r18 | 7/6/6/6/6, flips 7 -- FAILS TARGET | every trick a canned playback, loose tuck; wall-run is a crawl |
| r19 | 6/4/6/4/5, flips 7 -- FAILS TARGET | wall-run frog scramble; black frames; parapet hides perch; RMB waits |
| r20 | 7/6/6/6/6, flips 7 -- FAILS TARGET | side-run plank, legs together; c setback = 3 m hop; w2 side run 0.31 s |
| r21 | 7/6/6/6/6, flips 7 -- FAILS TARGET (`critic/round-21-CRITIC.md`), merged | side run a slither (box wider than tall 29/44), facade luma 15-30 |
| r22 | not judged yet -- pack `_scratch/critic-P3-r22/pack` (side runs w1 / w2 vs S3 side run, vertical vs glass, swing / flips, r21 vs r22 side-run progress) | -- |

## 8. Queue for the next session
1. Run the blind critic on `/Users/midir/sm2-n1/_scratch/critic-P3-r22/pack` (key `pack.key.json` stays outside the pack; rebuild with
   `round-22/tools/critic_make_pairs.sh`); record `critic/round-22-CRITIC.md` + §7.
2. The 12 fps frame test PASSED (9/10), so per the director the next target is decided after the critic. Director's fallback list if the wall run is
   frozen: swing/camera -- camera after a swing-cancel yaw <= 90 deg/s and distance >= 3.5 m; roofline apex every 4 s; web on-screen <= 45 %
   (camera items need a TC unfreeze from the director). Owner priority #1: the most beautiful swinging.
3. Small r22 follow-ups: make `SSw=28` the compiled default; w1 onto the tower; recapture w1 + x2 with the final build.
4. Re-capture recipe: `_scratch/traversal/r22/batch_a.sh` (probes -> pick -> GO/NOGO -> captures `SEQS_A`), `batch_b.sh` (tower probes -> pick ->
   w2 + `SEQS_B`); wrap each in ONE `GPU_SLOT_CAPTURE_WAIT_TIMEOUT=14400 nohup .../gpu_slot.sh capture --label traversal -- <batch>` (max hold 40 min;
   copies in `round-22/tools/`). The GPU queue was 2-3 h per hold tonight; launch holds with the CURRENT `slots` value (the monitor clamped it to 1 at
   01:04; waiters keep the env they started with -- r22 stopped and re-queued its own waiters). Then `r22_checks.py` + `make_shotlist.py`.
5. Ask the integrator to merge night1/traversal if the critic passes (no axis below r21 [7,6,6,6,6,7]).
6. Teardown once the r22 critic has run: `_scratch/traversal/r22/probe/*`, `_scratch/critic-P3-r21/` (the 27 GB capture frame folders
   `_scratch/traversal/capture/*` were deleted at the end of r22; the movies + telemetry are committed).
