# P3 round 15: blind critic (Opus 5.5)
*Homage fan game. Not an official Marvel, Sony or Insomniac game.*
Evidence: `_scratch/critic-P3-r15-work/` (4 fps frames, 10 fps flip sheets, telemetry stats)

## Scores
- **Swing arc and rhythm: 7.** T1/T2 pass: holds 0.53–1.37 s, attach gaps now vary 1.68–2.62 s (a). T7 low point is still 0.6 m.
- **Camera: 5.** Pitch cap holds (f4 max 1.9° down; T11 median 5.5° down). T8 fails everywhere (median .246–.299; f4 p90 .497). T9 f4 .31–.67. T10 a .18. T14 b/c/d 93–95°. f4 5.62–5.82 s: camera flies through tree canopy and the hero leaves frame.
- **Web read: 6.** T5 passes. Web on for 53% of a (T3 ≤45%).
- **Moves: 6.** T22 passes (c 2.3–4.5 s, >20° up). Wall-run is one diagonal pose sliding up (c 2.25–3.25 s). Throne 0.07 s (c 4.68 s).
- **Body: 6.** Tuck is now a closed ball (f1 3.7–4.2 s). The corkscrew twist (f3 1.85–2.05 s) is unreadable because it washes out.
- **Flips / air tricks: 7.** Eased rotation. Pike held 0.38 s, swan 0.43 s at 83°/s. Every trick flows into the catch within 0.02 s. Glare is down from 93–97% to a peak of 25% of the hero box at luma ≥245 (f4 9.85 s: tuck still white and orange against the sunlit facade; f2 4.75 s 15%; f3 2.0–2.1 s 12%). The flips look canned: every backDouble has an identical rate curve (145→766→73°/s in a, f1, f4 ×2 and f5), and the tuck spins 1.18 s with no shape change.

## A/B (judged blind, before identity)
| Pair | Better | Why |
|---|---|---|
| multi-flip | A | Organic, varied shapes. B's hero goes white with orange flare at 2.1–2.3 s. |
| pencil-throne | A | Pencil held about 0.4 s, throne about 0.6 s against sky. B flares at 2.0–2.4 s and clips at the edge at 2.1 s. |
| layout-catch | B | Steady camera; layout held about 0.4 s. A yaws about 90° at 0.75–1.1 s; hero cut at the right edge at 2.4–2.6 s. |
| chain-flips | B | Continuous weight. A's frame at 2.375 s has no hero. |
| wallrun-flip | A | Real run and asymmetric twist. B slides one pose for about 1 s, then a symmetric inverted Y. |
| progress-chain | B | Flare over the tuck is gone (A: 1.0–1.5 s and 4.0–4.5 s). B is byte-identical to chain-flips A. |

Identity guessed afterwards: the reference won all 5 reference pairs. Progress: B (newer) beats A.

## Biggest gap
The flip camera orbits freely during tricks. It over-fills the frame, pushes the hero off-centre, flies through trees and still finds the sun.

**Instruction:** at release, pick one side-on yaw that keeps at least 100° between sun and view and has a clear line of sight (foliage included). Hold it within ±30° for the whole trick. Set distance so hero height is .15–.38 and hero centre x is .44–.56.

**Test (f4, while flip_t ≥ 0 and 0.5 s after):**
- hero_in_frame = 1 on every frame;
- bbox h p90 ≤ .38;
- cx p5–p95 inside .44–.56;
- no sample with more than 5% of hero-box pixels at luma ≥245;
- no frame without the hero between 5.5 and 6.0 s.

## Secondary
1. De-can the tricks: scale rate and hold ±15% from release speed and height, and add limb asymmetry.
2. Split the 1.18 s tuck (tuck, open, tuck). Kickout ≥0.3 s (now 0.27). Throne ≥0.3 s.
3. Wall-run: blend a stride cycle instead of one held pose (c 2.25–3.25 s).
4. T8 median ≤.23 on all clips. T14 100–110° on b/c/d. T10 ≥.20 on a.

Brand: the chest emblem copies the real game's (P2). c 3–5 s has a faded wall sign ("…UNA GARAGE") and a mural; P4 should check both for copied art.

## Verdict: FAILS TARGET
The lowest axis is Camera at 5.
