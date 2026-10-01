# P3 Traversal + camera — handoff (after round 19)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

**Status (round 19, 2026-10-01, Opus 5.5): owner-playtest fixes built, captured and checked; blind critic NOT run yet.**
Pack: `/Users/midir/sm2-n1/_scratch/critic-P3-r19/pack` (6 pairs, built by `_scratch/critic-P3-r19/make_pairs.sh`; answer key beside it, refcuts scratch-only).
Round dir `docs/night1/traversal/round-19/` (movies, telemetry, `R19_CHECK.txt`, `SHOTLIST.md`, `inputtest_*.log`, `floor_{on,off}.csv.gz`, `probes/`).
Batch B captures (b, d, f5, s1, f2) were queued behind the owner's game (`gpu_slot` waits on "owner game running"); see §8 if they are missing.
Older history (rounds 01-18 architecture notes, per-round checks, critic table): `git show 047a342:docs/night1/traversal/HANDOFF.md` (98 KB).

Owned paths: `unreal/WebHomage/Source/WebHomage/Traversal/**`, `/Game/Traversal`, `/Game/Tests/Traversal`,
`unreal/WebHomage/Scripts/build_traversal.py`, `docs/night1/traversal/**`. Branch `night1/traversal`, worktree `~/sm2-n1/traversal`.
Integration (`origin/Opus-5.5-Loop-Night-1`) is merged up to 690dfa7 (e8cba9f). GPU cap is ONE heavy renderer; every engine run goes through
`/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh`; `PAUSED` = no launches (CPU work only); stop with `stop_ue.sh "<worktree>"`, never kill -9.

## 0. Round 19 — owner playtest bugs (2026-10-01, live mouse+keyboard play) and what was done

| # | Owner report | Root cause found | Fix (file) | Proof |
|---|---|---|---|---|
| 0 | "Landing in mid-air and being able to run is still around" | 690dfa7 only de-collided components > 60 m wide; smaller visual meshes with simple-collision hulls stayed traversal solids. Floor audit: the Times Square screen / frame / sign meshes (`tsFrames`, `tsScreens`, ...) put invisible floors up to **99 m above the real roofs** (x -40..60, y -310..-210; 61 grid cells, 144 m floor over a 45 m roof) | Boxes-only solid filter: in a map with WHBox per-building boxes, `FWebTravWorld::Raycast` re-traces past any hit that is not a WHBox cube or a WHGround actor (<= 8 layers), `PushOutCapsule` ignores them, `GroundHeight` takes the ray surface (ground tiles only as fallback), thick WHGround actors are no floor boxes. `-WHTravSolidFilter=0` = old (A/B) (`WebTravWorld.*`) | `round-19/floor_{on,off}.csv.gz` (5 m grid, `-WHTravHeightmap` now writes the traversal floor + source), `R19_CHECK.txt` §F; every landing on a non-box / non-ground floor now logs `WH_TRAV landing on a non-traversal floor` |
| 1 | RMB swing "eventually breaks" | (a) **High-band search bug**: above street + ~30-40 m the anchor search aimed 1.5-2.5 m over the body while `TryStartSwing` refuses any web under `AnchorMinAbove` 3 m -> every candidate rejected; only cone rays / roof-edge fallbacks rescued some presses (the higher he climbs -- wall runs, rooftops -- the deader RMB gets). (b) defensive: held buttons were Enhanced-Input event latches | (a) high band aims >= 4 m (+4 m target) over the body, low zip-point fallback needs >= 3 m (`WebTravAnchors.cpp`, `-WHTravHighFix=0` = old). (b) live buttons / sticks are POLLED from the player input key state every frame; a skipped frame (pause) or 0.3 s real-time gap re-arms held buttons as fresh presses; the "behind the body" web rule only at > 6 m/s (`WebTravCharacter.cpp` `PollLiveInput`, `WebTraversalComponent.cpp`) | s1 A/B (`round-19/probes/s1_high_swing_probe_{r18hf0,r19}_telemetry.csv`): RMB at 48 m: first web 0.93 s later with the r18 search (fell 15 m in a dive) vs 0.40 s; second press 0.40 s vs 0.0 s. Input repro `-WHTravInputTest=pauseRelease` (real key events injected through the controller, pause, release during the pause, re-press): 5/6 presses swing with BOTH paths (the 6th is held across the pause, correctly no new swing) -> the event-latch theory is NOT reproduced; polling kept as hardening |
| 2 | E (zip) does nothing while running on the side / top of buildings | E was ignored during any kinematic move (vault / corner wrap / wall hop), in a side run it needed a highlighted point, in a wall run it always did the facade burst, on a roof run with nothing highlighted it was dead | E from every mode: a kinematic move is cut; highlighted point first, else `NearestZip` (on a wall: the top edge of this facade if <= 58 m up; else the nearest visible roof edge / corner in front of the camera), else wall burst / perch launch / air dash. `WH_TRAV zip press: <mode> -> <why>` log + `zip_why` telemetry (`WebTraversalComponent.cpp`) | `R19_CHECK.txt` §Z: w1 wall run -> `facadeTop` zip -> perch on the 97 m roof, perch E -> zip; r1 roof run -> zip; w2 side run -> wall burst (facade top 97 m > 58 m range) |
| 3 | Wall-run animation "super cooked" | r06-r18 wall run = the ground sprint clip on a rotated body at 1.8-2.6 steps/s while moving 15 m/s (sliding feet, legs kicking off the wall, body rolling sideways) | Procedural IK stride (`Anim/WebTravAnimInstance.cpp`, proxy `TwoBone`): contralateral gait 3.4-6 steps/s from wall speed; stance feet planted on the facade and swept down it (push), knees drive up-and-out between contacts; hands plant above the shoulder and pull down to the hip (palm on the wall), elbows out; shoulders counter-twist with the arms; head looks up the wall; base pose = upright idle. Body leans 0.28 rad off the wall, hips 0.28 m from it (`WallGaitLean/FootOff`). Same stride on side runs. `-WHWallGait=0` = r18 | `R19_CHECK.txt` §W: >= 1 limb on the facade 100 % of stride frames, feet on the wall 62-75 %, hands 46-59 %, 5.6-5.7 steps/s, head above hips 100 % (vertical). Movies `w1_wallrun_tall_zip.mp4` (long run up the 97 m tower), `c_wallrun_perch.mp4`, `w2_wallrun_side_zip.mp4` |
| 4 | Swing / in-air poses at speed not good enough | swing legs = clip only; air attitude upright at any speed | Swing: legs IK-trail the velocity at the arc bottom (straight, together, slight scissor), knees tuck on the rising front, the free arm opens against the arc (weight 0.65). Air: a fast descent tips the body toward the flight path (sky-dive 0.85 rad, dive / glide 1.25 rad). The release-cycle tuck closes into a tight tuck (`TuckW`) | `a_swing_chain.mp4` (frames checked: arm along the web, legs trailing together, tuck ball, horizontal sky-dive between webs) |
| 5 | Mouse "stops working" (camera no longer turns) | Not reproduced offscreen (no real window). Candidates: the viewport losing its mouse capture / focus while the controller still believes it has it (GameOnly input mode only captures on focus change), a hidden un-captured cursor drifting onto the second display | Capture watchdog: player has the game captured, app active, no menu, but the viewport has no capture for 0.3 s -> re-take focus + capture + lock + high-precision mouse (rate 1/s). `WH_INPUT` log lines on every state change (player-captured / viewport capture / viewport focus / app active / menu), a 10 s summary (mouse px, rmb presses, swings, failed searches, zip presses, recaptures) and `WH_INPUT swing press from X: no web after 0.6 s (...)` diagnosis; telemetry `in_cap, vp_cap, vp_focus, look_px` | Needs the owner's next live log (`~/Library/Logs/WebHomage/` of the integrated build -- read by the integrator, not by loop agents) |

