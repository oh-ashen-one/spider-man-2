# P3 Traversal + camera — handoff (after round 13)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

**Status (end of round 13, 2026-09-30): code done and pushed, NO fresh rendered captures.** Round 13 answers the critic r12 single gap
("each trick is an isolated set piece: 1.7 s rise, trick, 1.3 s dive, then a camera cut"): a trick pressed at a web release now starts its
flip program AT the release (**flow flip**), the climb is solved so the program floats back to ~3 m over the release height inside the
canyon, and the next web attaches in the program's final reach; backDouble is two shapes (tuck double + keyed Kickout); the camera's
"too close: cut" rule is gone and the camera output is slew-limited per frame; a hero-only fill light lifts the backlit silhouette.
**Verified only in -nullrhi game probes** (real game, lit Manhattan, telemetry, no pixels; `round-13/PROBE_FLOW_CHECK.txt`, code ac851f7):
release -> first shape 0.00 s, reach -> next attach +0.05 s (one +0.25 s), T4 web-less air max 0.80-1.25 s (<= 3.1), T2 attach -> attach
max 1.97-2.92 s (<= 3.3), per-frame camera max |d pitch| 2.70 deg / |d yaw| 3.60 deg / |d pos| 1.11 m (limits 3 / 4 / 1.2) in all nine clips,
camera in geometry 0-3 frames. In those probes every program was downgraded to backSingle by the old ballistic air test — fixed in
14d0b97 (not yet re-probed). **Blocker:** the rendered captures never ran: a P6 (life) UnrealEditor sat stuck exiting from 06:54 (GPU
100 %, every gpu_slot launch refused), then the Studio's WindowServer watchdog reset at 06:55 and the orchestrator paused the GPU lock
(`_scratch/gpu/PAUSED`: "desktop session dead until the owner logs in"). **Next:** once the lock is un-paused, run §8 step 1 exactly.

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
    camera weight; `-WHHeroFill=<base>,<flip>` overrides (0,0 = off); telemetry `hero_fill_cd`. **Untuned** (no render yet): check hero V in
    the first capture (`flow_check.py --video`) and against P4's look.
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
- **Round 13 (flow flips):**
  - *Not rendered*: no mp4 / pixel numbers exist for round 13 (GPU lock paused, see Status). Unknown until captured: hero fill strength
    (V), sky behind the flips (the flips now play at 10-35 m in the canyon; the r12 sky-ring test will likely drop from 95-100 % -- the
    flip camera still searches the most open sky from below), hero size T8/F9 with FlipDist 3.3.
  - The FitFlip fix (14d0b97) is untested: probes ran with every program downgraded to backSingle; programs up to 1.7 s may push T2 to
    ~3.0-3.3 s when the swing before the trick runs its full 1.2 s.
  - The slew limiter clips attach look-ups (pitch limited in 20-41 frames per clip in the probes) -- no cuts, but a 2.7 deg/frame cap on
    the attach beat; the flip camera's 30 deg look-up floor now starts from the chase view at the release (big pitch ramp in ~0.5 s).
  - The trick camera starts only at the release (no anticipation); wallFront top-out still cut by the landing (Throne 0.09 s, critic r12
    secondary); edge vault / flips on the web still not built.
  - `bTrickLaunch` (r12 apex sky launch) still exists, default off; `SkyPeakNeeded` / sky bookkeeping only run with it or `skyEvery` > 0.
