# P3 round 13: blind critic (Opus 5.5)
*Homage fan game. Not an official Marvel, Sony or Insomniac game.*
Evidence: `_scratch/critic-P3-r13-work/` (4 fps and 12 fps contact sheets, frame-diff scan, telemetry stats)

## Scores
- **Swing arc and rhythm: 6.**
  - Pass: T1 (ropes held 0.98–1.40 s), T2 (attach to attach 1.80–2.65 s) and T4 (longest gap 1.62 s, with a trick in it).
  - Fail: the cadence is metronomic. Every chain alternates 0.80 s and 1.48 s gaps (a, f1–f5).
- **Camera: 5.**
  - Fixed: the one-frame cut is gone. The largest frame difference is 2.3× the median, spread over 5 frames.
  - Fail: T11. Pitch p5 is 51–56° **up** in every clip, the f4 median is 11° up, and the camera stays 53° up after the attach (f4 8.2–8.3 s).
  - Fail: T8 (median .24–.29, f4 p90 .42) and T10 (spread .12–.19).
  - At f4 8.75–9.0 s the camera is in foliage.
- **Web read: 6.** T5 passes. T3 fails: the rope is on for 53–56% (a, f1, f2, f5).
- **Moves: 7.** T22 passes (c 2.23–3.85 s, 13→56° up). The throne still lasts 0.09 s (c 4.68–4.77 s). The wall-run uses a floor-sprint clip.
- **Body: 6.** The hero is no longer black. The swan and layout shapes are a symmetric inverted T with arms at 90°, which looks like a mannequin (f4 7.4–7.8 and 11.5 s).
- **Flips / air tricks: 6.**
  - Now good: the shape starts 0.03 s after release (f4 1.47→1.50 s), and the web attaches at the end of the flip (2.95 s). Tricks now chain.
  - Fail: the tuck spins at a constant 678°/s for 0.95 s, then drops to 123°/s in one step. There is no ease in or out.
  - Fail: the camera sits under and behind the hero, so backDouble reads as a spinning ball (f4 1.9–2.4 s).
  - Fail: b uses 5 shapes in 1.7 s.

## A/B (judged blind, before identity)
| Pair | Better | Why |
|---|---|---|
| multi-flip | A | Continuous, organic tumbling. B loses the hero off the bottom edge at 2.375 s. |
| pencil-throne | A | Close. Both have clear shapes. A's limbs vary, B's inverted T is stiff. |
| layout-catch | B | One continuous tumble into the web. A holds a rigid T. |
| chain-flips | B | Flows with no camera whip. A has clearer flips but stiff X and T shapes. |
| wallrun-flip | A | Natural. B's flip is clean but lands after a camera swing. |
| progress-trick | A | Catches the web within 2.5 s. B has a black hero (0.75–1.9 s) and a web-less stretch of more than 5 s. |

After guessing identity (60 fps, lit city), ours lost all 5 reference pairs. The pencil-throne pair was the closest.

## Biggest gap
The flip camera looks up from under the hero. The somersault axis points at the lens, so rotation doesn't read, and the camera stays tilted up into the next swing.

**Instruction:** during a trick, orbit the camera side-on to the somersault axis (at least 60° from it) and cap the upward pitch at 30°. Within 0.5 s of attach, return the pitch to 4–12° down.

**Test on f4:**
- `pcm_pitch` is never above 30° up.
- The median pitch 0.5–1.0 s after each attach is 4–12° down.
- On the capture, the tuck silhouette's head-to-hip axis rotates at least 300° in the screen plane.

## Secondary
1. Ease the rotation: peak rate at mid-flip, at least 30% slower at the start and end. Hold each named shape at least 0.3 s. Throne at least 0.3 s.
2. Replace the symmetric 90° arm shapes with asymmetric shapes: arms 30–60° off horizontal, legs split.
3. T8: bbox median at most .23. T10: cy spread at least .20. T3: rope on at most 45%.
4. Vary the rope and gap lengths by at least ±25%.

Brand: the chest emblem copies the real game's (P2). The signs (BREWHOUSE COFFEE, SONARA, LUMEN, HALEY'S) are invented; none is a real brand.

## Verdict: FAILS TARGET
The lowest axis is Camera at 5.
