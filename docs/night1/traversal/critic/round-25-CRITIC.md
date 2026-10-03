# P3 round 25: blind critic (Opus 5.5)
*Homage fan game. Not an official Marvel, Sony or Insomniac game.* Evidence: `_scratch/critic-P3-r25-work/` (rope_round-25_a_swing_chain.json, sm/ALL.jpg).

All 11 clips were re-captured. f1, m1, r1, s1, w2, x1 and x2 match r24 (mean frame diff 1.3–5.1/255). f4 was not captured. p1 is new.

The image tool delivered only one sheet (`sm/ALL.jpg`, 4 frames per pack clip). All other visual claims come from measurements.

## Scores (r24 in brackets)
- **Swing: 7 [7].** T7 passes: lows 7.5–11.2 m every 3.2–3.5 s, drops 21–27 m. T2 fails: attach gaps 3.37 and 3.38 s (max 3.3). T4 fails: a 12.4–13.1 s held fallCalm skydive.
- **Camera: 6 [6].** The c perch is fixed. Wall-run framing still fails T8/T15: w1, w2 and c bbox p50 .42, p90 .44–.45, cam 3.4 m. Pitch was checked against the vertical vanishing point on 7 a frames (within 0.4°).
- **Web: 7 [6].** Check (a) passes. T3 is 41.8%. Rope angle p50 36° (T6 8–54° on 99.7% of frames).
- **Moves: 6 [6].** T22 passes (29° up). The vertical run shows the same knee-up frog pose in all 4 sampled frames (wallrun-vertical B 0.3–2.2 s).
- **Body: 6 [6].** knee_gap_lat p50 .49 m (unchanged). The pawn run is upright and the camera is locked.
- **Flips: 7 [7].** f1 unchanged. a has one trick.

## Checks
- **(a) PASS.** Measured 65 web_on frames at 10 fps. 63 of them have ≥95.5% of samples at ≥25/255 contrast against both 6 px bands. Width median 2–4 px.
  - Dark glass, 10.5–11.2 s: ≥0.958 of samples pass, contrast p10 ≥51.
  - Dark glass, 0.9–1.1 s: ≥0.966 pass, p10 ≥55.
  - At 3.4 and 13.5 s the rope ends at an in-frame anchor (allowed by T5).
  - A control line 40 px off the rope passes 0.067, so the test discriminates.
- **(b) PASS.** c 8.6–10.47 s: hero_in_frame=1 on 113/113 frames. Hero pixels are present on every 60 fps frame, but only 77–206 red px at 8.80–8.82 s. Distance 4.14–6.0 m. Largest pitch change is 14.3° per 0.3 s at 8.68 s.
- **(c) PASS.** p1 head-top FFT over 1.5–11 s peaks at 3.61 Hz (10 fps and 60 fps).
- **(d) PASS.** T7 holds. web_on is 41.8% (r24 41.5%). c 0–8.6 s telemetry is identical to r24, with no ground-orbit snap. Owner bugs:
  - 1–4 and 6 pass: x1 swing 1.75 s, x2 swing 3.20 s, w2 zip→perch, a air 24–45 m/s, m1 yaw −95°→−57°.
  - 5 now passes.

## A/B (blind)
| Pair | Better | Why |
|---|---|---|
| swing-chain-1 | A | Climbs to rooftops, traffic. B: empty canyon, fog wall. |
| street-run | A | Lean, leaps. B: upright, locked cam, empty street. |
| multi-flip | B | Falls past facades. A stays at canopy height. |
| wallrun-vertical | A | Sprint, camera looks up. B: the same frog pose throughout. |
| wallrun-side | B | Lean, roof flip. A: short stride, then a zip past a flat wall. |
| rooftop-perch | B | Skyline ledge. A: flat louvered wall. |
| progress-perch | A | Steady. B whips top-down at 2.7 s. |
| progress-swing | B | Rope visible at 5.0 and 7.0 s. A shows none. |

swing-chain-2 was not judged (no image delivered). Identity guess: the reference won 6/6. progress B and perch A are r25.

## Biggest gap
**Instruction:** make the vertical wall-run a sprint (w1 0.95–3.58 s).
- knee_gap_lat_m median ≤0.25.
- At 10 fps, no two samples 0.3 s apart show the same limb pose.
- cam_dist ≥4.0 m, giving hero bbox p90 ≤.38 (T8/T15).

## Secondary
1. **T2:** attach gaps ≤3.3 s. T4: the silhouette must change every 0.1 s at 12.4–13.1 s.
2. **Hero visibility at c 8.80–8.82 s:** ≥500 suit px.
3. **P4:**
   - Empty streets and a white fog wall at the canyon end.
   - A green ghost shape on the facade at swing-chain-1 B3.0.
   - An untextured olive wall at w2.
4. **P2 IP:** the white spider emblem on the suit's back copies the licensed suit. No readable brand text was found.

## Verdict: FAILS TARGET
Lowest axis is 6. No axis is below r24, and bug 5 passes, so merging is allowed.
