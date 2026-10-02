# Round 07 hold B findings (sweep B 80 stills + lapse windows of the best-guess table v0, 2026-10-02 11:20-11:38)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

1. `pp.AutoExposureMaxBrightness 15` changed nothing on the sun-facing stills (S4w 19:48 mean 84, clip 34 %): the twilight exposure sits on its MIN clamp (min EV 3.0 / 2.46 at 19:48 / 20:00; average metering b4 also changed nothing there), so S4 and S4w get the same exposure and the brighter sun-facing view blows out at the high S4 bias (2.2). v1 frees the twilight meter (min EV -1 from 19:24 to 20:36 and 06:00-06:54) and starts the biases from a smooth curve.
2. Aerial-perspective distance x0.3 / Mie anisotropy .6 move the sun-facing sky-far by only +2..+5 Y (S4w 20:00 stays ~0): the far band toward the sun is the glow itself.
3. 20:30 warm hue [4, 1, .4] x 40: S4w B-R -51 / -61 with sky-far +21 / +30, S4 +24 / +30: L27a and L27d pass at 20:30.
4. Golden 18:24 with cutoff 0: bias -.35 + metering high 95 % (g2) = L1 6 of 8 (S3 60.5, S4 105.1); max opacity .7 = S4 116. v1 tries g2 + golden fog inscattering x0.7.
5. Night 22:00 with moon volumetric scattering 0 / .2: S4m mean 41.6 / 39.7, moon 55 / 52 px peak 255, high-pass 3.11 / 2.86 (L25b passes at 0); S4 38.6 / 45.8. v1 uses .1.
6. Lapse windows of table v0 (x16, `holdB_lapse_windows_v0.json`): dusk max jump 5.9 (p99 5.8): a steady fall 118 -> 41 Y from 18:36 to 19:40 (-3..-4.5 Y per frame: the geometric surface decay with the exposure on its min clamp) and +5.9 at 19:44-19:49 (the bias seed ramp); dawn max 11.8 at 06:34-06:43 (zigzag of round-06 dawn biases between main keys and snapshot keys). No 20:30 pit in the lapse (40 vs 42 at 21:20).
