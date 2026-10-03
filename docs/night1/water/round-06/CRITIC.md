# Critic W r06: water (blind)

Homage fan game. Not an official Marvel, Sony or Insomniac game.

Method: Rec.709 luma (Y); hp = Y−gauss σ8. Dollies at 4 fps, plus 60 fps frames for t=4–5 s. My instrument reproduces the r05 critic's r05/r03 numbers.

## A/B (decided before identity)
- **Reference vs ours:** the reference wins 6/6.
  - river-low B
  - seawall A (Y 66 vs 108)
  - harbour-high B
  - harbour-sun A
  - river-sun A
  - perch A
- **Previous vs this:**
  - river-low B
  - seawall A (B is a sugar crust)
  - harbour A (mirror)
  - river-sun A
  - perch A
  - dolly B (A smears)
  - sun-dolly A
- **Identity, from frame matching:** I picked r06 in 3/7.

## Scores
1. **Motion & detail: 4.** hp 18.25, ac80 .071. One micro-chop scale. The water's best-match shift is 0 px while the promenade moves 14 px.
2. **Colour & depth: 5.** Near Y 75.4 and flanks 80.2. harbour_sun (mean 127, R−B 93) and S4 haze are unchanged.
3. **Reflections & glints: 5.** Path/flank 2.60. Glints are 2.38 % with 2 px median size. Pier reflections are visible. Sparkle width 36.9 %. The r03 island mirror is lost.
4. **Shore & pier foam: 3.** A frosted crust: seawall crop x0–300 Y 96.9 (reference 66). Uniform rim plus the pier rectangle.
5. **Horizon & believability: 4.** The rivers read as water. Harbour brass with a tile grid, harbour leather and S4 haze are unchanged.

## Checks
- **(a) PASS:** 75.4.
- **(b) PASS:** 80.2 and 2.60. The left flank alone is 94.3.
- **(c) PASS:** gate a 65.9 % (contiguous 26 %); gate c 75.6 %.
- **(d) PASS:** XOR/OR ≥.52 in all 39 pairs; ac80 .071.
- **(e) FAIL:** Δ27.9, reflections present, hp 18.25 all pass; sparkle width 36.9 % < 50 %.
- **(f) PASS:** 4 / 5 / 5 / 3 / 4.
- **(g) PASS.**
- **(h) FAIL:** 3/7.
- **(i) Painted:** the foam fades in place. IoU .70 → .14 over 0.5 s, with no shift.

## Biggest gap
The seawall foam is a frosted crust fading in place. Make it world-anchored, advected lace on dark water.

Test: `river_low_dolly` 60 fps frames, x780–980 y600–1080, 15-frame gap. Pass when:
- the best-correlation shift tracks the promenade's (≥10 px), with ≥0.1 correlation gain over zero shift;
- seawall crop x0–300 mean Y ≤80;
- gate a holds.

## Secondary
1. river_sun sparkle width ≥50 %, with each flank ≤85.
2. harbour_sun_high: mean ≤110, p1 ≤40, R−B ≤70, and no tile grid.
3. harbour_high: restore the r03 mirror; rim width cv ≥.5; no pier rectangle.
4. Add swell-scale wave groups. S4 river Y ≤100.

## Verdict
**FAILS TARGET.** Lowest axis 3. Mean 4.2.
