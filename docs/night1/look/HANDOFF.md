# P4 Look, lighting, post, perf: handoff (round 02)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Branch `night1/look`, worktree `~/sm2-n1/look`, UE MCP 8774, dev port 5205. Owns `/Game/Look`, `/Game/Tests/Look`, `tools/perf_ue/`, `Scripts/build_look.py`, `Scripts/look_presets.json`,
`Scripts/look_ts_screens.json`, `Source/WebHomage/Look/` (new in round 02), `docs/night1/look/`. Nothing in `Content/` is committed: scripts rebuild everything.
Numbers of the round: `round-02/NOTES.md` (capture facts + test numbers), `round-02/TESTS.md` (spec table), `round-02/PERF.md`. Targets: `docs/night1/look/SPEC.md` (LOOK-SPEC L1..L20).

## State (end of round 02)
- Round-01 critic (`round-01/CRITIC.md`): FAILS, biggest gap = night street lighting and exposure. Round 02 is that gap plus the golden numbers of the new spec. Merged `Opus-5.5-Loop-Night-1` at the start
  (P1 city round 4: new facade emission, signage, leaves, props; C++ traversal / characters). The city was re-exported and re-imported (`rebuild_city.sh`: 29 min in an editor without DDC).
  midday / golden differ from round 01 mostly because of that city update, not because of look settings.
- **Night** (`look_presets.json` presets.night, `build_look.py` step `night` -> `/Game/Look/Look_NightLights`, an always-loaded sublevel of the night maps):
  - fixed exposure EV 3.7 (min = max), cooler white balance (6100 K), contrast 1.35, `color_offset` black lift (0.004 / 0.005 / 0.009), lens flare 0.25, bloom 0.85; moon 30 lux; sky light 5 (tint 0.75 / 0.85 / 1.0);
    four unshadowed low-elevation horizon "city glow" directional fills (`fills`; they light facades by cos(incidence) but streets only by sin(8 deg), so the road pools stay distinct).
  - 634 street lamps (layout.json `instances.lamp`, the browser's own positions, head = base + 2.9 m arm, 9.15 m up): spot pool (7000 cd, 46 deg outer) + small halo point light + emissive head,
    temperatures 3500 / 4300 / 5500 K, volumetric scattering on.
  - about 900 storefront spot lights on the street-facing ground-floor faces of the footprints (sidewalk spill), 160 coloured spot lights in front of the Times-Square-like LED screens
    (`look_ts_screens.json`, positions from `tools/perf_ue/extract_ts_screens.py`; the screens' own ad content is IP-excluded, their emission is black, so this restores the district's colour spill),
  - STAND-IN TRAFFIC (P6 owns real traffic): about 1300 box-and-cylinder car proxies in the avenue / street lanes (NoCollision, no livery / brand, generic paint palette), head lights (spot on the road) and tail lights (red point),
    emissive light bars. Replace with P6's vehicles when they exist; keep the light setup (`lights.cars`).
  - damp streets: one big deferred decal (`M_LookWet`, roads + sidewalks by reconstructed normal, world-noise puddles) so pools and lights read as reflections.
  - `AWHLookHeroLight` (C++, `Source/WebHomage/Look`, placed in the night level): rim + fill + top light that follow the player's pawn on lighting channel 1 only (the pawn's meshes are on 0 + 1),
    so the hero stays readable in dark canyons without lighting the world.
- **Golden** retuned to the spec (L1 / L5 / L6): sun 9 deg elevation, az 238 (behind the buildings at the end of the avenue views), 4200 K, warm sky-light tint, white balance 7300 K, lens flare 0 (no sourceless ghost),
  three low fills, colour offset black lift, exposure bias 0.95, less aerial haze (distance scale 3), Mie 0.01. **Midday unchanged** (`look_presets.json` midday block untouched).
- **Tools** (all under `tools/perf_ue/`): `night_tests.py` (round-1 critic tests: mean luma / share < 10, pools in the bottom third, hero pixel-box luma per frame from the P3 hero-only depth mask),
  `look_lum_check.py` (LOOK-SPEC L1..L8, L13, L14 numbers per still), `extract_ts_screens.py`, `ensure_boxes.py`, `capture_looks.py` (now: GPU slot, shader warm-up render, 0.8 s pre-roll trimmed, hero-luma test,
  tests of night S1 / S6), `run_perf.py` (GPU lock `perf`, sidecar `perf_gpu.json`), `launch_editor.sh` (`-RenderOffScreen -NoSound`, waits while 3+ editors run).

## Commands (from the worktree root; UE 5.8.3 at /Users/Shared/Epic Games/UE_5.8; scratch root env `SM2_LOOK_SCRATCH`, default `/Users/midir/sm2-n1/_scratch/look`)
```
unreal/WebHomage/Scripts/build_editor.sh                      # C++ (Traversal, Characters, Look), editor closed
tools/perf_ue/launch_editor.sh                                # only for the city import / interactive work (MCP 8774 or $SM2_LOOK_MCP_PORT, job server); pkill -9 -f "$PWD/unreal/WebHomage/WebHomage.uproject"
tools/perf_ue/rebuild_city.sh                                 # export + import (10-30 min) and, automatically, the box / look rebuild below
tools/perf_ue/rebuild_look.sh [geo,rigs,night,maps] [midday,golden,night]     # headless, editor closed (about 1 min for everything)
tools/perf_ue/ensure_boxes.py [--check]                       # re-runs `geo` when the traversal boxes are older than the city geometry level
tools/perf_ue/capture_looks.py --round docs/night1/look/round-NN --clips  # stills S1..S8 x presets x 4K/1080p + 3 swing clips; GPU slot 'capture'
tools/perf_ue/run_perf.py --out <dir> --map /Game/Tests/Look/Look_Midtown_night --configs tsr50 --fixed-step     # GPU lock 'perf' (exclusive), sidecar perf_gpu.json
tools/perf_ue/look_lum_check.py --dir docs/night1/look/round-NN/stills     # spec table
tools/perf_ue/night_tests.py all --still <night_S1.png> [--clip-frames <dir> --csv <telemetry.csv> --skip N]
```
Iterate on a look: edit `look_presets.json`, `rebuild_look.sh rigs <preset>` (rig) or `night night` (night level; about 20 s), then
`/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label look -- unreal/WebHomage/Scripts/run_game.sh <dir> -map /Game/Tests/Look/Look_View_<preset>_<S#> -res 1920x1080 -shots 14,20 -exec "r.ScreenPercentage 100"`.

