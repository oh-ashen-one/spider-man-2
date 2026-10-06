# M5 Spider-Man showcase — rolling handoff (started 2026-10-06)

Owner direction: a polished 4K Manhattan swinging showcase. Night look = the original author's newer night mode (~/spiderbench @ 64d957f9), translated into Unreal. Full island is the target. Launches/tests are owner-authorized under the shared GPU rules (2026-10-06 prompt supersedes "keep closed").

## Branch / state
- Task branch: `codex/m5-showcase-20261006` (pushed to origin), based on migration 4e768e78.
- M1 code is committed at 67a835e4. It covers the build pipeline repair, strict builders, render profiles and launchers. Content builds have NOT completed yet: they are queued on the shared GPU coordinator (see Blockers).
- Baseline preserved: read-only APFS clone at `~/sm2-baselines/r5b-preview-4e768e78/` (Content: 1843 files / 1,366,398,226 bytes, matches the source). Launch it with `tools/showcase/play.py --map baseline --launch`, which runs from a disposable clone under Saved/Showcase/baseline-run. The original `tools/owner_preview/*` is unchanged.

## Milestone 1 (pipeline) — what changed
- `Scripts/build_manhattan.py` steps: cpp, city_export, city_prep, city_extra, city, traversal, characters (now incl. `skins` → DA_HeroSuits), look (now incl. `night`), water, life, map, terrain (/Game/Terrain only; /Game/TerrainR5b refused), showcase, validate.
- Showcase maps: `/Game/Showcase/Maps/Manhattan_Showcase` (golden), `_Midday` and `_Night`. Each composes City_Geo_T, Look_Boxes, Look_Rig_<preset>, Manhattan_Actors, Terrain_Land, Water_River and Life_Actors. Only the Night map also gets `sm2_common.NIGHT_LIGHTS_LEVEL`, the single swap point for the night-light system.
- Strict mode (`SM2_STRICT=1`, `Scripts/sm2_common.py`): each builder prints `SM2_BUILD_OK: <script>` or `SM2_BUILD_FAILED`. The orchestrator fails on a nonzero rc, Python errors or a missing sentinel.
- Commandlets run through `tools/gpu/gpu_slot.sh capture` with `GPU_SLOT_DIR=~/.cache/gpu-slot`. They refuse to start on PAUSED or a stuck-exiting engine, and stop their own child with SIGTERM, then 60 s, then SIGKILL.
- Render profiles: `-WHProfile=fidelity` (Cinematic, 100%, 3840x2160) and `-WHProfile=playable` (Cinematic, TSR, `-WHResScale`, default 67). Profile runs never persist to saved settings. The game logs `WH_RES profile= output= internal= aa= quality=` 3 s after load.
- `tools/showcase/check.py` is an offline asset check. `tools/showcase/play.py` is a guarded launcher (`--map showcase|showcase-midday|showcase-night|baseline --profile ... --max-fps 0 [--launch]`) with an unattended `--capture` mode.

## Milestone 2 (night port) — design in progress
- Author's system: about 2k clustered local lights (street lamps, shop-front rects, lit-window rects near the camera, neon point and strip lights, screen tiles coloured by ad region, blade signs, signal lenses, headlights and taillights, skyline and crown floods). It also has lit haze in-scatter, emissive bounce, a reduced night sky fill on the suit plus "area ambient", and a night exposure of x4.5.
- Unreal plan:
  - Export the author's data from the pinned spiderbench with `tools/night/export_night.mjs` (layout.js is identical to our fork, so coordinates align; to be verified by `tools/night/check_alignment.py`).
  - A C++ city-lights actor that activates unshadowed local lights around the camera with per-category caps, plus a few shadow slots near the hero.
  - Volumetric fog scattering per light, Lumen for bounce, neon and word instanced meshes, a screen emissive night boost, and the facade window model regenerated from the author's facade.js.
  - This replaces the old Look_NightLights in the Night map, so the two systems never stack.

### M2 part 1 (built, no runtime yet)
- `tools/night/prep_night.py` packs `night_lights.json` into `Content/Night/CityLights.bin` (+ meta, `NightGeometry.json`); `Scripts/night_city.json` is the tuning copied to `Content/Night/CityLights.json` (`wh.CityLights.Reload`).
- `AWHCityLights` (Source/WebHomage/Look/WHCityLights.*) streams a budgeted light pool around the camera, ports the author's area ambient into `AWHLookHeroLight`, and exposes `UWHCityLightsLibrary::SelfTest`.
- `build_look.py` step `night` builds `/Game/Look/Look_NightCity` (replaces `Look_NightLights`, kept as `build_night_legacy`): `AWHCityLights`, hero lights, 6 emissive HISMs. `sm2_common.NIGHT_LIGHTS_LEVEL` points at it; the showcase night map composes it.
- Verified headless: look/showcase/validate rc 0, validate.json 120/120 (SelfTest at 3 positions, HISM counts, one AWHCityLights). Shader compile, lights and emissive look are NOT verified (null RHI).

### M2 part 2 / M3 kickoff
- Offline shader check: `python3 tools/night/hlsl_check.py` (UE's libdxcompiler via ctypes) compiles the 6 City .ush files and every Custom-node body (build_city `custom_nodes()`, build_look `night_custom_nodes()`): 31/31 compile.
- `Facade.ush` now comes from the author's facade.js (night windows, shop interiors, crown floods baked from the export); `--facade-src=fork` regenerates the old one. `node tools/export/facade_hash_parity.mjs`: nhu/nh3/nh01 JS vs HLSL, 0 mismatches. Day (NightK 0) paths are unchanged.
- `AWHCityLights::RegisterDynamicProvider`; `AWHLifeTraffic` emits the author's headlight/taillight pairs into the `cars` group (night_city.json `cars_provider`). Not exercised at runtime yet.
- Island (worktree ~/sm2-n1/island, branch codex/m5-island-20261006): city content resumed on M5 (kit, fsky/map/coll, wp) in 681 s total; WP map saved (1642 meshes, 198,063 instances, 175,671 WHBox cubes). Traversal/characters/look/map steps of the island are not run.

## Blockers (live)
- 14:33: both shared capture slots are held by a foreign task: pid 17065 `m5-flash-next-resident`, reserved_slots [0,1]. Earlier, pid 34549 `chicago-loop-unity-play` held them. A foreign UnrealEditor (pid 9864) and Blender (3196) are also running, which is 2 renderer-bearing engines, the global cap. No game/renderer launch is possible without exceeding the cap. Our M1 commandlets are queued FIFO in gpu_slot (wait timeout 3 h). Foreign processes are not touched.

## Not yet verified
No runtime, visual, suit-switch, traversal, resolution or FPS result is claimed yet. The baseline has not been opened, because of the GPU blocker.
