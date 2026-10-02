# P3 Traversal + camera — handoff (round 22)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

**Status (round 22, 2026-10-02 00:50, Opus 5.5): code built + pushed; route probes and captures QUEUED behind the shared GPU lock (not run yet).**
Round 21 critic FAILED TARGET (7/6/6/6/6/7; `critic/round-21-CRITIC.md`): side run "a slither" (box wider than tall in 29/44 w2 frames), facade luma 15-30.
Director r22 target: wallRunSide = upright parkour sprint on a SUNLIT facade (torso <= 30 deg off wall-up, chest along the run line, alternating
contacts <= .18 s, along-run foot sep peak >= .6 m and >= .3 m for >= 70 %), box h >= w in >= 80 % of w1+w2 side frames, facade luma >= 45, no
mullion over the hero, w2 3.1-3.85 s at 12 fps legs apart >= 7/10; keep c's r21 vertical-run numbers; TC-A..K frozen (no WebTravCamera edits); no
flip-code edits (f1/f4 telemetry bit-identical to r21). If r22 fails the 12 fps test: freeze the wall run, switch to swing/camera (see §8).

### Round 22 -- what changed (A/B at run time)
| # | Item | Fix (file) | A/B flag (r21 values) |
|---|---|---|---|
| 1 | Side run = plank / slither | `WallSideUpright`: upright runner side-on to the facade -- body up = wall-up leaned `WallSideLeanDeg` 14 fwd along the run line and `WallSideOutDeg` 16 out from the wall, chest along the run line, root `WallSideFootOff` .36 m (feet ~.1 m off the face, hips ~.36 m); `W.SideUpK` blends it in (12/s) / out (8/s) (`WebTraversalComponent.cpp` Orient) | `-WHTravTune=WallSideUpright=0` |
| 2 | Legs / arms for the upright run | `FWebTravAnimFrame::SideUpW`, `WallZ`: legs stride along the run line under the hips (touchdown .45 / toe-off .50 leg lengths, smootherstep recovery, heel tuck .55, recovery toe 14 cm off the face, stance reach .95), knees forward; sprint arm pump contralateral, elbows back; shoulders counter-rotate about the body axis (`Anim/WebTravAnimInstance.cpp`) | `-WHGaitTune=STd=,STo=,STuck=,SSw=,SReach=,SArm=` |
| 3 | Characters critic: idle -> run = 1-frame weight pop | ground locomotion weights (idle/walk/jog/run/sprint) move <= 1/0.18 s per s (`GroundW`, first frame of the node snaps; moving phase rate = r21) | `-WHGaitTune=GBlend=0.02` |
| 4 | Telemetry | `torso_wallup_deg` (3D hips->head vs wall-up), `chest_run_deg`, `side_up_k`, `ankle_sep_plane_m` | -- |
| 5 | Sunlit route | w1/w2 moved to the west face of the 96 m tower at x ~267.5, y -620..-570 (park to its west; sun yaw -178 elev 8 => lit from ~15 m up); variant auto-picked by `round-22/tools/pick_route.py` from -nullrhi probes, scripts written by `make_final.py` | r21 scripts: `git show 5f1970b:docs/night1/traversal/scripts/city/w2_wallrun_side_zip.json` |

Checker: `python3 docs/night1/traversal/r22_checks.py <round dir> --sheets <dir> --prev docs/night1/traversal/round-21` (U22 torso/stride, B22 box,
L22 facade luma + hero_occl, F22 12 fps frame test, C22 c kept, I22 f1/f4/c/a vs r21 cell by cell, G22 ground blend). On round-21 it reproduces
the critic: w2 box tall 13/41, luma 14-27, F22 4/10.
Queue state: two holds enqueued 00:31 (`_scratch/traversal/r22/holdA.log` / `holdB.log`, PIDs in `hold*.pid`): A = 18 -nullrhi probes
(`r22/PROBES`) -> pick -> w1/w2 scripts -> waits <= 6 min for `r22/GO` (extra game args) or `NOGO` -> captures `SEQS_A` (c w2 w1 x2 s1 r1);
B = `SEQS_B` (a f1 f4 x1 m1). The lock queue was stuck behind a 3 h look hold and waiters launched with the old 1-slot env.

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

