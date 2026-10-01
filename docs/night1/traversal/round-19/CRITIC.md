# P3 round 19: blind critic (Opus 5.5)
*Homage fan game. Not an official Marvel, Sony or Insomniac game.* Evidence: `_scratch/critic-P3-r19-work/`

## Scores (r18 in brackets)
- **Swing: 6 [7].** Passes T1 (holds 0.97–1.38 s) and T2. Fails T7: apex 16–21 m, never at roofline. The swing-bottom plank pose is the same at 31 and 55 m/s (a 1.0 / 15.25 s).
- **Camera: 4 [6].** f4 1.75–6.5 s: 15 of 21 frames have mean luma <15. At 5.25 s the max pixel is 1 (all black). f1 2.0/3.0/4.0 s: luma ≤0.4. After a zip, the parapet hides the hero: c 9.0–10.25 s shows only the shoulders, about 40 px. Telemetry reports bbox .22–.25 and occl 0 there. The instrument is wrong.
- **Web: 6 [6].** Web on for 55% of a (T3 limit 45%).
- **Moves: 4 [6].** The vertical wall-run is a frog scramble with knees splayed: silhouette w/h median 0.73, body pitch −24…−33°. The side-run lies flat: w/h 1.30, pitch −68° (w2 2.5–3.5 s). T22 passes (camera pitch 27–29°).
- **Body: 5 [6].** fallCalm stands upright at 43–51 m/s (a 4.25 and 10.25 s). On a zip the hero hangs limp (w1 3.75–4.45 s).
- **Flips: 7 [7].** The r18 gap is closed:
  - Durations 1.25–1.55 s, flip_scale .84–.99, peak rate 791–924°/s.
  - Tuck: wrist .03–.04 m, knee ≤.20 m, held 0.87 s.
  - But most flips in f1/f4 play in black frames.

## Owner bugs
1. **Swing always available: FAIL (partial).** Swing restarts after a release during pause: 5 of 5, in 0.02 s (inputtest logs). But a held RMB during a trick or wall-run waits 0.47–1.08 s (f4 11.02 s: 1.08 s; probe s1 3.13 s: 0.92 s).
2. **Zip: FAIL (partial).**
   - From the roof it passes: c 8.50→8.92 s and r1 6.20→6.72 s.
   - From a vertical wall-run it passes: w1 3.60 s → perch at 97.7 m.
   - From a side-run it fails: w2 3.50 s goes into wallZip, then he clings mid-facade at 61 m for 2 s.
3. **Wall-run animation: FAIL.** Same evidence as Moves.
4. **Swing/air at speed: FAIL.** The pose does not change with speed.
5. **Mouse look: UNPROVEN, so FAIL.** Both input logs read "mouse 0 px over 0 frames".
- **Mid-air landing: UNPROVEN.** The r1 landing at 9.37 s falls in a black frame and the clip ends at 9.48 s. The roof run in c 6.2–7.3 s is grounded.

## A/B (judged blind, before identity)
| Pair | Better | Why |
|---|---|---|
| wallrun | A | Upright alternating sprint. B scrambles, then the hero shrinks to a dot. |
| wallrun-flip | A | Horizontal stride, then a flip off the wall. B is a frog climb with head-down ledge flips. |
| swing-chain | A | Continuous pose change and speed blur. B repeats one plank. |
| multi-flip | A | B goes black in an alley. |
| chain-flips | A | Same as multi-flip. |
| progress-wallrun | B | Lean stride, one top flip, crouch landing. A has two head-down mid-facade flips. |

Identity, guessed afterwards: A is the reference in five pairs. In progress-wallrun, A matches c 2.25–5.75 s frame for frame, so r19 regressed.

## Biggest gap
The wall-run is a frog crawl.

**Instruction:** replace it with an upright sprint.
- Vertical run: torso within ±15° of the wall's up axis, silhouette w/h ≤0.55 median.
- Side-run: body long axis within 20° of the run direction, head leading.
- Knee gap ≤0.35 m.
- Alternate hand/foot contacts every ≤0.18 s.
- No mid-facade flips at the setbacks.
- E from a side-run must end on a perch or roof.

**Test:** log the knee gap and run these clips: c 2.75–3.25 s, w1 2.4–3.6 s, w2 2.5–3.5 s.

## Secondary
1. **Blackouts:** no capture frame below mean luma 25 while the hero is on screen (f1, f4). Route swings away from unlit courtyards, and log it with P4.
2. **Perch camera:** keep the parapet from occluding the hero. Fix the bbox/occl telemetry against pixels.
3. **Swing input:** RMB cancels a trick or wall-run into a swing within ≤0.1 s.
4. **Missing tests:**
   - Inject mouse movement into the input test.
   - Show a lit street landing.
   - Brand check (P4): "POP TH… GUM" billboard (a 12.0 s), "R" ghost sign (r1 7.5 s).

## Verdict: FAILS TARGET
The lowest axes are at 4.
