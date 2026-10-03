# Terrain (E) round 6: critic verdict

Homage fan game, not official Marvel, Sony or Insomniac. All numbers are mine, from the r05/r06 4K stills and t4/t5 frames at 4 fps. r05 scores in brackets.

## Scores
- **Lawn 4 (4):** p10 σ6 20.35, R/G 0.884, pass. p4 σ6 6.52 > 5 (SPEC E1), worse than r05's 5.71. The p10 slabs remain.
- **Paths + water edges 4 (4):** egg boulders on the pond banks. Infields faint.
- **Shoreline 4 (4):** p6 water khaki (85,77,43), σ6 2.32. Seam step 30.8 per 25 px at (3083,2000). Esplanade trees cast no shadows.
- **Trees 5 (5):** 23/24 crowns at σ3 ≥ 9, median 13.25. Saturation 0.646. Lime clones in rows.
- **Overall 3 (3):** dark ground under the canopy, but no long low-sun shadows.

## Checks
- **a) FAIL (numbers pass).** Darkest boxes vs lit lawn 108.3: 0.52, 0.47, 0.46. None is that tree's crown-shaped shadow:
  - (3055,1133): shade under the big tree cluster.
  - (3071,1027): path near a lamp.
  - (2929,1050): dark pocket at the crown base.

  Toward 135° (where the cluster's own shade falls): 0.79, 0.66, 0.77. Lit lawn fell 127.7 → 108.3, which eases the ratio. Reads as canopy darkening.
- **b) FAIL.** Trees (830,1312) 0.70 and (1170,1495) 0.62. No shadow visible on the deck.
- **c) FAIL (marginal).** The r05 hull ball is gone. A 31 px smooth dark patch remains at (175,532), SD 3.76.
- **d) PASS.** Crowns 23/24, median 13.25 (lowest: (1500,1950) 7.37). E9c crown 29.5 px; the 61.7 px segment is a lamp lantern. p10 σ6 and R/G pass.
- **e) FAIL.**
  - t4: no blanket quads, but an untextured trunk ≥ 170 px (SD < 1.5) at 1.25–4.5 s, and smooth steps at 0 s.
  - t5: ground σ3 1.98–3.64 at 12.0–12.75 s and 14.0–15.0 s. The ending is buried in canopy blur.
- **f) PASS:** [4,4,4,5,3].
- **g) PASS.** Luma matching confirms the new build was preferred in park-south, great-lawn and lawn-eye.

## A/B (decided before identity)
- **Views:** reference won 8/9: south A, reservoir B, pond B, great-lawn A, lawn-eye A, shore-west A, shore-east A, piers A. Panorama A (ours, marginal).
- **Motion:** sprint A, avenue A.
- **Progress:** park-south A, reservoir A, lawn-eye B, great-lawn A, panorama B.

## Biggest gap
Trees must cast offset sun shadows. Test:
- p4: trees (3005,1100), (3040,1078) and (2900,1060) each have a lawn box ≤ 0.6× lit lawn, 40–120 px along the anti-sun direction.
- The dark centroid (≤ 0.7× lit lawn, within 120 px) is ≥ 30 px from the crown centroid and outside any other object's shade.
- Lit lawn ≥ 120.
- p6: every esplanade tree ≤ 0.6× paving.

## Secondary
1. p6 water σ6 ≥ 12, B ≥ R, step ≤ 8.
2. p4 σ6 ≤ 5.
3. Crown saturation ≥ 0.65, no yellow hot spots.
4. Barked trunks. t5 ground σ3 ≥ 5. Grey rocks.

## Brand
None seen.

## Verdict
**FAILS TARGET.** Lowest score 3.
