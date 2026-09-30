# P3 Traversal + camera — handoff (after round 10)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

Branch `night1/traversal`, worktree `~/sm2-n1/traversal`, UE MCP port 8773 (never used; everything runs through commandlets and `-game`).
Owned paths: `unreal/WebHomage/Source/WebHomage/Traversal/**`, `/Game/Traversal`, `/Game/Tests/Traversal`,
`unreal/WebHomage/Scripts/build_traversal.py`, `docs/night1/traversal/**`.

## 1. Architecture map (Source/WebHomage/Traversal)

| File / class | What it does |
|---|---|
| `WebTravTypes.h` | `FWebTravInput` (held + edge flags: move, look, swing, jump, sprint, zip, drop, quick, trick), `FWebTravAnim` (C1 anim contract, see §2), `FWebTravEvent`, `FWebTravStrand` (web strand state). |
| `WebTravWorld.*` `FWebTravWorld` | World queries in METRES: `Raycast` (line trace, WorldStatic/Dynamic, ignores the pawn), `GroundHeight` (downward trace + terrain boxes tagged `WHGround`), `PushOutCapsule` (overlap + `ComputePenetration`, horizontal MTD), `SphereSweep`/`SphereOverlaps` (camera), `Near` (24 m XY grid of building AABBs), `Inside`. |
| `WebTravAnchors.*` `FWebTravAnchors` | Port of anchors.js (face candidates around a desired point ahead/up, 30-40 m band over the street, raycast confirm, `OnModel` probe, low zip-point fallback, cone rays) + zippoints.js (roof edge / corner / water-tower points from boxes, screen-centre targeting with hysteresis). No tree anchors. |
| `WebTraversalComponent.*` `UWebTraversalComponent` | Port of traversal.js: 120 Hz substeps; modes ground/air/swing/wall/zip/perch; kin moves vault/cornerWrap/wallHop; jump charge, landing tiers, glide, dive, corridor, facade avoid, side peel, rope wrap/reanchor, pump/climb assist/first-arc motor, drag, release boosts, momentum chain, tricks (TRICK_DEF, boost at snap), wall run/zip/corner/hop, zip bezier with speed profile, perch, point/anchor launch, web dash, quick boost. Writes `Anim` (C1), `Events`, `Strands[2]`. Browser function order kept. |
| `WebTravCamera.*` `FWebTravCamera` | Yaw auto-recenter + FOV/kick/punch/shake/roll/motion-blur from camera.js; composition replaced in round 03/05 by `ComposeChase` (see §3). Outputs `CamPos` (m), `CamRot`, `OutVFov` (VERTICAL deg), `MotionBlur`, `HeroDist`, `bCamInGeometry`. |
| `WebTravCharacter.*` `AWebTravCharacter` (+ `AWebTravGameMode`) | Pawn: Enhanced Input built at runtime (RMB/R2 swing, Space/A jump, Shift/R2 sprint, E/MMB/Y/L2+R2 zip, C/Ctrl/B drop, Q/L1 quick, F/X trick, WASD/LS, mouse/RS look). Tick: input (live or script) → camera look → traversal → events→camera → camera → actor + FollowCamera (absolute; vertical→horizontal FOV) → figure root (BodyQ + trick spin + air sway) → anim drive → webs → telemetry. Hero mesh `SetupHeroMesh` (axis correction from ref pose), placeholder block figure fallback, web strands = 2×12 cylinder segments (min ~1.6 px width, retract on release, culled within 3 m of lens), hero pixel-mask capture (telemetry only). |
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

## 3. Changes vs the browser build (and why)
- **Travel-plane pivot** (`PivotLateralKeep` 0.1; browser = 1): the browser pivots on the real anchor; a facade anchor 15-25 m to
  the side swung him into cross streets and walls. Web still draws to the real anchor; steering rotates the pivot about the body.