## 6. Known issues / open (after round 21)
- **Setback crossing camera** (c ~3.5 s): the wall camera follows the hero 4 m inward onto the ledge and sits right behind his hips for ~0.1 s.
  The crossing pose (face-down on the ledge) reads as a roll from below. Next lever: hold the wall camera's XY during the `MantleStep` path.
- **Knees** stay close to the facade (median .05-.10 m): physically right (hip flexion points the knee at the wall) but "knee lifting off the wall"
  is mostly the knee rising up the run. `-WHGaitTune=PoleN=` (more negative = closer) / `-WHTravTune=WallGaitFootOffR=` (hips further out) tune it.
- **x2** side run is cut by RMB at 0.35 s by design (S21 FAIL row is the x2 cancel test, not a regression). r22 secondary: x2 post-cancel camera
  whip (yaw <= 90 deg/s, distance >= 3.5 m, cx .44-.56).
- **s1 vertical run** body-to-wall-up only 27 % within 15 deg (short run after a 33 m/s impact). **r1** perch path shares c's opening.
- Carried: corkscrew variation pair 24 deg/s; short tucks; mouse stop only watchdogged; foliage not counted in hero_occl; web on > 45 % of a; T7 altitude.

## 7. Critic history (summary; full table in `git show 047a342:docs/night1/traversal/HANDOFF.md` §7)
| Round | Scores (swing/camera/web/moves/body, flips) | Biggest gap |
|---|---|---|
| r16 | 7/5/6/6/6, flips 6 | tricks shot into a dark facade facing the sun |
| r17 | 7/6/6/6/6, flips 6 | frozen inverted split |
| r18 | 7/6/6/6/6, flips 7 -- FAILS TARGET | every trick a canned playback, loose tuck; wall-run is a crawl |
| r19 | 6/4/6/4/5, flips 7 -- FAILS TARGET (`critic/round-19-CRITIC.md`) | wall-run frog scramble; black frames; parapet hides perch; RMB waits |
| r20 | 7/6/6/6/6, flips 7 -- FAILS TARGET (`critic/round-20-CRITIC.md`) | side-run plank, legs together (w1 legs apart 0/6 frames); c 3.55 s setback = 3 m hop; w2 side run 0.31 s |
| r21 | not judged yet -- pack `_scratch/critic-P3-r21/pack` (vertical run vs glass, side runs w1 / w2 vs S3 side run, swing / flips, r20 vs r21 side-run progress) | -- |

## 8. Queue for the next session
1. Run the blind critic on `/Users/midir/sm2-n1/_scratch/critic-P3-r21/pack` (never hand it `pack.key.json`); record `critic/round-21-CRITIC.md` + §7.
2. Re-capture recipe: `cd /Users/midir/sm2-n1/_scratch/traversal/r21`; `SEQS` lists the batch-1 sequences, `probe_batch.sh <probes>` runs -nullrhi
   probes, then waits <= 10 min for a `GO` file (extra game args; `VARS` lines "tag|args|jobs" run variant probes meanwhile), then captures `SEQS`;
   `cap_batch2.sh <seqs>` = straight captures. Wrap each in ONE `GPU_SLOT_CAPTURE_WAIT_TIMEOUT=10800 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label traversal -- ...`
   (never while `PAUSED` exists; never build while a capture runs). Then `r21_checks.py` + `r20_checks.py` + `make_shotlist.py`.
3. Ask the integrator to merge night1/traversal if the critic passes (Moves >= 7, no axis below r20 [7,6,6,6,6,7]).
4. r22: x2 camera whip; setback-crossing camera (§6).
5. Teardown once the r21 critic has run: `_scratch/traversal/capture/*` frame folders, `_scratch/traversal/r21/probe/*`, `_scratch/critic-P3-r20/`.
