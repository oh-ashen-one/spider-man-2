# P3 Traversal + camera — handoff (after round 18)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

**Status (round 18, 2026-10-01, Opus 5.5): IN PROGRESS -- a third render of a, b, f1-f5 with the FlipCompact-weighted pull-in (commit `1337646`) is queued;
the round-18/ folder holds render 2 (commit `d4c8ad1` / `93f413e` for b, c, d). Checks, critic pack and §6o numbers are from render 2.**
Round 18 answered the r17 critic's single gap ("every trick holds a frozen inverted split"; flips 6) with dense-keyed continuous shapes (§3 "Round 18").
Critic test (`round-18/LIMB_CHECK.txt`): limb_z slow samples on f1-f5 **0 of 238** (r17 31 of 242); a / b / c trick windows 0 of 51.
**Next:** if render 3 finished, re-run the checks and rebuild the critic pack (§8), else run the blind critic on `_scratch/critic-P3-r18/pack`.

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
- **Round 15 — sun-aware near-level trick camera (critic r14 single gap: "the trick camera climbs to 20-27 deg up and looks into the sun, which
  flares out the flips"; instruction: cap at 8 up, orbit to the side that puts the sun behind the camera, >= 100 deg sun-view; orchestrator:
  sky behind the hero by HEIGHT, not by pitch):**
  - *Sun*: the character finds the level's atmosphere sun light (`UDirectionalLightComponent`, sun index 0; fallback brightest directional;
    retried for 240 frames) and hands `Cam.SunDir` (unit vector TO the sun) to the camera. /Game/Maps/Manhattan golden: yaw -178, 8 deg up =
    due WEST (the look preset's az 238 maps to this; trust the logged value).
  - *Trick view* (`SearchSkyView`): elevations `FlipMinElev..FlipElevMax` -3..6 deg (camera from 0.17 m above to 0.35 m below the hero),
    cost prefers `FlipPrefElev` 1 deg -> trick pitch 4-9 deg DOWN; `FlipPitchUpMax` 8 (applied from FlipK 0.3 on, also blending out),
    `MaxLookUpDeg` 10 for every other non-wall view, `CapUpDeg` = the cap used this frame (the output slew re-aim respects it). Sun rule:
    views closer than `SunMinDeg` 100 to the sun are rejected; cost term below `SunPrefDeg` 140. Staged fallback passes: 0 = sun + r14
    clearance, 1 = sun + 0.5 m margin / half path, 2 = sun + reachable only, 3 = anything (probe: with only "sun / any" the first f4 flip
    fell back to looking into the sun at 8-31 deg). Glare term: ring rays that hit a facade whose mirror direction is within `GlareDeg` 25 of
    the sun cost `GlareW` 8 x share (rendered f4 9.65-9.85 s: glass mirrored the sun into the lens) -- it moved the view off square-on but
    does not remove the hot-spot (§6). `FlipInT` 0.25 -> 0.30 (the slew-limited yaw is past 100 deg by k 0.5).
  - *Wall camera*: `WallCamBelow` 2.2 -> 1.3, `WallCamOut` 2.2 -> 3.1, `WallCamDist` 3.4, `WallFrameS` 0.68 -> 0.60, look-up cap
    `WallMaxUpDeg` 30 (was 80).
  - *Foliage*: with the hero inside a canopy (`bNoSweep`) the camera spot is lifted 0.8-5 m (then pulled in / out) until the 0.25 m lens
    sphere is clear.
  - *Hero fill* (`UpdateHeroFill`): the flip boost (18000 cd) only when the view looks toward the sun (backlit); front-lit = `HeroFillFrontK`
    0.3 x base (1500 cd). The first r15 render (18000 cd + front sun) read the hero pale / clipped.
  - *Roofline flow flip* (`FlowRoofOver` 3, `FlowRiseMax` 14, `FlowRoofAhead` 40, `FlowRoofMinH` 16): the flow climb targets 3 m over the
    lower street wall's roofline (`RoofBesideAhead`) when that needs a rise of 3..14 m; roofs under 16 m are ignored (street-tree canopies read
    as 9-15 m "roofs" in the first probe). On the r14 routes it fires once per ~5 flips (the rest are 45-146 m walls).
  - *Zip reticle*: while FlipK > 0.3 the targeting view is the chase heading from 3.8 m behind, 6 deg up (the sun-away side view hid b's roof
    point: the 2.88 s zip fell to the street in the probe).
  - Telemetry adds `flipcam_sun_deg, view_sun_deg` (rendered camera forward vs the sun), `flow_roof_m, flow_rise_m, flipcam_glare`.
    `-WHCamTune=Name=V,...` sets camera doubles (`FWebTravCamera::SetTune`: SunMinDeg, SunPrefDeg, FlipPrefElev, FlipMinElev, FlipElevMax,
    FlipPitchUpMax, MaxLookUpDeg, FlipSFrame, FlipDist, FlipPrefYaw, Wall*, SettleDown*, GlareDeg, GlareW).
  - Tried and dropped: moving the f-series to the y -560 cross street (north side 10-29 m low-rise): only ~20 m wide with trees, no side spot
    passed the clearance (flip camera never left the chase), swings bottomed at 2-4 m at 12 m/s, and a north-looking view is 88 deg from a
    due-west sun anyway. Scripts in `_scratch/traversal/r15/scripts/`.