- **Deep pendulum** (round 02, critic "flat swings"; round 07 retuned for cadence): each swing's virtual pivot is built so
  the arc bottoms at `ArcBottomMin..Max` 5-12 m over the floor (random) and ≥ `MinArcDrop` 14 m + 0..`ArcDropJitter` 5 m below
  entry; rope ≤ `MaxArcRope` 34 m x (1 - `RopeCapJitter` 0.12 x rand) = 30-34 m; pivot ≥ `MinPivotRise` 6 m above the body;
  ahead ≤ `MaxPivotAhead` 30 m. (r02-r06: 16 m drop, 50 m rope, 55 m ahead -> 2-4 s swings.) Replaces browser SWING_DIP (r10f) in this mode.
  `CanyonDipK` / `MinPivotElevDeg` still apply in the reanchor path (`PivotFor`).
- **Tricks only on input** (round 04; browser: ~80 % of releases). Trick input buffers 0.4 s (release or in air).
- **Camera** (rounds 03-05, replaces camera.js composition): 3.8 m behind the lagged heading yaw (horizontal spring 0.07 s,
  held 3.5-5.0 m), 1.1 m above (vertical spring 0.05 s, held 0.7-1.8 m), 0.3 m shoulder; yaw toward hero; pitch puts the hero's
  screen centre at 0.48 (arc bottom) .. 0.40 (arc ends), clamped 5-22° down; attach beat (SwingT < 0.5 s): pitch up / yaw / widen
  (≤ 26° vfov) so the anchor is in frame; sphere-swept collision with clear-orbit search, cut instead of passing < 3 m;
  view held when the hero himself clips geometry. FOV formula, kick/punch/shake, motion blur are the browser's.
- **Wall-run body** (round 06, critic r05; browser user feedback #5 had "run cycle rotated onto the wall", body up = wall normal):
  body up = along the wall, forward = into the wall, leaned back `WallRunLean` 0.16 rad x RunK; feet `WallRunFootOff` 0.42 m
  off the wall plane while running (0.30 crawling). Anim = sprint stride, steps/s from wall speed.
- **Wall camera** (round 06): `WallK` spring (0.16 s in / 0.22 s out) blends the chase position to 2.2 m below + 2.2 m out from
  the hero (`WallCamBelow/Out`; floor-clamped at street +0.6 m, then pushed out to keep `WallCamDist` 3.2 m), yaw to the wall,
  pitch from framing (hero at `WallFrameS` 0.68), lower pitch clamp opens to 80 deg up, +4 deg vfov. Held on while the top-out
  rises (`topOut` && vz > 0), using the last wall XY so it does not follow him inward.
- **Top-out** (round 06): `StartWallHop` run branch launches `topOut` (inward 3.0 + up 11.5 m/s, was jumpLaunch 2.6 + 12-15);
  `Land` after it = `landTopOut` (LandLock 0.34, Lim 0.62 s, severity >= 0.3). The flip is the clip's own somersault (no
  figure-root spin; `releaseTuck` only does half a flip).
- **Swing cadence** (round 07, critic r06: ~4 s cycles, 1.5-2 s web-less falls; ref ~5 swings in 8 s): release keeps at most
  `ReleaseVzMax` 8 m/s up (16 m/s within 12 m of the floor, eased to 8 at 24 m), the rest becomes forward speed (browser
  REL_UP_VY floor made every release a 1-2 s ballistic climb). StepAir: a fresh swing press resets the search throttle (it was
  swallowed by `SearchT` left over from the previous search), and a held button re-searches from `ReattachAfter` 0.22 s after a
  release even while rising. A web found while rising faster than `PendingVz` 5 m/s is attached at once (`bWebPending`,
  strand drawn, arm aimed) and its pendulum starts at vz <= 5 or after `PendingMax` 0.5 s (a taut rope on the rise flung him up the
  back of the arc and stalled ~1.3 s; a slack-rope variant lost the drop). Result on a: 7 attaches in 12 s, swings 1.1-1.75 s,
  next web 0.15 s after a release (0.63 s after a trick release).
