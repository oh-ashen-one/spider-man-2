# P3 round 22: blind critic (Opus 5.5)
*Homage fan game. Not an official Marvel, Sony or Insomniac game.* Evidence: `_scratch/critic-P3-r22-work/`

Telemetry shows the r21 and r22 trajectories are identical in a, c, f1, f4, m1, r1, s1, w1, x1 and x2. Only the wall poses changed, and w2 now runs on a sunlit tower.

## Scores (r21 merged in brackets)
- **Swing: 7 [7].** Unchanged. T1 holds are 0.88–1.38 s in a. T7 fails: z only reaches 6–24 m.
- **Camera: 6 [6].** x2 3.38 s: cx .19, distance 2.48 m. The w2 zip is framed too tight: bbox .46–.60, distance 3.2–4.1 m (T8, T15).
- **Web: 6 [6].** Rope is on screen 55% of a (T3 limit 45%). In the w2 zip, web_on=0 from 5.25–6.97 s while he flies at 60 m/s.
- **Moves: 6 [6].** The side-run is fixed: box taller than wide in 69/69 frames, legs apart in 7/10 frames at 12 fps (3.10–3.85 s), facade luma 59–107. But the w2 vertical run (1.0–2.8 s) freezes.
- **Body: 6 [6].** The side-run stride alternates cleanly. The vertical run is legs-together from behind: bbox_w is .082–.088 and knee gap .164 m, both fixed for 1.5 s. Sun bloom greys his legs (1.6 s hips RGB 97/74/81).
- **Flips: 7 [7].** Unchanged (f1 and f4 trajectories identical).

No axis is below r21.

## Owner bugs
1. **Swing always: PASS.** x1: RMB at backDouble 1.50 s, swing at 1.75 s (flip_cancels=1). x2: side-run at 2.88 s, swing at 3.25 s.
2. **Zip from side-run: PASS.** w2: wallRunSide, then zipFire at 4.00 s. The zip never lands: z is 232 m at 6.97 s.
3. **Wall-run animation: FAIL.** The side run passes. The vertical run is a frozen slide: foot_sep climbs steadily .12→.47 m with no alternation.
4. **Air at speed: PASS.** Same as r21.
5. **Perch occlusion: PASS.** hero_occl is 0 in the c and w2_r21route perches. Separate T19 issue: s1 hits 0.70 at 5.22 s.
6. **Mouse look: PASS.** At 3.0 s, m1 yaw is −45° against a's −81°.

## A/B (judged blind, before identity)
| Pair | Better | Why |
|---|---|---|
| wallrun-side-1 | A | Lit facade, vault into flip. B: dark slab, ends on a dead hang. |
| wallrun-side-2 | B | Same as above. A's stride is good but pasted on a flat band. |
| wallrun-vertical | B | Sprint, camera pitched hard up. A crouch-clambers (1.12 s). |
| swing-chain | B | Roof altitude. A is low, past a white gray-box plaza (6.0 s). |
| multi-flip | A | Real fall past towers. B skims the canopy. |
| chain-flips | A | Tower arcs. B is the canopy. |
| progress-wallrun | B | Upright stride. A planks (0.75–1.12 s). |

Guessed identity: the reference won 6 of 6. Progress B is r22.

## Biggest gap
**Instruction:** make the vertical wall-run cycle its legs on every facade.
**Test (w2, 1.0–2.8 s):**
- foot_sep_run_m crosses below 0.15 m and above 0.35 m at least 4 times per second.
- bbox_w changes by ≥25% within every 0.4 s.
- At 12 fps, the legs are visibly apart in ≥6 of 10 frames.

## Secondary
1. **Zip:** draw the rope through the whole zipFlight, or cap the zip at 1.2 s. End the clip with a perch. Right now he holds arms up for 2.7 s with no rope (T4, T5).
2. **Camera after a cancel (x2):** yaw swings −28°→+26° in 0.25 s (216°/s). Not fixed since r21: keep cx .44–.56, distance ≥3.5 m.
3. **Altitude:** T7 roofline drop every 4 s. f4 still skims the canopy (height above floor 12–29 m).
4. **Wall framing:** median bbox .40–.43 (T15 says distance 4–7 m).
5. **P4:** the face mural "…ION DU…" (c 4.5 s) needs a source check. No real brand found.

## Verdict: FAILS TARGET
Lowest axes are 6. No axis is below r21, so merging is allowed on the no-regression rule.
