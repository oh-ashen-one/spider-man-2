# P3 Traversal + camera — handoff (after round 13)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

**Status (end of round 13, 2026-09-30 ~11:40): rendered and measured. The critic pack is built, the blind critic has NOT run yet.** Round 13
(critic r12 single gap: "each trick is an isolated set piece: rise, trick, dive, camera cut") = flow flips: a trick pressed at a web release
starts its program AT the release, the climb floats back to ~2 m over the release height, the next web attaches in the program's final Reach;
backDouble = 2 shapes (Tuck + keyed Kickout); no camera cut + a per-frame output slew limit; hero-only fill light. This session (Sonnet 5.5,
after the 06:55 reset and a reboot at ~10:00): re-probed 14d0b97 (works: backDouble / frontPikeSwan / corkscrew play), captured a, b, c, d and
f1-f5 in lit Manhattan (1920x1080 internal = output, 60 fps, 13-14 MB each, no 4K stills) and found + fixed ONE render-only regression
(commit 3b6765f): **camera hold froze in absolute space when the hero skimmed a street-tree canopy** (f4 8.75-9.17 s: camera stuck 20 m behind,
hero a dot; a 11.43-11.58 s: 10 frames, 13 m) -> hold now follows the hero. Two scripts re-tuned (f3 corkscrew now on EVERY release: on every 2nd
one the corkscrew did not fit at the low 2nd release and the 4th landed on a 14 m roof 0.3 s in; b zips at 3.08 s instead of dive + zip at 3.35 s).
**Measured on the renders** (`round-13/FLOW_CHECK.txt`, `FLIP_CHECK.txt`, `SKY_CHECK.txt`, `SPEC_CHECK.txt`, `ANIM_CAM_CHECK.txt`, `APEX_CHECK.txt`):
release -> first shape 0.00 s in every flip (<= .25); reach -> next attach -0.02..+0.27 s (<= .3; b 0.27, f4 4th flip 0.20); T4 web-less air max
0.38-1.68 s (<= 3.1); T2 attach -> attach max 2.13-2.65 s (<= 3.3); per-frame camera max |d pitch| 2.70 / |d yaw| 3.60 deg / |d pos| 1.11 m in
all nine clips (limits 3 / 4 / 1.2); no isolated image-diff spike (= no one-frame cut) in any movie except c 3.85 s (the wall top-out flip start;
telemetry camera continuous there, frames inspected: no cut); backDouble 2 shapes; 0 T-pose frames; hero V (median HSV V of the hero's central
pixels, trick frames) p50 164-222 in the f-series and a / b (critic r12 read 44/255), c wall-run flip p50 111 (min 46). **Open (numbers, not
fixed):** the r11 sky-ring test fell from 95-100 % (r12 apex launches) to 63 % overall (f1 53, f2 20, f3 66, f4 70, f5 66, a 62, b 70, c 77 %) --
flow flips play low in the canyon by design; backDouble's Kickout hold is 0.21-0.22 s (F4 wants >= .3 at <= 150 deg/s); frontPikeSwan peak rate
982-1183 deg/s (F3 <= 800); backDouble ease ratio 1.8-1.9 on its 3rd rotation in a / f4 / f5 (F5 >= 3); hero 0.093 of frame height at p10 in the
Midtown canyon flip (a) and 0.13 in f5; hero briefly hidden by tree foliage at f4 9.0-9.1 s (occlusion .6-.8, ~0.2 s) and the camera sits in
foliage 2 / 11 / 22 frames (a / f3 / f4). Details: §6j. **Next:** run the blind critic on `_scratch/critic-P3-r13/pack` (see §8).

Owned paths: `unreal/WebHomage/Source/WebHomage/Traversal/**`, `/Game/Traversal`, `/Game/Tests/Traversal`,
`unreal/WebHomage/Scripts/build_traversal.py`, `docs/night1/traversal/**`. Branch `night1/traversal`, worktree `~/sm2-n1/traversal`,
UE MCP port 8773 (never used; everything runs through commandlets and `-game`).

## 1. Architecture map (Source/WebHomage/Traversal)

