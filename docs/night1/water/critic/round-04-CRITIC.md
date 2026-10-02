# Critic W r04: water (blind)

Homage fan game. Not an official Marvel, Sony or Insomniac game.

Method: Rec.709 luma. hp = Y − gauss σ8. A glint is a pixel with Y≥200 and hp≥30. Near crop: 4K x0–1800, y1200–2160. Dollies at 4 fps. No SPEC.md exists, so the gates are the PLAN §4 lines.

## A/B (decided before identity)
- **harbour-sun-high: B.** Crisp crests: hp 34.5 vs 17.2, p1 44 vs 100.
- **harbour-high: B.** Sky and building reflections. A is flat leather.
- **river-low: A.** Whitecaps: p99.5 150 vs 104.
- **river-sun: B.** Glints 7.9 % of pixels, 100 % of columns. A is molten metal, horizontal ac80 .237.
- **seawall: B.** A has hard-edged oil-slick blotches. Neither has foam.
- **harbour: B.** It keeps the island reflection.
- **dolly: B.** It reflects the far shore.

The reference wins all four ref pairs. The previous build wins all three regression pairs.

## Scores
1. **Motion & detail: 4.** Near hp 12.05. Dolly hp 4.1. Harbour hp 7.45 (ref 9.3, with wakes). No rings.
2. **Colour & depth: 4.** Harbour-sun RGB 204/149/79, p1 100 (ref 130/94/67, p1 44). S4 river Y 128.
3. **Reflections & glints: 4.** Sun path: 2.68 % of pixels, 60 % of columns (ref 7.9 % / 100 %). Harbour and river-low: 0 %. The r03 island reflections are gone.
4. **Shore & pier foam: 1.** 0 px with Y≥180 within 30 px of the seawall. No band in any of the 40 dolly frames. The harbour seawall has a hard edge.
5. **Horizon & believability: 4.** River-sun reads as liquid gold with dark pits, harbour-sun as brass, S4 as haze.

## PLAN §4
| Line | Result |
|---|---|
| hp ≥ 12 | PASS 12.05 |
| p99.5 ≥ 150 | FAIL 104 |
| glints ≥ 1 % | FAIL 0 % |
| Y ≤ 80 | PASS 60.8 |
| C14 | PASS 25.4 |
| ac80 ≤ .10 | PASS .076 |
| foam | FAIL |
| ≤ 2.5 ms | FAIL 2.51; S4 and sun missing |

## Biggest gap
Contact foam is missing at the seawall, piles and island edges.

Pass when:
- In `crop_river_low_4k_seawall_foam`, a band ≥12 px wide with Y≥180 lines ≥60 % of the wall-edge rows.
- In `river_low_dolly`, the band's XOR/OR between frames is ≥0.2.
- `harbour_high_4k` shows a bright line ≥3 px wide along the island seawall.

## Secondary
1. Restore the r03 reflections. Test: the water under the island is ≥15 Y darker than open water 400 px away.
2. River-sun: horizontal ac80 ≤.10. Glints ≤6 px, covering ≥5 % of pixels and ≥80 % of columns.
3. Harbour-sun: p1 ≤55 and R−B ≤70 (now 125).
4. Brand: the "AMBROCHE" billboard is still in S4.

## Verdict
**FAILS TARGET.** Lowest axis 1. Mean 3.4 (r03 4.0).
