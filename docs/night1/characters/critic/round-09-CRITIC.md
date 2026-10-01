# P2 Characters, round 09: blind critic (Opus 5.5)

Homage fan game, not affiliated with Marvel, Sony or Insomniac. Times are clip seconds. Coordinates are 1080p unless marked 4K.

## Scores
| Axis | Score | Evidence |
|---|---|---|
| Hero model & suit | **5** | No new hero capture this round. Pack hero-face: egg head, no brow or nose. CH1 fails: pack hero-standing rows 144–1813 = ≥0.92H, feet cropped. |
| Hero animation | **5** | CH6 met: pack hero-run head-bob peaks at 3.52 Hz. That clip is a 5.4 s constant run with no start, stop, turn or idle (CH10, §5). |
| Enemies | **6** | Knockdowns now exist. `street_fight_34`: the cap thug falls at about 0.85 s and gets up at 3.2 s. The bat thug falls 4.40–4.67 and stays grounded until 7.30 (2.6 s). The orbit clip has 2 down at 4.0 s. `street_fight_wide` has 0 knockdowns in 7.4 s. The red-hoodie thug holds the same face guard in all 32 sampled frames from 0 to 7.75 s. |
| Civilians | **5** | The hijab walker's rear shin is horizontal with the knee at about 0.2 stature (crowd_tracking 0.0, 1.0, 2.0 s). progress-crowd A and B differ by a mean of 2/255 on her legs, so this is not fixed. Her coat is a rigid cone. |
| Image quality | **4** | Tee-mask holes are fixed: the largest is 18 px at 4K (was 198). New regression: the hero's left arm renders as an untextured grey-white limb at 1.30–1.50 s (around 860–930, 450–520). The collar still has a smeared brown polygon about 135×180 px (4K 1740–1875, 1345–1525). |

## A/B decisions
- **Ref vs ours: the ref wins every pair.**
  - fight-clip-34: at 9.0 s the ref has 5 or more enemies down plus airborne launches. Ours peaks at 1 down.
  - fight-cars, fight-wide, fight-orbit, enemy-knockdown: the ref has a lit street and airborne hits. Ours is a blank grey plane.
  - thugs-group, thug-close, citizens, hero: the ref wins on materials, lighting and density.
- **Our progress pairs:**
  - progress-fight and progress-fight-still: **A**. B is a spaced, idle ring.
  - progress-tee-mask: **A**. B has 195 px and 98 px holes.
  - tee-mouth-3x: **B**.
  - progress-thug-collar and thug-collar-3x: **B**. The wedge is less pink but still present.
  - knockdown-3x: **B**.
  - progress-crowd: **tie**. The two are identical.
- **Brand check:** no copied logo or text. The hero emblem is an original hexagon or chevron.

## Single biggest gap
Make the combat reactions dense and varied. In each 8 s fight clip, including `street_fight_wide`:
- at least 4 hit reactions, each moving the head or torso by 0.1 stature or more within 0.2 s of contact
- at least 2 knockdowns, with 2 enemies grounded at the same time for 1 s or more
- at least 2 distinct get-up animations; today one backward-roll get-up is reused at 3.2 s and 7.3 s, and in orbit at 4.5 s
- no enemy holding an identical guard pose for more than 2 s

## Secondary issues
1. The hero shows a default-material arm at `street_fight_34` 1.30–1.50 s. Zero grey or white limb frames are allowed.
2. The get-up pops. At 7.68→7.75 s the body yaws about 180° and goes from lying to crouched in 0.13 s, against the 0.15 s blend in CH10. The bat leaves the ground at 7.45 and reappears in the hand at 7.58. The hero's feet sink into the downed thug from 1.5 to 3.0 s.
3. Keep the walker's rear knee at 0.25 stature or higher during swing, and let the coat hem follow the legs.
4. Hair cards. `beard_face_4k` has a detached rear hair shell with background showing between the layers (4K about 2500, 400–640). `hood_face_4k` has loose ribbon strands (4K about 1360–1480, 440–840). The hero head needs brow and nose volume, and its framing should be 0.48–0.62H.

## Verdict: **FAILS TARGET**
Lowest axis: 4 (image quality). No axis has evidence of 8.
