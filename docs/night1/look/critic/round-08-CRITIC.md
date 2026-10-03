# P4 sky/ToD critic, round 08 (pixels only)

> Homage fan game, not official Marvel/Sony/Insomniac. Work: `_scratch/critic-P4-r08-work/`.

## Scores
1. **Sun/sky/ToD: 5.** The disk below the horizon is gone. At 20:30 the sky is grey (sat 0.14). Dawn/dusk are one brown wash.
2. **GI & shadows: 4.** Twilight local contrast is 0.09–0.11; the refs read 0.17–0.37 (`sunset-river-og`, `skyline-perch-nm`). No sun/shade split.
3. **Atmosphere & depth: 4.** L10 at 13:00 is +3.5 and L24a at 21:00 is −13.4.
4. **Reflections & materials: 4.** No change from r07.
5. **Post & exposure: 4.** Lapse p99 is 2.19. swing_tod_22 clips 2.45 % at 10.75 s. Midday S7 mean is 75.4.
6. **Night look: 4.** L25b is 2.53 and the moon halo is Y 147 at r=100. Y<10 is 0 % on every 22:00 still.

## Checks
- **a)** Passes on numbers, fails on look. All three stills show a flat, lifted haze with crushed contrast (city p5 42, p95 ≤ 89).

  | still | mean | Y<10 | clip | sky sat |
  |---|---|---|---|---|
  | S4e 07:00 | 65.7 | 0 % | 0.01 % | 0.49 |
  | S4e 07:30 | 71.7 | 0 % | 0 % | 0.44 |
  | S4w 19:00 | 70.8 | 0 % | 0 % | 0.55 |

- **b)** Passes (+6.6), but the sky still reads grey.
- **c)** Passes: no disk pixels.
- **d)** **10/12.** S4e 06:30 has a 25.1 step (L27b) and S4w 20:30 is −13.2 (L27d).
- **e)** Max 2.80 passes; p99 2.19 **fails**.
- **f)** Fails:
  - L2: 7/8 (S7).
  - L7, L3, L8: 8/8.
  - L13: 6/8.
  - L25a: passes.
  - Golden L1: **5/8**.
  - L22a: 2.84 %, passes.
- **g)** **Fails.** Sun/sky 5 < 6 and night 4 < 5.
- **h)** **No.** The only disk is at S4e 07:00 and is 13.5 px.

## A/B (decided first)
Refs: dawn-sun B, dawn-late A, dusk-low B, dusk-early B, dusk-sun B, dusk-skyline A, blue-hour B, dawn-skyline A, golden-skyline A, sunstreet B, avenue B, rooftop B, moon B, night-skyline B, night-street B, day B, overcast A. Ours lost all 17.

Progress: s4e-7 B, s4e-75 A, s4e-65 A, s4w-19 A, s4w-195 B, s4w-198 B, s4w-20 B, s4w-205 A, s4-7 A, s4-19 A, s4-195 A, s4-205 A, lapse A, golden s4/s7/s1 A, night s4/s1 B, midday s4 B, s2 A, s7 B.

## Biggest gap
Light the twilight city with a low directional sun, not a uniform lift. Test S4e 07:00, S4e 07:30 and S4w 19:00, rows 270–1079, with L5 still passing. Targets:
- p5 Y ≤ 15 and p95 ≥ 120.
- 32-px local contrast ≥ 0.17.
- One facade pair, sunlit vs shaded, at a ratio of 3 or more.

## Secondary
1. Bring L27 back to 12/12 and get lapse p99 ≤ 1.5.
2. Restore golden L1 to ≥ 7/8 and the midday S7 mean to 83–97.
3. Show a sun disk of 12 px or more at S4w 19:00. The 20:30 sky must read blue.
4. **Brand:** the rooftop wall on S3 reads "ROCK…" (pack: "…OCKSTAR…"). Remove it.

## Verdict: FAILS TARGET (lowest 4)
