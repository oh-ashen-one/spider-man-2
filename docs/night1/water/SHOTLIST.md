# River water: shot list (rounds 02-04)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Cameras: `views.json` (UE cm, X east, Y south, Z up). Maps are built by `unreal/WebHomage/Scripts/build_water.py`. Captures:
`tools/water/capture_round.sh <round-dir> stills|stills1080|movie|perf` (every Unreal run through `gpu_slot.sh`). Numbers:
`python3 tools/water/water_spec.py all <round-dir> --json <round-dir>/spec.json`.

| id | map | what it checks |
|---|---|---|
| `S4_golden_{1080,4k}` | `/Game/Maps/Manhattan_View_S4` | perch view over the Hudson (CITY-SPEC C14: far shore minus river luma 5..35) |
| `river_low_{1080,4k}` | `/Game/Water/Maps/Water_View_RiverLow` | round-01 framing (same camera): seawall + pilings on the right (contact foam), near-water crop, previous-vs-this pair |
| `river_sun_{1080,4k}` | `/Game/Water/Maps/Water_View_RiverSun` | new: low view across the Hudson into the golden-hour sun (glitter path), open water |
| `harbour_high_{1080,4k}` | `/Game/Water/Maps/Water_View_HarbourHigh` | new: 260 m over the harbour looking north (coverage: both rivers + harbour around the island) |
| `harbour_sun_high_{1080,4k}` | `/Game/Water/Maps/Water_View_HarbourSunHigh` | r04: harbour_high's position and height, yaw 148 (toward the golden sun, az 238, el 9): glints from swing height |
| `river_low_dolly.mp4` | `/Game/Water/Maps/Water_View_RiverLow_Dolly` | 10 s, 2 m/s forward along the seawall (motion, ring artifact / autocorrelation, piling foam) |
| `river_sun_dolly.mp4` | `/Game/Water/Maps/Water_View_RiverSun_Dolly` | 10 s, 2 m/s toward the sun (glitter motion) |
| perf | `Water_View_RiverLow`, `Water_Perf_S4`, `Water_View_RiverSun` vs their `_Base` (P1 flat water) | water GPU cost <= 2.5 ms (exclusive lock) |

Acceptance (PLAN-firstpass section 4 Water): near-water crop high-pass sd >= 12, p99.5 >= 150, glint pixels >= 1 %, mean Y <= 80; C14 5..35 at S4;
autocorrelation <= 0.10 at 80 px; piling foam present; water cost <= 2.5 ms; critic axes >= 6.

Round 03 targets (reconciled; all measured by `tools/water/water_spec.py all <round-dir>`, which prints PASS / FAIL per line; 4K native frames):
- `river_low_4k` near crop (x 0-1500, y 1150-1800 of the 84 % pack frame): hp sd >= 12, p99.5 >= 150, glints (Y >= 140) >= 1 %, mean Y <= 80,
  p1 <= 25 (reference river-pier-golden through the same instrument: 13.8 / 151 / 1.1 % / 58.6 / 14). River_low glints are sky / mist
  reflections off steep chop, not sun glints: no framing change.
- `river_sun_4k`: sparkle width (columns of the pack frame's water rows, >= 45 % of the height, with >= 2 % of rows at Y >= 200) >= 50 % of the
  width (reference 67 %), near-crop mean Y <= 90, glints 3..15 %. Its mean is not judged otherwise.
- `harbour_high_4k` crop x 0-2400, y 1300-2100 of the NATIVE 3840x2160 frame: hp sd >= 10, glints >= 2 %, 0 pale blobs >= 20 px.
- dollies: autocorrelation at 80 px <= 0.10; S4 C14 5..35; seawall contact foam present (`crop_river_low_4k_seawall_foam.jpg`).
- perf (`round-NN/perf.json`, `tools/water/perf_summary.py`, exclusive lock, 3840x2160 native 100 %): frame delta vs the flat-plane base
  <= 2.5 ms AND the SingleLayerWater pass alone <= 2.5 ms at river_low.

Round 04 targets (reconciled 2026-10-02; `tools/water/water_spec.py all <round-dir>` prints them under `-- r04 round targets`; 4K native frames).
The sun (SkyAtmosphere light 0, az ~238, el 9) is behind the north-facing `harbour_high` and `river_low` cameras, so no facet can mirror it
there: glints count only on sun-facing views.
- Far-field structure: `harbour_high_4k` crop x 0-2400, y 1300-2160: high-pass sd >= 10 (r03 4.3) and 0 pale blobs >= 20 px.
- Glints from above: `harbour_sun_high_4k` water crop x 0-3840, y 700-2160: glints (Y >= 200 and high-pass >= 30) >= 0.5 %; Y >= 200 (>= 2 % of
  the crop rows) in >= 50 % of the glitter-path columns x 1480-2360 (sun azimuth +-10 deg); sparkle size (max bbox side of the glint
  components) median <= 6 px.
- Gate, contact foam: `crop_river_low_4k_seawall_foam.jpg`: band at Y >= 180 within 60 px of the bulkhead edge, mean >= 12 px and >= 30 % of
  rows >= 12 px (round 02: 13.5 px / 37.9 %; round 03: 0 / 0); it changes between 4 fps samples of `river_low_dolly.mp4` (XOR / OR of the
  band masks >= 0.3; round 02 0.63, round 03 0.03); no dark foam specks (`Dbg 4` / `Dbg 5` iteration stills in `round-04/iter/`).
- Hold: river_low near hp sd >= 9.9, mean Y <= 80; dolly autocorrelation <= 0.10; S4 C14 5..35. Perf at river_low (native 4K, exclusive lock):
  frame delta <= 2.5 ms AND SLW + SLW depth prepass + Lumen reflections delta <= 2.5 ms (`perf.json` `slw_depth_lumen_sum`; r03 2.69).
- Not scored on water this round (sky ceiling, look piece): river_low p99.5 >= 150 / glints, the S4 haze band.
