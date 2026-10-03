# Request to traversal (P3 / B) from Tricks (C)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Tricks owns `WebTravFlips.{h,cpp}`, the flip programs / clips (`docs/night1/traversal/blender/make_flip_shapes.py` keys) and the trick input
mapping, but the hooks that CALL them live in traversal-owned files. Round 1 needs these two one-line hooks (not done by C):

1. **Auto / player choice uses the new programs.** `UWebTraversalComponent::ChooseTrick` (WebTraversalComponent.cpp, the `!bLegacyTricks`
   branch) still cycles `SkyP = {backDouble, frontPikeSwan, corkscrew}` / `LowP`. Replace both lists with
   `WebFlips::ChooseForInput(InD0.Y_forward, S.TrickLat, S.AutoFlipK++, Air, S.LastTrickName)` (stick forward / lateral at the trick press;
   `Air` = `AirTimeToClear()` for a plain release, `<= 0` for flow / sky flips whose air is solved) and pass the result through `FitFlip`.
   Until then only scripts (`"flip": "a,b,..."`) reach the 8 new programs (frontSingle, frontDouble, backPike, backLayout, barani, fullTwist,
   rudi, backTripleChain).
2. **`FitFlip`'s fallback** returns `backSingle` when the wanted program does not fit; with 12 programs it should ask
   `WebFlips::ChooseForInput(0, 0, K, Air, Last)` for the longest one that fits instead.

Nothing else in traversal is needed: programs, shapes, tempo variation and the pose logger are inside WebTravFlips.cpp.

## Seen in the round-1 reel (traversal-owned, not fixed by C)
3. **Trick camera inside a facade at an avenue turn.** `t60_trick_reel` ~13.6-13.9 s (frontDouble's kick-out while the chain turns from the
   y -560 street into 5th Av at x ~250): the held 3/4 trick view sits inside / against the corner building's facade (blurred brick fills
   the frame). The held world azimuth (TRICK_CAMERA_SPEC) does not re-check obstruction when the travel heading turns under it.
4. **A flip whose catch swings into a corner tower starts a vertical wall-run** (probe, a west turn into the 10 m cross street at y 80
   mid-backTripleChain: 30 s of wall-run up a 166 m tower). Not in the reel (route changed), noted for the corridor / catch logic.

## After traversal r26 (Tricks C r01 resume, 2026-10-03)
5. **r26 critic T4 gap (a_swing_chain 12.4-13.1 s, held fallCalm).** A trick program can fill it only if the release that precedes it
   asks for one: the shortest release program at base tempo (`WebFlips::FindBase(..)->CatchT()`) is backLayout / backPike, ~1.2-1.3 s,
   so a 0.7 s fall needs either a re-attach (traversal) or the hook in item 1 with `Air` from `AirTimeToClear()` (ChooseForInput
   returns NAME_None when nothing fits). In the tricks reel the same pattern appears after a program ends before the catch
   (e.g. probe 13.35 s: backLayout ends, node `air_fallCalm` until the next web); WebTravFlips now keeps the final reach / kick-out moving
   while the flip node is active, but the fallCalm node itself is traversal's.
6. Items 1-2 are still open (the reel reaches the 8 new programs through its script's `flip` list only).

## Tricks C r02 (catch snap; critic r01 "every catch snaps", target <= 250 deg/s chest rotation in every 0.1 s window after a trick)
Tricks r02 starts the catch inside the program (WebTravFlips.cpp catch lean: the predicted swing frame is reached by the flip's pitch +
twist before the web attaches, and the shapes blend into the swing node's starting pose). Three parts of the catch are outside
WebTravFlips and keep a pop at the attach frame (measured in the r02 probes, see round-02/NUMBERS.md):
7. **SpineBank switches on in one frame** (WebTravAnimInstance.cpp `Frame.SpineBank = A.Mode == Swing ? -0.35f * A.Swing.Bank : 0.f`):
   at the catch the chest rolls by 0.35 x |Sw.Bank| rad (up to 20 deg) in a single frame, and Sw.Bank is the PREVIOUS swing's stale
   bank (StartSwing does not reset it; Orient only updates it while swinging). Ask: ramp SpineBank like BodyAlignW (e.g. `Dt / 0.2f`
   steps) and start Sw.Bank from 0 (or from the air bank S.Bank) in StartSwing. The same stale bank drives the swing node's
   corner-bank clip weight at the catch.
8. **No roll channel for a flip**: PoseFigure applies `Ry(pitch) * Rz(twist)` only, so the rope's sideways lean at the catch
   (8-68 deg in the r02 probe) cannot be prepared by the program and is left to the 14/s body slerp. Ask: an optional roll term
   (e.g. `FWebFlipPose::RollDeg`, applied as `* FQuat(FVector(1,0,0), Roll)` after the twist) -- WebTravFlips already computes it
   (`GC.Rho`, logged as catch_rho in the -WHTrickPose log).
9. **A program that ends with no web in reach** pitches the body to the streamlined air frame (Orient, AirAlignV0/V1) and the web
   often catches 0.1-0.3 s later from that dive frame (r02 probe: barani 10.63 s, backLayout 45.73 s, frontDouble 49.40 s): the
   second change lands inside the 0.4 s after the trick end. WebTravFlips now leans into the air frame before such an end; the late
   catch itself is a traversal transition.
