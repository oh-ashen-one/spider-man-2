# P4 LOOK critic, round 03 (pixels only)

> Homage fan game, not official Marvel/Sony/Insomniac. Instruments: lum.py (lum_by_tod method + L13/L14 blobs), Laplacian edge/centre ratio, row profiles. Scratch: `_scratch/critic-P4-r03-work/`.

## Scores (Spider-Man 2 standard)
1. **Sun/sky/time of day: 6.** Midday now meets L2/L7 on 8/8 stills (mean 84.9–94.3, Y<10 0.00, B−R −12.0…+3.0). Two lines fail: clipping in S3 (0.03%) and S7 (0.04%) against a 0.00 limit (L2), and the swing clip peaks at 0.45% at t=10.50 s. Golden fails L1 on S4 (109.7), L5 on S7 (3.02% clipped against ≤0.7) and L6 on S3 (B−R −19.6).
2. **GI & shadows: 4.** Golden shadows are lifted and flat. p5 Y is 17.6–39.6 against the refs' 8–11 (golden-canyon/A, golden-skyline/A, golden-sunstreet/B). p95/p5 is 4.6–11.3 against 18–26. S1, S5 and S6 show no sun/shade split at street level. The "overcast" swing has crisp cast shadows on facades (t≈5–6 s).
3. **Atmosphere & depth: 4.** L10 fails. In golden S4 the far band sits 35–44 Y below the sky, and its B−R is −40 against −76 for the sky. In midday S4 the far band sits 43–49 below the sky. The overcast far field is a purple-grey mush with the river lost (overcast-skyline). The canyon god-ray haze in golden S7 is good.
4. **Reflections & materials: 4.** Windows are flat fills that reflect nothing: swing t=8.25 s glass reads Y 24.2, std 0.7. L17 passes only because the flat colour is ≥20. The gold glass tower in midday S2 still glows gold under an overcast sky. The night wet asphalt is good.
5. **Post & exposure: 5.** L18 fails: swing edge/centre p50 is 0.69 (limit 0.20–0.65), and from t=8.0 to 9.5 s it is ≥1.0, so the frame edges get no blur at all. Clipping failures are listed under axis 1.
6. **Night look: 5.** L3, L8 and L13 pass on 8/8. L14 passes on the street views (S1 p90 167 / p10 26). The skyline is day-for-night: city median Y is 58 (ref 37), bright window points cover 0.96% of the frame (ref 4.38%) and p99 is 160 (ref 241). The Times Square screens are procedural gradient blobs with fake text bars, and the trees glow neon green.

## A/B (decided before identity)
- golden-canyon: **A** (raking sun, deep cast shadows). golden-skyline: **A** (B is a sepia wash with card-like far blocks). golden-sunstreet: **B** (ground shadow pattern; A clips 3.54%).
- night-district: **A**. night-skyline: **B** (window-point city, lit bridges). night-street: **B** (sodium warmth; A is close). night-street-2: **B**.
- overcast-skyline: **B**. overcast-street: **B**. overcast-swing: **A** (blur, cloud sky; B is flat, with hard shadows).
- progress-golden: **A** (B−R −39.6 is in spec; B is −61.6). progress-midday: **A** (no self-lit white shore, neutral). progress-night: **A** (no neon trees).
- Identity guess: ours is B, B, A, B, A, A, A, A, A, B.

## Single biggest gap
Rebuild golden-hour key/fill contrast. Keep direct sun and let the shadow sides fall to ref depth with only a cool sky fill. Pass means that on golden S1–S8 at 1080p, p5 Y is ≤12, p95/p5 is ≥16, and mean HSV saturation is ≥0.44. L1 must still hold (Y<10 ≤8%, clipped ≤1.8%, mean 61–100, so S4 comes down from 109.7), and S1, S5 and S6 must each show a sunlit/shaded facade pair with a luma ratio ≥3.

## Secondary
1. Night skyline S4 needs bright window points on ≥3% of the frame and city median Y ≤42. Remove the diffuse facade ambient.
2. L10: far band 15–32 Y below the sky, with B−R within ±10 of the sky, on golden S4 and midday S4.
3. Overcast: no crisp sun shadows in the midday swing, and 0.00% clipping on S3 and S7.
4. L18: edge/centre p50 ≤0.65 in swing clips. Glass needs a sky/city reflection (glass std ≥8).

No copied brands seen (the sneaker, AMBROCHE and VESPERA are invented).

## Verdict: FAILS TARGET (no axis ≥8; lowest 4)
