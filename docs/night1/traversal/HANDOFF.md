# P3 Traversal + camera — handoff (after round 05)

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
| `Anim/WebTravAnimInstance.*` `UWebTravAnimInstance` + `FWebTravAnimProxy` | No AnimBP: game thread picks a node from C1 (ground loco blend walk/jog/run/sprint by speed; land_*; swing 3-way low/bottom/high + L variants + corner bank; zip_*; perch_*; wall crawl/run/side/corner/zip; air cycle timelines; trick_*), crossfades with browser TRANS times; proxy `Evaluate` samples/blends `UAnimSequence`s, spine bank, web-arm aim (upper arm → anchor, elbow eased straight). Clips from `/Game/Traversal/HeroDev/<clip>`. |

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

## 3. Changes vs the browser build (and why)
- **Travel-plane pivot** (`PivotLateralKeep` 0.1; browser = 1): the browser pivots on the real anchor; a facade anchor 15-25 m to
  the side swung him into cross streets and walls. Web still draws to the real anchor; steering rotates the pivot about the body.
- **Deep pendulum** (round 02, critic "flat swings"): each swing's virtual pivot is built so the arc bottoms at
  `ArcBottomMin..Max` 5-12 m over the floor (random per swing) and ≥ `MinArcDrop` 16 m below entry; rope ≤ `MaxArcRope` 50 m;
  pivot ≥ `MinPivotRise` 6 m above the body; ahead ≤ `MaxPivotAhead` 55 m. Replaces browser SWING_DIP (r10f) in this mode.
  `CanyonDipK` / `MinPivotElevDeg` still apply in the reanchor path (`PivotFor`).
- **Tricks only on input** (round 04; browser: ~80 % of releases). Trick input buffers 0.4 s (release or in air).
- **Camera** (rounds 03-05, replaces camera.js composition): 3.8 m behind the lagged heading yaw (horizontal spring 0.07 s,
  held 3.5-5.0 m), 1.1 m above (vertical spring 0.05 s, held 0.7-1.8 m), 0.3 m shoulder; yaw toward hero; pitch puts the hero's
  screen centre at 0.48 (arc bottom) .. 0.40 (arc ends), clamped 5-22° down; attach beat (SwingT < 0.5 s): pitch up / yaw / widen
  (≤ 26° vfov) so the anchor is in frame; sphere-swept collision with clear-orbit search, cut instead of passing < 3 m;
  view held when the hero himself clips geometry. FOV formula, kick/punch/shake, motion blur are the browser's.
- Other: terrain boxes are always a floor (thin ground slab bug); swing anchor lean is horizontal only.

## 4. Commands
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
python3 docs/night1/traversal/scripts/bake_keys.py <auto.json> <telemetry.csv> <out.json> <name>  # rule → plain timed keys
python3 docs/night1/traversal/make_shotlist.py <round dir> "round NN" <commit>   # neutral SHOTLIST.md
```
Telemetry quirk: `anim_*`, `pose_sig`, `pcm_*`, `px_*` are sampled at the start of the next frame (mesh evaluates / camera
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
re-press after `gap` once vz ≤ repressVz; `trickEvery` N presses trick on every Nth release. `*_auto.json` = rule form; the
capture scripts `a_swing_chain`, `d_sprint_jump_first_swing` are baked (bit-identical replay verified); `b`, `c` are hand-timed
(zip timings depend on camera pose — re-verify b/c after any camera change). Sequences: a (spawn 22 m, first press 0.4 s, 15.6 s),
b (spawn 58 m, swing → release+trick 3.2 s → dive → zip 4.8 s → perch), c (street → wall-run up B04_N0 podium → roof → camera
turn → zip to roof edge → perch), d (street sprint → charged jump → first swing → chain, 12 s).

## 6. Known bugs / open issues
- **White / unshaded suit at clip starts** (reported by the orchestrator): the hero sometimes renders white/flat in the first
  frames of a capture. Not diagnosed. Suspects: Interchange materials (`SpiderSuit` MIC) or textures streaming in late under
  `-benchmark -dumpmovie`; test with `-exec "r.Streaming.PoolSize 0"` / force-load textures, or check the MIC parents.
- **b zip framing**: hero ≥160 px only in 41 % of b frames (median 140, min 0 during zip/perch). Zip flight at 50-60 m/s and
  perch orbit search pull the camera far / behind; not tuned in round 05 (test only covered a).
- Anchor on screen at the attach FRAME only 2/4 in a (4/4 within 0.1 s) — the camera turns after attach, no anticipation.
- d: 7 frames at the arms-up jump launch exceed 0.30 model bbox (round 04 rule).
- c: 1 of 7 air sample pairs shares a silhouette (short hop onto the roof); c zip lands on its own podium edge (target hysteresis
  keeps the nearer point); zip perch points can sit 0.3 m from a taller neighbour's wall (hero clips it on arrival, b 5.6 s).
- Swings are slow (2-3.4 s per swing, ~4.5 s per cycle) and apexes reach ~60 m; the reference tempo is faster.
- Chain speeds reach ~60 m/s (browser r10g chain cap 45 + 2.5 × 6).
- Interchange renames bones (`upperArm.R` → `upperarm_r`); code uses `upperArm_R` style (FName is case-insensitive). P2's hero
  swap = change `ClipRoot` and the mesh paths in `SetupHeroMesh`.
- Wall-run: no limb phase variety beyond the clip, camera looks straight at the wall (round-05 critic's biggest gap).
- Not ported: slingshot, tightrope, water/bridge bounces, car roofs, tree anchors, web slack/whip, zip reticle, look-at, foot IK.

## 7. Critic history (blind critic vs Marvel's Spider-Man 2 refs; arc / camera / web / moves / body)
| Round | Scores | Biggest gap | What changed next |
|---|---|---|---|
| r01 | 3/3/3/2/2 | Swings flat: hero holds one height down a rail corridor | r02 deep pendulum, height-driven pitch, web retract |
| r02 | 3/2/4/3/3 | Camera: fixed offset, rigid lock-behind, clips into hero (b 5.5 s, c 6.5-7.2 s) | r03 chase camera + collision + framing checks |
| r03 | 3/3/4/2/2 | Dead air phase: rigid T-pose placeholder between release and attach | r04 real hero GLB + C++ anim, air-cycle variety, tricks on input |
| r04 | 4/3/4/3/4 | Framing: hero 4-6 % of frame, camera far/steep, no sky; metric distrusted | r05 close camera, attach look-up, pixel-true measurement |
| r05 | 5/3/5/4/3 | Wall-run: camera behind/below pitched 20-35° up the facade with the roof edge; head-up body, alternating hands/feet 2-3 steps/s; test ≥4 limb phases at 6 fps, head above hips, hero in frame through the top-out (ref wallrun-glass-midday 2-6 s) | → round 06 (fresh builder) |

Round folders `docs/night1/traversal/round-0N/` hold videos, stills, telemetry, SHOTLIST, CRITIC and the check outputs.