| File / class | What it does |
|---|---|
| `WebTravTypes.h` | `FWebTravInput` (held + edge flags: move, look, swing, jump, sprint, zip, drop, quick, trick), `FWebTravAnim` (C1 anim contract, see §2), `FWebTravEvent`, `FWebTravStrand` (web strand state). |
| `WebTravWorld.*` `FWebTravWorld` | World queries in METRES: `Raycast` (line trace, WorldStatic/Dynamic, ignores the pawn), `GroundHeight` (downward trace + terrain boxes tagged `WHGround`), `PushOutCapsule` (overlap + `ComputePenetration`, horizontal MTD), `SphereSweep`/`SphereOverlaps` (camera), `Near` (24 m XY grid of building AABBs), `Inside`. |
| `WebTravAnchors.*` `FWebTravAnchors` | Port of anchors.js (face candidates around a desired point ahead/up, 30-40 m band over the street, raycast confirm, `OnModel` probe, low zip-point fallback, cone rays) + zippoints.js (roof edge / corner / water-tower points from boxes, screen-centre targeting with hysteresis). No tree anchors. |
| `WebTraversalComponent.*` `UWebTraversalComponent` | Port of traversal.js: 120 Hz substeps; modes ground/air/swing/wall/zip/perch; kin moves vault/cornerWrap/wallHop; jump charge, landing tiers, glide, dive, corridor, facade avoid, side peel, rope wrap/reanchor, pump/climb assist/first-arc motor, drag, release boosts, momentum chain, tricks (TRICK_DEF, boost at snap), wall run/zip/corner/hop, zip bezier with speed profile, perch, point/anchor launch, web dash, quick boost. Writes `Anim` (C1), `Events`, `Strands[2]`. Browser function order kept. |
| `WebTravCamera.*` `FWebTravCamera` | Yaw auto-recenter + FOV/kick/punch/shake/roll/motion-blur from camera.js; composition replaced in round 03/05 by `ComposeChase` (see §3). Outputs `CamPos` (m), `CamRot`, `OutVFov` (VERTICAL deg), `MotionBlur`, `HeroDist`, `bCamInGeometry`. |
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
- **Round 11 — gymnast flips (owner FLIPS_BRIEF, spec FLIPS_SPEC.md measured from the owner clip):**
  - *Shapes* are Blender-keyed clips on the hero rig: `docs/night1/traversal/blender/make_flip_shapes.py` (headless, CPU) aims every spine / limb
    bone at a body-frame direction per shape (parent first; pointed toes follow the shin), keys 0 s = shape and 1 s = the same shape ~7 % more
    open ("breathing" over a hold), exports only those actions + `airApex`. `splice_flips.py` appends them (rotation channels, matched by
    bone name) to `Saved/HeroDev.glb`, but only after the untouched `airApex` survives the Blender round trip (max quaternion error 1e-5;
    the scene fps must be set to 30 BEFORE the import or every clip comes back time-scaled 24/30). `build_traversal.py` runs both, then the
    Interchange import makes `/Game/Traversal/HeroDev/flip<Shape>` (89 clips). Stick-figure check of the shapes: `_scratch/traversal/r11/blender/shapes.png`.
  - *Rotation* is not keyed: one angular momentum per program, rate = L x env(t) / I(shape(t)), L solved so the program ends exactly on its
    total angle (upright). Effective inertia per shape (tuck 1, pike 1.35, layout 3.2, twist 3.5, straddle 6, reach 7, swan 7.5, pencil 9,
    throne 9) was tuned to the owner clip: tucks spin ~520-620 deg/s, the open holds turn 60-120 deg/s, so the ease comes from the shapes.
    Set-in 0.12 s / settle 0.22 s envelopes at the ends. Shape changes blend over 0.06 s before + 0.11 s after a boundary.
  - *Overlap*: upper body samples the program 0.04 s ahead, legs 0.07 s behind (`Frame.LegLayers`, blended onto the leg bones in the proxy).
  - *Character*: `FlipOffQ` = pitch about the lateral axis x twist about the long axis (twist sign = `TrickSide`, toward the stick) about the
    body centre; when a program is cut (web catch / landing / wall) the last rotation springs back to the body frame in ~0.07 s (no pop).
    The wall-run top-out plays `wallFront` when the flip clips exist (the old `releaseFlip` clip spun by itself, so it is the fallback).
  - *Traversal*: `ChooseTrick` returns a program: script / caller request `FWebTravInput::FlipReq` (script key `"flip": "a,b,c"`, cycled per
    trick), else sky launch cycles backDouble / frontPikeSwan / corkscrew, plain release backSingle when < 30 m over the floor. The next web
    is searched only during the program's final reach; the reach is held up to `FlipReachHold` 0.2 s while the swing button is held.
    `bLegacyTricks` = the old browser tricks. Program boost 3.5 m/s forward + 1.5 up at 30 % of the first shape.
  - *Camera* (`FlipK`, 0.3 s in / 0.45 s out): orbits `FlipOrbitDeg` 40 deg off the travel axis toward the side with more open space
    (raycasts at the flip start), sinks `FlipCamBelow` 1.6 m under the hero, frames him at 0.42, look-up limit `FlipPitchUp` 18 deg (the first
    capture with 1.0 m / 10 deg framed the flips against facades), 0.2 m closer; never rolls with the body.
  - *Telemetry*: `flip_prog, flip_t, flip_pitch_deg, flip_twist_deg, flip_rate_dps, flip_shape, flip_shape_legs` (program state) and
    `body_axis_deg, body_pitch_deg, body_roll_deg` (RENDERED hips->head axis from the bones; one-row shift like every bone column).
  - Mouse: `MouseRadPerUnit` 0.011 (was 0.033) x console variable `wh.MouseSensitivity` (default 1).
