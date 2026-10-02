# Round 07 hold A findings (twilight dome sweep, 120 stills, 2026-10-02 10:11-10:37)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Real game, `Look_Midtown_tod` baked with the round-06 C table, live pins (`gen_sweep_a.py`), 1920x1080, internal 100 %, settle 8 s first pose / 5 s next. Numbers: `holdA_DOME.md`, `holdA_pivot.md` (dome_check.py).
1. `fog.FogCutoffDistance 0` (fog on the sky pixels) removes the horizon step everywhere: S4w 19:48 8-row step 92.8 -> 15.8 Y, S4 20:00 21.6 -> 4.2; L27b passes on every twilight still of every combo except a few sky-factor-heavy ones (25.7 max).
2. The black ceiling is the twilight cloud deck (coverage .14-.25 / density .022-.03, unlit once the sun is down; raising the sky factor did nothing behind it, hold 6A W4). Thin clouds (.05 / .012) + a lit SkyLuminanceFactor (g x [1.6, 1, .8]) give L27a on S4: 20:00 +13 (g 16) / +29 (g 40), 20:30 +18 / +31, 19:48 +14 / +29.
3. The sun-facing stills clip because the exposure is CLAMPED by `pp.AutoExposureMaxBrightness` (S4w 19:48 / 20:00: frame mean 75-83, rows 0-150 clipped 13-56 %; S4e 07:00 33-51 %). Their far band (150-185 Y) is the glow toward the sun on the far city (sun volumetric scattering 0 and directional inscattering x0.2 only took it 178 -> 171).
4. Without clouds the sky near the sun clips at 19:30 / 06:30 (21-25 %) with the r06 factor; the r06 clouds hid it.
5. Golden 18:24 with cutoff 0: S4 mean 98.6 -> 113.6 (fogged sky band brighter), S3 59 -> 46 (its sky brighter, exposure down); a lower sky factor raises S4 (119: the sky is the metered region).
6. Night 22:00 with cutoff 0: S4 41.5 (r06 41.1), S1 45.2, S6 48.6 (L3 ok) but S4m 74.8: the moonlit volumetric fog now lies over the sky (a veil; blob 64.6 px).
7. Baseline repeatability: the no-pin 20:00 S4 reads 12.4 / 38.6 (r06 baked still 13.8 / 38.0).
