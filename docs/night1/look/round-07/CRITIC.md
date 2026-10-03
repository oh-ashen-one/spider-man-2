# P4 sky / time-of-day critic, round 07 (pixels only)

> Homage fan game, not official Marvel/Sony/Insomniac. Work: `_scratch/critic-P4-r07-work/`. Lapse = 04:00 + 2 h/s.

## Scores
1. **Sun/sky/ToD: 4.** The dome steps are gone. Dusk is a sepia-grey murk: S4w 19:48 sky saturation is 0.25 (ref `sunset-river-og` 0.52). At "blue hour" (S4 20:30) B−R is −34, so it reads brown. A 32–36 px disk (peak Y 168–208) sits below the horizon at S4w (1406,387) at 19:48–20:30. No day still shows the sun.
2. **GI & shadows: 4.** L1 Y<10 fails on S1 9.5 %, S3 12.3, S5 8.7 and S7 15.2. L21 fails on S4 (p5 26.3, ratio 6.3) and S2 (12.8, 15.5). S4e 07:00 is 54.5 % Y<10, rows 400+ mean 6.5.
3. **Atmosphere & depth: 4.** L10 sky−far: 13:00 +5.1, 18:24 +14.9. At S4 21:00 it is −11.7, so L24a fails. The far city at dawn is magenta soup with blob LODs.
4. **Reflections & materials: 4.** S7 glass reflects. The 18:24 river is matte. The after-sunset hot glint/disk is wrong.
5. **Post & exposure: 5.** Lapse p99 is 1.99; L23b wants ≤1.5. S7 clips 1.80 %, against L5 ≤0.7. The twilight tonemap is milky.
6. **Night look: 4.** L3 and L8 pass 8/8. L22a is 2.71 % (target ≥3). The moon halo is Y 166 at r=100 (r06 asked ≤60). L25b is 2.32 (≥3). Night Y<10 is 0.00 % and p1 17.4 (S4), so the blacks are lifted.

## Checks
- **a) L27:** passes 12/12 on dome_check.py. I re-read the tool. Rows 0–150 clip ≤0.22 %. The worst 8-row step is S4 19:48 at 24.3, a near-fail, and its worst column band is 75. Facing B−R is −32…−78. L27e: 46.6 ≥ 42.3. Outside the L27 hours, S4w 19:00 B−R is −96.
- **b) L23b:** the max jump is 2.55 at 20:14, which passes. p99 is 1.99, which **fails**. 05:00–21:30 max mean is 97.8 and clip 0.56 %.
- **c)** L24a fails at 21:00. L25a passes (30.8 px, peak 255). L25b fails. L21 fails on S2 and S4. L5 facing clip: S4w 19:00 0.00 and S4e 07:00 0.01 pass. L5 mean fails: S4e 07:00 27.9, S4w 19:00 48.0 (59–118).
- **d) Fails.** Sun/sky 4 < 6 and night 4 < 5.
- **e) No.** The only disk is 14 px at S4e 07:00. S7 18:24 is a clipped column.

## A/B (decided before identity)
dusk-sun-facing A · dusk-early B · dusk-skyline B · blue-hour B · dawn-skyline A · dawn-sun-facing B · day B · golden-skyline A · sunstreet B (narrow) · avenue B · rooftop A · night-moon B · night-skyline A · night-street A. Guess: ours lost all 14.

Progress: s4w-195 A · s4w-198 B · s4w-20 B · s4w-205 B · s4-195 A · s4-198 A · s4-20 A · s4-205 B · s4-65 A · s4-7 A · s4e-65 A · s4e-7 B · golden B · night A · lapse A. Every loser that has the black ceiling is probably r06. Probably r07 lost s4-7 and s4e-7, where its sunrise is dead.

## Biggest gap
Light the city under the twilight sky, and keep L27a–e and lapse max ≤3 passing. Targets on S4e 07:00 and 07:30 and S4w 19:00:
- L5: frame mean 59–118, Y<10 ≤8.8 %, clip ≤0.7 %;
- sky rows 0–89 saturation ≥0.40;
- S4 20:30 sky B−R ≥ 0, which is real blue;
- lapse p99 ≤1.5.

## Secondary
1. Remove the disk below the horizon on S4w 19:48–20:30, or prove it is the moon.
2. On S4m, bring the halo to Y ≤60 at r=100 and L25b to ≥3. Night p1 ≤8.
3. Fix L10 at 13:00 and 18:24 (15–32) and L24a at 21:00.
4. Show the sun disk at day and golden hours.

Brands: AMBROCHE reads as fictional. Pack golden-rooftop/B carries a billboard that reads "…OCKSTART…", which may contain "ROCKSTAR". Verify it.

## Verdict: FAILS TARGET (lowest 4)
