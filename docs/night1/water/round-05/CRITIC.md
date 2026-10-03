# Critic W r05: water (blind)

Homage fan game. Not an official Marvel, Sony or Insomniac game.

Method: Rec.709 Y; hp = Y − gauss σ8; glint = Y≥200 & hp≥30. 4K frames; dollies at 4 fps. Compared with r03 (merged) and r04.

## A/B (decided before identity)
- **seawall: B.** Coherent swell. A has flecks.
- **river-low: B.** Wakes. A is frosted (Y 118 vs 56).
- **harbour-high: B.** A is grey leather.
- **harbour-sun: A.** B is brass soup (Y 146).
- **river-sun: B.** Glints 5.5 %. A is a gold sheet.
- **perch: A.** B is a haze band.
- **Previous vs this:**
  - seawall: B, the lace (A has oil specks)
  - river-low: B
  - harbour: A, the island mirror
  - river-sun: B, the sun column
  - perch: A, by a hair
  - dolly: B (A smears into streaks)
  - sun-dolly: A (B is frost)

The reference wins 6/6. The previous build wins 5/7.

## Scores
1. **Motion & detail: 4.** Near hp 20.9. Dolly ac80 ≤ .075. Fine glitter, no wave groups.
2. **Colour & depth: 3.** Near Y 94.1 (r03 76.4, limit 80). S4 river Y 136.
3. **Reflections & glints: 5.** Sun width 53.5 %. Harbour-sun glints 1.67 %. Island Δ 28. Path/flank 1.49 (r03 2.41).
4. **Shore & pier foam: 3.** The gates pass, but it is flecks plus a painted rim.
5. **Horizon & believability: 3.** Frosted river, brass harbour, haze S4.

## Checks
- **(a) PASS.** 74.5 % of rows have ≥12 px with Y≥180 within 60 px of the wall. As a contiguous run, 36.8 %.
- **(b) PASS.** XOR/OR min .64. ac80 .075. But presence is only 12.8 % of rows (needs 30 %); band Y 150–197.
- **(c) PASS.** 96.6 % of the 710 edge columns have a line ≥3 px. Peak Y 204, sd 6.
- **(d) PASS.** Under-island water is 28.0 Y darker (r03 32). Pier reflections are visible.
- **(e) PASS.** hp 20.9, width 53.5 %.
- **(f) Brass soup.** Glints 1.67 %, median 2 px. p1 51, R−B 93.
- **(g) FAIL.** Colour 3 < 5 and believability 3 < 4. Foam 3 > 2.
- **(h) Painted.** The flecks fade in a ramp. XOR .73 is flicker, not drift. The island has a uniform rim and a pier rectangle.

## Biggest gap
The sparkle/foam layer frosts the open water.

Pass when:
- river_low near crop (x0–1800, y1200–2160): mean Y ≤ 80.
- river_sun flanks (x200–700 and 2600–3100, y1000–2160): mean Y ≤ 85.
- river_sun path/flank ≥ 2.2.
- Gates a and c still pass.

## Secondary
1. Make the foam drift. Target: XOR/OR .2–.5, and ≥30 % of rows with ≥6 px.
2. Island line: width cv ≥ .5. Remove the rectangle.
3. Harbour-sun: p1 ≤ 40, mean Y ≤ 110.
4. Brand: the "AMBROCHE" billboard is still in S4.

## Verdict
**FAILS TARGET.** Lowest axis 3. Mean 3.6 (r03 4.0).