- **Round 16 -- held 3/4 trick camera (director's `TRICK_CAMERA_SPEC.md`, TC1-TC12, tests TC-A..TC-K; SUPERSEDES the r11 70 % sky ring, r12 tilt-bought sky,
  r13 >= 60 deg side-on + 30 deg cap, r14 box-luma and r15 +-30 deg / .44-.56 demands; the r11-r15 flip-camera bullets above are history):**
  - *Deleted* (`WebTravCamera.*`): `SearchSkyView` and its 0.15 s re-search, the 70-115 deg side-on orbit and elevation grid, the yaw/elevation springs
    (`FlipYawOff/FlipElev/FlipAimT`), `FlipCloser`, `FlipPitchUp`, the r11 orbit constants, the lateral wall push and the attach yaw beat while the
    trick camera is in.
  - *`ChooseFlipView`* (once, at the first frame of `bFlip || bFlipSoon`, never re-run): candidates = yaw offsets 40/45/50/55 deg from the
    travel-behind direction on both sides at `FlipDist`; order = obstruction (spot sweep-reachable from the hero with r 0.3, `FlipWallMargin` 1.5 m free
    beyond it, a clear path `FlipAheadT` 0.5 s along the travel, lens over the floor) -> sun (view >= `SunMinDeg` 100) -> open space (lateral free distance,
    ring sky share, graded clear-path time, glare facade, 45 deg preference, current side). Tiers: 0 obstruction + sun ok, 1 only a sun-facing side is
    clear, 2 pulled in (4.0 .. `FlipDist` along the same yaw), 3 nothing clear -> plain chase (`bFlipAbort`). The log line `WH_TRAV trick camera choice`
    prints every candidate (`failN`: 1 sweep to the spot, 2 margin beyond it, 3 path ahead, 4 floor).
  - *Held view*: the camera sits `FlipDistNow` from the hero on the chosen WORLD azimuth -- 4.4 m (`FlipDist`), pulled in `FlipTuckPull` 0.6 m while the upper-body
    shape is compact (tuck 1 / pike 0.6, spring 0.25 s; the character hands `FlipCompact` in `FTravCamInput`) -- `FlipDrop` 1.0 m under his body centre, hero framed at
    `FlipSFrame` 0.36, `FlipLeadDeg` 3 deg yaw bias toward his travel (hero on the trailing side, x ~ .45-.55), pitch cap `FlipPitchUpMax` 7.5 up, no roll
    (TC12), FOV / kick / punch / shake untouched. The chase camera keeps running underneath (`Desired / CamXY / CamZ`); the trick spot is blended onto
    its result in POLAR coordinates about the hero (azimuth + radius by `FlipK`, height by `FlipZK`) -- a Cartesian lerp of two spots 45 deg apart swung the
    view 2x faster than the spring asked for.
  - *Blends*: in = critically damped springs (`FlipInT` 0.35 s horizontal, `FlipZInT` 0.15 s height); out = smoothstep over `FlipOutT` 0.9 s from the web attach
    (height weight held `FlipZHold` 0.3 s first) from the weights at its start -- finite, so the next trick of a chain never starts on the exponential tail of
    this one (a spring tail left 22 % of the old side in the next flip: a 19 deg jump, 216 deg/s). Output yaw slew 2.4 deg/frame (144 deg/s) while `FlipK > 0`.
  - *Obstruction during the trick* (TC11): every frame a sweep (r 0.3) chest -> held spot; a hit dollies the camera IN along the held axis (spring 0.08 s in /
    0.6 s out, floor 2.8 m); blocked under `FlipDistMin` 4.0 m for `FlipAbortGrace` 0.2 s -> blend to the plain chase over `FlipOutT`.
  - *Telemetry* adds `flipcam_dist_m, flipcam_tier, flipcam_abort, flipcam_zk, cam_lens25` (lens sphere 0.25 m touching anything) and re-defines
    `flipcam_yaw_deg` (signed offset of the camera azimuth from travel-behind at the release) / `flipcam_elev_deg` (asin(drop / dist)) / `flipcam_sky` (ring sky share
    of the chosen view at the selection). `-WHCamTune=` names: SunMinDeg SunPrefDeg FlipDist FlipDistMin FlipDrop FlipYawMin FlipYawMax FlipPrefYaw FlipLeadDeg
    FlipSFrame FlipPitchUpMax MaxLookUpDeg FlipInT FlipOutT FlipZInT FlipDollyInT FlipDollyOutT FlipWallMargin FlipAheadT Wall* Settle* GlareDeg GlareW.
  - *Routes*: f1 spawn x -250 -> -246 and f4 spawn y 375 -> 367 (scripts `scripts/city/`): with the sun due west (yaw -178, 8 deg up) the sun-away trick side is the
    west half of the avenue, whose street-tree canopies (8-15 m at x -265..-257) made the r15 starts (f1 first flip y 270 at 7 m, f4 first flip y 342) fail the
    obstruction rule on that side, so the spec rule (obstruction first) picked the sun-facing side (view 38-41 deg from the sun). Probed variants:
    `_scratch/traversal/r16/scan/`, `varscan.sh`. Chain rule / flip programs / f2 f3 f5 / a b c d unchanged.