Critic r18 gap: per-trick variation + tight tuck.
- `WebFlips::MakeVariant` (called in `StartTrick`): each instance scales the program 0.78-1.22 from release speed (fast -> shorter) and apex height
  (high -> longer) + 5 % jitter, jitters each segment 0.92-1.08 (renormalised) and its ease, and its own arm lead 0.02-0.08 s / leg lag 0.05-0.11 s;
  `Find()` returns the live variant (durations, catch window, camera, anim all agree), `FindBase()` for planning (FitFlip). Own RNG stream
  (`FlipRng`), so the swing solver's random sequence is unchanged. `-WHFlipVar=0` = off. Measured scales 0.84-0.99 (the f-series release fast).
  §V: every same-type pair differs by 42-435 deg/s in at least one 0.1 s sample (f1 6 pairs, f4 2 pairs) -> PASS.
- Tight tuck (proxy): knees pulled to 8 cm from their midpoint, each hand IK'd to its shin a third down from the knee, weight from the program's tuck
  share. §T: f1 / f4 backDouble tucks: wrist-shin 0.03-0.04 m, knees 0.15-0.16 m, closed 0.75-1.08 s -> PASS. The short tucks (frontPikeSwan 0.38 s,
  wallFront 0.27 s) close for 0.13-0.20 s only (segment too short for the 0.25 s hold; not in the critic's f1 / f5 test).

New telemetry columns (appended): `in_cap, vp_cap, vp_focus, look_px, ground_src` (0 none, 1 ground box, 2 ground mesh, 3 building box, 4 other;
read 0.4 m under the feet, so a hero standing on a roof can read 1), `wall_ik_w, gait_ph, swing_leg_w, tuck_w, tuck_wrist_shin_m, tuck_knee_gap_m,
flip_scale, foot_wall_l/r, hand_wall_l/r` (m off the facade while on a wall), `zip_why`.

New scripts (`scripts/city/`): `w1_wallrun_tall_zip` (c's swing-to-wall shifted 95 m south onto the 97 m tower x 266 y 88-122), `w2_wallrun_side_zip`,
`r1_roofrun_zip`, `s1_high_swing` (48 m over the y -560 street, RMB held). `capture_round.sh` knows them and now passes `-WHTravMask` (integration
gated the hero-mask telemetry behind it). Checker: `python3 docs/night1/traversal/r19_checks.py <round dir>` -> `R19_CHECK.txt` (W / Z / V / T / I / F).
Probe batch: `_scratch/traversal/r19/probe_batch.sh input floor s1old <script>:<quit s> ...` (nullrhi, inside one `gpu_slot.sh capture` hold).

Captures (round-19): 1920x1080 movies, internal 1920x1080 (`r.ScreenPercentage 100`, TSR + Lumen), fixed 1/60 s step, 0.8 s pre-roll trimmed, no 4K stills.
GPU shared -> every run `contaminated` (no perf claim).

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

## 6. Known issues / open (after round 19)
- **Mouse stop** (bug 5) is only instrumented + watchdogged, not reproduced: ask the integrator for the owner's next live log and grep `WH_INPUT`.
  If `viewport capture 0` appears while `player-captured 1`, the watchdog's `recapture` lines show whether it recovered.
- **RMB latch theory not reproduced** by `-WHTravInputTest=pauseRelease` (both paths 5/6). The confirmed swing failure is the high-band one (fixed).
  Other ways RMB "does nothing" by design: on the ground it only hops into a swing when an anchor >= 6 m up exists; above all nearby roofs there is
  no anchor (the glide takes over); a held RMB on a wall keeps wall-running (release + press to kick off and swing).
- **Wall stride**: hands reach the facade ~50 % of frames (shoulders 0.40 m off it); the hands do not visibly reach high above the head as in the ref
  (`refs/traversal/clips/wallrun-glass-midday`). Tunables: `OUp` 0.62 La, `WallGaitLean` 0.28, `WallGaitFootOff` 0.28. The entry blend from the swing
  shows one frame of an arm out sideways (c 2.6 s). Side runs keep the body's head pointing along the travel (horizontal body).
- **Solid filter scope**: only maps that carry WHBox cubes (Manhattan); props / street trees / Times Square boards are now pass-through for the
  traversal (the camera sweeps still collide with them). A building missing from the browser's collision.json is not a solid any more.
- **E on a side run** with the facade top > 58 m up: still the vertical wall burst (no nearest point found in front of the camera there).
- **Short tucks** (frontPikeSwan / wallFront) close < 0.25 s; lengthen those segments if a critic demands it.
- Pre-existing (r18): TC-C knife-edge on backDouble, foliage not counted in hero_occl, web on > 45 % of a, a / b still Midtown canyons.

## 7. Critic history (summary; full table in `git show 047a342:docs/night1/traversal/HANDOFF.md` §7)
| Round | Scores (swing/camera/web/moves/body, flips) | Biggest gap |
|---|---|---|
| r16 | 7/5/6/6/6, flips 6 | tricks shot into a dark facade facing the sun |
| r17 | 7/6/6/6/6, flips 6 | frozen inverted split |
| r18 | 7/6/6/6/6, flips 7 -- FAILS TARGET (`critic/round-18-CRITIC.md`) | every trick a canned playback, loose tuck; secondaries: foliage at arc bottoms, web 53 % on a, wall-run is a crawl |
| r19 | not judged yet -- pack `_scratch/critic-P3-r19/pack` (wallrun, wallrun-flip, swing-chain, multi-flip, chain-flips vs refs; r18 vs r19 wall-run progress) | -- |

## 8. Queue for the next session
1. If `round-19/` lacks b / d / f5 / s1 / f2 movies: `cd /Users/midir/sm2-n1/_scratch/traversal/r19 && SKIP_WARM=1 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label traversal -- ./cap_batch.sh <seqs>`
   (one batch at a time, never while `PAUSED` exists, never build while it runs), then `python3 docs/night1/traversal/r19_checks.py docs/night1/traversal/round-19`.
2. Run the blind critic on `/Users/midir/sm2-n1/_scratch/critic-P3-r19/pack` (do not hand it the key); record `critic/round-19-CRITIC.md` + §7.
3. Ask the integrator to merge night1/traversal (owner bug fixes) and to grep the owner's next live log for `WH_INPUT` / `WH_TRAV landing on a non-traversal floor` / `zip press`.
4. Wall stride polish (§6), then the r18 secondaries.
5. Teardown: `_scratch/traversal/capture/*` frame folders can go once the r19 critic has run.