- **Round 12 — apex flips over the rooftops (critic r11 single gap: release tricks low in the canyon, facades behind the hero):**
  - *Trick release = sky launch* (`bTrickLaunch`, default on): a trick pressed at a web release is converted to a jump-release. The launch
    (`SolveSkyPeak`) aims the apex `SkyApexOver` 6 m over the TALLEST roof within `SkyTallR` 30 m of the stretch of path the flip program will
    cover (`TallestRoofAlong`: 5 m down-ray grid over the strip from the predicted program start to +2.4 s of travel, 2 passes), at least the
    r10 lower-street-wall rule; cap `SkyPeakMax` 58 -> 90 m over the street, `SkyLaunchVzMax` 52 -> 60 m/s, climb gravity `SkyRiseK` 1.4 -> 1.0.
  - *Armed program*: the flip is not started at the release; it is armed (`S.ArmedFlip`) and starts when the climb slows to `SkyTrickVz` 9 m/s,
    then floats at `SkyFlipGK` 0.32 g while the program plays (from 9 m/s it climbs ~5 m more and ends near its start height), so the whole
    program plays 3-10 m over that roof. A sky launch always has room (`bRoom`; a launch off a roof used to skip the arming).
    **FLIPS_SPEC F10 conflict:** the trick now starts ~1.6-2.1 s after the release (the climb), not <= 0.1 s — the critic's apex rule wins here.
  - *autoChain*: a release is a sky launch only where `SkyPeakNeeded` (same solver, current velocity, 0.1 s cache, 4 m margin) says the apex
    clears the roofs; the r10 "forced launch 5.5 s after the last one" is gone (it flipped under the roofline). The web is re-pressed in the
    program's final reach; the skyMax clock runs only outside the climb / program. A trick-every release with `bTrickLaunch` gets the same
    sky bookkeeping.
  - *Flip camera = sky search* (`SearchSkyView`, replaces the r11 fixed 40 deg orbit): every 0.15 s (and at the flip start, from the current
    camera placement) it scores orbit yaw offsets -120..120 deg from behind x look-up elevations `FlipMinElev` 30 .. 60 deg (camera below
    the hero) by the share of 16 rays around the hero (the hero box + 40 px at 1080p: +-8 deg horizontal, +-11 deg vertical) that reach
    open sky within 900 m, cast from the camera spot; cost = no-sky x10 + distance from a 55 deg 3/4 side view + elevation above the floor +
    hysteresis. Springs 0.3 s; the camera sits `FlipDist` 2.9 m from the hero ON that line (taken exactly, blended by FlipK: the 0.07 s chase
    spring trailed ~3 m at 25 m/s), starts ~0.35 s before an armed flip (`bFlipSoon`), look-up limit = elevation + 20 deg. First capture
    (min elevation 8 deg, 3.4 m, spring-placed) measured f1 24 %: far skyline towers (visual only, no collision) filled the ring's lower half
    at 12-20 deg — hence the 30 deg floor.
  - *backDouble* (critic r11 secondary): tuck 0.55 / layout 0.5 / tuck 0.55 / layout 0.5 / reach 0.2 s (was nine segments of 0.14-0.36 s).
  - Telemetry adds `flip_armed, flipcam_k, flipcam_yaw_deg, flipcam_elev_deg, flipcam_sky` (ray-predicted ring sky of the chosen view),
    `sky_tall_m, sky_peak_want_m`. Planning dump: `-WHTravHeightmap=<csv>` (5 m grid of the traversal world's tops, x -320..680, y -620..380;
    `_scratch/traversal/r12/hm/heightmap.csv`, feasibility maps `hm_feas.txt` via `hm_need.py` / `hm_feas.py`).
  - *Where launches can clear the roofs* (engine height field): almost nowhere in Midtown's avenues (towers 100-320 m); the west avenue
    x -250 heading south from y ~195 (roofs 60-75 m), the avenue x ~335 south of y 285, and the southern edge (y > 310). f1-f4 moved to
    x -250 heading south; f5 = the r11 f1 stretch (x 250 north), where no release is a sky launch.
