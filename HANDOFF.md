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

### Runtime fixes (first captures)
- Night daylight: no lighting actor leaks into the composed maps (validated per map: exactly one atmosphere sun / SkyLight / SkyAtmosphere / height fog, the rig PPV the only unbound one, everything from the rig level). The cause was the night rig's auto-exposure range (min_ev 1.0, max_ev 4.3) against the 16 lux moon key: 16 lux x albedo / pi = 2-4 cd/m2 against a white point of 2.4 cd/m2 at EV 1 saturates the scene to a daytime-grey image. Night exposure is now [6.5, 8.5] (first pass, to be tuned by the owner's look judgement).
- Custom-node texture samples use Texture2DSample() (never Tex.Sample): the ray-tracing hit shader (lib_6_6 closesthit) rejects the implicit-derivative Sample opcode. tools/night/hlsl_check.py compiles every body for ps_6_6 and as a closesthit lib; 98/98.
- The terrain step runs tools/terrain/prep_terrain.py (Shaders/Terrain/ParkData.ush is generated and gitignored); check.py verifies every `#include "/Project/..."`. Pre-existing baseline defect: ~/sm2-baselines lacks ParkData.ush (baseline terrain materials fail to compile); play.py copies this checkout's file into Saved/Showcase/baseline-run only.
- WH_RES logs 3 s after map start in every mode; -WHProfile also applies its render settings in captures (window untouched). Cold-DDC captures stall the game thread for seconds on BC7 texture builds (ts_ads, props atlas, TA_walls): warm the DDC before perf windows.
- A handled DoubleFloat ensure (distance-field object matrix precision) appears in baseline, golden and night logs: pre-existing.

### Night rig in the author's units (K = 200)
- look_presets.json night.units: K, display exposure 3.6, EV100 = log2(K / (1.2 x 3.6)) = 5.533 -> auto exposure [4.8, 6.3], bias 0; moon 83.5 lux (0.4577, 0.6217, 1.0) as the one atmosphere light (browser el 36 / az 15), no Sun, no fills, no colour_offset; fog from derive_fog() (density 0.00511, falloff 0.0481, start 217 m: T(300 m) 0.9585, T(2 km) 0.4021); fog in-scatter NH.low x K; MPC EmissiveScale = K, InteriorGain 2.5, ShopGain 1.05. Sky calibrated on view_skyline_high / view_waterfront: SkyAtmosphere default Rayleigh, sky_luminance_factor 0.06, SkyLight 3.0.
- Matched cameras: `tools/showcase/gen_shot_cams.py` -> shot_cams.json; `play.py --capture DIR --shot-cams FILE --name night`; `tools/showcase/pairs.py DIR` writes pair_<shot>.png + pairs.json; `tools/showcase/skyprobe.py`; `cal_iter.sh` = one calibration iteration. `play.py --exec "cvar"` adds console commands to a capture.
- Traversal hero fill fades with (1 - NightK). Open: the matched street shot's asphalt is still ~5x the reference (GI off: 2.6x, lamps off: not lower), see the lead report.

### Night calibration round 2 (fixed exposure EV 5.53)
- Cause of the flat bright night: the SkyAtmosphere aerial perspective (aerial_perspective_distance_scale 5.0 of the old rig) added ~0.5 display units to every far pixel, and day-tuned emissive fills ran at K units (terrain foliage fill 650 cd/m2 x albedo; city screens at the day constant 2.0 instead of K x screenK). AP scale is now 0.05, foliage fill x (1 - NightK), M_CityVC / M_CitySignage use MPC ScreenNightGain (= K x 0.1), M_CityFarMass windows use FarWinGain (0.14).
- Night has no VolumetricCloud actor; sky hue via sky_luminance_factor (0.0342, 0.0432, 0.0962). units.auto_range = 0 (fixed exposure); +-0.75 tested: lifts dark views, over-brightens bright ones (see the report).
- Boards: `tools/night/board_check.py --write` (run by the look step) keeps only boards inside the detailed midtown region, projects floating / buried ones onto our facade planes within 3 m, drops the rest (2526 -> 458).
- Tools: `tools/showcase/{cap_run.sh,table.py,skyprobe.py,pairs.py}`; `build_manhattan.py` accepts SM2_CITY_ONLY=mat and SM2_TERRAIN_ONLY=mat.

### Night calibration round 3
- Root cause of the "sky calibration" so far: AWHLifeCrowd's NewObject directional CrowdFill (1800 lux) was an atmosphere sun light (index 0) and outranked the 83 lux moon: it lit the sky, and the AP, of the night rig. It is now not an atmosphere light and fades with (1 - NightK) (Look/WHNightK.h). The night sky factor was recalibrated on the real moon (sky_luminance_factor 1.6/1.4/1.55).
- Emissive screens: M_CityVC emits the three.js emissive (EmisColor x EmisI instance params, base colour is a dark 0.023) x map at night with the author's screen shading (ScreenK 0.1, ScrBoost 2, shoulder 0.28 -> 0.46) x K x ScrCal; M_CitySignage K3/K4 likewise. Painted markings use MarkNightK, canopies LeafNightK, far windows the author's farshore.js 1.4 + 0.15 albedo.
- `-WHShotCam` entries may carry hero_pos_m / hero_yaw_deg (tools/night/ref_players.mjs -> gen_shot_cams.py): the hero is teleported there and held. `tools/showcase/with_holder.sh` waits for the approved Qwen resident to be the only holder (it re-registers under new pids); `regions.py` measures boards / leaves / lit windows on masks picked in the reference.

