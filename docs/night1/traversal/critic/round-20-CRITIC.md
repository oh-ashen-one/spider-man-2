# P3 round 20: blind critic (Opus 5.5)
*Homage fan game. Not an official Marvel, Sony or Insomniac game.* Evidence: `_scratch/critic-P3-r20-work/`

## Scores (r18 merged in brackets)
- **Swing: 7 [7].**
  - Passes: T1 holds 0.88–1.37 s (a). T2 gives 4 attaches in 8 s.
  - T7 fails: the apex is 14–24 m and never reaches the roofline. All 8 low points in a sit at 5.8–7.9 m.
  - T1 fails in s1: one hold lasts 2.18 s.
- **Camera: 6 [6].**
  - Perch and blackout are fixed: f4 min mean luma 57.6.
  - Fails after a wall cancel (x2 3.3–3.7 s): the camera is 2.5 m away, the hero sits at cx .17, and yaw whips −35°→+32° in 0.45 s.
  - Fails at w2 3.125 s: the hero fills the frame and is cut off (p90 .58, T8).
  - T19 fails: leaf cards cover the torso (f4 3.5 s) and feet (4.0 s), yet hero_occl reads 0.
- **Web: 6 [6].** T3 fails: web is on 55% of a and 78% of s1.
- **Moves: 6 [6].**
  - The vertical run is now upright and narrow, with camera pitch +29° (T22 passes, c 2.65–4.15 s).
  - At c 3.55 s, a mid-facade hop puts the limbs 3 m off the wall.
  - The side-run is a stiff plank: the legs stay together in 6 of 6 samples (w1 2.9–3.53 s).
- **Body: 6 [6].** At 42–60 m/s the body is within 4–13° of the velocity, but the pose is the same arms-back shape at a 4.25, 8.25, 10.25 and 14.0 s.
- **Flips: 7 [7].** f1 and f4 are now lit against the sky and the tuck and pike read. The arc bottoms dip into the canopy.

No axis is below r18.

## Owner bugs
1. **Swing always available: PASS.**
   - x1: RMB at 1.750 s, rope visible at 1.767 s, mid-flip.
   - x2: RMB at 3.20 s from a side-run, swing starts the same frame.
2. **Zip from side wall-run: PASS.** w2: E at 3.50 s, crouched on the parapet at 5.08 s. But the side-run lasted only 0.31 s.
3. **Wall-run animation: FAIL.** See Moves.
4. **Air at speed: PASS.** The pose differs from the 32 m/s tumble (a 2.25 s).
5. **Perch camera occlusion: PASS.**
   - c 9.0–10.3 s: full body, bbox .227.
   - r1 7.6 s and w1 5.25 s are clear.
   - w2 5.25 s is too far: bbox .079, pitch −52°.
6. **Mouse look: PASS.**
   - In m1 yaw differs from a by 36° at 2.75 s, and pitch is +8° against −8° at 4.0 s. The frames differ.
   - The input is injected (in_cap 0). The input log gives 0.0075°/px, against about 0.12°/px in m1.

## A/B (judged blind, before identity)
| Pair | Better | Why |
|---|---|---|
| wallrun | B | Alternating sprint, camera up the wall. A splays, then planks. |
| wallrun-flip | B | Fluid stride and vault. A is a stiff climb with a mid-facade tuck. |
| swing-chain | B | Street-to-roof altitude. A repeats one low arc. |
| multi-flip | A | Real fall near the facades. B sinks into leaves. |
| chain-flips | B | High arcs between towers. A skims the canopy. |
| progress-wallrun | A | Upright. B is a frog climb with a head-down flip. |

Identity, guessed afterwards: the reference won 5 of 5. In progress-wallrun, A matches c, so r20 improved.

## Biggest gap
**Instruction:** make wallRunSide a stride.
- Feet alternate contacts every ≤0.18 s.
- Peak foot gap ≥0.35 m in every ≤0.36 s cycle.
- Torso within 30° of the wall's up axis, leaning into the run (no plank).
- Run ≥0.6 s before any input.
- No limb more than 0.5 m off the wall mid-facade.

**Test:**
- w1 2.9–3.6 s at 8 fps: legs visibly apart in ≥3 of 6 frames.
- c 3.4–3.7 s: all limbs within 0.3 m of the wall.

## Secondary
1. **Camera after a cancel:** yaw ≤90°/s, distance ≥3.5 m, cx .44–.56 (x2 3.2–3.8 s).
2. **Altitude and canopy:**
   - T7: reach the roofline at least every 4 s.
   - Park arcs bottom ≥3 m above the canopy.
   - hero_occl must count leaf cards.
3. **Web and hold:** T3 web ≤45% of a. T1: s1 hold ≤1.6 s.
4. **Light and brand:**
   - The checker is wrong: it reports 0 dark frames, but the test facade's mean luma is 12–25 at w1, w2 and x2 2.0–4.0 s.
   - Brand check: "POP TH… GUMM" billboard (a 12.25 s, P4) and the chest emblem (P2).

## Verdict: FAILS TARGET
The lowest axes are at 6. No axis is below r18.
