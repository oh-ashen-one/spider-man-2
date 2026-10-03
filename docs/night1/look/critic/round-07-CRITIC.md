# P4 sky/ToD critic, round 07 (pixels only)

> Homage fan game, not official Marvel/Sony/Insomniac. Work: `_scratch/critic-P4-r07-work/`.

## Scores
1. **Sun/sky/ToD: 4.** The dome steps are gone. Dusk is a sepia murk: S4w 19:48 sky saturation is 0.25 (`sunset-river-og` 0.52). S4 20:30 "blue hour" has B−R −34, so it reads brown. A 32–36 px disk (peak Y 199) sits below the horizon at S4w (1406,387) from 19:48 to 20:30.
2. **GI & shadows: 4.** L1 Y<10 fails on S1 9.5 %, S3 12.3, S5 8.7 and S7 15.2. L21 fails on S4 (p5 26.3, ratio 6.3) and S2. S4e 07:00 is 54.5 % Y<10.
3. **Atmosphere & depth: 4.** L10 sky−far: 13:00 +5.1, 18:24 +14.9. S4 21:00 is −11.7, so L24a fails. The far city at dawn is magenta soup.
4. **Reflections & materials: 4.** S7 glass reflects. The 18:24 river is matte. A hot glint remains after sunset.
5. **Post & exposure: 5.** Lapse p99 is 1.99 (≤1.5). S7 clips 1.80 % (L5 ≤0.7). The twilight tonemap is milky.
6. **Night look: 4.** L3 and L8 pass 8/8. L22a is 2.71 %. The moon halo is Y 166 at r=100. L25b is 2.32. Blacks are lifted: Y<10 is 0.00 %, p1 17.4.

## Checks
- **a)** L27a–e pass 12/12 (dome_check.py, code read). The worst step is S4 19:48 at 24.3, close to the limit. Clip ≤0.22 %.
- **b)** Lapse max jump 2.55 passes. p99 1.99 **fails**.
- **c)** L24a fails at 21:00. L25a passes (30.8 px, peak 255). L25b fails. L21 fails. L5 facing clip passes (0.00 / 0.01 %), but L5 mean fails: S4e 07:00 27.9, S4w 19:00 48.0.
- **d)** **Fails**: sun/sky 4 < 6 and night 4 < 5.
- **e)** **No.** The only disk is 14 px, at S4e 07:00.

## A/B (decided before identity)
- dusk-sun A
- dusk-early B
- dusk-skyline B
- blue-hour B
- dawn-skyline A
- dawn-sun B
- day B
- golden-skyline A
- sunstreet B (narrow)
- avenue B
- rooftop A
- moon B
- night-skyline A
- night-street A

Guess: ours lost all 14.

Progress pairs:
- s4w-195 A
- s4w-198 B
- s4w-20 B
- s4w-205 B
- s4-195 A
- s4-198 A
- s4-20 A
- s4-205 B
- s4-65 A
- s4-7 A
- s4e-65 A
- s4e-7 B
- golden B
- night A
- lapse A

The black-ceiling losers look like r06. r07 likely lost s4-7 and s4e-7 (dead sunrise).

## Biggest gap
Light the city under the twilight sky. On S4e 07:00 and 07:30 and on S4w 19:00:
- L5: frame mean 59–118, Y<10 ≤8.8 %, clip ≤0.7 %;
- sky rows 0–89 saturation ≥0.40.

Also, S4 at 20:30 sky B−R ≥0. Keep L27a–e passing, with lapse max ≤3 and p99 ≤1.5.

## Secondary
1. Remove the sub-horizon disk on S4w.
2. Bring the S4m halo to Y ≤60 at r=100 and L25b to ≥3.
3. Fix L10 at 13:00 and 18:24, and L24a at 21:00.
4. Show the sun disk at day and golden hours.

Brands: AMBROCHE reads as fictional. The pack golden-rooftop/B billboard reads "…OCKSTART…" and may contain ROCKSTAR. Verify it.

## Verdict: FAILS TARGET (lowest 4)
