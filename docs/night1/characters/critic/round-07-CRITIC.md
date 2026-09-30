# P2 Characters, round 07: blind critic (Opus 5.5)

Homage fan game, not affiliated with Marvel, Sony or Insomniac. Flat test stage, so lighting is not judged. Coordinates are native 4K.

## Scores
| Axis | Score | Evidence |
|---|---|---|
| Hero model & suit (CH1/3/4/5) | **4** | `hero_face_lens_4k` matches r06 apart from a camera shift. The right lens sheet sticks out past the head, and background shows between the rim and the lens (x3250–3300, y900–1250). Web lines stair-step (x1850–1950, y750–1100). **IP:** the Advanced-Suit layout is still copied. |
| Hero animation (CH6/7/9/10) | **5** | CH6 met: bob 3.53 Hz side, 3.51 Hz toward, 3.61 Hz 3/4. CH2 met: chase 0.41–0.45H at 0.5–5 s. There is still no start, stop, turn or idle. Every clip is a constant loop, and the hero is mid-stride in the standing view. |
| Enemies (CH11–14) | **5** | `street_fight_34` is unchanged: PSNR 38.7 dB against r06, 6 thugs, 0 knockdowns in 8 s. `thug_face_4k` still has the collar shards: a skin strip (1745–1800, 1345–1520) and a dark shard (1880–1970, 1460–1630). Lips still read through the `tee_face` mask. |
| Civilians (CH16/17/19) | **5** | Up from 4. `crowd_avoidance_demo` 2.5–3.4 s: the hoodie passes the tee at a visibly different depth, with no pass-through. Density is 11 people in `crowd_tracking_4k` and 10–14 in the key stills, which is inside CH16 but below the busy 16–25. The rear foot still lifts 17–23 % of stature (63/273 px at 2.75 s, 40/228 px at 6.125 s). |
| Image quality (CH5/18) | **5** | Up from 4. All four key stills have 0 green-dominant interior pixels (after a 3 px erosion), and the triangle is gone. Detached shoe shards remain: 29 px at (308,1256) in `crowd_key_a` and 19 px at (1244,1389) in `crowd_key_wide`. Clips are 1080p. |

## A/B decisions (judged before identity)
- hero-run **B**: it has starts, a crouch and a vault; A is a loop.
- hero-chase **A**: it has traffic, a sprint and a launch.
- hero-standing **B**: a grounded idle; A is mid-stride.
- suit-close **A**: a weave and raised lines; B has flat painted lines.
- hero-face **B**: sealed rims; A has a doubled rim with a gap.
- thugs-group **A** and fight-clip **A**: knockdowns and FX; B is guard poses.
- thug-close **A**: the face reads; B is buried in FX.
- citizens-clip **A** and citizens-still **B**: the reference side, for density.
- progress-crowd-clip **A**: in B the hoodie passes through the coat woman at 0.5–0.75 s.
- progress-crowd-still: **tie**. A has fused heads between the yellow-skirt woman and the brown-suit man; B has the hijab and black-jacket woman merged.
- progress-key-a **B**: in A the tee head is inside the hoodie.
- progress-key-c **A**: B has a green coat and the triangle.
- progress-avoid **A**: B has legs inside the coat at 0.5–0.75 s.
- jeans-leg, overlap-near, ankle-close and floating-shape: all **A**. B has green tint, touching heads, a cuff sliver and the triangle.

## Single biggest gap
**The hero head and suit (CH4, plus IP).** Replace the copied suit layout with an original panel, emblem and stripe design. Rebuild each lens as one closed rim mesh sealed to a lens that sits inside the head silhouette.

Re-capture `hero_face_lens_4k` and `suit_closeup_4k`. At 3× crops they must pass three checks:
- 0 background pixels between rim and lens;
- the lens never extends past the mask outline;
- web-line edges have no stair steps wider than 2 px.

## Secondary issues
1. Cap rear-foot lift at 12 % of stature. Measure it on walkers 0.3H and taller.
2. Enforce at least 0.5 m of personal space. In `crowd_tracking_4k` the yellow-skirt woman's face sits inside the brown-suit man's head (1440–1560, 850–920). In `crowd_key_tracking` the suit man's hand sinks into the woman's back (about 3690, 1030).
3. Fix the thugs: delete the collar shards, drape the tee mask, and give each landed hit a stagger or knockdown.
4. Remove the detached shoe shards (keep every component at 4 px or less), and raise density to at least 16 people in frame.

## Verdict: **FAILS TARGET**
Lowest axis 4 (hero model & suit).
