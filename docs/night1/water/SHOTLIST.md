# River water: shot list (round 02)

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
| `river_low_dolly.mp4` | `/Game/Water/Maps/Water_View_RiverLow_Dolly` | 10 s, 2 m/s forward along the seawall (motion, ring artifact / autocorrelation, piling foam) |
| `river_sun_dolly.mp4` | `/Game/Water/Maps/Water_View_RiverSun_Dolly` | 10 s, 2 m/s toward the sun (glitter motion) |
| perf | `Water_View_RiverLow`, `Water_Perf_S4`, `Water_View_RiverSun` vs their `_Base` (P1 flat water) | water GPU cost <= 2.5 ms (exclusive lock) |

Acceptance (PLAN-firstpass section 4 Water): near-water crop high-pass sd >= 12, p99.5 >= 150, glint pixels >= 1 %, mean Y <= 80; C14 5..35 at S4;
autocorrelation <= 0.10 at 80 px; piling foam present; water cost <= 2.5 ms; critic axes >= 6.
