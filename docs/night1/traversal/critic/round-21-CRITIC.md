# P3 round 21: blind critic (Opus 5.5)
*Homage fan game. Not an official Marvel, Sony or Insomniac game.* Evidence: `_scratch/critic-P3-r21-work/`

## Scores (r18 merged in brackets)
- **Swing: 7 [7].** T1 holds 0.88–1.38 s (a). T7 fails: z ≤24 m, never the roofline.
- **Camera: 6 [6].**
  - Perch fixed.
  - x2 3.27–3.53 s: cx .17, distance 2.5 m, yaw swings 50° and back.
  - s1 3.5 s: sun flare washes the hero (luma p90 247).
  - Leaves cover his hands at a 12.0 s, yet occl reads 0 (T19).
- **Web: 6 [6].** Web is on 55% of a (T3 limit 45%).
- **Moves: 6 [6].**
  - The side-run now lasts 0.73 s (w2; r20 0.31 s).
  - It is still a slither: the box is wider than tall in 29 of 44 frames, and the legs trail at 3.58 and 3.75 s.
  - The vertical run is upright, camera +29° (T22).
- **Body: 6 [6].** One glide pose repeats (a 4.25, 10.25 and 14.0 s).
- **Flips: 7 [7].** backDouble now varies, 1.38–1.58 s. The tuck is loose: wrist–shin 0.34–0.45 m.

No axis is below r18.

## Owner bugs
1. **Swing always: PASS.** RMB mid-flip → rope at 1.75 s (x1). Side-run → swing at 3.20 s (x2).
2. **Zip from side-run: PASS.** w2: zip at 3.85 s, perch at 5.38 s.
3. **Wall-run animation: FAIL.** Better, but see Moves.
4. **Air at speed: PASS.** The body streams along travel (a 4.0, 14.25 s).
5. **Perch occlusion: PASS.** The full body is visible at c 9–10 s and w2 5.5–6.5 s.
6. **Mouse look: PASS.** At 3.0 s, m1 yaw is −45° against a's −81°.

## A/B (judged blind, before identity)
| Pair | Better | Why |
|---|---|---|
| wallrun-vertical | A | Sprint. B climbs. |
| wallrun-side-1 | B | Stride and vault. A slithers. |
| wallrun-side-2 | B | Same. |
| swing-chain | A | Roof altitude. B is low. |
| multi-flip | A | Real fall. B skims the canopy. |
| chain-flips | A | Tower arcs. B is the canopy. |
| progress-wallrun | B | Knees drive. A planks. |

Identity, guessed afterwards: the reference won 6 of 6. In progress-wallrun, B is r21.

## Biggest gap
**Instruction:** make wallRunSide an upright sprint.
- Box height ≥ width in ≥80% of wall frames.
- Feet ≥0.3 m apart at each 0.17 s contact.
- Facade luma ≥45 (now 15–30).

**Test:** w2 3.1–3.9 s at 12 fps.
- Legs apart in ≥7 of 10 frames.
- The hero is never hidden by a mullion.

## Secondary
1. **Camera after a cancel:** cx .44–.56, distance ≥3.5 m, yaw ≤90°/s (x2).
2. **Altitude:**
   - T7: reach the roofline every 4 s.
   - Arc bottoms ≥3 m above the canopy (f4 3.2–3.7 s has a flat olive leaf card).
   - occl must count leaves.
3. **Web, light, tuck:**
   - T3 ≤45%.
   - No flip shot into the sun.
   - Tuck wrist–shin ≤0.15 m.
4. **Brand (P4):** the "POP TH… SUMM…" billboard with a face is still there (a 12.25 s).

## Verdict: FAILS TARGET
The lowest axes are at 6. No axis is below r18 or r20.
