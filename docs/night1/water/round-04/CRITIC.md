# Critic W r04: water, island-wide (blind)

Homage fan game. Not an official Marvel, Sony or Insomniac game.

Method: luma is Rec.709. hp = Y − gauss σ8. A glint is a pixel with Y≥200 and hp≥30. Near crop: 4K x0–1800, y1200–2160. Dollies sampled at 4 fps. There is no SPEC.md, so the gates are the PLAN §4 lines (PLAN-firstpass:43).

## A/B (decided before identity)
- **harbour-sun-high: B.** Crisp crests and troughs: hp 34.5 vs 17.2, p1 44 vs 100. A is uniform orange sandpaper.
- **harbour-high: B.** It reflects the sky and buildings, Y 40–150. A is a flat leather texture (Y 57–114, no glints).
- **river-low: A.** Whitecaps: p99.5 150 vs 104, glints in 1.1 % of columns vs 0.
- **river-sun: B.** Small sharp glints cover 7.9 % of pixels and 100 % of columns. A looks like molten metal, with horizontal ac80 0.237 (B: 0.026).
- **seawall-foam: B.** A has blotchy dark oil-slick patches with hard edges. Neither has foam.
- **harbour: B.** It keeps the island reflection. A has more texture (hp 7.45 vs 3.71) but no reflection.
- **dolly: B.** The far shore and trees reflect in it. A has more chop (dT 10.0 vs 7.8) but reads as an opaque dark sheet.

Identity: the reference wins all four ref pairs, and the previous build wins all three regression pairs. **This round is a regression on reflections.**

## Scores
1. **Motion & detail: 4.** Near hp 12.05 meets the line. Dolly water hp is 4.1. Harbour hp is 7.45 against 9.3 for the ref crop, and the ref has wakes. No rings.
2. **Colour & depth: 4.** Harbour-sun water is RGB 204/149/79 with p1 100; the ref is 130/94/67 with p1 44. The S4 river is Y 128, a beige band.
3. **Reflections & glints: 4.** The sun path has glints on 2.68 % of pixels and 60 % of columns (ref 7.9 % and 100 %). Harbour-high and river-low have 0 % glints. The island and shore reflections from r03 are lost.
4. **Shore & pier foam: 1.** The seawall crop has 0 px with Y≥180 within 30 px of the wall. All 40 dolly frames have no band. The harbour seawall has a hard edge with no contact line.
5. **Horizon & believability: 4.** River-sun reads as liquid gold with dark pits. The harbour-sun view reads as hammered brass, and S4 as haze.

## PLAN §4
| Line | r04 |
|---|---|
| hp ≥ 12 | PASS 12.05 |
| p99.5 ≥ 150 | FAIL 104 |
| glints ≥ 1 % (near) | FAIL 0 % (sun 2.68 %) |
| Y ≤ 80 | PASS 60.8 |
| C14 5–35 | PASS 25.4 (153.2 − 127.8) |
| ac80 ≤ .10 | PASS .076 (river-sun far .237) |
| piling foam | FAIL 0 px |
| ≤ 2.5 ms | FAIL river-low 2.51. S4 and sun runs missing |
| axes ≥ 6 | FAIL |

## Biggest gap
Shore contact foam has been missing for two rounds. Add animated foam where the water meets the seawall, piles and island edges.

Pass when:
- In `crop_river_low_4k_seawall_foam`, a band ≥12 px wide with Y≥180 lines ≥60 % of the wall-edge rows.
- In `river_low_dolly` at 4 fps, the band's XOR/OR between consecutive frames is ≥0.2 (it moves).
- `harbour_high_4k` shows a bright line ≥3 px wide along the island seawall.

## Secondary
1. Restore the r03 reflections and keep the r04 hp. Test: in harbour_high_4k, the water under the island is ≥15 Y darker than open water 400 px away.
2. River-sun: cut the low-frequency normal amplitude to bring horizontal ac80 to ≤0.10. Add sharp glints (≤6 px) covering ≥5 % of pixels and ≥80 % of columns.
3. Harbour-sun: troughs need p1 ≤55 and R−B ≤70 (now 125). Harbour-high p99.5 needs to reach ≥140, from sky Fresnel.
4. Brand flag: the "AMBROCHE" billboard with a model's face is still in S4.

## Verdict
**FAILS TARGET.** Lowest axis 1, mean 3.4 (r03 4.0).