- **Round 17 -- flips over the roofline (critic r16 single gap: "every trick is shot from the street into a dark facade, and each starts facing the
  sun"; instruction: fire flips from an apex with the hips >= 3 m over the lower roofline within 30 m (TC8), pick the 35-55 deg side with view_sun >= 100,
  flipcam_k >= .9 by flip_t .35; the r16 held 3/4 camera architecture is KEPT):**
  - *Route* (`scripts/city/f1..f5`): the f-series runs EAST along the y -560 cross street (x -250..~150). North side = a park / low-rise strip
    (heightmap 10-30 m: tree canopy and 2-6 storey blocks), then the traversal world's north edge -- open sky and the far skyline behind the hero;
    south side = 46-466 m blocks to web onto. The sun is due west (yaw -178, 8 deg up), so every view of an east-bound chain is >= ~120 deg from it.
    Scripts carry their own tuning now (`"tune"` / `"camTune"` strings, same syntax as `-WHTravTune` / `-WHCamTune`, applied before the command line):
    `ArcLowMin=14,ArcDropShallow=8,ArcDropDeep=12` (arcs bottom >= 14 m: over the 10-14 m street-tree canopies, the chain stays near roof height)
    and `WallClearance=9` (keeps him mid-street: the sun-away camera side, south, needs ~3 m + 1.5 m margin). A flip on EVERY release (programs as r16).
    Tried and dropped (probes `_scratch/traversal/r17/probe/`): the street at the default arcs (bottoms 3-5 m, tree canopies, slow chain, low
    releases), spawning over the north row (the corridor pulls him back into the street), f4 from x -300 (60-69 m north blocks + an avenue-corner
    wall kick) and from x -225 at 45 m/s for 13 s (reaches the open plaza x 190-270: no anchors, turned back west into the sun).
  - *Apex solve* (`bFlowApexSolve`, `FlowRoofTarget`, `FlowApexGain`): a flow flip's climb is solved for the APEX (hips) = lower roofline within
    `FlowRoofR` 30 m + `FlowRoofOver` 3 + `FlowApexMargin` 1 m (>= `FlowApexMin` 2.5 m gain), vz <= `FlowApexVzMax` 20 (bisection on the gain incl.
    the program's Up boost). Roofline = per side of the route the highest down-ray top (5 m grid) in the 30 m capsule along the next ~1 s of travel;
    tops under `FlowRoofMinH` 16 m are canopies (a side with nothing taller counts as 16 m); the lower side wins. (v1 used the r10 horizontal wall
    rays: at 8 m they hit the canopy, found no low-side roof and used the 90 m side.) The capsule follows `RouteDir` (horizontal velocity smoothed
    over 1.5 s; the instantaneous velocity on a swing's rising front pointed across the street). Unreachable roofline (more than the capped climb)
    -> the r13/r15 rule ("fires anyway": a / b canyons; v1 rocketed 20 m for 2 s there). Log `WH_TRAV flow apex: ...`; telemetry `flow_apex_want_z`,
    `flow_gap_m`.
  - *Roof hold* (autoChain, `WebTravCharacter`): a swing that ends in a flip is held on its RISING front while `FlowApexGap` (target - hips) is over
    `FlowReadyGain` 9 m and under 9 + `FlowHoldMax` 12 m; the front apex / a stale swing still let go.
  - *Trick camera* (`WebTravCamera`): ranking at the release = sun first (rank 0 clear at FlipDist + sun ok, 1 sun ok pulled in, 2 only a
    sun-facing side clear -- r16 took that before pulling in); 35 deg offset added; ring-sky weight `FlipSkyW` 4 (was 1.5: the open-space term
    picked the street side). Blend-in = minimum-time profile over the azimuth change D0 (`FlipInRate` 140 deg/s, `FlipInAcc` 2400, `FlipInDec`
    380 deg/s^2; k = covered / D0) -> k >= .9 at ~0.25-0.35 s with the turn under ~55 deg/s by then (a smoothstep first: k .9 at .27 s but
    still turning ~130 deg/s -> TC-B held max 144; the r16 spring reached .9 at ~0.65 s).
  - *Shapes* (`blender/make_flip_shapes.py`, critic r16 "limbs symmetric", "pike a lump from 3/4 behind"): asymmetric tuck grab (left hand low on
    the shin, right on the knee, knees unevenly apart), pike with the right arm swept wide and back, swan with the left arm high / right low and
    the right knee bent (stag line), layout with the left arm leading, kick-out with a wide scissor and the arms out of step. Sticks:
    `_scratch/traversal/r17/blender/sticks.png`. Content rebuilt with `build_traversal.py` (commandlet).
  - *Checker* `roof_check.py` = the critic's single-gap test per flip on the telemetry (apex hips - lower roofline from `city/heightmap_5m.csv.gz`,
    share of program rows >= roofline + 3, flipcam_k at flip_t .35, view_sun_deg min over program + 0.5 s, side / tier).
- **Round 18 -- living bodies through every trick (critic r17 single gap: "every trick holds a frozen inverted split"; test: in every trick window one
  limb_z component changes >= 0.10 per 0.1 s sample, r17 31 of 242 failed; f2 / f3 / f4 shared one inverted split; kickouts froze):**
  - *Dense keyed clips* (`blender/make_flip_shapes.py`): the KEYED shapes are interpolated in the script per bone (normalised lerp of the aim
    directions, linear in u) and keyed on EVERY frame with LINEAR interpolation (r13-r17 keyed 4-5 frames and Blender's auto-Bezier eased every key to a
    standstill: the limbs stopped at each key). Keys are (u 0..1 of the 1 s clip, shape), staggered so no key is reached by every limb at once.
  - *Own inverted shape per program*: frontPikeSwan = `flipPike` (starts long with the arms up, folds) -> `flipSwan` = a continuous unwind (arms overhead,
    the LEFT sweeps out first, the right 0.15 later, back arches, right knee folds to a stag, re-extends, arms sweep on down past the hips, hips flex
    into the tuck); corkscrew = layout -> twist -> `flipStraddle` (NEW: arms fling out of the twist wrap, straight legs split wide to the sides -- an X,
    body straight -- arms rise into a V, legs scissor shut and knees bend into the tuck); backDouble = tuck -> `flipKickout` = a moving extension (legs
    shoot out in a scissor, left arm overhead, right wide, body arches, then the web arm swings up, the left sweeps down, the right knee folds and the
    scissor swaps, ending in the catch reach). `WebTravFlips.cpp`: corkscrew's third segment Swan -> Straddle (inertia 7.5, same timing).
    Sticks: `_scratch/traversal/r18/sticks_wip.png` (`sticks.py <report.json> <png>`).
  - *Offline estimator* `flip_motion_sim.py <HeroFlips_report.json>` (make_flip_shapes now dumps per-frame joints): replicates the program
    timeline + shape layering and runs the critic's test at all six 1/60 s phases. It predicted r17's fails (kickout 1-2, swan 2-4) and 0 for r18 on
    backDouble / frontPikeSwan / corkscrew (backSingle's pencil still fails 1-2: not used by the f-series; b uses frontPikeSwan).
  - *Checker* `limb_check.py <round dir> [prefix ...]` = the critic's test (reproduces r17's 31 of 242 exactly) + the critic's pose.py still count.
  - *Trick camera* (critic r17 TC-A p5 20-29 / range up to 34, TC-C distance 4.1-4.4 m with h p90 .37-.46):
    - pre-blend: the auto-chain predicts its next flow-flip release `FlipPreT` 0.38 s ahead (LongCut clock / the rising front nearing the release
      phase / a roof hold whose gap closes within FlipPreT at the climb rate) and sets `CI.bFlipPre`; latched until the release or the plan ends (an
      unlatched prediction blended out and back in at 110 deg/s). Live play: the trick button held while swinging. The window opens on the held view.
    - azimuth: a view re-chosen while the previous one is still blended moves at <= `FlipAzRate` 50 deg/s (`FlipAzNow`) and costs 0.08 / deg away from
      it; the azimuth weight holds `FlipAzHold` 0.25 s past the catch before the 0.9 s blend-out. Yaw offsets 40-55 (was 35-55: the look leads the
      azimuth by 5-7 deg, so 35 read 28-29).
    - distance: FlipDist 4.4 -> 5.0 (TC4) and it follows the hero's vertical extent (`FlipExtent` = posed joints + 0.2 m, max with the shape table
      `WebFlips::ShapeExtent` 0.1 / 0.25 s ahead): `FlipExtK` 2.6 m per m within [lerp(FlipDistSel, `FlipDistCompact` 4.5, FlipCompact), FlipDistMax 6.4]
      (tuck pulls in to 4.5, open shapes stay >= 5.0; a flat 4.5 floor pulled the open programs in too -> bone-box h p90 .36-.37 on f2 / f3).
  - *Catch guard* (critic r17 "f4's 4th flip missing its catch"): `CatchReachable(CatchFlightS 1.55)` runs the swing search (`Anchors->Find`, the
    AnchorAltDeg lean away from the previous web, AnchorMinAbove, ahead >= 2 m) from the predicted body position at CatchT -0.1 / +0.05 / +0.2 s
    (FULL speed x `CatchSpeedK` 1.08 along the travel heading -- the release turns the climb into forward speed -- 2 m under the release height); none
    attaching -> that release is a plain one (`WH_TRAV catch guard: ...` in the log). Skipped in canyons (FlowApexGap > FlowReadyGain + FlowHoldMax: the
    predictor gave false negatives in a and dropped both its tricks). `CatchGuard=0` turns it off. f4: 3 flips, a plain release at 9.12 s, the 4th flip
    at 10.88 s catching at 12.45 s -> clip 13.3 s (`capture_round.sh` F4Q).
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

