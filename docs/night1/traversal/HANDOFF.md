# P3 Traversal + camera — handoff (after round 25)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

**Status (round 25 DONE, 2026-10-02 23:25, builder Claude Opus 5.5 high via Devin): build 4 = HEAD code.** Clips in `round-25/`
(1920x1080 movies, internal 1920x1080 = `r.ScreenPercentage 100`, offscreen -game, fixed 1/60 s step, <= 15 MB): see
`round-25/CLIPS.md` for the build each clip was captured on and its path/camera check (builds 2-4 change only the web strand drawing).
11 clips captured this round (a, c, p1, w1, w2, r1, s1, m1, x1, x2, f1); f4 not re-captured (r24 file, build-4 probe
bit-identical); no 4K stills. Measurements: `round-25/ROPE_CHECK.txt`, `R25_GATES.txt`, `GAPS.txt`, `R24_CHECK.txt`, `WALL.txt`,
`OWNER_BUGS.txt`, `SIZES.txt`, `SHOTLIST.md`. Blind critic pack: `/Users/midir/sm2-n1/_scratch/critic-P3-r25/pack` (key `pack.key.json` outside; pairs
`/Users/midir/sm2-n1/_scratch/critic-P3-r25/pairs.json`; rebuild with `round-25/tools/critic_make_pairs.sh`). The critic has NOT run.
GPU worker of this round: `round-25/tools/hold4.sh <tag>` inside `gpu_slot.sh capture --label traversal --` (queue
`_scratch/traversal/r25/queue_<tag>.txt`, -nullrhi probes `probes_<tag>.txt`, extra args `tune.env`, time guard `est_scale`); queue
follow-up holds from your own shell (never inside a hold). At ~1-1.8 rendered frames/s (3 renders sharing the GPU) a 15.6 s clip takes ~19 min.
Older handoffs: r24 `git show c3415073:docs/night1/traversal/HANDOFF.md`, r23 `7a96916`, r22 `9ad5222`, r01-18 `047a342`.

## 0. Round 25 -- what changed (critic r24 biggest gap: rope readable on every web_on frame; merge gate: c perch 8.6-10.5 s; hard line: pawn run cadence)
| # | Item | Fix (file) |
|---|---|---|
| 1 | rope look, build 1 (`1034b587`) | unlit translucent two-tone strand `/Game/Traversal/Materials/M_TravWeb` (`Scripts/traversal_web_material.py`, built by `build_traversal.py` or `build_traversal_web.py`): bright core / dark rim whose share follows 4 scene-colour taps ~5 px out, divided by the eye adaptation (no bloom), screen-space width clamp. Measured 18/65 web frames (the resolved 3-4 px line averaged back to the background level). |
| 2 | build 2 (`ae40de7b`) | `RopeSolid` 1 = ONE tone over the whole strand (bright over a dark background, near-black over a bright one; switch `RopePivot` 0.20 exposed linear), translucency pass AFTER MOTION BLUR (before DOF the camera-speed blur smeared it into the background) with a manual scene-depth test in the material (`Occ` 25 cm; that pass has no engine depth test), width clamp `RopePxMin/Max` 2.8-3.4 px. 0-5 s probe 25/26; `RopePivot` 0.12 probe 25/27 with a worse whole-rope reading -> 0.20 kept. |
| 3 | build 3 (`e0ae46c9`) | `RopeKeepProxy` 1: unused segments stay registered as visible at a 1e-4 scale (a segment switched visible on the attach frame rendered one frame late). |
| 4 | build 4 (`54ddbbf5`) | `RopeWavePx` 1.5: the shot strand's travelling wave (30 cm world) bounded on screen (it put the attach-frame strand 5-15 px off its line). |
| 5 | c perch gate (build 1) | perch recenter yaw hold + zip lens dolly cap (`WebTravCamera.cpp`); body paths of c / w1 / w2 unchanged, their cameras differ from r24 only from the zip / perch on. |
| 6 | pawn run (build 1) | run anchor 9.3 m/s + weighted loco phase rate (`Anim/WebTravAnimInstance.cpp`), GroundBlendS 0.18 s kept; script `scripts/city/p1_pawn_run.json` (12 s full-stick run up the avenue). |
| 7 | a script | `repressVz` -12 -> -8 (T2 attach gaps; -nullrhi probes: -12 3.48/3.50/3.35, -10 3.43/3.43/3.33, -9 3.40/3.38/3.32, -8 3.37/3.38/3.30 with T7 100/100; -6 / -5 bring every gap <= 3.32 / <= 3.27 but T7 drops to 99 / 98 of 100: the clip-end window loses its qualifying release). |
| 8 | checkers | `rope_r25_check.py` (T5/T6 on the movie at 10 fps: hand -> frame edge along the telemetry projection, rope +-3 px re-centred, 6 px bands each side, 2-4 px measured width), `r25_checks.py` (perch gate G1, G1b), `cadence_r25.py` (head-top FFT), `round-25/tools/analyze.sh`. |

