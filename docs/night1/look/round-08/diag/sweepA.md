# Round 08, sweep A (live pins on the baked round-07 table v10)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Real game (`run_r06.py`, standalone `-game`, offscreen, `gpu_slot.sh capture`), 1920x1080, internal 100 %, settle 8 s on the first pose of a group, 5 s after. Plan: `sweepA_plan.json` (generator `tools/perf_ue/sweeps/r08/gen_sweep_a.py`). Numbers: `tools/perf_ue/sweeps/r08/quick.py`.

Instrument caveat found in this sweep: the baked round-07 table has no `pp.LocalExposure*` / `skyc.*` keys, so a pin of them stayed on the post volume after `wh.ToDClear` (the driver only writes keyed params). Every group after the first `le5` group carried the last local-exposure pins (shadow contrast .5, blurred-luminance blend .2) and `skyc.VolumetricScatteringIntensity` 1/3: the 07:30, 19:00, 20:30 and 20:00 rows below are relative comparisons only. Sweep B pins every new param on every group.

## 07:00 (clean: before the first local-exposure pin, except c1 / c2)
| still | mean | Y<10 % | clip % | sky Y | sky sat | sky B-R | far Y | sky-far | 8-row step |
|---|---|---|---|---|---|---|---|---|---|
| S4e b0 | 28.4 | 53.1 | 0.01 | 125.3 | .500 | -78.6 | 90.8 | +34.5 | 20.1 |
| S4e sk3 (sky light x3, fog scattering 1/3) | 31.5 | 38.7 | 0.01 | 125.2 | .490 | -78.3 | 92.2 | +33.0 | 20.3 |
| S4e sk6 | 35.9 | 24.7 | 0.01 | 126.4 | .484 | -78.7 | 92.1 | +34.2 | 21.1 |
| S4e fl8 (anti-solar fill x8 = 17.5 lux) | 28.5 | 52.6 | 0.01 | 125.7 | .495 | -77.5 | 90.8 | +34.9 | 20.5 |
| S4e le5 (local exposure shadow contrast .5) | 46.0 | 4.3 | 0.01 | 131.5 | .489 | -81.4 | 105.5 | +26.0 | 21.0 |
| S4e le4b (.4, blend .2) | 52.6 | 0.1 | 0.01 | 131.1 | .495 | -82.6 | 104.2 | +26.9 | 20.4 |
| S4 b0 | 57.6 | 2.8 | 0.00 | 143.4 | .385 | -66.7 | 85.8 | +57.6 | 18.1 |
| S4 sk6 | 66.5 | 0.4 | 0.00 | 114.1 | .448 | -65.7 | 77.5 | +36.5 | 14.4 |
| S4 le4b | 83.7 | 0.0 | 0.00 | 145.4 | .378 | -65.7 | 104.8 | +40.6 | 13.8 |

Readings: the horizon fills (unshadowed, 10 deg up) at tens of lux do not register at the dawn exposure; a 6x sky light lifts S4e by 7.5 Y and lowers the S4 sky by 29 Y (the metering follows the brighter city); the bilateral local exposure lifts the backlit city without moving the sky band (S4e 125 -> 131), but it lifts the far band too (S4 +19 Y).

## 19:00 (sticky local exposure .5 / blend .2 in every row)
S4w: b0 72.5, sky light x3 81.3 (sky-far +13.7 -> +5.6), x6 87.2 (-3.2), local exposure .4 79.3 (+13.7). S4: sky light x3 takes sky-far from +2.8 to -11.0 (the sky darkens 119 -> 103).

## 20:30 blue hour (sticky local exposure in every row)
| variant | S4 sky B-R | S4w sky B-R | S4 sky-far | S4w sky-far |
|---|---|---|---|---|
| b0 | -18.7 | -25.2 | -0.1 | +13.4 |
| bh1 SkyLuminanceFactor x[.4, .85, 1.6] | -0.2 | -1.1 | +13.6 | +28.1 |
| bh2 bh1 + warm Mie x3 | -0.4 | +0.0 | +22.9 | +34.2 |
| bh3 x[.25, .8, 2.0] + warm Mie x4 | +18.6 | +20.8 | +27.1 | +24.9 |
The sky luminance factor moves both views together; the Mie lobe does not separate the sun-facing view from S4 at a sun depression of 14 deg.

## Sub-horizon disk (S4w 20:00)
Still present with `sun.DiskScale 0`, with `sky.Intensity .001` and with `r.Lumen.Reflections.Allow 0` (crops `disk_sweepA.png`). Its screen position does not move between 19:30 and 20:30 and matches the mirror image of the `fill.W` horizon fill (az 270, 10 deg up) in the river (roughness .06): sweep B pins the four fills to 0.
