# Terrain (E) round 6: critic verdict

Homage fan game, not official Marvel, Sony or Insomniac. Every number below is my own measurement on the r05 and r06 4K stills, and on the t4/t5 frames extracted at 4 fps. Round-5 scores are in brackets.

## Scores
- **Lawn 4 (4):** p10 σ6 is 20.35 (guard 17.84) and R/G is 0.884, both passing. p4 σ6 is 6.52, which fails the SPEC E1 aerial limit of 5 and is worse than r05 (5.71). The pale slabs on the p10 lawn are still there.
- **Paths + water edges 4 (4):** the pond banks are still beige egg boulders. Infields are faint.
- **Shoreline 4 (4):** p6 water is unchanged: khaki (85,77,43), σ6 2.32. The seam is still a 30.8 luma step within 25 px at (3083,2000). Esplanade trees cast no shadows.
- **Trees 5 (5):** 23/24 crowns at σ3 ≥ 9, median 13.25. Median crown saturation is 0.646. The canopy is lime and yellow, with clone trees in orchard rows.
- **Overall 3 (3):** the high views gain dark ground under the canopy. Nothing casts the long low-sun shadows the reference shows.

## Checks
- **a) FAIL on the read (numbers pass).** Lit lawn is 108.3. The darkest boxes are 56, 51 and 50 (0.52×, 0.47×, 0.46×), but no box sits in a shadow shaped like that tree's crown:
  - Box (3055,1133) is shade under the big cluster.
  - Box (3071,1027) is the path near a lamp.
  - Box (2929,1050) is a dark pocket at the crown base.
  - Toward 135°, where the cluster's own shade falls, the minima are 0.79, 0.66 and 0.77.
  - Lit lawn also fell 15% (127.7 → 108.3), which makes the ratio easier to pass.

  This reads as canopy darkening, not cast shadow.
- **b) FAIL.** Tree (830,1312) scores 0.70. Tree (1170,1495) scores 0.62, and that box includes trunk pixels. No shadow is visible on the deck.
- **c) FAIL (marginal).** The r05 hull ball at (1142,237), 49–59 px wide, is gone. A smooth dark patch 31 px wide remains at (175,532), SD 3.76.
- **d) PASS.**
  - Crowns: 23/24, median 13.25. The only one below 9 is (1500,1950) at 7.37.
  - E9c: the longest straight crown edge is 29.5 px. The 61.7 px and 33.4 px segments are a lamp lantern and a lamp globe.
  - p10: σ6 and R/G pass.
- **e) FAIL.**
  - t4: there is no blanket quad. But an untextured trunk at least 170 px wide (hp3 SD < 1.5) appears at 1.25–4.5 s, and the stone steps at 0 s are smooth.
  - t5: ground σ3 drops to 1.98–3.64 at 12.0–12.75 s and 14.0–15.0 s, below 5. The last 3 s are buried in canopy blur.
- **f) PASS:** [4,4,4,5,3].
- **g) PASS.** Matching mean luma to the r05/r06 stills confirms I preferred the new build in park-south, great-lawn and lawn-eye.

## A/B (decided before identity)
- **Views:** south A, reservoir B, pond B, great-lawn A, panorama A (marginal), lawn-eye A, shore-west A, shore-east A, piers A. The reference won 8 of 9.
- **Motion:** sprint A, avenue A.
- **Progress:** park-south A, reservoir A, lawn-eye B, great-lawn A, panorama B.

## Biggest gap
Trees must cast real offset sun shadows. Test it in p4:
- Trees (3005,1100), (3040,1078) and (2900,1060) each need a lawn box ≤ 0.6× lit lawn, 40–120 px from the trunk along the anti-sun direction.
- The centroid of lawn pixels ≤ 0.7× lit within 120 px must sit ≥ 30 px from the crown centroid, without touching any other object's shade.
- Lit lawn must stay ≥ 120.
- In p6, every esplanade tree shadow must be ≤ 0.6× the paving luma.

## Secondary
1. p6 water: σ6 ≥ 12, B ≥ R, and no 25 px step above 8.
2. p4 σ6 ≤ 5.
3. Crown saturation ≥ 0.65, with no yellow hot spots.
4. Textured trunks in t4. In t5, ground σ3 ≥ 5 for the last 5 s. Grey rocks in place of egg boulders.

## Brand
I saw no copied brand or logo in the terrain frames I checked.

## Verdict
**FAILS TARGET.** Lowest score 3.
