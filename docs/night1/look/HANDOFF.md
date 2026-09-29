# P4 Look, lighting, post, perf: handoff (round 01)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Branch `night1/look`, worktree `~/sm2-n1/look`, UE MCP 8774, dev port 5205. Owns `/Game/Look`, `/Game/Tests/Look`, `tools/perf_ue/`,
`Scripts/build_look.py`, `Scripts/look_presets.json`, `docs/night1/look/`. Nothing in `Content/` is committed: scripts rebuild everything.

## State (end of round 01)
- **City rebuilt in this worktree** with P1's untouched pipeline on P4's own port / scratch (`tools/perf_ue/rebuild_city.sh`): export 507 tile meshes + 102 prototypes
  (about 40 s of Chrome), import into `/Game/City` + `/Game/Tests/City` about 9 min in the editor.
- **`Scripts/build_look.py`** (idempotent, runs headless in about 25 s, no editor needed) builds:
  - `/Game/Look/Rigs/Look_Rig_<midday|golden|night>`: ALL lighting per preset, as a sublevel: SkyAtmosphere (aerial perspective), sun (physical lux, temperature, 0.54 deg disc)
    + moon (night, atmosphere light 1), real-time-capture SkyLight, VolumetricCloud, ExponentialHeightFog + volumetric fog + second high haze layer,
    unbound PostProcessVolume (Lumen GI + reflections, histogram exposure range per preset, bloom, lens flare, vignette, fringe, filmic slope/toe/shoulder, grade, motion blur, AO),
    night star dome (`M_LookStars`), and a Level Sequence `LS_Look_<preset>` (auto-play, looping) that holds the `MPC_City` values (NightK, DnTime, InteriorGain, ShopGain, EmissiveScale)
    so a map is self-contained (the MPC asset itself is never edited). All numbers live in `Scripts/look_presets.json` (data, not code).
  - `/Game/Look/Look_Boxes`: 6683 invisible WorldStatic boxes from the export's `collision.json` (wall, glass, hero, spire, bulkhead, watertower) = the traversal's "building boxes".
  - `/Game/Tests/Look/Look_Midtown` (midday), `Look_Midtown_golden`, `Look_Midtown_night`: city geometry + Look_Boxes + rig + PlayerStart, `WebTravGameMode`
    (the P3 hero with the real HeroDev mesh runs through the city); and `Look_View_<preset>_<S1..S8>`: the P1 shot cameras under each preset (24 maps).
- **Traversal in the city works**: `-WHTravScript=tools/perf_ue/scripts/city_swing_avenue.json` gives a 30+ s swing chain up the avenue, 7067 boxes indexed, telemetry in `perf*/**/trav_telemetry.csv`.
- **Tools**: `run_perf.py` (3840x2160 real-gameplay perf, CSV profiler + WH_PERF, GPU util before/during, contamination flag), `sweep_views.sh`, `capture_looks.py` (stills, clips, NOTES.md),
  `make_perf_md.py`, `launch_editor.sh` + `job_server.py` + `uejob.py` (file job server for the P4 editor; run any .py in it), `rebuild_city.sh`, `rebuild_look.sh`.
- Evidence: `docs/night1/look/round-01/` (stills, 3 clips, NOTES.md neutral facts, PERF.md, perf run folders).

## Commands (from the worktree root; UE 5.8.3 at /Users/Shared/Epic Games/UE_5.8)
```
unreal/WebHomage/Scripts/build_editor.sh                   # C++ once (about 35 s), editor closed
tools/perf_ue/launch_editor.sh                             # only for the city import / interactive work (MCP 8774, job server)
tools/perf_ue/rebuild_city.sh                              # ~10 min; then: pkill -9 -f "$PWD/unreal/WebHomage/WebHomage.uproject"
"/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" $PWD/unreal/WebHomage/WebHomage.uproject \
  -run=pythonscript -script=$PWD/unreal/WebHomage/Scripts/build_traversal.py -unattended -nullrhi   # hero + Trav_Canyon, once (about 30 s)
tools/perf_ue/rebuild_look.sh [geo,rigs,maps] [midday,golden,night]   # headless, editor closed; geo must re-run after every city rebuild
tools/perf_ue/capture_looks.py --round docs/night1/look/round-NN --shot-times 12,20 --clips
tools/perf_ue/run_perf.py --out docs/night1/look/round-NN/perf_a --window 22:52 --wait-idle 60
tools/perf_ue/make_perf_md.py docs/night1/look/round-NN
```
Iterate on a look: edit `look_presets.json`, `rebuild_look.sh rigs <preset>` (about 20 s), `Scripts/run_game.sh <dir> -map /Game/Tests/Look/Look_View_<preset>_<S#> -res 1920x1080 -shots 14 -exec "r.ScreenPercentage 100"`.

## Gotchas
- **GPU contention makes frame times meaningless.** Device utilisation was 40 to 100 % from other agents' editors on every run; identical builds vary 2x. PERF.md flags it. Re-measure on an idle GPU (`run_perf.py --wait-idle`).
- `build_look.py` patches P1's `City_Midtown_Geo` in place (component object type WorldDynamic, ground actors tagged `WHGround`): the traversal indexes WorldStatic primitives by bounds as building boxes and one merged 256 m facade tile would be one giant solid.
  Re-run `geo` after `build_city.py`. Duplicating a map asset with `EditorAssetLibrary.duplicate_asset` leaves a leaked UWorld and crashes the next `load_map` (do not).
- MPC values are applied by a Level Sequence MPC track (`track.set_editor_property('mpc', ...)`, not `material_parameter_collection`). A stale unfinished `.py` in `_scratch/look/uejobs` re-runs when the editor restarts.
- Engine property names: `aerial_pespective_view_distance_scale` (engine typo), `enable_volumetric_fog`, `reflection_view_sample_count_scale_value`; `rayleigh_scattering_scale` default is 0.0331 (1.0 turns the sky orange).
- Headless `-nullrhi` builds the maps and the sequence fine; shaders compile at first game run (first run of a new map is slow, later ones use the project DDC).
- `run_game.sh -movie` dumps to `Saved/Screenshots/MacEditor` (shared by every run of this worktree): never run two movie runs at once.
- Commit only mp4/jpg/json/md: content, DDC and Intermediate stay out (`unreal/WebHomage/{DerivedDataCache,Intermediate}` are deleted at the end of a session).
- Console-variable overrides that are not in `DefaultEngine.ini` (integrator-owned) go through `run_game.sh -exec "cvar value,..."`.

## Open issues / next gaps (no self-assessment of quality; these are known facts)
1. **60 fps at 4K is not reached in any measured config** (see PERF.md); ranking of GPU costs: LumenScreenProbeGather, ShadowDepths (VSM), Basepass (facade material), Nanite passes, post (lens flare, motion blur). The heaviest view is S2 (42 m over the avenue).
   Untested hypotheses: lower `lumen_final_gather_quality`, screen-probe downsample, VSM cache, cheaper facade far LOD; measure only on an idle GPU.
2. The far ring (river, opposite shore) is a blown-out white/violet band in every preset, independent of the lights (P1 far LOD / hinterland material).
3. Tree leaves render grey and blow out on sun-facing faces (P1 `M_CityLeaves`).
4. Night: no street-lamp pools (`lampPool` prototypes are skipped by the city build), so street level is dark; stars are a simple procedural dome; no wet asphalt or rain.
5. No depth of field, no lens dirt, no sun shafts other than volumetric fog; cloud layer shows banding at low sample counts.
6. Presets are a fixed set of three; a runtime time-of-day blend (one rig, animated sun + MPC) is not built.