**Measured on the final captures (`round-25/`):**
| Test | r24 | r25 |
|---|---|---|
| T5/T6 rope on a_swing_chain web_on frames at 10 fps (contrast >= 25 to both 6 px bands at >= 80 % of points, median >= 25, width 2-4 px) | build 1 of r25: 18/65 | **65/65 PASS** (point-contrast median 125, p10 74; width median 3.5 px; whole-rope literal mean contrast >= 25 on 58/65); pale facades 0.9-1.1 s 3/3, dark glass 10.5-11.2 s 8/8 |
| same on m1_mouse_swing / s1_high_swing | -- | 26/26 / 39/43 (s1 fails: 0.2 s first attach, 2.7 s a 0.15 s swing (measured width 0.5 px), 5.3-5.4 s measured width 4.5 px close to the lens) |
| G1 c perch 8.6-10.5 s: in frame, cam 3.4-7 m, pitch change <= 15 deg / 0.3 s | FAIL (9 frames out of frame) | **PASS**: 113/113, 4.14-6.00 m, max 14.3 deg at 8.68 s, occl 0 |
| G1b c 7.7-8.5 s (r24 gate) | PASS | PASS (unchanged) |
| P1 pawn run head-top FFT 1.5-11 s (3.2-3.8 Hz) | -- | **3.549 Hz PASS** (mask top 3.549 Hz, 3.66 lows/s, speed 9.8 m/s, run clip on 571/571 rows) |
| T7 / T3 / T1 / T2-window / T4 (a) | 100/100, 41.5 %, pass | 100/100, 41.8 %, 1.03-1.52 s, 2-3 per 8 s, 17/17-23/23 -> all PASS |
| T2 attach-to-attach gaps (critic: <= 3.3 s) | 3.12/3.48/3.50/3.35 | 3.00/3.37/3.38/3.30 -> FAIL on 2 gaps |
| vertical run lateral knee gap median (<= .25 m) | .49 | .49 (not addressed) |

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


## 6. Known issues / open (after round 25)
- T2 attach gaps 3.37 / 3.38 s on a (<= 3.3 not met without losing T7 100/100; next lever: a later release phase or a shorter climb
  after the altitude release, re-check T7).
- T4 silhouette at 12.6-13.4 s (critic: a held sky-dive pose; the `AirFastW` arch/track layer in `WebTravAnimInstance.cpp` is a static
  pose) -- not changed. A time-varying flutter on that layer is the cheap lever (re-capture every fast-air clip after it).
- Vertical run knee_gap_lat median .49 m (target <= .25 m): not addressed (`-WHGaitTune=VKneeLat=,VTrack=` are the existing knobs).
- The strand alternates black / white along its length where the background crosses `RopePivot` (each part reads locally; the
  whole-rope mean contrast drops under 25 on 7/65 frames).
- The after-motion-blur strand is not anti-aliased by TSR (the material's 0.92-1.0 edge ramp only).
- Not re-captured this round: see `round-25/CLIPS.md` (f4 = r24 file; -nullrhi probe on build 4 bit-identical to r24).
- Carried: x2 post-cancel camera whip, T22 c pitch 55 % (r23), setback crossing posture on c 3.30-3.60 s, f4 canopy-height swings.

## 7. Critic history (summary; full table in `git show 047a342:docs/night1/traversal/HANDOFF.md` §7)
| Round | Scores (swing/camera/web/moves/body, flips) | Biggest gap |
|---|---|---|
| r20 | 7/6/6/6/6, flips 7 -- FAILS TARGET | side-run plank, legs together; c setback = 3 m hop; w2 side run 0.31 s |
| r21 | 7/6/6/6/6, flips 7 -- FAILS TARGET, merged | side run a slither, facade luma 15-30 |
| r22 | 7/6/6/6/6, flips 7 -- FAILS TARGET, mergeable | vertical run frozen, legs together |
| r23 | 7/6/6/6/6, flips 7 -- FAILS TARGET (`critic/round-23-CRITIC.md`), mergeable | swing chain altitude + rope time (T7 / T3); c camera snap 7.7-8.5 s |
| r24 | 7/6/6/6/6, flips 7 -- FAILS TARGET (`critic/round-24-CRITIC.md`), merge held on owner bug 5 | rope readable on every web frame (T5/T6) |
| r25 | not judged yet -- pack `_scratch/critic-P3-r25/pack` (swing chain x2 + perch + run at 1080p pixel scale, multi-flip, wall runs, r24 vs r25 swing and perch) | -- |

## 8. Queue for the next session
1. Blind critic on `/Users/midir/sm2-n1/_scratch/critic-P3-r25/pack` (orchestrator; key stays outside the pack); record `critic/round-25-CRITIC.md` + §7.
2. The r25 pack cuts the swing / perch / run pairs at the full 1080p pixel scale (centre 1440x1080 of both clips -> 1210x906 after abpack's 84 % crop; r22-r24 packs were 512x466: a 3 px line became ~1.3 px). Keep that for any rope judgement. swing-chain-2's reference is now `swing-low-street-speed` (the r24 `S45_chain` / avenue clips carry HUD pop-ups).
3. Teardown after the r25 critic: `_scratch/traversal/r25/` (probes, rprobe_*, dbg), `_scratch/critic-P3-r24/`, capture frame folders `_scratch/traversal/capture/*`.
