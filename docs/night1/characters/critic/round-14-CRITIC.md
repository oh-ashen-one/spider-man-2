# P2 hero skins, round 14: blind critic (Opus 5.5)
Homage fan game, not affiliated with Marvel, Sony or Insomniac. Coordinates are native pixels.

## Scores
- **Hero model & suit: 6.**
  - Met: CH1, fronts 0.545–0.547H. CH2, chase 0.41H.
  - The headside profile now has a brow, a notch, a nose, lips and a chin. On the Verdant profile the notch is 43 px deep (2.8% of the 1530 px head) at y=880. The nose tip is at y=1160.
  - Cinder cheek luma swings 53→126.
  - Failed: the lens rim (x≈2273, y=1000) sits 18 px proud of the brow (x=2255), so the brow does not overhang the lens.
  - The suit is matte with no gloss. The face cords read as tear-tracks.
- **Hero animation: 5.** Scripted runs are 3.59 steps/s (CH6 met).
  - The playable pawn runs at 4.13 steps/s (CH6 fail).
  - Pose pop between frames 7 and 8: the diff is 9.5 against 3–4 for the neighbouring frames.
  - The run starts in about 3 frames at 0.73 s, against the CH10 minimum of 0.15 s.
- **Enemies: 5.** Compared with r8:
  - Fight: in r8 the thugs were spaced and aiming. In r14 they swarm into the hero (they overlap at t=3 s) and there are no hit FX.
  - Knockdowns are new.
  - Lineup: the twin heads remain (slots 1/6 and 2/7). The pistol sits beside open fingers. The brute's sleeve texture smears onto his hand (white blotch).
- **Civilians: 5.** Unchanged from r8: the frames differ by about 9 luma.
  - The robe and coat are rigid.
  - The hard cut is still there at frame 449 (7.483 s), as it was in r8 at frame 443.
- **Image quality: 5.**
  - Fixed: the sash ends are now finished and the Sage trapezius is smooth.
  - New: a detached lime cord floats about 40 px off the Ash sash end (1490–1540, 760–1150).
  - The diamond grooves stop dead at the armpit.
  - The texture is stretched under the brow shelf.
  - The Verdant armpit piping is pinched (1160–1270, 1150–1270).

## IP gate: PASS
- No spider glyph, web, teardrop lens, red/blue or black/white blocking, or brand text appears on any suit.
- Tessera, Glacier, Ash, Plum and Sage resemble no official suit.
- Saffron's dark mask with gold lines and Cinder's charcoal with cyan don't match any ref suit.
- Cinder's chest rhombus doesn't match a known shield.
- Verdant is a generic green and yellow. Watch it.

## A/B decisions (made before checking identity)
- **progress-head-tessera A, progress-profile-verdant B, progress-head-cinder B, progress-head-sage B:** the cord version wins. It has a nose, a cheek plane, a mouth bulge and a clean trapezius, against the plain sock.
- **progress-chest-ash B and progress-chest-cinder B:** the sash ends are piped and the pecs are sculpted.
- **progress-lineup: tie.** The only difference is the finger pose, and luma is 91.9 against 91.5.
- **All 29 ref-vs-ours pairs: the ref wins.** The ref has gloss, micro-weave, raised webbing, hit sparks and a dressed street. Ours stands on a blank plane.

## Single biggest gap
The playable pawn still fails CH6/CH10 for the second round in a row. Retime the pawn's run to 3.2–3.8 steps/s. Blend idle→run and the spawn pose over at least 0.15 s.

**Test:** in swap_pawn_T_key.mp4:
- the head-top bob FFT gives 3.2–3.8 Hz;
- no frame-to-frame luma diff exceeds 2× its neighbours in 0–1.5 s.

## Secondary issues
1. Sink the lens rims at least 1% of head height behind the brow front.
2. Attach the Ash sash cord, and run the chest grooves out to a seam.
3. Space fight enemies at least 1.5 m apart, have them attack in turns and add hit FX. Close the fingers on the grips and give the twins distinct heads.
4. Remove the crowd cut at 7.48 s.

## Verdict: **FAILS TARGET**
Lowest axis: 5.
