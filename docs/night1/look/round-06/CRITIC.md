# P4 sky / time-of-day critic, round 06 (pixels only)

> Homage fan game, not official Marvel/Sony/Insomniac. Work: `_scratch/critic-P4-r06-work/`. Lapse = 04:00 + 2 h/s.

## Scores
1. **Sun/sky/ToD: 3.** No sun disk at any hour. At 19:30–20:30 a black ceiling with clipped lava streaks sits over a glowing fog band. On S4w 19:48, rows 140–180 read Y 25, then jump 113 Y at row 187; rows 0–150 clip 29.5 %. Sky B−R reaches −247 (S4w 19:00), against −84 for the most saturated ref (`sunset-river-og`). Midday clouds are faint streaks.
2. **GI & shadows: 5.** L21 passes on S1, S3 and S5–S8. S2 fails (p5 14, ratio 14.3) and so does S4 (p5 23.8, ratio 8.1). S7 has 11.7 % Y<10 (L1 ≤8).
3. **Atmosphere & depth: 4.** L10, S4 sky minus far: 13:00 +38 and 18:24 +45 are too deep. 20:00 is −24 (inverted; L24a fails). 22:00 passes (+15.5). The far skyline is flat cards.
4. **Reflections & materials: 5.** The S8 13:00 glass reflects. No change.
5. **Post & exposure: 4.** The lapse now passes the mean/clip limits (max 112, 1.51 %). L23b still fails: a 7.84 Y jump at t=7.85 s, p99 3.21. Facing stills clip 13.96 % (S4w 19:00) and 9.33 % (S4e 07:00), against L5 ≤0.7.
6. **Night look: 4.** The 22:00 moon disk is 20.5 px with peak 255, so L25a passes. Its halo is still Y 113 at r=200 px, against about 45 on `perch-moon`. L25b reads 2.17 (≥3). 20:30 (mean 22.8) is darker than 22:00 (41.1).

## A/B (decided before identity)
- dawn A
- day B
- dusk-skyline A
- dusk-sun-facing B
- golden-skyline B
- avenue A
- sunstreet B
- rooftop A
- night-moon B
- night-skyline A
- night-street B
- district A
- progress-dusk A: B has the black ceiling.
- progress-night A

My guess is that ours won only sunstreet.

## Biggest gap
Fix the inverted twilight dome. On S4 and S4w at 19:30, 19:48, 20:00 and 20:30, and on S4e at 06:30 and 07:00:
- sky rows 0–89 are ≥10 Y above the far band;
- no 8-row step over 25 Y occurs in rows 100–300;
- rows 0–150 clip ≤0.3 %;
- sky B−R stays between −20 and −90;
- the lapse's largest frame-to-frame jump is ≤3 Y.

## Secondary
1. On S4m, bring the moon halo to Y ≤60 at r=100 px, with moonlit cloud and high-pass ≥3.
2. Show a sun disk or bloom core at golden hour.
3. Remove the 20:30 dark pit.
4. Add real cloud structure at midday (L23c).

Brands: AMBROCHE and THE PAPER MILL read as fictional.

## Verdict: FAILS TARGET (lowest 3)
