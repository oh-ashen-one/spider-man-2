# Critic W r02: water, island-wide (blind)

Homage fan game. Not an official Marvel, Sony or Insomniac game.

Method: 4K stills, both dollies at 4 fps (40 frames each), luma Rec.709. "Near crop" means x0–1500, y1150–1800 at 3226 px wide (×1.19 at 4K). Refs: `river-pier-golden`, `waterfront-perch-trailer`, `waterfront-og`, `skyline-perch-nm`.

## A/B (decided before guessing identity)
- **river-sun: A.** Discrete white sparkles cover 61 % of the frame width. B has a soft gold smear over 30 %.
- **river-low: A.** A has churn, wake and contact foam. B is flat, with pale comet streaks.
- **harbour-high: B.** B glitters (hp sd 31, 14 % glints). A has hp sd 4.1, 0 % glints and 106 pale blob decals.
- **perch-s4: B.** A's river is a flat haze band (hp sd 2.7).
- **prev-vs-this still: A.** A has seawall foam, mean Y 79 vs 91, hp sd 7.5 vs 3.9.
- **prev-vs-this dolly: B.** A shows rings at f25 (autocorr80 0.294). B peaks at 0.047.
- **sun-dolly: B.** B has a sun path and moves (dT 23.4 vs 2.8).

**Identity:** the first four pairs are reference vs ours, and the reference wins every one. The current build beats the previous build in all three prev/this pairs.

## Scores (0–10)
| Axis | Score | Evidence |
|---|---|---|
| 1. Motion & detail | 4 | Rings are gone (≤0.05 on all 40 frames). Near hp sd is 7.5 (ref 16.9, spec ≥12). Comet streaks up to 417×73 px are +37 Y over the water around them. |
| 2. Colour, depth & absorption | 5 | Near mean Y 79.3 (≤80 passes), rgb (86,79,61). S4 river sits about 24 Y below the far shore (C14 passes). Range is p1 46 to p99.5 122 (ref 8–162): no dark troughs. |
| 3. Reflections & glints | 4 | river-low: 0 % glints, p99.5 122 (spec ≥1 %, ≥150). Harbour: 0 % vs ref 14 %. The sun path is a smeared sheen 30 % wide (ref 61 %). SSR of trees works. |
| 4. Shore & pier foam | 4 | The seawall foam is new (median 21 px, peak Y 227). Far-pier foam is flat white wedges between pilings. There is no contact foam at the harbour seawalls at swing height. |
| 5. Horizon & believability | 3 | From swing height (harbour, S4) the water reads as brown haze with blob decals. |

## Plan lines
- Near-water lines: hp sd FAIL, p99.5 FAIL, glints FAIL, mean Y PASS.
- C14: PASS.
- Autocorrelation ≤0.10: PASS.
- Piling foam: PASS, street level only.
- Cost ≤2.5 ms: FAIL. The SingleLayerWater passes cost 3.68 + 0.25 + 0.66 = 4.55 ms on RiverLow. The frame delta is only 1.23 ms.

## Biggest gap
The fine glint normals do not exist away from the sun. Add a high-frequency normal layer (wavelength 0.15–0.5 m, scrolling in two directions) and a sharp GGX sun lobe (roughness ≤0.08). Remove the comet streak and harbour blob decals.

**Pass when:**
- river-low near crop: hp sd ≥12, p99.5 ≥150, glints ≥1 %, mean Y ≤80.
- harbour_high 4K crop (x0–2400, y1300–2100): hp sd ≥10 and glints ≥2 %.
- river_sun: Y≥200 in ≥2 % of rows across ≥50 % of the frame width.

## Secondary
1. Add shoreline contact foam and a darker band where the water meets the harbour and S4 seawalls. Break up the far-pier wedges with noise and animation.
2. Get water passes ≤2.5 ms. SingleLayerWater alone is 3.68 ms.
3. Restore deep trough values (p1 ≤25).
4. **Brand flag (not water):** the "AMBROCHE" billboard with a woman's face in S4 needs an IP check before shipping.

## Verdict
**FAILS TARGET.** Lowest axis 3. Mean 4.0, up from 3.8.
