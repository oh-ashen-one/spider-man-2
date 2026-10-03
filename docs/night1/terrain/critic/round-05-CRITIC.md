# Terrain (E) round 5: critic verdict

Homage fan game, not official Marvel, Sony or Insomniac. All numbers are my own, measured on `round-05/stills` (4K), on `t4`/`t5` frames at 4 fps, and on refs `cp_0554`/`cp_0605` (upscaled 2x). Round-4 scores are in brackets.

## Scores
- **Lawn: 4 (4).** p10 R/G is 0.920 (fixed), but the lawn is still chartreuse (saturation 0.917 vs 0.84 on the ref). There is a pale 287 px slab at (449,1439). p4 σ6 is 5.48 vs 0.4–2.1 on the ref.
- **Paths + water edges: 4 (4).** The p3 bank rocks are smooth olive eggs (hp3 SD 0.75–0.90, saturation 0.56). The infields are faint.
- **Shoreline: 4 (4).** The p6 seam is still there: luma 89→67 within 25 px at y=2000. The water is khaki RGB (82,76,47) with σ6 3.7. The esplanade is empty and its trees cast no shadows.
- **Trees: 5 (4).** Crowns now read as leaves: 19/24 reach σ3 ≥ 9 and the median is 12.06 (r04: 9/24, 8.1). Their saturation is 0.636 and their trunks are untextured.
- **Overall: 3 (3).** Golden light falls but nothing casts a shadow onto the ground. The reference won all 11 pairs.

## Checks
- **a) FAIL.** 5 dark foreground boxes are below 9: (1500,1950) 6.11, (2250,1800) 7.12, (3450,1200) 8.14, (2400,1650) 8.25, (2100,1950) 8.34.
- **b) FAIL.** Median saturation 0.636; the far band is 0.54–0.57.
- **c) FAIL.** The straight silhouette edge passes: none of 30 px or more. But a smooth hull ball floats at (1125–1200, 235–295), hp3 SD 3.4 against 12.9 on the leaves next to it, and a second one at (2183,597).
- **d) FAIL.** Tree at (3005,1100): darkest lawn within 35 px is 0.71× the lit luma (~105). Tree at (3040,1078): 0.62. Only the pair at (2900,1060) passes, at 0.51.
- **e) PARTIAL.** p10 passes: σ6 18.68, guard 16.31, R/G 0.920/0.944. p4 fails: σ6 5.48 > 5.
- **f) b PASS, c marginal, d FAIL.**
  - b: saturation 0.70–0.95; the p9 guard sits exactly at 0.700.
  - c: the t4 blankets are woven, but at 0.75 s a trunk 360 px wide is untextured (hp3 SD 1.1).
  - d: ground σ3 (bottom 200 rows) is below 5 at 11.0–11.5 s and 14.75–15.25 s.
- **g) PASS.** [4,4,4,5,3].
- **h) PASS.** I preferred the summer build in 5 of 5 pairs.
- **GPU ms:** not credited.

## A/B (decided before identity)
- **Views:** south B, reservoir B, pond B, great-lawn A, panorama A, lawn-eye A, shore-west B, shore-east B, piers B. The winner had darker varied canopy, lawn shadows and grey rocks.
- **Motion:** sprint B (backlit dapple), avenue B.
- **Progress:** south B, reservoir B, lawn-eye A, great-lawn A, panorama B (marginal: lime clashes with the haze).
- **Pack flaw:** resolutions differ (1612 vs 3226 px), which leaks identity.

## Biggest gap
Trees and objects must cast sun shadows onto the lawn and esplanade. Test:
- In p4, each isolated tree at (3005,1100), (3040,1078) and (2900,1060) has a 15 px lawn box within 60 px on its anti-sun side at ≤ 0.6× the lit lawn luma.
- In p6, each esplanade tree has a shadow ≤ 0.6× the paving luma.

## Secondary
1. Remove the p10 hull balls: no sky-bordered patch wider than 30 px with hp3 SD < 5.
2. Lift the dark foreground crowns: all 24 at σ3 ≥ 9 and median saturation ≥ 0.65.
3. Water: p6 step < 8 across 50 px, σ6 ≥ 12, B ≥ R.
4. Rocks hp3 SD ≥ 5 and grey. No pale slab in p10. Bark on t4 trunks (hp3 SD ≥ 5). p4 σ6 ≤ 5.

## Brand flag
A t5 billboard at 7.0 s reads "NOVA FOLD". It is an invented phone ad that belongs to the city piece. No logo appears in the terrain.

## Verdict
**FAILS TARGET.** Lowest score 3.
