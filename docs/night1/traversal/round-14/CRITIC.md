# P3 round 14: blind critic (Opus 5.5)
*Homage fan game. Not an official Marvel, Sony or Insomniac game.*
Evidence: `_scratch/critic-P3-r14-work/` (4/12 fps sheets, crops, luma and telemetry scans)

## Scores
- **Swing arc and rhythm: 6.** T1 (0.88–1.38 s ropes) and T2 (4 per 8 s) pass. 5 of the 7 gaps in a are exactly 0.80 s. T7's low point drops to 0.6 m at a 10–14 s (floor is 3 m).
- **Camera: 5.**
  - Fixed: pitch 0.5–1.0 s after attach is 5.5–11.5° down, and the trick orbit is side-on (yaw about 85–100°).
  - Fail: T8 f4 median .27 / p90 .43; kickouts reach .53–.58 (2.67–2.92 s).
  - Fail: T10 spread .18–.19; T11 f4 median 2.6° down, 20.5° up.
  - Fail: T14 93–95° in b/c/d.
- **Web read: 6.** T5 passes. T3: f4 43% passes, a 53% fails.
- **Moves: 7.** T22 passes (c pitch p95 55.8° up). The throne still lasts 0.14 s (c 4.68–4.82 s). The wall-run still uses the sprint clip (c 2.23–3.93 s).
- **Body: 6.** Arms are now asymmetric (swan at f4 4.65 s). The tuck is open, with knees far from the chest (f4 1.95 s). The twist is a plank with its arms at its sides (f4 6.95 s).
- **Flips / air tricks: 7.**
  - Now good: rotation eases 308→766→410→73°/s (f4 1.42–2.67 s). Holds last 0.37–0.55 s. Four tricks chain, with a kickout into each catch.
  - Fail: at f4 9.75–10.05 s, 93–97% of the hero box is clipped white (luma ≥245), which hides the last half-turn. Flare ghosts cover the tuck at 1.75–2.05 s.

## A/B (judged blind, before identity)
| Pair | Better | Why |
|---|---|---|
| multi-flip | A | Continuous camera. B whips at 2.23–2.30 s (4.0× median frame difference) and puts the hero on the frame edge. |
| pencil-throne | A | Holds the throne about 0.75 s against clean sky. B's hero is flared white at 1.5 s. |
| layout-catch | A | Readable layout, twist, tuck and catch. B's hero is about 0.1 of the frame and twists illegibly. |
| chain-flips | B | Clearer shapes between the webs. A has more natural weight. |
| wallrun-flip | A | Organic. B uses a symmetric inverted Y and swings the camera at the landing. |
| progress-trick | B | Side-on tuck. A pitches steeply up with about 30° of building tilt. Both lose the hero at 2.375 s. |

Guessed identity afterwards: ours won 2 of 5 reference pairs (layout-catch, chain-flips).

## Biggest gap
The trick camera climbs to 20–27° up and looks into the sun. It flares out the flips the owner cares about most.

**Instruction:** cap the trick camera at 8° up. Pick the ±90° orbit side that puts the sun behind the camera (at least 100° between sun and view). Keep the hero box at most 5% clipped pixels.

**Test on f4:**
- `pcm_pitch` is never above 10° up.
- No frame has more than 5% of the hero-box pixels at luma ≥245.
- T11 median is 4–12° down.

## Secondary
1. Pull the trick framing back to T8: median at most .23, p90 at most .38.
2. Hold the throne and the kickout for at least 0.3 s. Replace the wall-run sprint clip.
3. Close the tuck (knees within 0.25 m of the chest). Wrap the arms in during the twist.
4. Vary the gaps by at least ±25% instead of 0.80 s. Fix T3 on a (at most 45%), T10 (spread at least .20) and T14 (100–110°) in b/c/d.

Brand: the chest emblem copies the real game's (P2). No copied sign text was read.

## Verdict: FAILS TARGET
The lowest axis is Camera at 5.
