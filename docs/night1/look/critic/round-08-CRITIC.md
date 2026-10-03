# P4 sky/ToD critic, round 08 (pixels only)

> Homage fan game, not official Marvel/Sony/Insomniac. Work: `_scratch/critic-P4-r08-work/`.

## Scores
1. **Sun/sky/ToD: 5.** The sub-horizon disk is gone. The 20:30 sky is grey (sat 0.139). Dawn and dusk are one brown wash (swing_tod_19, lapse 07:00/19:00).
2. **GI & shadows: 4.** Twilight city local contrast is 0.09–0.11, against 0.17–0.37 for the refs (`sunset-river-og`, `skyline-perch-nm`) and 0.14–0.22 for r07. There is no sun/shade split.
3. **Atmosphere & depth: 4.** L10 at 13:00 is +3.5. L24a at 21:00 is −13.4. The S4e 07:30 far city is a grey slab.
4. **Reflections & materials: 4.** Unchanged. Twilight surfaces are matte sepia.
5. **Post & exposure: 4.** Lapse p99 is 2.19. swing_tod_22 clips 2.45 % at t=10.75 s. Midday S7 is 75.4 (r03: 89.0).
6. **Night look: 4.** L25b is 2.53. The halo is Y 147 at r=100. Y<10 is 0.00 % on every 22:00 still.

## Checks
- **a)** Passes on numbers, fails on look. The three stills read as flat lifted haze with crushed contrast; city rows have p5 42 and p95 82–89.

  | still | mean | Y<10 | clip | sky sat |
  |---|---|---|---|---|
  | S4e 07:00 | 65.7 | 0.00 % | 0.01 % | 0.49 |
  | S4e 07:30 | 71.7 | 0.00 % | 0.00 % | 0.44 |
  | S4w 19:00 | 70.8 | 0.00 % | 0.00 % | 0.55 |
- **b)** Passes at +6.6, but the sky reads grey.
- **c)** Passes: 0 blobs on S4w 19:30–20:30.
- **d)** **10/12.** S4e 06:30 L27b step is 25.1. S4w 20:30 L27d is −13.2.
- **e)** Max 2.80 passes (raw json: 3.07). p99 2.19 **fails**.
- **f)**
  - L2 7/8, fails on S7.
  - L7, L3 and L8 pass 8/8.
  - L13 6/8 on my counter (S3, S6).
  - L25a passes at 22.5 px.
  - Golden L1 **5/8**, fails on S3, S5 and S7.
  - L22a passes at 2.84 %.
- **g)** **Fails**: sun/sky 5 < 6, night 4 < 5, post 4 < 5.
- **h)** **No.** The only disk is 13.5 px, at S4e 07:00.

## A/B (decided before identity)
Reference pairs:

| pair | pick | pair | pick | pair | pick |
|---|---|---|---|---|---|
| dawn-sun | B | dawn-late | A | dusk-low | B |
| dusk-early | B | dusk-sun | B | dusk-skyline | A |
| blue-hour | B | dawn-skyline | A | golden-skyline | A |
| sunstreet | B | avenue | B | rooftop | B |
| moon | B | night-skyline | B | night-street | B |
| day | B | overcast | A | | |

The winning side always looks like the reference, so I count all 17 as losses for ours.

Progress pairs:

| pair | pick | pair | pick | pair | pick |
|---|---|---|---|---|---|
| s4e-7 | B | s4e-75 | A | s4e-65 | A |
| s4w-19 | A | s4w-195 | B | s4w-198 | B |
| s4w-20 | B | s4w-205 | A | s4-7 | A |
| s4-19 | A | s4-195 | A | s4-205 | A |
| lapse | A | r03 golden-s4 | A | r03 golden-s7 | A |
| r03 golden-s1 | A | r03 night-s4 | B | r03 night-s1 | B |
| r03 midday-s4 | B | r03 midday-s2 | A | r03 midday-s7 | B |

## Biggest gap
Light the twilight city with a low directional sun instead of a uniform lift. Test S4e 07:00, S4e 07:30 and S4w 19:00 on rows 270–1079, keeping L5. Targets:
- p5 Y ≤ 15 and p95 ≥ 120;
- 32-px local contrast ≥ 0.17;
- one sunlit/shaded facade pair with a ratio ≥ 3.

## Secondary
1. Bring L27 back to 12/12 and the lapse p99 to ≤ 1.5.
2. Restore golden L1 to ≥ 7/8 and the midday S7 mean to 83–97.
3. Show a sun disk ≥ 12 px at S4w 19:00 and S7 18:24. The 20:30 sky must read blue.
4. Get L25b to ≥ 3. **Brand:** the S3 rooftop wall reads "ROCK…" (pack: "…OCKSTAR…"). Remove it.

## Verdict: FAILS TARGET (lowest 4)
