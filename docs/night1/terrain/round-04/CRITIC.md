# Terrain (E) round 4: critic verdict

Homage fan game. Not official Marvel, Sony or Insomniac; no affiliation. All numbers are my own, measured on `round-04/stills` (4K), on 4 fps frames and on the refs `streets/centralpark-meadow-skyline` and `streets/centralpark-aerial-ballfields` (cp_0554). Round-3 scores are in brackets.

## Scores

- **Lawn / ground cover: 4 (4).**
  - p10 has blades and no star sprites (σ6 11.25, saturation 0.93), but it is lime: R/G 0.77, against 0.88 on the meadow ref.
  - From altitude the lawn is moss noise: p4 σ6 is 10.85, against 1.2–1.6 on the cp_0554 lawn. The diamonds drown in that noise.
  - A 490 px pale slab sits in p10 at (300–790, 1450).
- **Paths + water edges: 4 (4).**
  - The p3 bank rocks are unchanged: 22 white blobs (luma > 190, saturation < 0.15, ≥ 400 px). The largest is 15.6k px with SD 3.3.
  - There are no clay infields.
- **Shoreline: 4 (4).**
  - The p6 seam remains: luma 93→62 within 50 px at y = 2000.
  - The river σ6 is 2.09. p7 water saturation is 0.29 (khaki). The esplanades are empty.
- **Trees / canopy: 4 (4).**
  - 9/24 p1 crowns reach σ3 ≥ 9 (5/24 in r3). The median is 8.1, against 13–23 on cp_0554, and crown saturation is 0.52.
  - Saucer cards still float in p10 (≈2280, 490). No visible tree shadow falls on the lawn.
- **Overall: 3 (3).** The t5 tail now flies over the park, but the reference wins every pair. In the progress pairs I preferred the old build 4 times out of 5.

## Checks

- **(a) PASS, measured.** p4: σ6 10.85, saturation 0.874. p10: σ6 11.25, saturation 0.930. Guard boxes: σ6 11.57 / 9.97 / 8.99, saturation ≥ 0.916. The yellow-pixel share in p10 fell from 1.21 % to 0.26 %. The lime hue and the aerial noise remain.
- **(b) PASS on quads.** The blankets are woven, though they are rigid boards. Separate flag: the t4 camera passes through untextured trunks 320–460 px wide at 1.0 s and 4.5 s.
- **(c) PASS, marginal.** The hero is 21–41 m over the park from 10.5 s. Lawn σ3 is 5.4–8.4 from 11.0 to 15.0 s, but 2.6 at 10.5 s. The camera pitches up by 2–6°.
- **(d) PASS.** Fewer hulls; no regression.
- **(e) PASS.** [4, 4, 4, 4, 3] equals r3.
- **(f) INVALID.**
  - The raw `_perf.json` records no GPU utilization, lock mode or contamination flag.
  - The runs are capture runs, not taken under `gpu_slot perf`.
  - The r03 re-run reads 169 / 113 ms against the 161 / 92 baseline, so the noise is 5–23 %.
  - r04 reads 165–169 / 102–104 ms, so even if valid, p10 would be +10–14 %.
  - No credit given.

## A/B (decided before identity)

- **Views:** park-south B, reservoir A, pond B, great-lawn A, panorama B (the views don't match), lawn-eye A, shore-west B, shore-east B, piers A.
- **Motion:** sprint B, avenue A.
- **Progress:** park-south A, reservoir A, lawn-eye B, great-lawn B, panorama B. The two shore pairs are a tie: they are identical.
- **Identity, guessed afterwards:** the reference side won all 11. My preferred side was the newer build once out of 5.

## Biggest gap

Make the crowns lit leaf volumes that cast shadows. Test:

- All 24 p1 crown crops reach σ3 ≥ 9, with a median ≥ 12.
- Median crown saturation ≥ 0.65.
- No floating cards in p10.
- Each isolated p4 tree casts a lawn shadow at ≤ 0.6× the lit luma.

## Secondary

1. **Aerial lawn:** replace the noise with structure (stripes, shadows, clay infields). Test: p4 σ6 ≤ 5 while p10 stays ≥ 8, and p10 R/G 0.85–0.95. This contradicts E1's p4 threshold of ≥ 8; the reference measures 1.2–1.6.
2. **Water:** no p6 seam (luma step < 8 across 50 px), and river σ6 ≥ 15.
3. **Bank rocks:** textured grey, with luma SD ≥ 12 inside each rock.
4. **t4:** trunks need bark and collision, and the blankets should lie in the grass.

## Brand flag

A t5 storefront at 5.5 s reads "THE PA… / SEAFOOD". It is generic and belongs to the city piece. No logo appears in the terrain.

## Verdict

**FAILS TARGET.** The lowest score is 3.
