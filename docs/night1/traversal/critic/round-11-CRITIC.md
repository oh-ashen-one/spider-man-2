# P3 traversal + camera, round 11: blind critic (Opus 5.5)

*Homage fan game. Not an official Marvel, Sony or Insomniac game.*

Pixels, telemetry and spec instruments only (`vp_cam.py`, `nearflow.py 8`, 10 fps crops, a 40 px sky ring around the hero box). Work files: `_scratch/critic-P3-r11-work/`.

## Scores
- **Swing arc and rhythm: 6.** T1, T4 and T7 pass in f4: holds 1.02–1.57 s, height 7.5 m to 49 m. T2 fails: gaps between attaches are 4.07 s and 3.62 s (limit 3.3 s).
- **Camera: 6.** T9 (.467–.532), T12 (7.5/15.4°), T13, T14 (103°) and T17 (.39/.54) pass. T8 fails (median .237 by pixel box), and so do T10 (spread .175), T11 (p5 4.1° down) and T18 (p50 .75). T20/T21 were not re-measured.
- **Web read: 7.** T3 passes at 41%. At f4 5.0 s the rope is dark, 2–3 px wide, 22° from vertical, and runs from the hand to the top edge.
- **Moves and transitions: 6.** T22: the camera looks up 44–56° on the c wall-run. The c top-out flip passes T23 with a 0.99 sky ring. The release tricks fail T23 (see Biggest gap). At b 6.4→6.5 s the hero goes from 52 m/s to a stop with no settle.
- **Body animation: 6.** The inverted swan and pencil read cleanly; at 5.0 s the body is 9.5° off the rope. At f4 12.5 s the blue legs wash out to saturation 8–21/255.
- **Flips and air tricks: 6.** f2 holds an inverted pencil then a swan for 1.08 s (swan at 81°/s), which meets the r10 rule. But f1/f4 backDouble snaps at 640°/s between four shapes that each last only 0.15–0.36 s. The f4 twist at 8.1–8.4 s shows the hero at .08 of frame height against brick.

## A/B (decided before identity)
- **multi-flip: A.** The rotation flows through 3.2 s. B switches pose in steps, then holds an upright fall for 1.2 s.
- **pencil-throne: A.** The pencil unwinds into a throne held 1.8–2.3 s against open sky. B unwinds into a superman in front of a billboard.
- **layout-catch: B.** Layout, tuck and catch in 1.9 s. A holds the pencil, then drifts.
- **chain-flips: B.** The web stays visible and the flips run into the next swing above the roofs. A flips in a canyon against concrete.
- **wallrun-flip: B.** A clean side-on tuck → inverted spread → landing against blue sky. A is dark and cluttered.
- **progress-trick: B.** A real inverted shape, then the swing continues. A ends clinging to a wall.

Identity afterwards: ours lost 4 of the 5 reference pairs and won wallrun-flip.

## Biggest gap
Tricks happen deep in the canyon, with a facade or billboard behind the hero. Measured sky ring, p50 over trick frames:

| clip | sky ring p50 | trick frames with at least 50% sky |
|---|---|---|
| f1 | .16 | 3% |
| f2 | .26 | 11% |
| f3 | .28 | 6% |
| f4 | .05 | 15% |

Fix: start every release trick from a swing apex at least 3 m above the tallest roof within 30 m. During the trick, bias camera pitch and yaw so the sky sits behind the hero.

Test (`sky.py` at 10 fps): in at least 70% of trick frames, at least 50% of the ring is sky, and the hero is at least 0.15 of frame height.

## Secondary
1. backDouble: hold each shape for at least 0.5 s, use at most 2 shapes per trick, and blend between shapes over at least 0.15 s.
2. Green lens ghosts sit over the hero at f4 8.1–8.7 s and b 6.7 s. Log to P4.
3. T2 attach gaps, and T8/T10/T11/T18 out of band.
4. Legs wash out in haze (f4 12.3–12.9 s).

**Brands:** no names from the exclusion list. The billboard and storefronts are invented ("NEON RACERS", "BLUEBIRD LAUNDRY"). The white chest emblem is for the owner to review.

## Verdict: FAILS TARGET
The lowest axis is 6.
