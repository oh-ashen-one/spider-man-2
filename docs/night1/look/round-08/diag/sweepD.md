# Round 08, sweep D (live pins on the baked round-07 table; every group pins every round-08 param)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Plan `sweepD_plan.json`. 07:00: e1 local exposure [0.0, .2, -1.5], e2 [.05, .2, -2.0]. 20:30: SkyLuminanceFactor x[.4, .95, 1.8] with the fog directional-inscattering lobe d1 .01 / exponent 12 / start 2 km, d2 .01 / 12 / 4 km, d3 .006 / 16 / 1 km, d4 no lobe.

Readings: e1 lifts S4e 07:00 to 60.0 and S4 by +8.6 (the most selective of all variants: S4e +32, S4 +8.6); e2 48.0. Blue hour: the factor alone (d4) gives S4 +4.4 and S4w +3.4; the 4 km lobe (d2) moves S4w to -17.4 (S4 +0.6) with the far band kept (50 Y) and an 8-row step of 18.6; at 1-2 km the far band toward the sun brightens to 79-88 Y (sky-far -1.8 / +0.4).

| still | mean | Y<10 | clip | skyY | sat | B-R | far | sky-far | step | c150 |
|---|---|---|---|---|---|---|---|---|---|---|
| S4@d1_h20.5 | 50.0 | 0.0 | 0.00 | 63.0 | 0.135 | +0.8 | 41.7 | +21.3 | 3.9 | 0.00 |
| S4@d2_h20.5 | 46.6 | 0.0 | 0.00 | 89.8 | 0.115 | +0.6 | 43.4 | +46.4 | 6.5 | 0.00 |
| S4@d3_h20.5 | 46.6 | 0.0 | 0.00 | 85.7 | 0.117 | +2.9 | 45.3 | +40.4 | 6.0 | 0.00 |
| S4@d4_h20.5 | 47.4 | 0.0 | 0.00 | 79.1 | 0.125 | +4.4 | 47.9 | +31.3 | 6.5 | 0.00 |
| S4@e1_h7 | 65.6 | 0.0 | 0.00 | 143.4 | 0.385 | -66.7 | 85.8 | +57.6 | 18.4 | 0.00 |
| S4@e2_h7 | 60.8 | 0.0 | 0.00 | 144.0 | 0.385 | -66.7 | 85.6 | +58.4 | 16.7 | 0.00 |
| S4e@e1_h7 | 60.0 | 0.0 | 0.01 | 129.0 | 0.498 | -81.6 | 92.8 | +36.2 | 19.3 | 0.05 |
| S4e@e2_h7 | 48.0 | 0.0 | 0.01 | 126.8 | 0.498 | -79.7 | 92.5 | +34.2 | 19.1 | 0.05 |
| S4w@d1_h20.5 | 43.8 | 0.0 | 0.00 | 86.4 | 0.192 | -16.2 | 88.2 | -1.8 | 9.4 | 0.00 |
| S4w@d2_h20.5 | 43.0 | 0.0 | 0.00 | 93.2 | 0.182 | -17.4 | 50.0 | +43.2 | 18.6 | 0.00 |
| S4w@d3_h20.5 | 44.7 | 0.0 | 0.00 | 79.7 | 0.149 | -7.6 | 79.3 | +0.4 | 6.8 | 0.00 |
| S4w@d4_h20.5 | 46.9 | 0.0 | 0.00 | 78.4 | 0.121 | +3.4 | 44.3 | +34.1 | 8.7 | 0.00 |
