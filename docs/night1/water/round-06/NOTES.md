# Water round 06: contact mask (the near-field sparkle stays at walls and piers), rough open water, open-water sun glints

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/water` on top of the r05b state (DistFix 1 kept). Builder: Claude Opus 5.5 high via Devin. Every Unreal process ran inside a
`gpu_slot.sh capture --label water` hold, one engine of this worktree at a time; engines were stopped only with `stop_ue.sh` (driver scripts
first). No engine crashed. Two screening stills ended in a ~4 min hang at exit (engine quit in the same frame as the screenshot request after a
long first-frame stall, no png written); both were cleared with `stop_ue.sh` (SIGTERM, "stopped cleanly"). The Studio was shared with the
terrain / look / city / island sessions (1-2 other engines). Perf was not run (unattended rule; not this round's gate).

FINAL_SECTION_PLACEHOLDER

## What changed in `build_water.py` (material parameters, defaults in PARAMS; ShoreMask 0 = r05b)
- **Contact mask** (`cmask`, `openW`): inside the contact box the 0.9 m/px contact map (distance to geometry crossing the water line:
  seawalls, bulkheads, pier piles, bridge piers) gives cmask = 1 - smoothstep(ShoreA 2 m, ShoreB 14 m, d); outside the box the 8 m/px layout
  shore map, 10-40 m (it reads ~28 m at the built river_low seawall, so it is only the fallback). Fade-out ends at 14 m (contact map) / 40 m
  (shore map). openW = (1 - cmask) within OpenD0..OpenD1 (250..400 m) of the camera: the swing-height views (harbour_high,
  harbour_sun_high: nearest water ~430 m) and the S4 perch keep r05b's shading (measured below). The contact-map fetch is shared with the far
  contact line (one fetch per pixel, as before).
- On open water (openW = 1): the resolved chop is not shaded (OpenChop 0; it is kept as `slopeX` for the glint pick), the second
  realization of the spectrum layers is off (OpenB 0), the whitecap flecks are off (OpenWC 0), and the GGX roughness has a floor
  **OpenRgh 0.5**. Within 2-14 m of walls / piers the r05b near field is unchanged (chop, two realizations, sharp lobe, lace foam).
- **Open-water sun glints** (OpenGlS, GlitPow, GlitSlK): a pixel whose full-detail normal (shaded slope + the unshaded open-water chop x
  GlitSlK) lies near the sun half-vector (pow(N.H, GlitPow)) is drawn as a sharp facet on the half-vector (roughness 0.06). Off on north-facing
  views (mirror direction more than 60 deg from the sun).
- Also added (variants, not used by the final unless listed): OpenSl (spectrum-layer gain on open water), OpenBend (BendK share on open water),
  OpenGlit / OpenGSp (gain / facet spread of the r03 noise glitter on open water). `Dbg 11` = the mask as unlit colour (R cmask, G openW, B nearW;
  `iter/a_DBG11_river_low.jpg`, `iter/a_DBG11_river_sun.jpg`).

## Screening (1080p stills at t = 16 s, `tools/water/r06/screen.py`; 1080p is upscaled to 4K before the crops, so hp reads ~0.75 x native
and the near mean ~4 Y above native)
What frosted the open water was not the chop: removing the chop, the second realization and the whitecaps from open water made river_low
brighter (101.1 vs 97.8 for ShoreMask 0), and a flatter open water (OpenSl 0.6) brighter still (107.6). The bright frost is the sharp
(<= 0.08) GGX lobe mirroring the bright horizon haze / golden sky at grazing angles. The legacy shader (DistFix 0) was darker because its garbage
distance pushed every pixel into the far-field roughness (~0.3); with DistFix 1 the near field (<= 150 m) is a sharp mirror. Roughness on open
water is the lever:

| variant (hold) | river_low near mean / hp (1080p) | river_sun flanks / path400 ratio / sparkle native (1080p) |
|---|---|---|
| OFF = r05b (A) | 97.8 / 15.6 | 116.3 / 1.38 / 56.1 % |
| mask, chop + B + whitecaps off (A) | 101.1 / 16.7 | 117.7 / 1.38 / 57.3 % |
| + OpenSl 0.6 (A) | 107.6 / 16.1 | |
| + OpenRgh 0.2 (A) | 96.9 / 16.0 | 107.9 / 1.69 / 45.5 % |
| DistFix 0 legacy (B) | 92.0 / 9.6 | 88.8 / 2.15 / 34.3 % |
| + OpenRgh 0.3 (B) | 89.0 / 15.2 | 94.1 / 2.07 / 34.3 % |
| + OpenRgh 0.3, OpenBend 0 (B) | 90.7 / 14.5 | 94.0 / 1.99 / 34.3 % |
| + OpenBend 0 only (B) | 103.7 / 15.2 | 117.7 / 1.38 / 56.6 % |
| + OpenRgh 0.4 (B) | 81.3 / 14.0 | 82.3 / 2.37 / 29.5 % |
| + OpenRgh 0.4, glints GlitPow 3000 (C) | 83.1 / 14.2 | 82.2 / 2.41 / 30.9 % |
| + OpenRgh 0.4, chop + B shaded (C) | 78.3 / 13.1 | 81.8 / 2.36 / 30.3 % |
| + OpenRgh 0.45 (D) | 77.3 / 13.3 | |
| + OpenRgh 0.5 (C / D) | 74.5 / 12.6 | 73.1 / 2.66 / 30.0 % |
| glint variants on OpenRgh 0.4 (C / D: GlitPow 1000-10000, OpenGlS 4, GlitSlK 2-4, OpenGSp 3) | | 81-83 / 2.35-2.69 / 26.0-34.5 % |

The sparkle width (native rule: >= 2 % of the water rows at Y >= 200 per column) of r05b came mostly from that same frost (r05b's left flank
mean 132). Sun glints from 9-deg sun at 6 m height need facet tilts of 35 deg or more 10-25 deg off the sun azimuth, so the pow(N.H) glint
pick stayed at 26-35 % of the columns up to GlitPow 1000. Hold E tries broad picks (GlitPow 80-300).

HOLD_E_PLACEHOLDER