- **Round 13 — flow flips (critic r12 single gap: tricks were set pieces — 1.7 s rise, trick, 1.3 s web-less dive, camera cut):**
  - *Flow flip* (`bFlowTricks`, default on; `bTrickLaunch` r12 sky launch now default OFF): a trick buffered at a web release calls
    `StartTrick` in `ReleaseSwing` — program t = 0 at the release. Its climb is solved: vz0 = (FlowCatchRise 3 m + 0.5 g' Tc^2) / Tc minus the
    program's own Up boost, clamped FlowVzMin..Max 6-14 m/s, g' = G x `FlowFlipGK` 0.45 while the program plays (`S.bFlowFlip`), Tc = the
    program's catch time; excess swing climb goes 60 % forward. So the arc rises ~5 m, apexes mid-program and the catch window opens ~3 m
    above the release height with facades above him (no over-the-roof apex any more: that is what forced the 1.3 s dive).
  - *Catch window* (`FWebFlipProgram::CatchOpen`, `CatchT()`): the anchor search opens CatchOpen s before the program's end (0.16 s; backDouble
    0.2 s) — inside the Reach pose (or the Kickout's web-arm-up finish). The catch cuts the last ~5-20 deg and the character's 0.07 s spring
    returns them. autoChain re-presses the web there (`bInReach`) and lets a swing that ends in a trick go at 1.05-1.2 s (T2 budget).
  - `FitFlip` for flow flips (`bFlowChoose`): any program as long as the release is >= FlipFloorClear 6 m over the floor (the ballistic test
    swapped every program for backSingle at the chain's 9-14 m releases). Unforced flow releases cycle backDouble / frontPikeSwan / corkscrew.
  - *Programs* (`WebTravFlips.cpp`): backDouble = Tuck 1.0 s + **Kickout** 0.7 s (2 shapes; peak ~680 deg/s, <= 150 deg/s for ~0.65 s,
    mean ~420); frontPikeSwan 1.65 s, corkscrew 1.66 s, backSingle 1.22 s (all shorter than r12). `_scratch/traversal/r13/flipsim.py` = the
    rate model offline.
  - *Keyed shapes* (`blender/make_flip_shapes.py` `KEYED`): `flipKickout` (new shape, inertia 5.5): arms swing up/forward, sweep wide and back
    while the body arches and the legs straighten then scissor 3-6 frames later, web arm (right) up at the end; `flipLayout` is no longer a held
    plank: arms float out and forward, legs part a little behind them (keys 0/12/18/30). Stick check `_scratch/traversal/r13/sticks_kickout_layout.png`.
  - *Camera* (`WebTravCamera`): the r12 "closer than 3 m -> cut to the clear orbit" rule is deleted (it re-armed as FlipK fell: the 43/60 deg,
    3.1 m one-frame cuts at r12 f1 6.30 s / f4 8.58 s). **Output slew limit** per 1/60 s (`MaxStepPosM` 1.1 m, `MaxStepPitchDeg` 2.7,
    `MaxStepYawDeg` 3.6; position limited first and the view re-aimed by the same correction; telemetry `cam_slew` bit flags 1/2/4). Flip view
    search: first search prefers the side the camera is on, later searches move <= 45 deg; `FlipAimT` 0.4 s; `FlipDist` 2.9 -> 3.3 m (T8/F9 hero
    size); attach springs 0.25 s while the flip camera still blends out (0.45 s spring = ~0.9 s blend back).
  - *Hero fill* (`AWebTravCharacter::HeroFill`, critic r12 "hero black, V 44/255"): point light on lighting channel 1 only (hero mesh + lenses
    on 0 + 1), no shadows / GI, 1.8 m toward the camera + 0.4 m up, `HeroFillCd` 5000 cd blended to `HeroFillFlipCd` 18000 cd by the flip
    camera weight; `-WHHeroFill=<base>,<flip>` overrides (0,0 = off); telemetry `hero_fill_cd`. Rendered: hero V p50 164-222 in flip frames of
    the f-series (was 44/255 at r12); c (wallFront) p50 111 / min 46 -- the wall-run flip is still dim against the sky.
  - *Camera hold fix* (`FWebTravCamera::ComposeChase`, commit 3b6765f): when every sweep origin at the hero's chest (lifts 0 / 1 / 1.8 / 2.6 m) overlaps
    geometry (a street-tree canopy at a swing bottom, or a facade at a zip arrival) the view is HELD; it used to hold the absolute position, so the
    camera froze while the hero flew on at 43 m/s (rendered f4 8.75-9.17 s: 20 m away; a 11.43-11.58 s). It now moves with the hero (same offset, same
    rotation; members `LastComposeHero`, `bHaveComposeHero`). Trees are visual-only for the hero's physics, so he still swings THROUGH canopies.
- **Round 14 — side-on trick camera + eased rotation (critic r13 single gap: "the flip camera looks up from under the hero, so the rotation
  does not read and the camera stays tilted up into the next swing"; secondary 1: ease the rotation, hold every shape >= 0.3 s):**
  - *Side-on flip view* (`FWebTravCamera::SearchSkyView`): candidates only at yaw `FlipSideMin..FlipSideMax` 70-115 deg off the travel-behind
    direction (either side, then LOCKED to that side for the whole trick: no swing across behind him), elevations `FlipMinElev..FlipElevMax`
    4-28 deg below the hero (was 30-60), preference `FlipPrefYaw` 85; a spot must be sweep-reachable, have `FlipWallMargin` 1.5 m free beyond it
    and a clear path `FlipAheadT` 0.5 s along the travel (rendered f4 2.55-2.85 s before this: side spot against a facade cornice, the wall
    push shoved the camera over the hero, hero out of frame 0.3 s). Blend in `FlipInT` 0.25 s, out `FlipOutT` 0.18 s (was 0.3 / 0.45), aim
    spring `FlipAimT` 0.3 s. Flip look-up capped at `FlipPitchUpMax` 27 deg; every non-wall view capped at `MaxLookUpDeg` 29 (also after the
    output slew re-aim).
  - *Settle band after every attach* (`SettleDownMin..Max` 5.5-11.5 deg DOWN, blended in over `SettleT0..T1` 0.25-0.5 s of `SwingT`, widened
    only as far as needed to keep the hero inside 0.18-0.82 of the frame height; wall camera excluded). r13 f4 medians 0.5-1.0 s after the
    attaches were 1-9 deg UP (attach look-up beat + arc-bottom framing).
  - *Hero inside geometry* (street-tree canopy at a swing bottom): the camera no longer holds (r13 kept offset + rotation: probe f3 hero slid to
    0.90 of the frame, 28 deg down for 0.8 s); it composes normally without collision sweeps (`bNoSweep`). The camera then sits in foliage for
    those frames (f3 ~0.7 s) -- trees are still the open issue (§6).
  - *Eased rotation* (`WebTravFlips`): `FWebFlipSeg::EaseIn / EaseOut` raise a segment's inertia toward its ends (x (1 + e), smoothstep over 45 %
    of the segment), so the rate is lowest going into and out of a tuck / pike and highest mid-tuck. Programs: backDouble Tuck 1.20 s (ease
    .85 / .8, peak ~766 deg/s program) + Kickout 0.60 s (inertia 5.5 -> 10.5: <= ~100 deg/s), catch 1.60 s after the release (r13 1.50);
    frontPikeSwan Pike .40 (1.3 / .3) + Swan .55 + Tuck .38 (1.2 / .7) + Reach .26 = 1.59 s (Pencil dropped: critic r13 "5 shapes in 1.7 s");
    corkscrew Layout .31 + Twist .42 + Swan .36 + Tuck .34 (1.2 / .7) + Reach .24 = 1.67 s; backSingle Tuck .32 / Pencil .36 / Tuck .32 / Reach .24.
    Offline model: `_scratch/traversal/r14/flipsim14.py` (same table integration as the C++).
  - *Shape axis compensation* (`WebFlips::ShapeAxisDeg`, `FWebFlipPose::AxisOffDeg`, character `PoseFigure`): each keyed shape leans the
    hips->head axis off the body frame (measured on the probe: Tuck +20, Pike +22, Swan -15, Kickout -6, Reach +3 deg, + = head forward); the root
    pitch subtracts the blended lean (ramped in over the first 0.15 s), so the VISIBLE axis turns at the eased program rate (r13: a swan -> tuck
    change curled the axis ~55 deg in 0.17 s on top of the program; tuck entries ran ~460 deg/s and pikeSwan peaked 1045-1090 rendered).
  - *autoChain*: a swing that ends in a flip is let go at 0.92-1.06 s (was 1.05-1.2) even before it rises (T2 kept <= ~2.6 s with the longer
    backDouble). Scripts: f4 now runs NORTH from y 375 (r13 ran south and its 4th flip left the traversal world's south edge at y ~515: hero
    pinned on the corridor clamp, camera hold), capture 11.6 s = 4 flips + 1 s after the 4th catch; b fires the zip from the program's final
    Reach at 2.88 s (the zip target is on screen in the side view; r13 dropped at 3.05 and zipped at 3.08 after the program).
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
python3 docs/night1/traversal/flip_check.py <telemetry.csv> <label>   # round 11: FLIPS_SPEC F1-F5, F7-F11 per trick (rendered body axis, px height)
python3 docs/night1/traversal/sky_check.py <round dir> <clip> ...   # round 12: critic r11 sky-ring test (10 fps trick frames: >= 50 % sky in a 40 px ring AND hero >= .15 in >= 70 %)
python3 docs/night1/traversal/apex_check.py <telemetry.csv> <label>   # round 12: per flip program: height over the solver's tallest roof, release -> start, flip camera view, next web
python3 docs/night1/traversal/flow_check.py <telemetry.csv> <label> [--video <mp4>]   # round 13: critic r12 test -- release->shape <= .25 s, reach->attach <= .3 s, T4 <= 3.1 s, T2 <= 3.3 s, per-frame camera <= 3 deg / 4 deg / 1.2 m, flip-camera blend-out >= .4 s, backDouble <= 2 shapes, hero V (video)
GPU_OUTER=1 docs/night1/traversal/capture_round.sh ...   # round 12: inside ONE outer `gpu_slot.sh capture --label traversal -- <batch script>` hold (max 40 min): no per-run queueing
python3 docs/night1/traversal/wall_check.py <telemetry.csv> <label>   # wall-run: limb phases @6 fps, head>hips, steps/s, px in frame through top-out
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

## 6. Known bugs / open issues
- **Round 13 (flow flips), state after the renders (numbers in §6j):**
  - *Sky behind the flips fell* (r11 sky-ring test 95-100 % -> 63 %): flow flips play at 7-25 m over the street inside the canyon; the searched
    flip camera looks up from below (look-up p50 37-52 deg) but facades stay in the ring for the first ~0.6 s (f1 3.6-4.1 s ring .22-.30).
  - *Flip quality lines still failing* (owner priority = gymnast-quality flips): backDouble Kickout hold 0.21-0.22 s (F4 needs >= .3 s at
    <= 150 deg/s), backDouble ease ratio 1.8-1.9 on rotation 3 (F5 >= 3); frontPikeSwan peak 982-1183 deg/s (F3 <= 800; r12 877); all programs
    are 1.47 s to the catch (r12: 2.2-2.5 s). A longer Kickout (+0.15 s) moves the catch window and every backDouble path (a, f1, f4, f5 recapture).
  - *Trees*: the hero swings through street-tree canopies at swing bottoms (f4 9.0-9.2 s occlusion .6-.8, hero cropped at 9.2 s; the camera then
    sits in foliage 22 frames). TRAVERSAL-SPEC T19 says never occluded: needs either canopy avoidance in the swing solver or P1 tree collision
    / a lower-alpha canopy near the path; the camera hold (3b6765f) only keeps him framed.
  - Scripts: f3 = corkscrew on every release (`trickEvery 1`); on every 2nd release FitFlip found no corkscrew that fits at the low 2nd release
    (5.8 m over the floor, 1 s after the first swing) and the 4th one landed on a 14 m roof. b = zip pressed at 3.08 s (the zip target only
    reappears ~3.07 s; before that the press is ignored: `zipPull` without flight).
  - The slew limiter clips attach look-ups (pitch limited 2-37 frames per clip) -- no cuts; a 2.7 deg/frame cap on the attach beat.
  - The trick camera starts only at the release (no anticipation); wallFront top-out still cut by the landing (Throne 0.09 s, critic r12
    secondary); edge vault / flips on the web still not built.
- Interchange renames bones (`upperArm.R` → `upperarm_r`); code uses `upperArm_R` style (FName is case-insensitive). P2's hero
  swap = change `ClipRoot` and the mesh paths in `SetupHeroMesh`.
- Wall-run (round 06): the stride is the ground sprint clip on the wall (no authored wall-run cycle, no hand plants, no foot IK
  on the facade); side runs (`wallRunSide`) keep the old chase framing blended with the wall camera but were not captured.
- c after the top-out: when the camera turns 180 deg on the 10 m podium strip it is squeezed against the tower and lifts 2-5 m
  (occlusion search), looking down steeply; the zip target then depends on the look-up in the script.
- Not ported: slingshot, tightrope, water/bridge bounces, car roofs, tree anchors, web slack/whip, zip reticle, look-at, foot IK.

## 6b-6g. Rounds 06-11 checks
Per-round check tables (rounds 06-11) are in git history of this file (commit 7ca115c) and in each `round-NN/` folder (CHECK / SPEC_CHECK /
FLIP_CHECK files). Still-relevant results: wall-run c = 14 limb phases, head above hips, hero in frame through the top-out; a swing chain r10
T1/T2/T8/T9/T11-T14/T16/T19 PASS, T10 spread marginal (.199), T18 side third .68 FAIL.

## 6i. Round-12 checks (captures in `round-12/`: SKY_CHECK.txt, APEX_CHECK.txt, FLIP_CHECK.txt, ANIM_CAM_CHECK.txt, SHOTLIST.md; lit Manhattan golden)
Movies 1920x1080 internal = output (`r.ScreenPercentage 100`, TSR + Lumen defaults), fixed 1/60 s step, 0.8 s pre-roll trimmed, 13.6-14.2 MB. No 4K
stills this round (the first batch's stills were taken with the discarded v1 camera and deleted). GPU shared (every run `contaminated`: no perf claim).
f1-f4 are the final code; c and f5 come from the first batch (same code outside the flip camera, which neither uses).
| Line | f1 backDouble | f2 frontPikeSwan | f3 corkscrew | f4 chain | c wallFront | f5 canyon |
|---|---|---|---|---|---|---|
| **Critic r11 test: trick frames sky >= .5 AND hero >= .15 (need >= 70 %)** | **100 %** (ring p50 .83) | **100 %** (.76) | **95 %** (.92) | **100 %** (.89) | 77 % (.99) | no trick (no launch can clear 140-250 m towers) |
| Flip start over the tallest roof within 30 m (solver) | +3.3 m (roof 68 m) | +3.5 (67.8) | +3.6 (61.7) | +3.6 (62.4) | — | — |
| Flip camera (searched) | yaw -50, look-up 30 deg | -50 / 30 | -65 / 30 | -79 / 30-39 | wall camera | — |
| Hero px height p10 / p50 | .18 / .29 | .25 / .41 | .23 / .40 | .20 / .27 | .17 / .24 | — |
| F1 rotations (program / rendered) | 2.00 / 1.89 | 1.00 / 1.09 | 1.00 / 1.05 + 360 twist | 2.00 / 2.01 | 0.97 / 0.87 | — |
| F2 mean / F3 peak deg/s | 298 FAIL (300-500) / 680 | 199 / 877 FAIL | 201 / 707 | 318 / 680 | 347 / 643 | — |
| F4 longest hold / F5 ease | 0.46 s / PASS | 1.06 / PASS | 0.61 / PASS | 0.46 / PASS | 0.12 FAIL / PASS | — |
| F8 catch after the program | 1.13 s FAIL | 1.53 s FAIL | 1.08 s FAIL | 0.07 s / 27 deg PASS | landing | — |
| F9 hero 0.18-0.36 | PASS | p50 .41 FAIL | .40 FAIL | PASS | PASS | — |
| F10 release -> trick (<= 0.1 s) | 1.68 s FAIL (by design: apex start) | 1.65 FAIL | 1.55 FAIL | 1.85 FAIL | 0.00 | — |
Safety: 0 T-pose frames, camera in geometry 0 frames, hero fully in frame 100 % (c 608/629: roof camera turn, as r10/r11). Same-silhouette air
pairs only inside the held final reach of backDouble (f1 5.5-5.8 s, f4 7.8-8.2 s) and f2's reach -> dive.
Iterations this round (evidence `_scratch/traversal/r12/`): camera v1 (look-up 8-56 deg, 3.4 m, spring-placed) f1 24 % / f2 76 % / f3 75 % /
f4 28 % (far visual-only skyline in the ring, camera trailing 4.4 m at 17 deg; `v1/`, `look/f1_sheet.jpg`); v2 (30 deg floor, 2.9 m) snapped to
the chase orbit every frame (the 3 m "too close" cut, `look/f1v2_sheet.jpg`); v3 = final (cut threshold follows FlipDist).

## 6j. Round-13 checks (captures in `round-13/`; lit Manhattan golden; GPU shared, every run `contaminated` = no perf claim)
Movies 1920x1080 internal = output (`r.ScreenPercentage 100`, TSR + Lumen), fixed 1/60 s step, 0.8 s pre-roll trimmed, 12.8-14.1 MB; no 4K stills.
Build: dylib of 14d0b97 (c, d, f1, f2, f5) and of 3b6765f (a, b, f3, f4). A -nullrhi probe of 3b6765f reproduced c / d / f1 / f2 / f5 hero AND
camera telemetry exactly (max diff 0.000 m), so those five captures stand for the final build. Warm-up render ran once (first batch).
| Line (`FLOW_CHECK.txt`) | a | b | c | d | f1 | f2 | f3 | f4 | f5 |
|---|---|---|---|---|---|---|---|---|---|
| flips (program) | backDouble, frontPikeSwan | frontPikeSwan | wallFront | -- | backDouble | frontPikeSwan | corkscrew x2 | backDouble, pike, corkscrew, pike | backDouble (+1 cut by the clip end) |
| R1 release -> first shape (<= .25 s) | 0 / 0 | 0 | -- | -- | 0 | 0 | 0 / 0 | 0 x4 | 0 |
| R2 reach -> next attach (<= .3 s) | -.02 / +.07 | +.27 (zip) | -- | -- | -.02 | +.07 | +.05 / +.05 | -.02 / +.07 / +.05 / +.20 | -.02 |
| T4 max web-less air (<= 3.1 s) | 1.48 | 1.68 | 0.38 | 0.80 | 1.48 | 1.48 | 1.48 | 1.62 | 1.48 |
| T2 max attach -> attach (<= 3.3 s) | 2.65 | -- | -- | 2.13 | 2.60 | 2.60 | 2.65 | 2.63 | 2.60 |
| C1 per-frame camera max pitch / yaw / pos | 2.70 / 3.30 / 1.11 | 2.70 / 1.96 / 1.01 | 2.70 / 3.60 / 1.11 | 2.70 / 1.54 / 0.92 | 2.70 / 3.60 / 1.10 | 2.70 / 2.48 / 0.89 | 2.70 / 3.31 / 1.11 | 2.70 / 3.60 / 1.10 | 2.70 / 2.76 / 1.09 |
| image-diff isolated spikes (cuts) | none | none | 3.85 s (not a cut) | none | none | none | none | none | none |
| frozen-camera frames (fix 3b6765f) | 0 (was 10) | 0 | 0 | 0 | 0 | 0 | 0 | 0 (was 24) | 0 |
| camera in geometry (frames) | 2 | 0 | 0 | 0 | 0 | 0 | 11 | 22 | 0 |
| hero V trick frames p10 / p50 | 180 / 217 | 195 / 214 | 59 / 111 | -- | 124 / 164 | 182 / 209 | 141 / 179 | 132 / 203 | 193 / 222 |
| sky ring (>= 50 % sky AND hero >= .15) | 62 % | 70 % | 77 % | -- | 53 % | 20 % | 66 % | 70 % | 66 % |
FLIPS_SPEC (`FLIP_CHECK.txt`): F1 rotations 1.9-2.0 (backDouble) / 1.0-1.1 (pike, corkscrew + 360 deg twist); F2 mean 473-485 deg/s backDouble;
F3 peak 769-781 (backDouble) / 775-778 (corkscrew) PASS, 757-1183 (pikeSwan: b 757 PASS, f2 982, a 1027, f4 1141 / 1183 FAIL); F4 hold: pikeSwan
0.86 s, corkscrew 0.47 s PASS, backDouble Kickout 0.21-0.22 s FAIL; F8 catch 0.02 s after the program with the body 12-23 deg from upright PASS
in all; F9 hero height p50 .17-.30 (a t1 p10 .093 and f5 t1 p10 .13 FAIL); F10 release -> trick 0.000 s. TRAVERSAL-SPEC engine side
(`SPEC_CHECK.txt`, video instruments NOT run): a T8/T9/T12/T13/T14/T16 PASS, T10 spread .167 FAIL, T11 p5 -51 deg (flip camera) FAIL, T19 FAIL (2 frames);
d T8 p10 .189 / T9 .377-.572 / T14 FAIL; b / c are single-release sequences (their T8-T14 are not the chain test). Safety: 0 T-pose frames.
Sheets used for the visual read: `_scratch/traversal/r13/look/*.jpg`. Tools written this session (scratch): `cutscan.py` (image-diff cut
finder), `freeze_scan.py` (camera not moving while the hero is), `checks.sh`, `spec_engine.sh`.

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
| r10 | 6/6/6/5/5, flips 4 — FAILS TARGET | Flips: two 180 deg flips in 0.2 s each (~900 deg/s), no shape held > 0.3 s, seen foreshortened from behind; build each web-less trick as 180 deg in <= 0.35 s, one extended shape held >= 0.6 s at <= 150 deg/s, <= 0.4 s ease into the next attach; side-on, hero >= 0.20 of frame height against sky | r11 flips (owner brief = same gap): shape programs, momentum easing, flip camera |
| r11 | 6/6/7/6/6, flips 6 — FAILS TARGET (lost 4 of 5 owner pairs) | Release tricks low in the canyon, facade / billboard behind the hero: ring sky p50 f1 .16 f2 .26 f3 .28 f4 .05; start every release trick from an apex >= 3 m over the tallest roof within 30 m, camera biased so the sky is behind him; test >= 70 % of trick frames >= 50 % sky ring with hero >= .15. Secondary: backDouble <= 2 shapes held >= 0.5 s; green lens ghosts (P4); T2/T8/T10/T11/T18 | r12 apex sky launch over the tallest roof, armed program at the top of the climb, sky-searching flip camera, backDouble tuck/layout |
| r12 | 5/5/6/7/6, flips 6 — FAILS TARGET (lost 5/5 owner pairs "on flow") | Tricks are isolated set pieces: 1.7 s rise, trick, 1.3 s web-less dive, one-frame camera cut (f4 8.58 s, f1 6.30 s); start the first shape <= .25 s after release, attach <= .3 s after Reach, blend the trick camera back >= .4 s; test T4 <= 3.1 s, T2 <= 3.3 s, per frame pitch <= 3 / yaw <= 4 deg / pos <= 1.2 m. Secondary: backDouble <= 3 shapes, throne >= .3 s, Reach bbox <= .38, hero black against backlight, billboards | r13 flow flips from the release, catch window in the reach, 2-shape backDouble + keyed Kickout / Layout, no camera cut + slew limit, hero fill light (probe-verified only) |
| r13 | 6/5/6/7/6, flips 6 -- FAILS TARGET (lowest: camera 5; lost all 5 owner pairs) | The flip camera looks up from under the hero (pitch p5 51-56 deg up, still 53 up after the f4 8.2 s attach): rotation does not read; orbit side-on >= 60 deg from the somersault axis, pitch <= 30 up, back to 4-12 down within 0.5 s of the attach; test on f4: pitch never > 30 up, median pitch 0.5-1.0 s after each attach 4-12 down, tuck axis >= 300 deg on screen. Secondary: ease the rotation (ends >= 30 % slower), every shape >= 0.3 s, asymmetric 90 deg arm shapes (swan / layout read as a mannequin), T8 / T10 / T3, vary rope and gap lengths +-25 %; brand: chest emblem copies the real game's (P2) | r14 side-on trick camera + settle band, eased programs + shape-axis compensation, clearance-checked side spots |
| r14 | not judged yet -- pack `_scratch/critic-P3-r14/pack` (same 5 owner-clip pairs + r13-vs-r14 f1 progress pair) | expected: sky ring low (f-series 26 %, side-on <= 30 deg up sees facades in canyons), swan / layout arms still symmetric, camera in foliage f3 ~0.7 s | -- |

Round folders `docs/night1/traversal/round-0N/` hold videos, stills, telemetry, SHOTLIST, CRITIC and the check outputs.

## 8. Queue for the next session
1. **Run the blind critic** on `/Users/midir/sm2-n1/_scratch/critic-P3-r13/pack` (6 pairs, A/B randomised; `pack.key.json` is the answer key -- do not hand
   it to the critic; owner-clip cuts are in `_scratch/critic-P3-r13/refcuts/` and never committed). Rebuild: `_scratch/critic-P3-r13/make_pairs.sh`
   (cuts our clips to 0.5 s before the release .. 1 s after the next web, crops to the owner clip's framing, calls `abpack.py`). Record the verdict in
   `critic/round-13-CRITIC.md` + §7.
2. Then, by the numbers in §6j, owner priority = gymnast-quality flips: (a) backDouble Kickout hold >= .3 s at <= 150 deg/s and a better ease
   (F4 / F5; costs ~0.15 s of program -> recapture a, f1, f4, f5), (b) frontPikeSwan peak <= 800 deg/s (F3; f2, a, f4), (c) sky behind the flow flips
   (ring 63 %: raise the flip camera floor sooner / bias the climb toward the open side; do not go back to isolated apex launches), (d) hero size in the
   Midtown canyon (a t1 p10 .093), (e) wallFront hero brightness (c V p50 111) and the throne hold, (f) foliage: hero swings through street-tree canopies
   (f4 9.0-9.2 s) -- canyon keeping / anchor choice or P1 tree collision.
3. Capture protocol (this session, all fine): `SKIP_WARM=1 gpu_slot.sh capture --label traversal -- _scratch/traversal/r13/cap_batch.sh <seqs>` one batch
   at a time (a, b, f3, f4 ~16 min incl. queueing; f1-f3 ~10 min); `_scratch/traversal/r13/batch_probe.sh <name>:<quit>` = -nullrhi probes (~25 s each)
   -- the replay is deterministic, so probes tell which clips a code change touches (compare hero / camera columns to the captured telemetry) and need
   no re-render when unchanged. Then `_scratch/traversal/r13/checks.sh` (FLOW / FLIP / SKY / APEX / ANIM_CAM) and `spec_engine.sh`, `make_shotlist.py`.
   The exclusive `perf` lock of another session held the queue for 7-12 min twice; a Studio reboot clears stuck exits.
4. 4K stills and the SPEC video instruments (YOLO on mps: wrap in `gpu_slot.sh capture`) were not run this round.
5. Mouse (Hari, `wh.MouseSensitivity`), P5 combat hooks (`docs/night1/manhattan/INTEGRATION_BUGS.md`), awning-safe street wall-run, P2 hero swap.
6. Teardown: `_scratch/traversal/capture/*` frame folders (PNG frames) were removed after this round; the critic pack + refcuts stay until the critic
   has run; the worktree `Intermediate` (1.3 GB) was kept (a rebuild is ~15 s but the content build is ~40 s + shader compile).
