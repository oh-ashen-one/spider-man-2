# P2 Characters, round 08: blind critic (Opus 5.5)

Homage fan game, not affiliated with Marvel, Sony or Insomniac. Coordinates are native 4K unless marked 1080.

## Scores
| Axis | Score | Evidence |
|---|---|---|
| Hero model & suit | **5** | The suit is now original: teal and amber with a chevron emblem, no copied layout. The lens rim is sealed, with 0 background pixels at 3×. The head is an unsculpted egg with no brow or nose form. CH1 fails: `hero_turntable_4k` hero spans y 317–2018 (0.79H, target 0.48–0.62). |
| Hero animation | **5** | CH6 met: head-top bob 3.53 Hz (60 fps chase). CH7 met: lean 21° (hip 2375,1225 → neck 2575,700). CH2 met: chase 0.44H. There is no start, stop, turn or idle, and §5 clips are absent. |
| Enemies | **5** | CH11/12 met: 7 thugs at 0.23–0.39H, carrying a bat, a pipe and a pistol. `street_fight_34` shows every thug in a guard idle from 1.5–5.5 s (frame-diff 1.2–2.0 % px). There are 0 knockdowns and 0 hit reactions in 32 frames. |
| Civilians | **5** | Heads are now separated. `crowd_tracking` has 10–11 people (CH16 low end). The hijab walker's rear shin goes horizontal at 18 % of stature (1080 frame 0.25 s, 7.0 s), and her coat stays rigid. |
| Image quality | **5** | CH18 fails. `tee_face_4k` has 3 see-through holes in the mask: 198 px (2240,1071), 91 px (2327,1062) and 24 px. The `thug_face_4k` collar still has a 100×180 px skin wedge (1750–1850, 1350–1530). Clips are 1080p. |

## A/B decisions (pixels first)
- The ref-vs-ours pairs all go to the ref: hero-run A, hero-chase B, hero-standing A, suit-close A, hero-face A, thugs-group A, fight-clip B, thug-close A, citizens-clip A, citizens-still B. The ref sides show lit streets, knockdowns and blended motion.
- progress-hero-standing: **A**. B copies a famous suit's emblem and colour blocking.
- progress-hero-face: **B**. In A the lens sits beyond the head outline.
- progress-suit-close: **B**. It has an original emblem, and A copies the white emblem.
- progress-crowd-still: **B**. A has fused heads.
- progress-tee-mask: **B**. A shows an open mouth slit.
- progress-thug-collar: **tie**. The shard is identical.
- hero-eye-3x: **B**.
- hero-lines-3x: **A**. B's lines stair-step.
- tee-mouth-3x: **B**.
- thug-collar-3x: **tie**.
- crowd-heads-3x: **B**.
- Brand check: no copied logo or text in our frames. The hoodie print is illegible.

## Single biggest gap
Give enemies real combat reactions. Re-capture the 8 s `street_fight_34` and check:
- at least 3 distinct hit reactions (stagger, recoil) and at least 1 knockdown, with the thug's torso on the ground for 1 s or more;
- no 1 s window in which all 7 thugs hold guard idle;
- per-0.25 s frame-diff of at least 3 % px throughout.

## Secondary issues
1. Delete the tee-mask holes and the thug collar skin wedge, so no component is 20 px or larger inside character silhouettes (CH18).
2. Cap the civilian swing-foot height at 10 % of stature, and make long coats and robes deform with the legs.
3. Frame the hero showcase at 0.48–0.62H. Sculpt the brow, nose and cheek volume under the mask. The piped chest notch at (2362–2437, 937–1000) reads as a hole.
4. Add run start, stop, turn and idle clips (CH10, §5). Density is 10 people, against 16–25 on busy streets.

## Verdict: **FAILS TARGET**
Lowest axis: 5. No axis has evidence of 8.