- **Round 12 (apex flips):**
  - *Catch after an apex flip*: over the rooftops there is nothing above him to web onto (`AnchorMinAbove` 3 m), so the catch waits until he
    has fallen to where a facade is above him: f1-f3 catch 1.1-1.5 s after the program (FLIPS_SPEC F8 <= 0.25 s FAIL); f4's catch came 0.07 s
    after (a taller block ahead). Fix idea: a long "sky web" to the next taller tower ahead (<= 60-80 m), or end apex programs in a dive shape.
  - *F10 conflict*: the program starts at the top of the climb (1.6-2.1 s after the release), FLIPS_SPEC F10 says <= 0.1 s.
  - *Reachability*: only the lower southern / western blocks let a launch clear every roof within 30 m (SkyPeakMax 90). In Midtown's avenues a
    trick release by the PLAYER still launches (capped at 90 m) and flips under the rooftops; the camera search then finds the best sky it can.
    f5 (r11's f1 stretch) shows the script rule: no launch, no flip there.
  - *Far skyline*: towers beyond the collision world (visual only) are invisible to the camera's sky rays; the 30 deg look-up floor keeps them
    under the ring. A different city / time of day may need `FlipMinElev` retuned.
  - *T-lines during flips*: the flip camera looks up 30-60 deg from below (TRAVERSAL-SPEC T11 pitch, T12 yaw off-axis and T8 size bands are
    violated inside trick windows by design; FLIPS_SPEC F9 asks for exactly this view).
  - Air time: rise ~1.6-2.1 s + program ~2-2.4 s + fall to the catch: T2 (attaches per 8 s) fails around every launch.
  - `b_release_trick_dive_zip` not re-captured (its r10 timing was already broken in r11; a trick release is now an apex launch, so the drop /
    zip keys at 3.3 / 4.0 s fall inside the climb). a / d were not re-captured (no tricks on their plain releases; their sky launches — skyEvery
    2 — now only fire where the apex clears the roofs, i.e. never on their Midtown avenue, so their T7 roofline rise is gone).
- **Round 11 (flips):**
  - *Sky-launch catches come out of a dive, not the reach* (F8 FAIL on f1 0.43 s / 51 deg, f4 0.45 s and 0.77 s): at the 50-59 m apex the
    anchor search (`FindAnchor`: desired point 30-40 m over the street, or 2.5 m over the body when higher, faces 22-46 m ahead) finds no
    facade high enough, so the web only catches once he has fallen to ~45 m; the program's reach is held 0.2 s (`FlipReachHold`), then the
    forward stick tips him into the dive (the owner clip's S6 also ends in a forward pitch). A plain-release or mid-height program (f2, f3)
    catches 0.02 s after the reach with the body 12 deg from upright. Fix idea: a sky-web search for tower faces above the apex (longer reach,
    looking up), or end sky programs with a dive shape.
  - *TRAVERSAL-SPEC conflicts:* the flip camera's 40 deg orbit makes T12 yaw p90 ~35 deg in f1 / f2 (limit 25) and the larger hero makes T8
    p50 0.24-0.26 (limit 0.23); FLIPS_SPEC F9 asks for side-on rotation and hero 0.18-0.36. The director should say which wins during tricks.
  - *Backgrounds:* in the Midtown avenue the 50-59 m apex is below most tower roofs, so f1 flips read against facades (the owner's S3 is too);
    f2 / f3 / c read against sky. The first f1 take (flip camera 1.0 m under the hero, look-up <= 10 deg) was worse
    (`_scratch/traversal/r11/camv1/`).
  - *b regression:* the r10 script `b_release_trick_dive_zip` presses drop at 3.3 s and zip at 4.0 s; the backDouble program runs to 3.75 s, so
    no zip target is taken and he falls to the street (6.4 s). Re-time b (or give it `"flip": "backSingle"`) next round.
  - *wallFront* (top-out): the top-out air is ~0.9 s, the program 1.14 s, so the landing cuts it at 0.97 turns (0.87 rendered) and the layout
    is not a hold (F4 FAIL, 0.12 s); shorten it or add hang to the top-out.
  - Not built: edge vault / edge grab into a flip (owner S2, F12), flips while still on the web (owner S2 inverted pencil on the rope),
    chaining a second program when the first ends early (`skyTricks` > 1 is disabled in the flip scripts).
  - P2's hero (`-WHHeroClips=...`) has no `flip<Shape>` clips: the anim instance then falls back to the old trick clips, but the root still
    rotates on the program timeline (wall top-out falls back to `releaseFlip` entirely). Splicing the same actions into P2's GLB is a
    path change in `build_traversal.py` + a matching prefix.
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
| r13 | not judged: no rendered captures (GPU lock paused after the 06:55 WindowServer reset) | — | — |

Round folders `docs/night1/traversal/round-0N/` hold videos, stills, telemetry, SHOTLIST, CRITIC and the check outputs.

## 8. Queue for the next session
1. **Capture round 13** once `/Users/midir/sm2-n1/_scratch/gpu/PAUSED` is gone and no UnrealEditor is stuck exiting: rebuild nothing (C++ at
   14d0b97 is built; content was rebuilt this round: `flipKickout` exists, 10/10 flip shapes load), first re-probe the flow flips
   (`_scratch/traversal/r13/batch_probe.sh f1_flow_backDouble:8 f4_chain_flips:13` inside one `gpu_slot.sh capture --label traversal` hold,
   then `flow_check.py` -- confirm backDouble / frontPikeSwan / corkscrew now play and T2 <= 3.3), then capture ONE batch at a time (one engine
   per agent): `gpu_slot.sh capture --label traversal -- _scratch/traversal/r13/cap_batch.sh f1_flow_backDouble f2_flow_pikeSwan f3_flow_corkscrew`
   (first batch without SKIP_WARM), then `f4_chain_flips f5_canyon_backDouble`, then `a_swing_chain b_release_trick_dive_zip c_wallrun_perch
   d_sprint_jump_first_swing` (each batch < 40 min hold; capture_round.sh also waits while 3+ UnrealEditor run, and that wait counts against the hold).
2. Measure: `flow_check.py <clip>_telemetry.csv <clip> --video <clip>.mp4` for every clip -> `round-13/FLOW_CHECK.txt`; `flip_check.py`,
   `sky_check.py round-13 f1_flow_backDouble ...`, `make_shotlist.py`. Tune `HeroFillCd/FlipCd` from the V numbers (-WHHeroFill=).
3. Critic pack: `_scratch/critic-P3-r13/make_pairs.sh` (cuts 0.5 s before the first trick's release .. 1 s after the next web, pairs with
   `refcuts/` owner cuts + r12 f1 vs r13 f1) -> `abpack.py` -> `_scratch/critic-P3-r13/pack`.
4. Then the critic r12 secondaries: wallFront throne hold (top-out air ~0.9 s), Reach bbox <= .38, billboards (P1).
5. Mouse (Hari, `wh.MouseSensitivity`), P5 combat hooks (`docs/night1/manhattan/INTEGRATION_BUGS.md`), awning-safe street wall-run, P2 hero swap.
6. Teardown: `_scratch/traversal/capture/*` frame folders after each round; the critic pack + refcuts stay until the critic has run (never commit owner footage).