## 6. Known bugs / open issues
- **Round 18 state (numbers in §6o):**
  - *TC-C on the backDouble clips* is a knife-edge: the tuck (extent ~1 m) reads .15 of the frame at 5.0 m; the compact pull-in to 4.5 m lifts it to
    ~.18. The literal mask band (p50 .18-.28) vs the critic's p90 <= .36 pull in opposite directions (§6o).
  - *Catch guard is a predictor*: it runs the real swing search from predicted points; it can still be wrong (it passed the f4 4th flip at x 100 the
    first time because the pre-release speed was used). If a flip misses its catch again, look at `WH_TRAV catch guard` lines and the telemetry
    `anchor_x` after the program.
  - *f4 has a plain release* (9.12 s, x 100: no web in reach of a flip there -- the south side opens into the plaza at x ~190-270), so 4 flips take 13.3 s.
  - *a / b* still Midtown canyons (informative): a's 2nd trick (frontPikeSwan 11.9 s) has no clear 3/4 spot (sun 64 deg, TC-G / C fail on a).
  - *backSingle's pencil* still holds (flip_motion_sim: 1-2 slow samples) -- unused by the f-series / b; fix with a keyed pencil if a clip uses it.
- **Round 17 state (numbers in §6n):**
  - *f4 4th flip misses its catch* (11.10 s: no anchor in the reach -- the street's south side opens into a plaza at x ~190-270); 0.33 s dive, TC-K
    blend-out-from-attach reads 0.12 s. Earlier probes from x -225 at 45 m/s reached the plaza and turned back west into the sun. Fix options: slow the
    chain (the flow flips + boosts take it from 26 to 40-49 m/s), or anchors / a turn north at x ~180.
  - *Speed*: the f-series chain accelerates to 40-49 m/s (flow-flip boost + release boost + momentum chain); flips cover 40-70 m of ground.
  - *a / b* still flip inside Midtown canyons (r16 routes, informative): rooflines 63-200 m are out of reach -> r13 climb; a fails TC-B / C / G, view_sun
    81-94 at a's flips. Move a / b too if the critic counts them.
  - *Legacy FLIPS_SPEC lines* (`FLIP_CHECK.txt`): F9 hero px p50 .170-.178 on backDouble program rows (TC-C window passes .18-.21); F3 frontPikeSwan peak
    829 deg/s in a; F4 throne / tuck holds in c (wallFront 0.11 s, unchanged); F5 ease ratio on backDouble's 3rd segment.
  - *North strip is partly park*: the "roofline" there is tree canopy + 2-6 storey blocks (10-30 m in the engine heightmap); the backdrop is the far
    skyline (sky ring p50 .61-.66).
- **Round 16 state (numbers in §6m):**
  - *Sky behind the tricks* 1 % of f1-f5 trick samples (TC-I needs 35 %): route / altitude, not camera (§6m, §8.2).
  - *Hero through the street-tree row* (a 12.55 s): TC-B / TC-G fail on the informative clip a only (§8.3).
  - *Hero height* is a knife-edge on backDouble (tuck .15 vs kickout .30 at one range): tuck pull-in 0.6 m with 0.22 s anticipation keeps f1 / f5 inside .18-.36 on the mask, margins .005-.015.
  - *Obstruction-first vs sun*: with the sun due west the sun-away side is the west half of the avenue; tree canopies (8-15 m at x -265..-257) can make it the obstructed one -> tier 1 (looks into the sun, 38-41 deg).
    Routes f1 / f4 shifted to avoid it; a flip anywhere else in the canyon can still pick tier 1 (`flipcam_tier` = 1 in telemetry, the `choice` log line shows why).
- **Round 15 state (numbers in §6l):**
  - *Sky behind the tricks* 6 % of trick frames (need >= 50): see §8.2 -- a height / route problem, not a camera one. Offline heightmap study
    (`_scratch/traversal/r12/hm/heightmap.csv`): the only low-rise street wall is the y -560 cross street's north side (10-29 m) and the east edge
    x 620-680; every N-S avenue's east side is 45-146 m where the flow flips pass.
  - *Sun hot-spot in glass* (f4 9.85 s) and *pale front-lit hero* (f2 4.73 s, f4 1.77 s): the literal luma test fails (§6l); cross-piece (§8.3).
  - Wall camera now capped at 30 deg up (c 29.6 max, hero in frame through wall-run + top-out 183/183).
- **Round 14 state (numbers in §6k):**
  - *Sky behind the flips is LOW* (sky-ring test, f-series 26 % of trick frames; r13 63 %, r12 95-100 %): a side-on view capped at <= 30 deg
    up looks straight across the canyon at the opposite facade; flow flips play 7-25 m over the street. The offline scan (`sidesky.py`, h 14 m)
    finds side-view sky only on the west avenue x -250 between y ~230 and ~335 (low 6-storey blocks) and at y ~160; every Midtown avenue scores
    0. Getting both (side-on + sky) needs the tricks near roof height: a route over low blocks, or a flow flip that starts from a high release
    (r12's apex launch did it but was an isolated set piece). `FlowCatchRise` 8 (probe) raised the predicted sky only +0.02-0.06.
  - Engine dialog risk (this session): `build_p3.sh` deletes the WebHomage dylib FIRST, then refuses to build while this worktree's game runs --
    a capture batch running at that moment then launched `b` with "Incompatible or missing module: WebHomage" (the engine was stopped with
    stop_ue.sh within seconds; the modal "rebuild modules?" prompt may have shown briefly). Never run build_p3.sh while a capture batch runs.
  - Camera in foliage at a swing bottom through a street-tree canopy (f3 4.6-5.5 s, 43 frames, hero out of frame 5 frames): the camera now
    composes sweep-free instead of holding, so the framing is right but the lens is inside the leaves. Needs canopy avoidance in the swing
    solver or P1 tree collision.
  - Swan / layout arms still a symmetric 90 deg T (critic r13 secondary 2: make them asymmetric) -- a Blender shape edit
    (`blender/make_flip_shapes.py` KEYED) + content rebuild; not done.
  - Corkscrew Layout / Twist segments are near-constant 200-250 deg/s (E1 lists them; they are not tuck / pike phases, so not counted as fails).
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

## 6k. Round-14 checks (captures in `round-14/`; lit Manhattan golden; GPU shared, every run `contaminated` = no perf claim)
Movies 1920x1080 internal = output (`r.ScreenPercentage 100`, TSR + Lumen), fixed 1/60 s step, 0.8 s pre-roll trimmed, 12.8-14.2 MB; no 4K stills.
All nine from the final build (code of 43b13e8). f4 is now north-bound from y 375, 11.6 s (its 5th flip starts 0.15 s before the end: not judged).
| Line | a | b | c | d | f1 | f2 | f3 | f4 | f5 |
|---|---|---|---|---|---|---|---|---|---|
| flips | backDouble, pikeSwan | pikeSwan | wallFront | -- | backDouble | pikeSwan | corkscrew | backDouble, pikeSwan, corkscrew, backDouble | backDouble (+1 cut by the clip end) |
| P1 pitch max (deg up, <= 30) | 7.6 | 0.4 | **56.1 (wall camera)** | 1.7 | 21.7 | 21.6 | 21.5 | **21.2** | 1.5 |
| P2 median pitch 0.5-1.0 s after attaches (4-12 down) | all PASS | zip | -- | all PASS | all PASS | all PASS | all PASS | **5.5-8.3 down, 5/5** | all PASS |
| S1 view out of the flip plane p50 (>= 60) | PASS | PASS | -- | -- | PASS | PASS | PASS | **68 / 69 / 86 / 79** | PASS |
| A1 backDouble tuck on screen (>= 300 deg) | PASS | -- | -- | -- | PASS | -- | -- | **648 / 697** | PASS |
| E1 tuck / pike ends vs middle (<= 70 %) | PASS | PASS | FAIL (wallFront, unchanged) | -- | PASS | PASS | PASS | PASS (39-67 %) | PASS |
| F3 peak deg/s (<= 800) | 784 / **829 FAIL** | 631 | 679 | -- | 763 | 656 | 716 | 790 / 781 / 718 / 763 | 784 |
| F4 longest hold (>= .3 s) | .31 / .56 | .56 | .11 (throne 0.08 s, cut by the landing) | -- | .31 | .56 | .36 | .31 / .56 / .36 / .31 | .31 |
| T4 / T2 max (s) | 1.58 / 2.62 | 1.48 / -- | -- | 0.80 / 2.13 | 1.58 / 2.58 | 1.42 / 2.42 | 1.50 / 2.45 | 1.58 / 2.57 | 1.58 / 2.58 |
| sky ring (>= 50 % sky AND hero >= .15; need >= 70 %) | 0 % | 0 % | 88 % | -- | 26 % | 42 % | 60 % | 16 % | 22 % |
| hero fully in frame | 100 % | 408/419 (perch 4.58-4.75 s) | 594/629 | -- | 100 % | 100 % | 5 frames out (canopy) | 100 % | 100 % |
| camera in geometry (frames) | 0 | 0 | 0 | 0 | 0 | 0 | 43 (tree canopy) | 0 | 0 |
C1 per-frame camera max 2.70 deg pitch / 3.60 deg yaw / 1.11 m in every clip, no isolated image-diff spike except c 3.85 s (the wall top-out, as
r13), 0 frozen-camera frames, 0 T-pose frames. F8 catch 0.02 s after every program with the body 9-24 deg from upright. SPEC_CHECK (engine side):
a T8 PASS p50 .222, T10 FAIL spread .171, **T11 PASS** p50 7.5 down (r13 FAIL); d T8 / T10 / T11 FAIL (d's first swing).
Earlier renders this session (deleted / overwritten): the first f1-f4 renders (before the clearance check) had f4 2.55-2.85 s with the side spot
against a facade -- camera shoved over the hero, hero out of frame 0.3 s (`_scratch/traversal/r14/look/f4_bd_sheet.jpg`); final contact sheet
`_scratch/traversal/r14/look/f4_final_sheet.jpg`.

## 6l. Round-15 checks (captures in `round-15/`; lit Manhattan golden; GPU shared, every run `contaminated` = no perf claim)
Movies 1920x1080 internal = output (`r.ScreenPercentage 100`, TSR + Lumen), fixed 1/60 s step, 0.8 s pre-roll trimmed, 12.8-14.2 MB; no 4K stills.
All nine from the final build (code `0c2934a`), f1-f5 in one GPU hold, a-d in a second. Same routes and scripts as r14 (b: same keys; its zip
now aims along the chase heading).
| Line (`SUNCAM_CHECK.txt` etc.) | a | b | c | d | f1 | f2 | f3 | f4 | f5 |
|---|---|---|---|---|---|---|---|---|---|
| U1 pcm_pitch max (deg UP, <= 10) | -2.0 | -2.8 | **29.6 (wall cam, cap 30; r14 56.1)** | 1.7 | -5.0 | -4.9 | -0.1 | **-1.9** (r14 21.2) | -3.7 |
| U2 trick frames pitch p50 / max (deg up, <= 8) | -5.7 / -2.0 | -8.2 / -6.4 | -- | -- | -7.9 / -5.9 | -6.9 / -5.3 | -5.6 / -4.9 | **-5.2 / -1.9** | -4.9 / -3.7 |
| S1 trick view to sun min / p50 (>= 100 deg) | 112 / 169 | 128 / 157 | -- | -- | 110 / 171 | 115 / 171 | 120 / 155 | **109 / 161** | 112 / 155 |
| T11 median pitch down (4-12) | 7.6 | 11.5 | -0.4 | 6.9 | 8.3 | 9.1 | 7.0 | **5.5** (r14 2.6) | 9.1 |
| L1 hero-box luma >= 245: max / frames > 5 % | .265 / 235 | .129 / 22 | .088 / 29 | .136 / 52 | .138 / 25 | .216 / 67 | .145 / 15 | **.258 @9.85 s / 45** (r14 .934 / 87) | .221 / 100 |
| sky ring (>= 50 % sky AND hero >= .15; need >= 50 %) | 0 % | 0 % | 77 % | -- | 0 % | 7 % | 6 % | 4 % | 0 % |
| hero fully in frame | 100 % | 408/419 | 595/629 | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % |
| camera in geometry (frames) | 0 | 0 | 0 | 0 | 0 | 0 | **8** (r14 43) | 0 | 0 |
| T4 / T2 max (s) | 1.58 / 2.62 | 1.48 / -- | 0.38 / -- | 0.80 / 2.13 | 1.58 / 2.58 | 1.42 / 2.42 | 1.50 / 2.45 | 1.58 / 2.57 | 1.58 / 2.58 |
L1 literally fails in every clip: the box includes background. f4 9.85 s = a glass curtain wall mirroring the sun behind the hero (bloom +
flare ghosts, the hero reads white); f2 4.73 s / f4 1.77 s = a front-lit hero in the 8-deg sun reads pale (fill already 1500 cd there); the
rest are sunlit stone edges / avenue haze inside the box (`_scratch/traversal/r15/look/*.jpg`). f4 per-trick: side view out of the flip plane
p50 73 / 73 / 67 deg, backDouble tuck 685 deg on screen, E1 ends 53-62 % of mid (corkscrew Layout / Twist near-constant, as r14), F3 peaks
784 / 691 / 712 / 760, F4 Kickout hold 0.31 / **0.29** s (2nd backDouble: its roofline rise 6.9 m moved the catch). Flow flips over the lower
roofline: 1 of 5 in f4 (+3.7 m over a 16.6 m wall at 8.87 s); the others are 25-70 m under 45-84 m walls. C1 slew 2.70 / 3.60 deg / 1.11 m,
no isolated image-diff spike, 0 frozen-camera frames. SPEC (engine side): a T8 PASS p50 .222, T10 FAIL spread .187, T11 FAIL only on p5 +3.8
(median 7.6 PASS); d T8 FAIL (first swing), T10 PASS .207.

## 6m. Round-16 checks (captures in `round-16/`; lit Manhattan golden; GPU shared, every run `contaminated` = no perf claim)
Movies 1920x1080 internal = output (`r.ScreenPercentage 100`, TSR + Lumen), fixed 1/60 s step, 0.8 s pre-roll trimmed, 13.4-13.9 MB each; no 4K stills. Seven clips (f1-f5, a, b) came
from the final build `2e86dc8` in one GPU hold; c and d are from the first round-16 hold (same wall camera / no trick camera: identical code path). Table and reading notes: `round-16/TC_TABLE.md`.
- **What each clip did** (`TRICKCAM_CHECK.txt` "selection:" lines): every judged flip chose tier 0 (obstruction + sun ok) at 4.4 m; f4 flips 1.35 / 3.93 / 6.38 / 8.88 s (offsets +40 / +50 / +50 / +50),
  f1 -50, f2 -50, f3 -45, f5 +40; f5's second flip (7.78 s, clip end) and nothing else fell back to the plain chase (tier 3).
- **TC-I sky:** f1 6 %, f2 0, f3 0, f4 1 %, f5 0 (pooled 1 %; a 0, b 0, c 77 % = wall camera looking up the facade). Offline study (heightmap, view ENE / ESE from x -253,
  lens 12 .. 39 m): the skyline over the hero's 11 deg is reached at 67-70 of 70 positions along the west avenue; flow flips fly 13-17 m under 45-146 m walls; nothing on these routes has
  the hero above the skyline. Options (unchanged from r15 §8.2): a route over low ground / the east edge, or a chain mode that flies roof-high (traversal, not camera).
- **Why the camera numbers are what they are** (iteration log, `_scratch/traversal/r16/`): r15 telemetry had the camera 85-107 deg off the heading with p90 216 deg/s; the first held-view build's window max was 216 deg/s
  (slew cap) from a Cartesian blend and from a critically damped blend-out whose tail leaked 22 % of the previous side into the next flip of a chain -> polar blend about the hero + a finite 0.9 s smoothstep blend-out;
  a constant 4.2-4.5 m left backDouble tuck frames at mask .15-.17 -> tuck pull-in with 0.22 s anticipation; hero y .36 -> .38 with constant elevation (pitch p50 was 5.1-5.5 up).
- **Legacy lines** (`FLIP_CHECK.txt`, `FLOW_CHECK.txt`, `SUNCAM_CHECK.txt`): F3 / F4 / F5 are the r15 flip lines (f4 Kickout hold 0.31 s; f5 is one backDouble cut by the clip end); F9 (FLIPS_SPEC: hero px p50 .18-.36 over the
  PROGRAM rows only) reads .159-.174 and FAILS on the backDouble programs (a 1st .163, f1 .170, f4 1st .174 / 4th .167, f5 1st .159) and passes on every other program -- TC-C passes on those clips because its window
  adds 0.5 s of larger chase frames (HOLD mask p50: f1 .185, f5 .178): the knife-edge noted in §8.4. `SUNCAM_CHECK.txt` L1 (hero-BOX luma) still fails as literally written (the box includes sky), L1h = the tight suit mask
  passes; flow C2 "7.97 s" = the clip ends 0.03 s into f5's fallback flip.
- **Probes** (`-nullrhi`, ~15 s each, `_scratch/traversal/r16/batch_probe.sh`, `probe_all.sh`, `scan.sh`, `varscan.sh`, `tc_all.sh`): telemetry-only, enough for TC-A..F, TC-K, the selection log and hero_bbox_h; the mask, occlusion, luma and sky
  tests need a render. `WH_TRAV trick camera choice at hero ...` prints every candidate (`failN`: 1 sweep to the spot, 2 margin beyond it, 3 path ahead, 4 floor; sun / open / sky / clear-time / cost).

## 6n. Round-17 checks (captures in `round-17/`; lit Manhattan golden; GPU shared, every run `contaminated` = no perf claim)
Movies 1920x1080 internal = output (`r.ScreenPercentage 100`, TSR + Lumen), fixed 1/60 s step, 0.8 s pre-roll trimmed, 12.7-13.9 MB each; no 4K stills. f1-f5, a, b are
from the final code (`0d1ab79` build = this commit's C++); c and d come from the previous r17 hold (build of `fe9e0b8`: everything but the blend-in v2) -- their telemetry
has flipcam_k = 0 throughout (no trick camera, no flow flip), so the changed code never ran in them. Files: `ROOF_CHECK.txt` (TC8 / critic test), `SKY_CHECK.txt`
(TC-I), `TRICKCAM_CHECK.txt` + `TC_TABLE.md`, `FLOW_CHECK.txt`, `FLIP_CHECK.txt`, `SUNCAM_CHECK.txt`, `APEX_CHECK.txt`, `ANIM_CAM_CHECK.txt`, `SHOTLIST.md`.
- Per flip (f1-f5, 16 programs): release hips 14-28 m, apex 25-34 m, lower roofline 19-29 m -> apex margin +3.2 .. +14.3 m; share of program rows over
  roofline + 3: f1 90 %, f2 91 %, f3 56 %, f4 75 %, f5 73 %. Camera side -40 .. -50 deg (south side, looking NE over the low strip), tier 0 every time.
- TC-I per clip 75-80 % (ring sky p50 .61-.66); hero mask h p50 .185-.259, p10 .121-.162. Suit-mask luma >= 245 max 0.9 % (TC-H). View_sun min 129-135.
- T2 attach -> attach max 2.87-3.30 s (f4 3.30 = the missed 4th catch), T4 max 1.42-2.32 s.
- Iterations (probes `_scratch/traversal/r17/probe/`, scripts `_scratch/traversal/r17/scripts/`): v1 roof rays hit canopies -> grid down-rays; default arcs in
  the street = 3-5 m bottoms, slow chain -> ArcLowMin 14; f4 from x -300 / -225 (see §6); blend-in smoothstep (TC-B 144) -> minimum-time profile.

## 6o. Round-18 checks (captures in `round-18/`; lit Manhattan golden; GPU shared, every run `contaminated` = no perf claim)
Movies 1920x1080 internal = output (`r.ScreenPercentage 100`, TSR + Lumen), fixed 1/60 s step, 0.8 s pre-roll trimmed, 12.6-14.0 MB each; no 4K stills.
Files: `LIMB_CHECK.txt` (critic r17 test), `TC_CRITIC_TOOL.txt` (the r17 critic's own tc.py), `TRICKCAM_CHECK.txt` + `TC_TABLE.md`, `ROOF_CHECK.txt`,
`SKY_CHECK.txt`, `FLOW_CHECK.txt`, `FLIP_CHECK.txt`, `SUNCAM_CHECK.txt`, `APEX_CHECK.txt`, `ANIM_CAM_CHECK.txt`, `SHOTLIST.md`.
- limb_z slow samples (>= .10 per 0.1 s in every trick window): f1-f5 0 of 238 (r17 31 of 242), a / b / c 0 of 51; pose.py still count 0 everywhere.
- Critic-tool TC-A per trick: offset p5 31-48, p95 32-50, world-yaw range 4-6 deg (r17 p5 20-29, range up to 34). TC-B held p95 7-20, max 19-34 deg/s.
- TC table (render 2): TC-A / B / D-K PASS on f1-f5 and b; TC-C FAIL on f1 / f5 (mask p50 .170-.178 vs .18), a informative (TC-C / G fail: canyon).
  Critic-tool bone box h p90 .29-.37 (f2 / f3 .34-.37 with the flat 4.5 m floor -> render 3 weights the pull-in by FlipCompact).
- TC8 / roof check: every f-series flip PASS (apex margin +3.2 .. +14.4 m). TC-I pooled 66 % (r17 78 %). view_sun min 132-144. Suit luma >= 245 max < 1 %.
- f4: 3 flips, plain release 9.12 s (catch guard), 4th flip 10.88-12.45 s caught (r17: missed). Every f-series flip catches.

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
| r14 | 6/5/6/7/6, flips 7 -- FAILS TARGET (lowest camera 5; won 2 of 5 owner pairs) | The trick camera climbs to 20-27 deg up and looks into the sun, which flares out the flips (f4 9.75-10.05 s: 93-97 % of the hero box clipped); cap 8 up, orbit to the side that puts the sun behind the camera (>= 100 deg); test on f4: pitch never > 10 up, no frame > 5 % hero-box luma >= 245, T11 median 4-12 down. Secondary: T8 (median <= .23, p90 <= .38), throne / kickout >= .3 s, close the tuck + wrap arms in the twist, gaps +-25 %, T3 on a, T10, T14; brand: chest emblem (P2) | r15 sun-aware near-level trick camera, wall cap 30, canopy lift, sun-aware fill, glare term |
| r15 | 7/5/6/6/6, flips 7 -- FAILS TARGET (lowest: camera 5; lost all 5 owner pairs, newer beat older) | The flip camera orbits freely: it overfills the frame, pushes the hero off centre, flies through trees (f4 5.62-5.82 s, hero lost) and finds the sun; pick one side-on yaw clear of trees and >= 100 deg from the sun, hold +-30 deg, hero h .15-.38, x .44-.56, no frame > 5 % luma >= 245. Secondary: trick rate / holds +-15 %, split the tuck, stride-cycle wall-run, T8 <= .23, T14 100-110 on b/c/d; brand: chest emblem (P2) | director's TRICK_CAMERA_SPEC (supersedes the side-on demands): r16 held 3/4 trick camera |
| r16 | 7/5/6/6/6, flips 6 -- FAILS TARGET (lowest camera 5; reference won 6 of 6) | Every trick is shot from the street into a dark facade, and each starts facing the sun; fire flips from an apex with hips >= 3 m over the lower roofline (TC8), pick the 35-55 deg side with view_sun >= 100, blend in within 0.35 s; test f1-f5: >= 35 % sky-ring samples, view_sun min >= 100, suit luma >= 245 <= 5 %, flipcam_k >= .9 by flip_t .35. Secondary: FlipDist 5.5 (h p90 <= .36, cy p95 <= .48), foliage in the occlusion probe, asymmetric limbs / pike side-on, wall-run stride, web <= 45 % on a, T8 | r17 f-series east along the y -560 street over a low strip, flow apex solve + roof hold, sun-first side, minimum-time blend-in, asymmetric shapes |
| r17 | 7/6/6/6/6, flips 6 -- FAILS TARGET (lowest 6; reference won 6 of 6, r17 beat r16 on progress) | Every trick holds a frozen inverted split (f2 / f3 / f4 share it; limbs < .10 per 0.1 s, 31 of 242 samples), kickouts freeze; test: one limb_z component moves >= .10 per 0.1 s in every trick window, pose.py 0 slow on f1-f5. Secondary: TC-A p5 20-29 / range 34, TC-C distance 4.1-4.4 (h p90 .37-.46), foliage in hero_occl, web 53 % on a, wall-run stride; brand: emblem (P2), wall ad / billboard (P4) | r18 continuous dense-keyed shapes (own inverted shape per program, moving kickout), trick-camera pre-blend + extent-following distance, catch guard |
| r18 | not judged yet -- pack `_scratch/critic-P3-r18/pack` (5 owner-clip pairs + street backDouble pair + r17-vs-r18 f4 progress pair) | expected: backDouble tuck small (h p50 ~.18), f4 one plain release | -- |

Round folders `docs/night1/traversal/round-0N/` hold videos, stills, telemetry, SHOTLIST, CRITIC and the check outputs.

## 8. Queue for the next session
1. **Run the blind critic** on `/Users/midir/sm2-n1/_scratch/critic-P3-r18/pack` (7 pairs, A/B randomised by abpack; the answer key is beside it -- do not hand it
   to the critic; owner-clip cuts in `_scratch/critic-P3-r18/refcuts/` (copied from r17's), never committed). Rebuild: `_scratch/critic-P3-r18/make_pairs.sh`
   (our clips from 0.5 s before the first trick's release to 1 s after the next web; f4 = all four flips, <= 12.5 s; progress pair = r17 f4 vs r18 f4,
   same route). Record the verdict in `critic/round-18-CRITIC.md` + §7. The critic's r17 test: `round-18/LIMB_CHECK.txt` (0 of 238 on f1-f5).
2. TC-C knife-edge on backDouble (§6, §6o): if the critic cites hero size, tune `FlipDistCompact` / `FlipExtK` with `-WHCamTune=` (no rebuild).
3. Critic r17 secondaries still open: foliage counted in hero_occl (a 12.3 s), web on <= 45 % of a (53 %), wall-run stride (c: one sliding pose), a / b
   routes still in Midtown canyons (informative). Brand items are cross-piece (P2 emblem, P4 wall ad / billboard).
4. Capture protocol (this session): `SKIP_WARM=1 NO_STILLS=1 gpu_slot.sh capture --label traversal -- _scratch/traversal/r18/cap_batch.sh <seqs>` (<= 7 clips per
   hold, ~25 min; ONE batch at a time -- never queue a second capture of this piece while one is queued or running: one engine per agent);
   checks `bash _scratch/traversal/r18/checks.sh` (FLOW / FLIP / SKY / APEX / ANIM_CAM / TRICKCAM / SUNCAM / ROOF / LIMB / TC_CRITIC_TOOL) + `python3 tc_table.py round-18`;
   `make_shotlist.py round-18 "round 18" <commit>`; nullrhi probes `OUTD=<dir> gpu_slot.sh capture --label traversal -- _scratch/traversal/r18/batch_probe.sh <name>:<s> ...`
   (`BUILD=1` runs build_traversal.py first; the nullrhi limb_z / camera telemetry tracks the render closely: r17 probe 29 vs render 31 slow samples).
   Shapes: edit `blender/make_flip_shapes.py`, check offline with Blender -b + `flip_motion_sim.py` before any engine run.
   **Never build (`build_p3.sh`) while a capture of this worktree is queued or running** unless you want that capture on the new code: the batch loads the dylib at each launch.
   To cancel your own queued gpu_slot waiter send SIGINT to its PID (SIGTERM was ignored while queued).
5. Integration branch still not merged (`origin/Opus-5.5-Loop-Night-1` ~150 commits ahead; its F-perf patch gates the hero-mask telemetry behind `-WHTravMask` --
   capture_round.sh must pass it after a merge).
6. Teardown: `_scratch/traversal/capture/*` frame folders can go once the r18 critic has run; the r17 / r18 critic packs stay until their critics have run.
