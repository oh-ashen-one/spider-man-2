# Water round 04 (WIP): capture hold 1 of 2 (Opus 5.5)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

The files in this folder are capture hold 1 (08:10, build c331645 + final params LongK 3, FarRough 0.2, TopVarK 0.1). `spec.json` holds
the numbers. Hold 1 PASSES: harbour_sun_high glints, column coverage and sparkle size; the river_low / dolly / S4 holds. It FAILS: harbour_high hp sd
8.19 (needs 10) with 187 "pale blobs" (crest highlights, median 29 px), and the seawall foam band (0 px). The `Dbg 4` iteration still
(`iter/DBG4_river_low.jpg`) shows **no contact coverage** at the bulkhead: the coast_m piles and wall lean landward below the water, so the
water-line contact map sat about 2 m behind the visible lip. Capture hold 2 (queued 08:08) rebuilds with a contact map taken up to the
lip and then replaces these files.
