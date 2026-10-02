# P4 sky / time-of-day critic, round 05 (pixels only)

> Homage fan game, not official Marvel/Sony/Insomniac. Work: `_scratch/critic-P4-r05-work/`. The lapse starts at 04:00 and runs at 2 h/s.

## Scores
1. **Sun/sky/ToD: 3.** L23b fails: the worst jump is 14.4 Y at t=7.55 s (19:06), p99 7.9. At 07:00 the frame whites out (mean 180, 10.4 % clipped). At 20:30 it becomes a lavender fog wash (mean 202). No hour shows a sun disk or a moon disk. The clear 13:00 sky gets darker toward the horizon (Y 143 → 87, a navy wall). Refs `perch-moon`, `skyline-empire-top`.
2. **GI & shadows: 5.** L21 passes on S1, S3 and S5–S8 at 18:24. S4 fails (p5 31.9, p95/p5 5.9). Y<10 reaches 11.6–13.4 % on S3, S5 and S7 (L1 ≤8).
3. **Atmosphere & depth: 4.** L10, S4 far band minus sky: golden −16.2 passes, with B−R +9. Dawn −9.6, noon −12.9, overcast +0.4, dusk +27.7 (inverted) and night −5.9 fail. The overcast tint is brown.
4. **Reflections & materials: 5.** At 13:00 the S8 glass reflects sky and towers. Night windows vary.
5. **Post & exposure: 3.** In the night swing the hero turns white: 21,218 clipped px at t=8.0 s. S7 golden clips 3.53 % (L5 ≤0.7). Overcast clips 0.03 % (L2 0.00).
6. **Night look: 4.** At 22:00 the S4 sky is flat (Y 32–38, high-pass std 1.27, against 3.98 on `perch-moon`). It shows 3–4 stars and no moon, and the far skyline is unlit cards. At 19:48 the sky is black (Y 22–29) while the tower tops are still sunlit.

## A/B (better, decided before identity)
day-skyline B · dusk A · golden-skyline B · night-skyline A · overcast A · golden-aerial A · avenue-street B · rooftop A · sunstreet B (A has a blown sun column) · night-district B (key art, not comparable) · night-street B · progress-golden A · progress-night A. Guess: ours lost all 11 pairs against the reference.

## Biggest gap
Make the sky lit and legible at every hour, with no exposure excursions. In `tod_lapse_S4`:
- every frame-to-frame jump is ≤3 Y and p99 ≤1.5;
- from 05:00 to 21:30 the frame mean is ≤130 and clipping ≤1.8 %;
- in the 06:30–07:30 and 19:00–21:30 stills, the sky band (rows 0–90) is brighter than the far city, with B−R ≤ −20 near the sun;
- at 22:00 a moon disk shows (≥12 px, Y ≥200), with moonlit cloud and sky high-pass std ≥3.

## Secondary
1. Clear noon: horizon ≥ zenith (L11).
2. L10 at every non-golden hour.
3. Zero clipped suit pixels at night.
4. Dawn at 07:36 copies golden at 18:24: S1 luma correlation is 0.85 dawn-golden against 0.37 dawn-noon, with the same B−R. Give dawn its own palette, with the sun on the opposite side.

No copied brands seen (AMBROCHE, KESTREL and THE PAPER MILL read as fictional).

## Verdict: FAILS TARGET (lowest 3)
