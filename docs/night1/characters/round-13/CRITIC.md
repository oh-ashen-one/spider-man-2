# P2 hero skins, round 13: blind critic (Opus 5.5)

Homage fan game, not affiliated with Marvel, Sony or Insomniac. Stills are 4K; clips are 1080p60. Coordinates are in native pixels.

## Scores
- **Hero model & suit: 6.** CH1 is met: every front still measures 0.545–0.547H. CH2 is met: chase heights are 0.41–0.47. The lenses are now about 1.6× larger with a closed raised chrome rim. The Verdant profile has a nose that sits 110 px (7.4% of head height) proud of the brow–chin line. But there is no brow ridge, no recess at the nose bridge (the profile edge rises steadily from y=860 to 1140), and no cheekbones, mouth or chin plane.
- **Hero animation: 5.** CH7 is met: about 23° lean (hero_run_side, frame 9). Scripted runs are 3.53 steps/s. CH6 fails on the playable pawn: swap_pawn_T_key runs at 4.07 steps/s (bob minima at frames 72, 86, 101 … 234). The clip also opens with a pose/position pop between frames 7 and 8.
- **Enemies: 5.** CH11 is met: 7 enemies, with three weapon types (pistol, pipe, bat). Exposure is fixed (mean luma 91, against 161 before). CH12 is met: fight heights are 0.28–0.43. But there are two pairs of twin heads, and the pistol is held in open fingers at (2000,1100). In the fight, enemies stay within about 1 m, overlap the hero and get no hit FX.
- **Civilians: 5.** Unchanged. The robe and coat are rigid, and there is a hard cut at frame 449 (7.483 s).
- **Image quality: 5.**
  - The upper end of the Ash sash is still a raw, bulged edge with no piping (1410–1440, 700–1050).
  - Ash armpit: the stitches zigzag and the piping crosses the panel (1120–1200, 1530–1620).
  - The Sage trapezius groove is kinked and torn (head34, about 1030–1080, 1710–1880).
  - Cinder's shoulders show faceting.
  - Every suit's back repeats its front sash and emblem.

## IP gate: PASS
No glyph resembling a spider, no web, teardrop lenses, red/blue or red-on-black blocking, or brand text. OCR found no text.
- Tessera, Cinder, Glacier, Ash, Saffron, Sage and Plum show no resemblance.
- Verdant's green and yellow are generic, with no emblem, so it passes. Watch that it does not drift toward a known green-and-yellow costume.
- On the masks, lenses are ovals, not teardrops, and the face seam is now coloured piping, not ink.

## A/B decisions
- **All 25 ref-vs-ours pairs: the ref wins.** The ref has glossy micro-weave, sculpted brow and cheeks, angular rimmed lenses, dressed streets and hit FX. Ours has matte fabric, a bald egg cranium and empty planes.
- **progress-head-tessera: A.** A has a nose, larger rimmed lenses and teal piping instead of a black ink seam. I guess A is round 13.
- **progress-head-sage: A.** Same reasons.
- **progress-lineup: A.** A has 7 enemies against 6 and is correctly exposed (p99 luma 168 against 217).

## Single biggest gap
Finish the mask sculpt:
- a brow ridge that overhangs the lenses;
- a recess at the nose bridge;
- cheekbone planes;
- a mouth bulge and a chin plane.

**Test (4K headside still):**
- The profile's front edge has a local minimum (the recess) between brow and nose tip at least 1.5% of head height deep, and the brow protrudes at least 1% past the top of the lens.
- On the 4K front still, a horizontal luma line through the cheekbones shows at least 3 extrema with a swing of at least 20 on the dark suits (Tessera, Cinder).

## Secondary issues
1. Bring the playable pawn to 3.2–3.8 steps/s and remove the pop at frames 7–8.
2. Pipe the Ash sash end. Fix the armpit zigzag and the Sage trapezius kink. Give each back its own layout.
3. Give the twin enemies distinct heads and close fingers around the pistol grips. In fights, space enemies at least 1.5 m apart, have them attack in turns and add hit FX.
4. Remove the crowd cut at 7.48 s and add cloth motion to the robe and coat.

## Verdict: **FAILS TARGET**
Lowest axis: 5.
