# Water round 04: far field from swing height, sun glints from above, foam gate (Opus 5.5)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Build: `night1/water` at f73df3eb (shader + POT contact map) with the committed `PARAMS` (`LongK 3, FarRough 0.2, TopVarK 0.1, MidK 2,
CBias 0.8, SunClampK 1, FoamNK 3, GlitDist 4000, GlitFar 8, ChopFar 0` on top of the round-03 set). Two capture holds (`gpu_slot capture`,
cap 1): hold 1 07:45:52 to 08:10:59 (1507 s) and hold 2 09:46:21 to 10:11:58 (1537 s). Each one was: build, iteration stills, a decision
gate, the final build, stills and both dollies. The files in this folder come from hold 2. Hold 1's set is in `_scratch/water/r04/hold1_round/`;
its numbers match hold 2 to within 0.1 (it had the r03 contact map). Stills are 3840x2160 and 1920x1080 output at **native internal
resolution** (`r.ScreenPercentage 100`), shot at t = 16 s. Dollies are 1920x1080 at 100 %, 60 fps, t = 6 to 16 s (600 frames).
`river_sun_dolly.mp4` was re-encoded at CRF 23 to fit under 15 MB (12.2 MB).
Iteration stills: `iter/` (hold 1) and `iter/h2_*` (hold 2), downscaled to 1920 px. Their numbers are in `iter/report.txt` and
`iter/h2_report.txt`.

## What changed (see `unreal/WebHomage/Scripts/build_water.py`, `tools/water/water_inputs.py`)
- **Far-field long waves.** A 64 m slope layer (2.7 to 21 m waves, one realization) is sampled with true gradients at every distance.
  Beyond 100 to 300 m it gets a gain: `LongK` on it and on the 21 m layer, `MidK` on the 6.7 m layer. This is resolved slope, not
  roughness: the variance budget (`varL`) is not scaled.
- **View-dependent far roughness.** When the camera looks down (`down` = smoothstep(0.08, 0.25, V.z)), the far lobe is capped at
  `FarRough` 0.2 and the unresolved variance is weighted by `TopVarK` 0.1. At grazing views (river level) the far field beyond ~255 m keeps
  a rough lobe of at least `GrazeRough` 0.42. This is also the perf lever: Lumen does not trace above 0.4.
- **Sun glitter from above.** The facet glitter now runs only where the flat-water mirror direction lies within ~40 deg of the sun (an
  early-out, so the north-facing views skip it entirely). It reaches `GlitDist` 4 km (r03: 900 m), and beyond 250 to 600 m it uses facets
  8x coarser (`GlitFar`) so far sparkles stay a few pixels wide instead of mip-averaging away.
- **Foam.** Foam pixels take the long-wave normal (`FoamNK`). A soft clamp limits slopes facing away from the low sun (`SunClampK`). The
  contact-map term reaches `CBias` m further. The contact map is now built from crossings up to the +2.3 m lip, and written power-of-two.
  **None of this brought the foam back** (see below).
- Turbidity comes from the gust sample (one fetch less). `Dbg 5` shows N.L. `Dbg 7` shows the contact-map distance, the under-water ray
  length and cf. `Dbg 8` shows world-position stripes.
- New view `harbour_sun_high` (views.json, SHOTLIST, `capture_round.sh`). New checker modes `water_spec.py sunhigh` and `water_spec.py foam`,
  plus r04 checks. The harbour crop is now y 1300-2160, the critic's crop.

## Numbers (`spec.json`; `python3 tools/water/water_spec.py all docs/night1/water/round-04`)
| check | target | r03 | r04 |
|---|---|---|---|
| harbour_high crop hp sd | >= 10 | 4.27 | **8.19** FAIL (x1.9) |
| harbour_high pale blobs >= 20 px | 0 | 2 | **188** FAIL (see below: these are crest highlights) |
| harbour_sun_high glints (Y >= 200, hp >= 30) | >= 0.5 % | (new view) | **0.61 %** PASS |
| harbour_sun_high path columns with Y >= 200 | >= 50 % | | **100 %** PASS |
| harbour_sun_high sparkle size (median / p90) | <= 6 px | | **3 / 8 px** PASS (3848 sparkles) |
| seawall foam band (mean px / rows >= 12 px) | >= 12 / >= 30 % | 0 / 0 | **0 / 0 FAIL (gate)** |
| foam change between 4 fps dolly samples | >= 0.3 | 0.03 | **0.0** FAIL |
| river_low near hp sd (hold) | >= 9.9 | 9.93 | **11.74** PASS |
| river_low near mean Y (hold) | <= 80 | 78.5 | **62.0** PASS |
| river_low / river_sun dolly autocorr 80 px (hold) | <= 0.10 | 0.053 / 0.015 | **0.076 / 0.024** PASS |
| S4 C14 (hold) | 5 to 35 | 17.9 | **22.0** PASS |
| river_sun sparkle width (r03 target) | >= 50 % | 37.8 | **50.5 %** PASS |
| perf at river_low: frame delta / SLW + depth prepass + Lumen refl delta | <= 2.5 / <= 2.5 ms | -0.25 / 2.69 | **-0.80 PASS / 2.54 FAIL by 0.04** (1.09 + 0.47 + 0.98) |

`harbour_sun_high` water crop: x 0-3840, y 700-2160. A strip of the far shore intrudes at the top right (x > ~3000, y < ~880).

## Far field (harbour_high): what moved and what did not
- hp sd went from 4.3 to 8.2 at LongK 2, and held there. LongK 3 with FarRough 0.2 gave 8.26. MidK 2 gave 8.19. ChopFar 800 gave 8.22, and
  ChopFar 1500 with MidK 3 gave 7.59. LongK 1 gave 6.03. Past LongK 2 the high-pass is flat: more resolved slope only spreads the
  reflection over a sky that is nearly uniform 19 to 60 deg up. From this height the sun is behind the camera, and the haze lifts the far
  rows (mean Y 94 in the top 172 rows against 68 in the bottom ones). The structure that exists is wave-shaped, not decals (`iter/h2_*harbour_high*`).
- The "pale blob" rule (>= 18 Y above the sigma-24 mean, chroma <= 0.35, >= 20 px, peak < 140) now counts **crest highlights**: 188
  components, median 27 px, p90 49 px, elongated (w/h 1.7), spread evenly. The round-02 foam decals were 114 components, median 39 px. hp sd
  >= 10 and 0 such components contradict each other on this frame: every variant that raised hp raised the count (L1: hp 6.0 with 55; base:
  8.1 with 327; C15: 7.6 with 67). This needs an orchestrator decision: keep the blob rule for foam decals only (for example
  peak-to-area or isolation), or accept a hp sd < 10 target from this height without the sun.

## Foam gate: FAILED, diagnosis so far
- `iter/DBG4_river_low.jpg` (hold 1) shows wf = cf = 0 along the bulkhead, so **coverage** is missing. It is not only lit dark. The foam
  normal fix alone could not help.
- `iter/h2_DBG7_river_low.jpg` (hold 2) shows the **contact-map distance >= 4 m and the under-water ray >= 4 m everywhere along the wall**,
  so cf = 0. `iter/h2_DBG8_river_low.jpg` shows world-position stripes that line up exactly with a CPU ray-cast of the camera
  (`_scratch/water/r04/emu_contact.py`; the 1 m x-crossings match to the pixel). So the pixel position `p` is right, and the CPU reads the
  same map as **0.6 to 1.9 m** at the wall pixels.
- The export geometry here: fender piles at x -767.8 to -767.0 (vertical, y -10.8 to +0.3) and a bulkhead that leans landward under the
  water (crossing at x ~-765.5). So the depth test finds no near geometry under the water, as Dbg 7 shows, and the map is the only source.
- Writing the map power-of-two (2625 to 4096 px wide) did **not** change the in-engine reading. CBias 0.8 / 1.6 / 2.4 changed nothing
  either: cf stays 0. The fault is therefore in how `T_WaterContact` is sampled in the material (texture data or UV), not in the map
  geometry. Next step, one 1080p hold: a `Dbg 9` that outputs `tC` at fixed UVs (a known pile and open water) as **emissive**, and the
  same for `T_ShoreDist`. Also print `T_WaterContact` size and format from the build commandlet.
- The "dark specks" are still there. BendK 0.7 and 1.0 (`iter/h2_B7*`, `h2_B10*`) replace them with flat grey mirror patches, and the
  sun-side slope clamp did not remove them. They are dark reflections off steep near chop facets, not foam. They need their own look pass.

## Critic pack
`/Users/midir/sm2-n1/_scratch/critic-W-r04/pack` (key `pack.key.json` beside it; `pairs.json`). 7 pairs:
- 4 against references: harbour_sun_high vs `streets/waterfront-og__og_0244`, harbour_high vs `streets/skyline-perch-nm__nm_0846`,
  river_low vs `river-pier-golden`, river_sun vs `waterfront-perch-trailer`.
- 3 previous-vs-this: seawall foam crop, harbour_high, river_low dolly.

## PERF (`perf.json`, `perf_gpu.json`)
Exclusive `gpu_slot perf` at native 3840x2160, 100 % (no TSR upscale), static camera, frames 16 to 31 s, water map against the same map
with P1's flat plane. `GPU-LOCK: class=perf exclusive=yes util_before=0% util_after=35% util_during_avg=8.8% wait_s=3318
instances_before=0 instances_max=2 contaminated=false`. ioreg Device Utilization before the hold: 0 %. Only the river_low pair ran: the
chain's 720 s budget ran out before river_sun, because each run took ~6 min. S4 and river_sun were not re-measured this round.
| view | GPU frame water / flat (ms) | frame delta | SLW pass | SLW depth prepass | Lumen refl delta | SLW + depth + LR |
|---|---|---|---|---|---|---|
| river_low | 37.92 / 38.73 | **-0.80** PASS | 1.09 (r03 1.00) | 0.47 | +0.98 (r03 +1.22) | **2.54** FAIL (<= 2.5; r03 2.69) |
The grazing-view far roughness floor (`GrazeRough`) took 0.24 ms off Lumen reflections. The 64 m layer and the sun-side clamp added 0.09 ms
to the SLW pass. One sample less would close the last 0.04 ms (for example the 64 m layer only when `down` > 0, or the second gust
sample). The negative frame delta is run-to-run noise against the flat base, not a saving.