## Dependencies and gotchas
- **Traversal boxes depend on the city build.** `build_look.py` step `geo` patches P1's `City_Midtown_Geo` in place (every component WorldDynamic, ground actors tagged `WHGround`) and rebuilds `/Game/Look/Look_Boxes`
  (6683 invisible WorldStatic boxes from `collision.json`: the hero's building boxes; log check `WebTravWorld: N building boxes indexed`, 7067 expected). It MUST re-run after every `build_city.py`.
  Automated now: `rebuild_city.sh` ends by closing the editor and running `rebuild_look.sh geo,rigs,night,maps`; `capture_looks.py` and `run_perf.py` call `ensure_boxes.py` first (mtime check, re-runs `geo` when stale).
  Any other builder that rebuilds the city (integrated map, `Scripts/build_city.py`) has to run `tools/perf_ue/rebuild_look.sh geo` (or `ensure_boxes.py`) afterwards.
- Scratch is one root, `SM2_LOOK_SCRATCH` (default `/Users/midir/sm2-n1/_scratch/look`): city export (`export/midtown3x3`, `collision.json` and `layout.json` are what `build_look.py` reads; override with `SM2_CITY_EXPORT`),
  job dir, capture frames. `SM2_LOOK_WORKTREE` (default `/Users/midir/sm2-n1/look`) is only the fallback for `build_look.py` when `__file__` is unset. Dev port `SM2_LOOK_DEV_PORT`, MCP port `SM2_LOOK_MCP_PORT`.
- **`unreal.Color(...)` positional order is (B, G, R, A)**: use keyword arguments (`unreal.Color(r=, g=, b=, a=)`). The atmosphere `ground_albedo` (and `fix_type`) still use the positional form: midday / golden values are kept exactly as
  round 01 (R and B swapped, near-grey), night's is nearly grey too. Do not "fix" it without recapturing midday / golden.
- Post: `color_offset` is a black lift (pre-tonemap, works as a floor), `color_contrast` above 1 pivots around mid grey and darkens the road valleys (this is what separates the light pools).
  `white_temp` above 6500 warms the image, below cools it. Fog inscattering luminance values are physical (cd/m2) and invisible at daylight EV: the visible haze is the SkyAtmosphere aerial perspective.
- Lighting channels: the hero lights only work because `AWHLookHeroLight` sets the pawn's skeletal / static meshes to channels 0 + 1 at runtime; do not replace the hero pawn class without keeping that.
- `Light max_draw_distance` is what keeps 4000+ unshadowed lights affordable (lamps 200 m, halo 80 m, storefront 80 m, car heads 80 m, tails 45 m, screens 300 m).
- A deferred decal's `decal_blend_mode` property is deprecated in 5.8 (`translucent` is the default; the build logs a note, not an error).
- GPU: every capture goes through `gpu_slot.sh capture` (max 2 at once, others wait), every perf run through `gpu_slot.sh perf` (exclusive, waits for < 15 % for 10 s). A perf number not taken that way is contaminated.
- Headless `-nullrhi` builds the maps fine; shaders compile at the first game run (the first run after a DDC delete is slow). The first `-game` run of a map after `night` rebuilt is not slower than later ones (project DDC).
- Commit only mp4 / jpg / json / md: content, DDC and Intermediate stay out (`unreal/WebHomage/{DerivedDataCache,Intermediate}` are deleted at the end of a session).

## Open issues / next gap (facts, not self-assessment)
1. Perf: 60 fps at 4K is not reached (see `round-02/PERF.md`; the perf piece F profiles the integrated map and will send exact lighting changes). Night adds a `Lights` pass of roughly 5 ms GPU at TSR 50 %.
2. Night stand-in cars are boxes; the LED screens of the Times-Square-like district are black (IP exclusion); the far ring (river, opposite shore) is still a blown white / violet band in every preset (P1 far LOD).
3. Numbers not met (see `round-02/TESTS.md`): night S6 bottom-third p90 (spec L14) and golden S3 mean, golden S7 clipped share (sun-facing view).
4. From the integrated-map measurements (orchestrator note): S2 sunlit stone tower has 30.7 % of pixels above Y204 (spec C1/C2 <= 1.5 %), S1 shadowed tower too dark (mean 20, target 52), the river reads 13.5 luma brighter than
   the far shore (C14: needs distance-dependent haze or lower sky exposure), sky blown (Y 229) under the city test maps' manual exposure. These are Look items for the next round.
5. No depth of field, no lens dirt, no sun shafts other than volumetric fog; cloud layer banding at low sample counts; no runtime time-of-day blend (three fixed presets).
