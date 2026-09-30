# P5 Combat r02: independent critic (pixels only)

> Homage fan game. It is not an official Marvel, Sony or Insomniac game and has no affiliation with them.

Our clip: `round-02/fight30_1080p60.mp4` (@t). References: `refs/combat/clips/street-combo`, `street-fight-cars`, `plaza-fight`, `night-street-fight`, `symbiote-finisher`, and the still `group-fight-nm`. Frame diffs are mean absolute gray at 480x270. I resampled both our clip and the refs to 30 fps for a like-for-like comparison.

## Scores (0-10 vs the reference)
1. **Impact & feedback: 4** (r01: 3). Hit-stop now exists: I counted 39 freezes of 4-6 frames each. Each one stops the whole frame, camera included (the diff drops from about 11 to about 0.1, then jumps straight back to about 11, e.g. @3.63 and @13.40). Frozen frames make up 7.3% of ours against 0.3-2.7% in the refs, so the fight reads as stutter. The spark is a few 2-px yellow ticks. The victim hit @13.25-13.65 hardly changes pose over 24 frames. The refs show red rings, blur and bodies flying.
2. **Move set & flow: 4** (r01: 4). Jabs, launcher, air hits and a web-pin are present. The pinned enemy's web splats are flat white paper discs (@22.0). An enemy holds a **T-pose** @2.67-2.83. The hero's body passes through enemies @14.06, @22.0 and @25.9. The "finisher" in finisher/B is an arms-up pose on a downed thug with no cut, close-up or slow-mo (CB10).
3. **Enemy behaviour: 5** (r01: 3). The crowd is now dense (about 8-10 in frame) and has `!` markers and red aim lines (CB5 met visually). The enemies bunch into one knot and share the same hands-at-face guard pose, which reads as filming. The refs spread them into a ring and show tumbles.
4. **Combat camera: 4** (r01: 3). From 0 to 3 s the camera sits at eye level against the light with about 15° of dutch roll. Near-black pixels (<30) cover 26-34% of the frame @1.5 and @2.3. The hero's hands touch the top frame edge @14.06, which fails CB7's 5% margin. Diff spikes above 25 are unblurred whips @2.75 (28.1), @14.08 (35.0), @21.55 (32.7, a lamp pole sweeping across the foreground), @24.12 and @28.22. The refs' spikes are motion-blurred.
5. **Spectacle & variety: 4** (r01: 3). The fight is busier (30 fps median diff 11.9 vs 8.3-17.2 in the refs), but it happens on a flat, empty grey street with no environment use, no scale of FX and no motion blur.

## A/B (decided on quality first, identity guessed after)
- street-combo: **A** (environment slams, readable surround). B is ours.
- street-fight-2: **B** (car wreck, top-down slam). A is ours.
- plaza-fight: **A** (electric FX, props, cinematic cuts). B is ours.
- night-street-fight: **A** (fire and electric FX, lighting). B is ours.
- finisher: **A** (wall slam, close camera beat). B is ours; it has no beat.
- group-still, air-still, contact-still, web-still: **A** each (grounded materials, a real contact flare, a web reticle). B is ours; its web line is about 1 px.
- prev-vs-now: **A** (about 8 enemies with telegraphs vs a sparse duel). I guess A is r02 and B is r01.

## Single biggest gap (testable)
**Hit reaction and impact.** On every hero blow, hold only the hero and the victim for 3-5 frames while the camera keeps a 2-4 px shake, so the whole-frame diff stays at or above 1.0 during the hold. Spawn an additive red-orange flare and ring covering 1-3% of the frame, gone by frame 8. The victim must rotate at least 30° and displace at least 0.5 m within 0.3 s. Heavies and finishers must launch the victim 2 m or more. Test: a 60 fps victim-crop diff below 1.0 for 3 or more frames while the whole-frame diff is 1.0 or more, and whole-frame freeze frames at 3% or less.

## Secondary
1. Remove the 0-3 s eye-level, backlit, rolled opening: keep the pitch at 15-25° down and roll at 0°, and keep the hero bbox 5% or more from every edge, including raised hands.
2. Fix the T-pose and add capsule separation so the hero never interpenetrates an enemy.
3. Add a finisher camera beat: a cut to a close-up of 1 s or more, plus 0.3x slow-mo.
4. **Brand flag:** the hero's chest and back carry a white spider emblem copied from the reference suit (@15.3, @22.0). Replace it with an original mark.

## Verdict: **FAILS TARGET** (lowest axis 4; every axis is below 8)
