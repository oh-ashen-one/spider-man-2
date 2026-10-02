# Critic W r03: water, island-wide (blind)

Homage fan game. Not an official Marvel, Sony or Insomniac game.

Method: luma Rec.709; hp = Y − gauss(σ8); glint = Y≥200 and hp≥30. Near crop 4K x0–1800 y1200–2160. Dollies at 4 fps (40 frames each). docs/night1/water/SPEC.md does not exist, so the gates are the PLAN §4 lines from r02.

## A/B (decided before identity)
- **river-sun: A.** Glints reach 100 % of the columns at 9.4 %. B reaches 47 % at 1.8 %.
- **river-low: B.** Wakes and churn, hp sd 18.7, p99.5 151. A has hp 9.7, p99.5 112.
- **harbour-high: A.** Glint field, hp 33.3. B is a flat felt, hp 3.8 with 0 glints.
- **perch-s4: B.** A's river is a beige haze band, Y 132 (B is 73).
- **prev/this still: B.** The comet streaks are gone. But B has also lost the seawall foam.
- **prev/this harbour: B.** The blob decals are gone. Both are flat (hp 3.8 vs 4.1).
- **prev/this dolly: B.** No streaks, and dT is 7.9 vs 6.2.
- **sun-dolly: A.** Glints 0.23 % vs 0.19 %; B shows streak arcs.

The reference wins all four ref-vs-ours pairs.

## Scores
1. **Motion & detail: 4.** Near hp is 10.1 (ref 18.7). The harbour 4K crop is 4.3 (ref 33), so it reads as a uniform leather pattern. No rings: ac80 is 0.013.
2. **Colour & depth: 5.** Near mean Y 76, p1 36, p99.5 117 (ref 22–151). The S4 river sits at Y 132: a haze band, not water.
3. **Reflections & glints: 5.** The sun path is real now: 4K glints 1.61 %, and Y≥200 covers 41 % of the columns (ref 100 %). The glints are soft blobs. river-low and harbour have 0 % glints.
4. **Shore & pier foam: 2. REGRESSION.** The seawall crop shows no foam or contact band at all, even though it is named `_seawall_foam`. The far-pier pile foam and the harbour shore foam are also gone.
5. **Horizon & believability: 4.** The sun view is believable. From swing height the harbour and S4 still read as brown haze.

## Plan §4 Water
| Line | Result |
|---|---|
| hp sd ≥ 12 | FAIL (10.1) |
| p99.5 ≥ 150 | FAIL (117) |
| glints ≥ 1 % | FAIL near (0 %); PASS river-sun (1.61 %) |
| mean Y ≤ 80 | PASS (76.4) |
| C14 | not re-measured |
| autocorrelation ≤ 0.10 | PASS (0.013) |
| piling foam | FAIL (absent) |
| ≤ 2.5 ms | FAIL river-low: water passes 2.66 ms; S4 1.38 and sun 2.19 pass; frame delta −0.25 |

## Biggest gap
The distant, high-view water has no sparkle or structure. Add a sun-glint field that survives distance: a far-field normal layer, or a roughness that drops with distance and keeps a GGX lobe at ≤ 0.08 beyond 300 m.

Pass when:
- harbour_high_4k crop (x0–2400, y1300–2160): hp sd ≥ 10, glints ≥ 0.5 %, Y≥200 in ≥ 50 % of the columns.
- S4 river band: mean Y ≤ 100.

## Secondary
1. Restore animated contact foam on the seawall, the pilings and the harbour shore. Target: a band ≥ 12 px wide at Y ≥ 180 in the seawall crop, changing over frames, with no popping blob.
2. river-sun: the glints must be sharp (≤ 6 px) and cover ≥ 50 % of the columns.
3. river-low: p99.5 ≥ 150 and p1 ≤ 25.
4. Brand flag: the "AMBROCHE" billboard face is still visible in S4. It needs an IP check.

## Verdict
**FAILS TARGET.** Lowest axis 2; mean 4.0, flat against r02 (4.0).
