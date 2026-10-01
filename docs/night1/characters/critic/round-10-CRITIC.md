# P2 Characters, round 10: blind critic (Opus 5.5)

Homage fan game, not affiliated with Marvel, Sony or Insomniac. Coordinates are 1080p unless marked 4K. Frames come from `ffmpeg fps=4`.

## Scores
| Axis | Score | Evidence |
|---|---|---|
| Hero model & suit | **5** | CH1 is still unproven: pack hero-standing spans 0.92H, and there is no new standing capture. The head is a smooth egg. The lattice panels are asymmetric (left thigh and one shoulder only). In `street_fight_34` at 1.30–1.50 s, the yellow forearm sinks into the chest. |
| Hero animation | **5** | CH7 is met: hip→neck lean is 26° (pack hero-run 1.0 s, about (1020,500)→(1140,250)). The run is still a side-on treadmill loop with no start, stop or turn (CH10, §5). |
| Enemies | **6** | Met: CH11 (7 enemies), CH12 (about 0.2H) and CH13 (bat, crowbar, pistol; 6 or more silhouettes). Each clip has 2 knockdowns, with 2 enemies grounded together: 34 2.50–4.25 s, wide 2.75–4.25 s, orbit 3.50–5.25 s. Failed: blue-cap's guard pixel diff stays ≤20/255 from 0.0 to 3.25 s, and red-jacket's stays ≤34/255 from 0.0 to 5.0 s. All 7 enemies are packed within about 1 hero-height of the hero. |
| Civilians | **5** | The clip is reused from earlier rounds. The hijab walker's rear thigh is horizontal and her knee is about 0.15 stature (0.0, 1.0, 2.5 and 4.0 s). The coat hem is rigid. |
| Image quality | **4** | The grey arm is gone, which is a fix. Defects at 4K: `hood_face_4k` has two hair meshes overlapping with a hard maroon/blond seam about 570 px long ((1900,633)→(2350,283)). `beard_face_4k` has a flat brown card of at least 125×220 px at (2480–2610, 380–600). `thug_face_4k` still has a collar wedge of 72×151 px at (1746–1817, 1358–1508). |

## A/B decisions
- **Ref vs ours** (fight-clip-34, fight-clip-wide, fight-clip-cars, fight-orbit, thugs-group, hero-run, hero-standing, citizens-clip, knockdowns-still): **ref wins every pair**.
  - fight-clip-34 ref: 5 or more enemies are down at 8.5–9.5 s, and the enemies are spaced 3–6 m apart. Ours is a tight ring on a blank plane.
  - thug-close: ours is close on face fidelity, but the backdrop is flat.
- **Progress pairs:**
  - progress-fight-34: **B**. It has 2 knockdowns, against 1.
  - progress-fight-wide: **A**. B has none.
  - progress-fight-still: **A**.
  - arm-3x: **A**. B has the grey limb.
  - hero-limbs-34: **B**. A has the grey limb.
  - hero-limbs-wide and hero-limbs-orbit: **tie**.
  - thug-collar-3x: **tie**. The wedge is in both.
  - beard-hair-3x: **B**. A has the flat card, which matches the r10 4K.
  - hood-hair-3x: **B**. It has 1 ribbon, against 2.
- **Brand check:** no copied logo. The hoodie collar tag (thug 4K, about (1810,1700)) is illegible.

## Single biggest gap
Give every head exactly one hair asset, and remove the flat cards. At 4K, `hood_face`, `beard_face` and `tee_face` must show:
- no straight colour seam longer than 40 px inside the hair
- no opaque card wider than 20 px that is detached from the scalp
- no background pixels between hair and skin

Also remove the collar wedge: no skin-toned blob larger than 15×15 px in the `thug_face` collar.

## Secondary issues
1. Spread the enemies to 2–4 m from the hero, and let no enemy hold one guard for more than 2 s. Measure this as a torso-crop pixel diff above 30/255 at least every 2 s.
2. Stop the forearm interpenetrating the chest (`street_fight_34` 1.30–1.50 s). Make the lattice panels symmetric.
3. Make a new CH1 standing capture at 0.48–0.62H, with run start, stop and turn clips (§5).
4. Re-capture the crowd. The swing knee must be at 0.25 stature or higher, and the coat hem must follow the legs.

## Verdict: **FAILS TARGET**
Lowest axis: 4.