- **Body along the web** (round 07, critic r06 "plank ~45 deg off the rope"): the anim proxy rotates `hips` so hips->head
  points at the anchor, `BodyAlignW` = 1 - 0.4 |phase| while a web is held (0.2 s ramps); measured <= 12 deg at the arc bottoms.
- **Camera round 07**: `ChaseHeight` 1.8 (held `CamZMin..Max` 1.2-2.6), `PitchDownMin` 10 deg (critic: 10-25 deg down in canyons);
  attach look-up x clamp(1 - (fall - 8) / 14) and 12 deg bottom margin (the new swoops dropped the hero off the frame);
  attach yaw turn capped 25 deg, 0.12 s spring (a 45 deg / 0.1 s whip in d).
- **Canyon keeping** (round 08, critic r07: arcs carried him into facades, a 14.3 s / d 6.9 s): `Corridor()` rewritten. 8
  horizontal rays (every 0.05 s) find facade planes beside the travel direction (|N . heading| <= 0.5); along each normal the
  approach speed is capped at 2.5 m/s per m above `WallClearance` 3.5 m; between two opposite walls a damped spring
  (`WallKeepRate` 2.5 /s) steers to 1.2 /s x (metres off the centre line), <= 8 m/s. Runs while swinging and in the air from the
  release on (was: only >= 0.9 s after a release). The old version pushed away from the nearer wall with no damping and
  measured drift in the velocity's own frame, so chains zig-zagged into facades and out through intersections. A stick pushed
  into a near wall (<8 m) disables it (wall-run intent). Result: a / d stay within ~2 m of the centre line, >= 13 m from facades.
- **Camera facade clearance** (round 08): sideways rays from the camera; spring toward `CamWallSoft` 3 m, hard `CamWallHard`
  1.5 m, never moved past the hero's line of sight.
- **Blur / web** (round 08): motion blur 0 below 28 m/s, 0.35 x smoothstep(28, 50) (dive x 1.3), max 1-3 % (was 0.15 base, up
  to 0.65, max 7 %); web strands 1.2 cm / >= ~1.2 px, grey, no emissive (was 2.2 cm, emissive 0.35 -> bloom).
- **TRAVERSAL-SPEC** (director, 2026-09-29, `~/sm2-n1/_scratch/director/specs/TRAVERSAL-SPEC.md`) is the target from round
  09 on: it voids the r08 critic's 30-70 % screen weave (T9: hero centred), the r06 ">= 75 % rope on screen" (T3: 25-45 %)
  and anchor-in-frame demands (T5). From round 10 captures run in the lit `Look_Midtown_golden` map (P4), not Trav_Canyon.
- **Weave + alternating arcs** (round 09): `ArcDropShallow` 10.2 / `ArcDropDeep` 17.5 m alternate by swing index (+0-1.5 m); a
  high anchor lowers the virtual pivot to keep the low point. `AnchorAltDeg` 30: the anchor SEARCH heading leans toward the
  side opposite the previous web (`LastAnchorSide`; the swing plane keeps the travel heading — passing the rotated heading to
  StartSwing threw him down a cross street). Corridor: while swinging the target line is `WeaveK` 0.45 x the active anchor's
  offset from the centre (<= `WeaveAmp` 6 m); in the air no centring inside +/-8 m; clearance limits unchanged.
  `PivotLateralKeep` 0.25 (was 0.1).
