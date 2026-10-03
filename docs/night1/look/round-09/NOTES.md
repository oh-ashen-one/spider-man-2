# Look round 09: capture notes (neutral facts only)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Every frame in this folder was rendered by the running game (`unreal/WebHomage/Scripts/run_game.sh`: standalone `-game`, offscreen, true back-buffer size), each run inside `/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture` (shared GPU, background priority; the perf pass under `gpu_slot.sh perf`).

## Build
- Branch `night1/look` after `git merge origin/Opus-5.5-Loop-Night-1` (city r11 far-shore LOD facades, terrain r05, traversal r26, characters r17).
- C++: `unreal/WebHomage/Scripts/build_editor.sh` (step `cpp` of `build_manhattan.py`).
- Integrated maps: `SM2_MANHATTAN_SCR=/Users/midir/sm2-n1/_scratch/look/manhattan python3 unreal/WebHomage/Scripts/build_manhattan.py --steps cpp,city_prep,city_extra,city,traversal,characters,look,map` (two `gpu_slot.sh capture` holds: the first hold reached the 2400 s maximum after the `city` step had finished, the second ran `traversal,characters,look,map`).
  The city export (`city_export` step) was made with this worktree's own dev port 5205 (`npx vite --port 5205`, `node tools/export/export_city.mjs --url http://127.0.0.1:5205/ --out <scr>/export/midtown3x3`, manifest URLs rewritten 5205 -> 5202 as the step does for 5208); the step itself hard-codes the Manhattan piece's port 5208, which was not used.
  `build_water.py`, `build_life.py`, `build_combat.py` were not run: the S4 river is the city's own flat water plane.
- Look content: `tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod` (hold A), then `rigs,maps golden` twice (holds C, C2) with the city export above (`SM2_CITY_EXPORT`). The maps `/Game/Maps/Manhattan*` reference `Look_Rig_golden` as a sublevel, so a rig rebuild reaches them without a map rebuild.

## Golden preset (fixed, `Look_Rig_golden`; the integrated `/Game/Maps/Manhattan` and `Manhattan_View_S4` use it)
Changed keys of `presets.golden` (`unreal/WebHomage/Scripts/look_presets.json`, previous values in `presets.golden._r09_previous`):
| key | round 08 | round 09 |
|---|---|---|
| atmosphere.aerial_perspective_distance_scale | 5.0 | 2.5 |
| atmosphere.height_fog_contribution | 1.0 | 0.8 |
| atmosphere.sky_luminance_factor | 1, 1, 1 | 0.925, 0.925, 0.925 |
| atmosphere.sky_and_aerial_perspective_luminance_factor (new key) | (engine default 1) | 0.5, 0.5, 0.5 |
| sky.intensity (sky light) | 2.5 | 5.7 |
| fog.volumetric_fog_extinction_scale | 0.5 | 2.0 |
Bake history (`diag/bakes.txt`): bake 1 sky luminance .96 / sky light 5.5, bake 2 .925 / 5.5, bake 3 (committed) .925 / 5.7.

The time-of-day table derives 16 keys and the bases golden_am / dusk / dusk_am / dawn from `presets.golden`. To keep it unchanged, `tod.derived.golden_r08` = golden with the round-08 values of the six keys, and every tod reference to `golden` points to it (`tools/perf_ue/sweeps/r09/tod_guard.py apply`; `tod_guard.py --check caaf7002`: 71 of 71 keys equal to the round-08 expansion). `look_tod.ATM_DEFAULTS` gained `atm.SkyAndAerialPerspectiveLuminanceFactor` = 1 (engine default) so every key has the same params.
Note: `tools/perf_ue/sweeps/r08/make_v4.py --in-place` regenerates the whole document from the round-07/08 knob files and would drop the round-09 golden values and `golden_r08`.

## Sweeps (live tuning, not baked)
`diag/sweep1.txt` .. `sweep15.txt` (variants `diag/sweep*_variants.json`): `tools/perf_ue/capture_tour.py --map /Game/Maps/Manhattan --variants ...` on the baked round-08 golden rig, every variant sets every knob (`tools/perf_ue/sweeps/r09/gen_s4.py`), settle 5-6 s per pose (first pose 14 s, +2 s at each variant change), 1920x1080, internal 100 %. Sweeps 1-10 S4 only, 11-15 S1-S8 (`*_all.json`: L1 and Y<25 per still). Base variants repeated inside a session agree to 0.4 Y; the same knob set in different sessions differs by up to ~2 Y on the far / critic boxes (e.g. g03 / h01 / h10 / i01 / i11).

## Stills (1920x1080 output, internal 1920x1080 = `r.ScreenPercentage 100`)
- `stills/golden_S4_1920x1080_manhattan_view.jpg`: `/Game/Maps/Manhattan_View_S4` (the map's own S4 shot camera, default game mode, no hero), frame at t = 38 s of game time (pair t = 34 / 38 s; two separate sessions give identical numbers, `diag/bakes.txt`). PNG of the frame: `diag/png/view_s4_1_t038.png`.
- `stills/golden_S<n>_1920x1080_manhattan.jpg`: shot tour on `/Game/Maps/Manhattan` (golden rig, traversal game mode, hero teleported to the view's player position), 5 s per pose (first 14 s), >= 90 frames. S4 PNG: `diag/png/tour_S4.png`.
- `stills/before_golden_S<n>_1920x1080.jpg`: the round-08 golden preset on the same city build (sweep 15 base variant, same tour). S4 PNG: `diag/png/before_tour_S4.png`.
- `stills/midday_S<n>_1920x1080.jpg`, `night_S<n>_1920x1080.jpg`: fixed preset maps `/Game/Tests/Look/Look_Midtown`, `Look_Midtown_night` (inputs identical to round 08), one tour session each.
- `stills/tod_*`: `/Game/Tests/Look/Look_Midtown_tod` (round-08 table), one session of the round-08 `full` plan (48 poses, `stills_session_tod.json`): first pose of an hour 8-14 s after the hour change, next poses 5 s.

## Clip
`S4_perch_golden.mp4`: `/Game/Maps/Manhattan_View_S4`, 1920x1080 output, internal 100 %, fixed 1/60 s step (`-benchmark -fps=60 -dumpmovie`), game seconds 8-13 of the run (the first 8 s = warm-up / exposure settle, trimmed), H.264. A clip says nothing about real-time frame rate.

## Perf
See `perf/PERF.md` (exclusive `gpu_slot.sh perf` pass, or the reason it did not run).
