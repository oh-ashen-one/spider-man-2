# Terrain (E) round 2: critic verdict

Homage fan game. Not official Marvel, Sony or Insomniac; no affiliation. Axes are SPEC E5, the same as round 1. All numbers are my own measurements, taken on `round-02/stills` and on 4 fps frames.

**Scores (round 1 in brackets)**
- **Lawn / ground cover: 4 (3).** The lawn is green now: pure-lawn G/R is 1.12 to 1.40. Saturation is 0.46 to 0.64, against 0.80 to 0.83 on `centralpark-meadow-skyline`. E1 fails: 6 of 7 boxes score 1.33 to 6.09 (σ6). Only p4 900,1400 passes, at 13.5, and that box contains trees. E2 is unchanged at 89.90 %. In p10 the eye-level cover is sparse yellow star sprites, not grass blades. In t4 at 9.5 s a pale quad lies on the lawn (about 580 × 150 px, luma 172 against 101 for the lawn).
- **Paths + water edges: 4 (4).** The p2 Reservoir is good: it has reflections and the fence. The p3 pond banks are still untextured white lumps (luma 167 against 83 for the lawn, saturation 0.15). The paths are flat ribbons.
- **Shoreline: 4 (3).** The seawall and railing now run across 100 % of the p7 width and about 80 % of p6, and the p8 sheds are textured. The river is flat black: p6 water has high-pass SD 0.37 at luma 35, against 25.6 and 4.3 on `waterfront-og` and `waterfront-dn`. The esplanade is empty paving with high-pass SD 5.5 to 5.8, against 15.5 on the reference.
- **Trees / canopy: 3 (2).** Near leaf-card trees are acceptable. The 165–520 m band is faceted, camouflage-blotched boulders. In p10 they float above the tree line, with straight silhouette facets about 130 px long. E8 fails: 14 of 24 crowns score under 9 (minimum 5.4, median 8.3).
- **Overall beautiful terrain: 3 (3).** In t5 at 13.25 to 14.0 s the park-edge ground is still flat grey: σ3 SD 1.63 to 1.73, saturation 0.36 to 0.39, no markings.

**A/B (decided before guessing identity)**
- The reference-quality side wins all 11 view pairs.
- south-high B, reservoir B (grass and light), pond-woods A, great-lawn B, panorama A, lawn-eye A, shore-west A, shore-east B, piers A, lawn-sprint A, avenue-park A.
- The losing sides show boulder crowns, white bank rocks, dead-flat water and empty paving.
- Progress pairs:
  - park-south: B is better. The hull faces are gone.
  - reservoir: B is better.
  - lawn-eye: A is better. B has green hull blobs and a brown lawn.

**Biggest gap.** Replace the 165–520 m crown band (`trees-*-crown`) with clustered leaf-card canopies shaded like the near band.

Test: all 24 `p1_south` crown boxes must have σ3 high-pass SD ≥ 9. No crown silhouette in `p10_lawn_eye` may have a straight edge longer than 40 px. Nothing may sit above the tree line with luma variance coming from a blotch texture rather than leaves.

**Secondary**
1. Lawn: E1 ≥ 8 on the pure-lawn boxes and saturation ≥ 0.70. Replace the star tufts with blade clumps. Remove the pale lawn quads (t4 at 8 to 12.5 s).
2. River water: high-pass σ6 ≥ 4 and luma ≥ 55 in p6/p8, with sky reflection and chop.
3. Pond banks: textured grey schist, with luma no more than 1.3 × the lawn.
4. t5 at 13 to 15 s: perimeter ground σ3 SD ≥ 5, with curbs and markings.

**Brand flag.** The hero is not in t4 or t5. The t5 street billboard reading "POP THE SUMM…" (about 6.5 s) is outside this piece; the city owner should check it.

**Verdict: FAILS TARGET.** The lowest score is 3.