- **Camera round 09**: `ChaseHeight` 0.6 (band 0.2-1.8), `PitchDownMin` -8, framing 0.44 / 0.37 (T11 pitch median 4-12 down,
  T10); side slide `AnchorShift` 1.3 m toward the active anchor while in a swing chain (`SideK`, 0.3 s; `bInChain` ends after
  0.8 s without a web, in a dive, on ground / wall / perch / zip — the side view spoiled b's zip aim), roll <= 6 deg at the
  arc ends only (T13). A screen-space side offset of the hero (built first) was reverted per the spec.
- **Round 10 — altitude rhythm (critic r09 single gap T3/T4/T7):** a *sky launch* = jump-release with a trick buffered
  (`ReleaseSwing`): the launch speed is solved so the apex lands `SkyRoofOver` 3 m over the LOWER street wall's roofline ahead
  (`RoofBesideAhead`: per 10 m sample up to 60 m ahead a sideways ray finds each street wall, a down-ray 2.5 m inside it finds that
  wall's roof; side roofline = lowest sample; box AABBs were tried first and reported 225 m towers for a 45 m wall), clamped to
  `SkyPeakMin..SkyPeakMax` 38-58 m over the street and `SkyLaunchVz..SkyLaunchVzMax` 26-52 m/s; climb gravity x`SkyRiseK` 1.4, hang x0.55
  under 7 m/s. The next web is a long one (`SkyRopeMax` 50 m rope / pivot reach) designed to bottom `ArcLowMin` 5 + 0..4 m over the
  street (`StreetHeight` ignores trees / awnings / props). Camera during the rise: sinks `SkyCamBelow` 1.2 m under him, frames him at
  0.40, looks up <= 10 deg (`SkyK`). No web is searched on the way up.
- **Round 10 autoChain (script rule, `WebTravCharacter` Tick):** a release is a sky launch when >= `skyEvery` releases after the last
  one AND the lower street wall ahead is reachable (roof + 3 <= SkyPeakMax + 8), or 5.5 s after the last one anyway; skyPhase 0.8;
  the sky re-press waits until he has fallen 12 m from the peak (or `skyRepressH`, or `skyMax` s); 2 tricks chained in the air. Plain
  releases: releasePhase 0.55, re-press after `gap` 0.8 s. Any swing is let go 1.25-1.55 s in (varies by release count) once past its
  low point (T1 <= 1.6 s), and a stale swing after 2.4 s whatever its phase (Manhattan issue: releasePhase 0.85 hung him at 49 m).
- **Round 10 turns into facades (Manhattan issue P3-2):** while swinging, touching a wide facade with the stick held INTO it (and the
  stick direction itself blocked within 12 m, so a corner grazed while turning into a cross street does not count) lets go of the web
  and starts a wall-run up it (`N_swingToWall`); the air-contact wall entry uses the same "stick blocked" test. Result: no more
  swinging in place against the facade; a turn toward a block climbs it (top-out, then the chain continues over the roofs).
- **Round 10 rope placement:** a new web never anchors below `AnchorMinAbove` 3 m over the body or behind it (critic r09 b 2.0 s).
  No held reach pose while searching (critic r09 a 7.7 s raised-fist hang without a rope).
- **Round 10 camera:** attach look-up stops where the hero centre reaches `AttachMaxS` 0.64 of the frame (T5 voids anchor-in-frame;
  it drove cy to .87), attach springs 0.035 -> 0.12 s, the first composed frame starts AT its framing / attach targets (b 0.0 s pop:
  FrameS sprang from 0.55), arc-bottom framing `FrameLowS` 0.44 -> 0.50 (T10 spread), roll: yaw-rate lean 0.04 -> 0.03 (cap 4 deg),
  bank 0.05 -> 0.04, leans under `RollDeadDeg` 1 deg dropped (T13 median).
- **Pop fixes** (round 06): body roll / pitch leans are springs (`RollA/PitchA`, rate 14); the character's air-sway weight
  `SwayW` ramps 0.2 s (was full amplitude the frame a trick ended); chase pitch may pass 22 deg down when collision lifts the
  camera (hero centre kept <= 0.62 of the frame).
- Other: terrain boxes are always a floor (thin ground slab bug); swing anchor lean is horizontal only.

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
python3 docs/night1/traversal/wall_check.py <telemetry.csv> <label>   # wall-run: limb phases @6 fps, head>hips, steps/s, px in frame through top-out
python3 docs/night1/traversal/scripts/bake_keys.py <auto.json> <telemetry.csv> <out.json> <name>  # rule → plain timed keys
python3 docs/night1/traversal/make_shotlist.py <round dir> "round NN" <commit>   # neutral SHOTLIST.md
```
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
              "drop": false, "quick": false, "trick": false, "look": [yawDegPerS, pitchDownDegPerS],
              "autoChain": true, "releasePhase": 0.95, "gap": 0.3, "repressVz": 0.0, "trickEvery": 2 } ] }
```
Keys hold until the next key; omitted fields keep their value. `heading` = stick set each frame to that world yaw relative to the
camera (`"heading": false` clears). `autoChain` = release when swing phase > releasePhase while rising (or at the forward apex),
re-press after `gap` once vz ≤ repressVz; `trickEvery` N presses trick on every Nth release. Round 07: the release also
needs the swing to have come down first (vz < -3 m/s); a/d rule = releasePhase 0.7, gap 0.15, repressVz 99, trickEvery 3. `*_auto.json` = rule form; the
capture scripts `a_swing_chain`, `d_sprint_jump_first_swing` are baked (bit-identical replay verified); `b`, `c` are hand-timed
(zip timings depend on camera pose — re-verify b/c after any camera change). Sequences: a (spawn 22 m, first press 0.4 s, 15.6 s),
b (spawn 58 m, swing → release+trick 3.2 s → dive → zip 4.8 s → perch), c (street → wall-run up B04_N0 podium → roof → camera
turn → zip to roof edge → perch; round 06: the turn key looks UP, `look [-150, -10]`, or the zip finds no target), d (street sprint → charged jump → first swing → chain, 12 s).

## 6. Known bugs / open issues
- **Round 10 (Manhattan):** a street-level sprint into the avenue facades hits the P1 storefront awnings / canopies at 3-5 m: the
  wall-run starts, is capped by the awning and falls back (hops in place; c had to start airborne). Needs a wall-run that climbs
  around thin overhangs (or P1 awning collision off).
- Turning into a block now wall-runs up it: into a 200 m tower that is a 10+ s vertical climb (probe turn_mid); a turn at a cross
  street at 38 m/s cannot make the 17 m street and climbs the corner block (probe turn_x2), then continues west over the roofs.
- Sky launch peaks are capped at 58 m: where both street walls are 68-300 m (most of Midtown's avenue) the peak is under the
  roofline; the autoChain rule therefore launches where the lower wall is reachable (45-52 m lofts), and forces one 5.5 s after the
  last anyway.
- d: the sprint-jump start keeps hero x p95 at .56-.57 (T9 edge) and pitch median low during the street run.
- **White / blown-out suit at clip starts** (round 06, diagnosed): auto-exposure lag. The first engine frames are dark, exposure
  climbs, and the bright street takes ~1.5 s to adapt back; with `r.EyeAdaptationQuality 0` the suit renders correctly from frame
  0, Lumen reflections off did not change it, and an AutoExposureSpeed override on the camera did not help. Fix: capture pre-roll
  `-WHTravPreroll=<s>` (character renders the start pose, traversal only posed via `PosePreview`, camera state restored each
  frame, anim instance reset at the end; traversal + camera telemetry bit-identical to no pre-roll, body pose differs in the first
  0.27 s). `capture_round.sh` uses 0.8 s, trims the movie to the telemetry rows and shifts still times. Hero textures are also
  forced resident, and a warm-up render compiles shaders after a DDC wipe. A player in a live session still sees the adaptation.
- **b zip framing**: hero ≥160 px only in 41 % of b frames (median 140, min 0 during zip/perch). Zip flight at 50-60 m/s and
  perch orbit search pull the camera far / behind; not tuned in round 05 (test only covered a).
- Anchor on screen at the attach FRAME only 2/4 in a (4/4 within 0.1 s) — the camera turns after attach, no anticipation.
- d: 7 frames at the arms-up jump launch exceed 0.30 model bbox (round 04 rule).
- c: 1 of 7 air sample pairs shares a silhouette (short hop onto the roof); c zip lands on its own podium edge (target hysteresis
  keeps the nearer point); zip perch points can sit 0.3 m from a taller neighbour's wall (hero clips it on arrival, b 5.6 s).
- Round 07 swings stay 18-23 m over the street (entry) and bottom out 5-10 m over it; each swing opens with a steep swoop
  (the rope starts near horizontal, up to ~40 m/s down). b's script had to move its release to 3.0 s (the trick at 3.2 s became
  a layout with a held end pose); b now perches on a different roof corner (z 34.5 m).
- Interchange renames bones (`upperArm.R` → `upperarm_r`); code uses `upperArm_R` style (FName is case-insensitive). P2's hero
  swap = change `ClipRoot` and the mesh paths in `SetupHeroMesh`.
- Wall-run (round 06): the stride is the ground sprint clip on the wall (no authored wall-run cycle, no hand plants, no foot IK
  on the facade); side runs (`wallRunSide`) keep the old chase framing blended with the wall camera but were not captured.
- c after the top-out: when the camera turns 180 deg on the 10 m podium strip it is squeezed against the tower and lifts 2-5 m
  (occlusion search), looking down steeply; the zip target then depends on the look-up in the script.
- Not ported: slingshot, tightrope, water/bridge bounces, car roofs, tree anchors, web slack/whip, zip reticle, look-at, foot IK.

## 6b. Round-06 checks (captures in `round-06/`, all from the rendered videos' telemetry)
| Check | Result |
|---|---|
| Wall-run limb phases @ 6 fps (need >= 4) | 14 distinct |
| Head above hips, wall-run samples | 17/17 |
| Steps/s on the wall | 2.84 (L/R foot crossings) |
| Hero pixel box fully in frame, wall-run -> top-out -> landing (1.33-5.85 s) | 272/272 frames |
| Wall camera | pitch up to 55.7 deg, 2.2 m below, 3.1 m from the hero |
| a pixel framing (>= 160 px) | 90.5 % (r05 90.4 %) |
| Swing drop (a, d) | PASS / PASS |
| T-pose frames, same-silhouette air pairs (a/b/c/d) | 0 / 0 |
| Camera in geometry (all four) | 0 frames |
| Suit colour at clip starts | shaded from frame 0 (pre-roll) |
Open: model-bbox check (CAM_CHECK) flags c 1.52-2.50 s (padded bone boxes touch the edge; pixel box stays inside) and
6.97-7.17 s (roof camera turn); b hero >= 160 px only 41.9 %; the stride on the wall is the ground sprint clip.

## 6c. Round-07 checks (captures in `round-07/`, from the rendered videos' telemetry)
| Check (a_swing_chain, first 12 s unless noted) | Result |
|---|---|
| Web attaches (need >= 7) | 7 |
| Attach -> release | 1.10-1.75 s, mean 1.38 |
| Next web after a release | 0.15 s (0.63 s after trick releases) |
| Rope on screen (web stuck + hero in frame, need >= 75 %) | 81.1 % |
| Body vs rope at the arc bottom (need <= 15 deg) | max 10.5 deg |
| Drop per swing (>= 10 m, a and d) | a min 11.7 m, d min 10.6 m; DROP TEST PASS / PASS |
| Pixel framing >= 160 px | a 92.8 %, b 90.2 %, c 95.0 %, d 94.3 % |
| T-pose / same-silhouette air pairs / camera in geometry (all four) | 0 / 0 / 0 |
| Wall-run (c): limb phases, head > hips, hero in frame through the top-out | 14, 17/17, 272/272 |
Notes: d starts on the street (first web at 2.7 s), so its 12 s window has 5 attaches and 69 % rope; the targets are for a.
Camera snaps (per-frame camera move > hero move + 0.5 m, or yaw > 6 deg) in the headless runs: none in a / b / c / d.

## 6d. Round-08 checks (captures in `round-08/`, from the rendered videos' telemetry)
| Check | Result |
|---|---|
| a 13.5-15.5 s / d 6.5-7.5 s: near-wall share (non-hero, non-street pixels within 6 m), need <= 30 % | 0 % / 0 % (whole a, d, b-to-zip: 0 %) |
| Hero occluded (> 2 % of his pixels behind geometry) | 0 frames in a, b, d |
| Hero / camera to nearest facade while swinging | a >= 13.1 / 13.2 m, d >= 13.6 / 13.4 m (r07: 1.1 / 1.2 m, 0.6 / 1.6 m) |
| Pixel framing >= 160 px | a 91.9 %, b 95.2 %, c 95.0 %, d 95.5 % |
| Cadence (a, 12 s) | 7 attaches, swings 1.15-1.75 s, rope on screen 81.1 %, body vs rope <= 4.4 deg |
| Drop test a / d, T-pose, air variety, camera in geometry | PASS / PASS, 0, 0, 0 |
| Wall-run (c) | 14 limb phases, 17/17 head up, 272/272 in frame |
Notes: the attach FOV widening is capped at 10 deg (`AttachFovMax`, was 26; its 92-95 deg frames shrank the hero). The swing
chain now runs close to the canyon centre line (|y| < 2 m on a) — the weave is gone; a later round may want a gentle, bounded
weave. b perches on the B03 podium roof (198.6, 15.4, 49.6).

## 6e. Round-09 checks (captures in `round-09/`; SPEC_CHECK.txt = TRAVERSAL-SPEC lines)
| Spec line (a_swing_chain, chain window 0.4-15.6 s) | engine side | video instrument |
|---|---|---|
| T8 hero height / frame (med 0.15-0.23, p10 >= .09, p90 <= .38) | p10 .177 p50 .219 p90 .270 PASS | — |
| T9 hero centre x p5-p95 in .44-.56 | .463-.545 PASS | — |
| T10 hero centre y spread >= .20, range .20-.70 | .354-.726 (spread .372) FAIL: dips to .73 in fast swoops | — |
| T11 pitch down med 4-12, p95 15-30, p5 -10..3 | -8.2 / 11.5 / 22.0 PASS | vp_cam 3.0 / 11.8 / 22.1 |
| T12 yaw off axis med 2-10, p90 10-25 | 7.6 / 14.2 PASS | vp_cam 7.5 / 14.1 |
| T13 roll med <= 1.5, p90 <= 10 | 1.5 / 3.1, max 3.4 PASS | vp_cam 1.6 / 3.2, max 53 (13.8-14.0 s: VP misreads; engine max 3.4) |
| T14 hFOV 100-110 | med 104.1 PASS | vp_cam 102.7 |
| T16 hero in frame >= 94 %, T19 never occluded / camera never in geometry | 100 %, 0 / 0 PASS | — |
| T17 near-field coverage p50 .20-.45, p90 <= .55 | — | nearflow .29 / .46 PASS |
| T18 side third p50 .45-.65, > 50 % in 40-80 % of frames | — | .48, 47 % PASS |
| Arc low points vary (brief: >= 3 m) | 9.2/2.9/7.7/4.1/7.1/3.5/8.7/4.4, min diff 3.1 m | — |
| Facade clearance (hero >= 3 m, camera >= 1.5 m) | hero >= 5.7 m, camera >= 5.0 m | — |
Not addressed this round (spec lines untouched): T1-T3 cadence — a has 7 attaches / 12 s (~4.7 per 8 s, spec 2-4) and web
on ~80 % of the chain (spec 25-45 %): round 10 should lengthen the web-less flips/dives (T4 allows <= 3.1 s with a changing
pose) and hold webs 0.5-1.6 s. T6 rope angle/width not measured yet (width set to >= ~2 px). T20/T21 blur not measured.
d (street start in its window) passes 4/9: pitch p5 -11, yaw p50 10.0, hero x p95 .62 and y .82 during the sprint-jump
start; its swing part looks like a. Other checks: pixel framing >= 160 px 96-98 %, drop test PASS/PASS, air variety 0 held
pairs, T-pose 0, camera in geometry 0, wall-run 14 phases / 17-17 / 272-272.

## 7. Critic history (blind critic vs Marvel's Spider-Man 2 refs; arc / camera / web / moves / body)
| Round | Scores | Biggest gap | What changed next |
|---|---|---|---|
| r01 | 3/3/3/2/2 | Swings flat: hero holds one height down a rail corridor | r02 deep pendulum, height-driven pitch, web retract |
| r02 | 3/2/4/3/3 | Camera: fixed offset, rigid lock-behind, clips into hero (b 5.5 s, c 6.5-7.2 s) | r03 chase camera + collision + framing checks |
| r03 | 3/3/4/2/2 | Dead air phase: rigid T-pose placeholder between release and attach | r04 real hero GLB + C++ anim, air-cycle variety, tricks on input |
| r04 | 4/3/4/3/4 | Framing: hero 4-6 % of frame, camera far/steep, no sky; metric distrusted | r05 close camera, attach look-up, pixel-true measurement |
| r05 | 5/3/5/4/3 | Wall-run: camera behind/below pitched 20-35° up the facade with the roof edge; head-up body, alternating hands/feet 2-3 steps/s; test ≥4 limb phases at 6 fps, head above hips, hero in frame through the top-out (ref wallrun-glass-midday 2-6 s) | r06 head-up sprint-stride wall-run, up-the-facade wall camera, flip top-out + crouch landing, release pop springs, suit warm-up |
| r06 | 4/4/5/4/4 | Swing cadence: ~4 s cycles, 3 attaches in 12 s, 1.5-2 s web-less falls; target attach->release 1.2-1.8 s, next web <= 0.5 s, no web-less fall > 0.6 s without a trick, body within 15 deg of the rope at the bottom; test >= 7 attaches in 12 s, rope on screen >= 75 % | r07 short virtual-pivot arcs, release climb cap, immediate re-search + pending attach on the rise, body-along-web, canyon camera pitch |
| r07 | 4/3/4/4/4 | Facade clearance + occlusion during swings (a 14.3-14.8 s, d 6.8-7.3 s): path >= 3 m from walls, camera >= 1.5 m, no facade > 30 % of frame, hero never occluded; also blur on everything, thick blooming rope (orchestrator: the critic's "hero 6-8 % of frame" was wrong, ~17 %) | r08 wall-frame canyon keeping, camera wall clearance, wall_frac / hero_occl capture, blur only at speed, thin matte web |
| r08 | 4/4/4/3/3 | Locked symmetric camera + identical swings (critic asked 30-70 % screen weave — voided by TRAVERSAL-SPEC T9); orchestrator/spec: lively weave inside the safe corridor, camera 2-25 deg off axis, near facade in a side third 40-80 % of frames, pitch median 4-12 down, hFOV 100-110, arc low points vary | r09 alternating arc depth, alternating anchor sides + bounded weave, camera side slide + arc-end roll, lower camera, dark 2 px rope, crouch-first landings |
| r09 | 5/6/4/5/5 | T3/T4/T7: four identical 2 s swings, rope on screen 52-67 %, never at roofline height | r10 Manhattan captures, roofline-solved sky launch + long web back to the street, rope 25-45 %, swing-to-wall-run turns, configurable hero paths |
| r10 | (critic pending) | | |

Round folders `docs/night1/traversal/round-0N/` hold videos, stills, telemetry, SHOTLIST, CRITIC and the check outputs.
