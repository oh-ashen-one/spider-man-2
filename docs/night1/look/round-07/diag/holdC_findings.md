# Round 07 hold C (table v1: free twilight meter, dense bias curve, 2 loop iterations, build, 22 stills, stitched lapse; 2026-10-02 12:11-12:36)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

- Stitched lapse (`holdC_lapse_S4.json`): max jump 5.45, p99 2.97, 54 frames > 1.5, 8 > 3, mean <= 119, clipped <= 2.71 % (r06 C: 8.10 / 3.21). Remaining jumps: 19:19-19:27 zigzag (the free meter hunting while the sunset clouds clip), 08:30-08:45 (-3.4 per frame, outside the loop window), 18:24 (x4 / x16 segment boundary), 20:47 (min EV clamp re-engaging).
- Dome stills (`holdC_DOME.md`): L27b (8-row step) passes on all 14; L27e passes (20:30 57.8 vs 22:00 38.4); L27a passes on S4 19:30 / 19:48 / 20:30, S4e 07:00, S4w 20:30; fails S4 20:00 (-1.2), S4w 19:30 / 19:48 / 20:00 (the glow toward the sun on the far city), S4e 06:30. L27c fails on 13 of 14 (twilight frames brighter: means 56-58 and pink clouds clipping). L27d passes on S4w 19:48 / 20:00 / 20:30 and S4e 06:30.
- Golden 18:24: S4 103.4, S3 52.6 (L1 6 of 8). Night 22:00: S4 38.4, S4m moon-lit cloud halo (Y >= 200 blob 192 px).
v2 (hold D): twilight biases -0.6 EV, min EV clamp held longer through 19:24-19:48 / 06:24-06:54, sun cloud luminance x0.15 at twilight, moon cloud luminance 3 -> 1.5, golden bias .95 + fog x0.6, cooler dawn factor, loop on wide windows (05:30-09:12, 17:36-21:24) and every key in them, x16 lapse segments widened to the same windows.
