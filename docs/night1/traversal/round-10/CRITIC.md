# P3 traversal + camera, round 10: blind critic (Opus 5.5)

*Homage fan game. It is not an official Marvel, Sony or Insomniac game.*

This review judges pixels only. Instruments: `vp_cam.py`, `nearflow.py 8` and `ref_hero_dets.py` (10 fps), plus 10 fps hero crops read by hand. Scratch data is in `_scratch/critic-P3-r10-work/`. Clips: a = `a_swing_chain`, b, c and d are the other round-10 clips.

## Scores

**Swing arc and rhythm: 6**
- T1, T2 and T7 pass. Rope holds last 0.6–1.3 s and there are 3 and 2 attaches per 8 s. The hero drops from high at 3.8 s to one storey at 6.7 s, then climbs again by 9.0 s.
- T4 fails. The hero holds an arms-spread pose with no web at 12.4–13.0 s.

**Camera: 6**
- These lines pass: T8 (median .213), T9 (.456–.532), T11 (2.6/10.2/22.0°), T12, T13, T14 (103°), T17 (.37), T20 (.39) and T21 (2.17).
- T10 fails narrowly (spread .198) and T18 fails narrowly (p50 .68).
- In b, the hFOV is 96° and pitch p95 is 32°.

**Web read: 6**
- T3 passes: the rope is on screen about 29% of each 8 s window (hand-read). The detector picks up tower edges, so its number was not used.
- T5 and T6 pass. At a 5.4 s the rope runs from the hand to the top edge at 20°, about 3–4 px wide.
- The rope is a faint grey line against the haze.

**Moves and transitions: 5**
- T22 passes: the camera pitches up 42–52° at c 2.3–3.2 s. But the wall-run lasts only 1.2 s.
- T23 fails in b. The trick at 2.5–3.3 s is framed against a facade.
- b ends clinging to a wall at 4.75–6.75 s, with no zip.

**Body animation: 5**
- The arms-out pose held at a 8.7–8.8 and 12.4–13.0 s looks like a stiff mannequin.
- The body lines up with the rope at 5.4 s.

**Flips and air tricks: 4**
- At a 1.9–3.4 s there are two 180° flips, each done in about 0.2 s (about 900°/s). Each shape holds for 0.3 s or less. The camera sits behind the hero, so the flips look foreshortened. Hero height is median .18.
- The reference (release-trick-dive A) does it differently:
  - a tuck at 0.9–1.2 s;
  - an inverted pencil held for 0.8 s (1.3–2.1 s);
  - an inverted swan held for 1.2 s (6.0–7.2 s) with a slow unwind of about 150°/s;
  - the hero at about 0.3 of frame height, side-on against open sky.

## A/B decisions (motion judged first)
- **swing-chain:** A is better (the ref). It has rooftop altitude, blur and web flourishes. B is ours.
- **swing-chain-2:** A is better (the ref). B is ours.
- **release-trick-dive:** A is better (the ref). It holds its shapes and is lit against the sky. B is ours.
- **wallrun:** A is better (the ref). The run is continuous and lasts 3 s or more. B is ours.
- **sprint-jump-swing:** B is better (the ref). The launch reads clearly and the framing is tight. A is ours.
- **progress-swing:** both are ours. B (lit city, round 10) beats A (gray box). B has altitude variety and flips, and its rope time is inside the band.

## Single biggest gap
Rebuild each web-less trick in a as three timed beats:
1. **Rotation:** one 180° rotation in 0.35 s or less.
2. **Hold:** one clean extended shape (inverted pencil or swan) held for 0.6 s or more, rotating at 150°/s or less.
3. **Ease out:** 0.4 s or less into the next attach.

Frame the trick side-on, with the hero at 0.20 of frame height or more and open sky above the roofline behind him.

**Test on 10 fps crops:** each trick shows at least 6 consecutive samples of the same silhouette, and there is at most one full flip per second.

## Secondary issues
1. The hero is hard to read in three places:
   - a 6.7–6.8 s: a near-black blob (luma 28–30, height .07);
   - a 14.8 s: legs washed white by haze;
   - c 2.3–3.5 s: the suit reads black.
2. Camera lines T10, T18 and b's hFOV are just out of band.
3. T4 fails on the held arms-spread pose at a 12.4–13.0 s.
4. The b trick is framed against a facade, b has no zip, and the wall-run is short.

No copied brand or logo was seen in our frames.

## Verdict: FAILS TARGET
The lowest axis is flips and air tricks, at 4.