### Night calibration round 4 + route perf
- Author's night city ambient (render/surface.js:171-193) ported as CityNightAmb in Shaders/City/ShadeFill.ush (Facade, Detail, Roof, Asphalt, Sidewalk): it is zero within ~220 m of the camera by the author's design (the local light grid replaces it), so it only changes far views; Times Square's screen-colour field is included. NightAmbK (MPC 0.04) adds the author's unoccluded night sky fill for canyon facades (Lumen's SkyLight is occluded there).
- Route runs: `tools/showcase/route_run.sh <name> <map> <profile> [--res-scale N]` (warm-up route, shots every 3 s, perf 15:45), `perf_report.py` (frames.csv stats, telemetry summary, contact sheet). The 4K screenshot frames hitch ~1 s each: use the `excluding_screenshot_hitches` block.
- `tools/showcase/with_holder.sh` waits for the approved Qwen resident; `build_manhattan.py --steps ray|probe` (SM2_RAYS / SM2_PROBE) trace the night map (only the invisible WHBox collision is hit).

### M3a: the island in the main project
- Checkpoint of the midtown night showcase (Content / Shaders / Config, APFS clone, read-only): `~/sm2-baselines/m2-midtown-night-9c368f39/` (BASELINE.json). The merge of codex/m5-island-20261006 keeps our strict sentinels / gpu_slot-always / showcase steps and all island steps; `build_manhattan.py --steps city` with SM2_CITY_ONLY=mat on the island env (SM2_MANHATTAN_SCR=~/sm2-n1/_scratch/island SM2_ISLAND_REGION=island SM2_CITY_SCRATCH/EXPORT/TEX) rebuilds only the materials. A pass with steps containing wp / clean / kit / mesh drops the WP map files first; a mat-only pass must not (fixed after it deleted them once).
- MPC_City.uasset must stay the main project's (parameter GUIDs: the Night / terrain / life materials reference it); island content copies must not overwrite it.
- Island maps: `--steps island` (duplicates /Game/Maps/Manhattan_WP ~4 min first, ~1.5 min each next + one non-spatial ALevelInstance per level, LevelStreaming, + a non-spatial PlayerStart), `--steps islandvalidate` (35 checks), play.py `--map island|island-midday|island-night`. WHIslandRules (C++) hides the city actors the terrain supersedes as WP cells stream in. FWebTravWorld::AddLevel / RemoveLevel index and drop the solids of streamed levels (per-level ownership, tombstoned box indices, anchors inside a removed level are released).
- `SM2_BOARD_EXPORT` selects the layout board_check projects against; `SM2_LOOK_ONLY=rigs,night` builds the night level without the midtown geo.

### Perf milestone A (2026-10-08, commits 64cfe7f4 / 6521a1e6 / 458836db)
- `build_manhattan.py --steps ddc` fills the DDC for the island maps (one-time, 337 s): island night route frames > 500 ms 9 -> 0.
- Playable profile applies `Config/PerfPlayable.cvars` (17 cvars); opt-in `Config/PerfPlayableFast.cvars` (+ Lumen screen-probe downsample 24) via `-WHPerfPreset=<path>`. Fixed-step island night at 4K output: preset off 58 % p50 34.3 ms; preset on 27.0 ms; Fast + island life 17.5 ms (58 %), 15.9 ms (50 %). Fixed-step only; no real-time route measured. Owner played 1080x608 window with Fast at 100 %: ~64-67 fps standing (log frame counts).
- Island-wide life data (Scripts/life_data_island), traffic `ActiveRadiusM` 900 m.
- Max (fidelity) in the owner window ran ~20 fps standing, ~10 fps swinging: game-thread "waiting on static mesh being ready" stalls when WP cells stream in remain (open).
- 16d24911: F in the air picks from 12 flip programs by stick direction (`WebFlips::ChooseForInput`).

## Final refinement loop (owner brief 2026-10-08, ACTIVE)
- Scope: swing / air / flips / web deployment only, plus the supplied-GLB integration exception. Contract `docs/night1/final/OWNERSHIP.md`, spec `docs/night1/final/SPEC_FINAL.md` (W1-W10, A1-A7 + carried traversal/flip specs). Loop = the claude-code-game-builder Gauntlet Loop (policy copy: `~/Documents/Documents - Midir’s Mac Studio/Codex/m5-unreal-setup-20261006/policy/claude-code-game-builder/`): builder captures scripted native `-game` clips → orchestrator packs blind A/B (`tools/night1/abpack.py`) → fresh blind critic (prompt `~/sm2-n1/_scratch/final/CRITIC_PROMPT_SW.md`) → 2-3 gaps → builder fixes.
- BEFORE checkpoint: tag `final-before` = 16d24911. Round folders `docs/night1/final/swing/round-NN/`; critic scratch `~/sm2-n1/_scratch/final/critic-rNN/`.
- Supplied GLBs (read-only): `~/Documents/SpiderMan_Asset_Import_M3_2026-10-08_task-4/GLBs/` (56, hashes verified by the owner's transfer). Orchestrator inspection: the 11 human GLBs are unrigged A-pose civilians in everyday clothing; none is a Spider-Man suit, so no supplied suit is integrated (blocker reported to the owner). Previews `~/sm2-n1/_scratch/assets_m3/humans_{front,side}.jpg`. Props plan: `docs/night1/final/assets/PLAN.md` (builder PA).

### Loop log (resumed 2026-10-10 by a Kimi K3 session with subagents; owner-authorized overnight run)
- Critic scores (deploy / web read / swing body / flips / air / camera): r00 2/5/3/4/3/3, r01 3/5/3/4/3/3, r02 4/6/4/3/3/2, r03 4/5/4/6/4/4; all FAILS. **r04 7/7/6/5/6/5 → APPROACHES TARGET** (first non-FAILS; blind critic, verdict `docs/night1/final/swing/round-04/CRITIC.md`; pack `~/sm2-n1/_scratch/final/pack_r04` via restored `abpack_norm.py`, paths now `/Users/midir/`).
- r04 top gaps for round 05: (1) trick rotations/holds — 0-1 rotations per release vs owner's 2-3; add fast tuck 450-750 °/s + held open shape ≥0.3 s + catch ≤0.25 s after last shape; (2) camera occlusion — hero fully hidden behind a rooftop ~0.8 s in s1/s5 at t≈10.4-11.4 (orchestrator-verified on frames); no >0.25 s occluded window; (3) stiff swing poses — arms-up V + 4 s micro-rocking hang s2 t=8-12; leg lag + knee drive, cap hangs ~1.5 s.
- **r05 (build d5198769, clips 72bdeb95) judged blind → FAILS 6/7/6/6/5/5** (verdict `docs/night1/final/swing/round-05/CRITIC.md`). Fixed vs r04: occlusion gone (0 frames >0.5 s hidden, orchestrator-verified on s1 t=10.2/10.9), doubles/triples lead the trick pools (s3 frontDouble 2.20 rotations), catch delay 0.70→0.00 s, hang cap works (s2 stall gone per checker), P1 improved on all clips. Orchestrator verification of r05 critic claims: "s4 hero 5-10 % of frame at t=7.0" mis-measured (actual ~0.22); "strand vanishes in one frame at s4 t≈1.72" mis-timed (strand visible at t=1.717 and 1.783) — core gaps stand anyway.
- r05 → round 06 gaps: (1) camera distance on floats/long air (s4 in-band 62 %; hero dips below the P1 band mid-float; chase cam 3-6 m, hero ≥0.25 frame height on ≥95 % of swing frames); (2) flip rotation count per long release (owner 1080°/2.8 s ≈ 385 °/s mean; ours ~2.2 rotations best; trim near-frozen mid-trick holds ≤0.4-0.5 s; F1/F2/F5); (3) s2 static plumb-bob dangle (critic r05: s2 t=10.4-12.8 dangles >2 s despite the hang cap — cap did not fire; investigate threshold). Watch small-sample regressions: s3b W3 6/7, s4 W3 7/8, s3b/s4 A1 borderline; A5 chest-rate (400-700 °/s lead-in turn) and F8 upright clause still fail; flip_check rendered peaks >800 °/s on 3 programs (shape-transition lean stacking).
- Rounds 00-02 were captured in the Cinder suit (the owner's saved GameUserSettings HeroSuit=3); r03+ force `-WHSuit=tessera`.
- Supplied props: `/Game/PropsM3/Maps/PropsM3_Island` composed into the 3 island maps (1e11bab5), 1,600 instances, no collision.
- Open: trick-camera hero size (P1) misses the 90 % band (pose-dependent extent; s1/s5 regressed 95 -> 88 % in r04; critic r04 also saw hero 0.11-0.15 of frame in s3b 22.0-23.2), W2/W3/W9/W10 on s2 cases, W5 by day, A5 catch timing, F11, s3 flow web-on ~38 %.
- Machine note (2026-10-10): workspace restored on the M5 at `/Users/midir/` from the M5 backup (`~/Documents/Codex/2026-10-09/task-2/M5-backup-2026-10-09`); scratch `~/sm2-n1/_scratch/final/` + refs `~/spiderman-learnings/` live again. Loop runs on Kimi subagents (coder/explore), one at a time; critic blindness = fresh zero-context spawn.

## Blockers (live)
- No supplied Spider-Man suit exists among the 56 GLBs (see above).
- Island streaming stalls in live play (see Perf milestone A).
