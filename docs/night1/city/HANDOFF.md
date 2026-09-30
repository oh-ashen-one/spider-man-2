# P1 City — handoff after round 07 (for the next builder)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Branch `night1/city`, worktree `/Users/midir/sm2-n1/city`. UE MCP port 8771 (editor not needed any more), browser dev port **5202**.
Owned: `tools/export/`, `/Game/City`, `/Game/Tests/City`, `docs/night1/city/`, plus (flagged to the integrator)
`unreal/WebHomage/Shaders/City/` and `unreal/WebHomage/Scripts/{build_city.py,city_shots.json}`.
Content/ is NOT committed (public fork, no LFS): everything is rebuilt by scripts from the browser city.

## Read this first: state at the end of round 07 (finished by Sonnet 5.5 on 2026-09-30 after the 23:08 kernel panic)
Critic r06: facades 5, street 4, skyline 4, Manhattan 5, image quality 5, FAILS. Its gaps: (1) far field C11/C13-C15, (2) parked cars / props C4/C6, (3) facade albedo C1.
**Round 07 fixed (1) and (3) by measurement, not (2).** Numbers, before / after, sweep table and change log: `round-07/README.md`; raw checker output: `round-07/city_spec_check.md` + `.json`
(`python3 tools/export/city_spec_check.py <round_dir> [--yolo] [--ip]`, regions `docs/night1/city/spec_regions.json`, ONE measurement for builder and critic).
| line | r06 | r07 final (1080p / 4K) | target |
|---|---|---|---|
| C11 far-shore Laplacian / sky | 4.76 | 27.3 / 23.4 | >= 6 |
| C13 far-shore Y - sky Y | -14.0 | -33.7 / -33.9 | -35..-25 |
| C14 far shore - river | -3.4 | +23.5 | 5..35 |
| C15 RMS far / near | 0.08 | 0.257 / 0.258 | >= 0.25 |
| C1 facade crops pass | 10/18 | 17/18 / 17/18 | 18/18 |
| C2 facade crops pass | 9/18 | 10/18 / 10/18 | 18/18 |
| C4 / C6 cars, people (YOLO) | 0 / 0 | 0 / 0 (S1, S2, S6) | 5-19 cars, 14-22 vehicles |
IP OCR: 0 hits. Captures: `round-07/S1..S8_*_{1920x1080,3840x2160}.jpg`, internal resolution 1399x787 / 1920x1080 (TSR), frame times contaminated (shared GPU, see README).
Critic pack for r07: `/Users/midir/sm2-n1/_scratch/critic-P1-r07/pack` (key outside the pack: `pack.key.json`).

### Ranked to-do for round 08 (each item = one rerun of the checker)
1. **C4 / C6 empty streets** (critic gap 2, unchanged since r06, and the loudest thing in S1 / S2 / S6 now): the browser has `src/world/vehicles.js`, `vehinst.js`, `npc/traffic.js`; the export has no vehicle protos. Either export a parked-car prototype set
   (yellow taxis + ~6 body types, no livery IP: see `IP_EXCLUSIONS.md`, `vehicles_atlas2.webp` liveries are excluded) and place 5-19 at the S1 curbs / 14-22 along the S2 avenue (P1 owns parked cars per SPEC), or coordinate with P6 (`/Game/Life`) and have the integrated map carry them.
   S1 also lacks street trees on the left and any crowd (P6).
2. **C2 crush (S1 / S6 / S7, lighting):** sun 6 vs sky fill 1.7 at +2 EV is ~30:1; the SunK cap fixed C1 but darkened canyon-shadowed sun-facing walls (S1 left stone 33.5 -> 23.8). The material cannot see shadows.
   P4 fix: a sun / sky-fill ratio near 4:1 (and a gentler exposure); then `SunK -> 1` (MPC, no recompile) and re-run the checker. If P4 re-lights the maps, ALSO re-run the far-field check: the C13 / C15 window is only ~0.01 wide (below).
3. `s5_grey_tower` C1 (3.7 % > Y 204 = lit interior windows in daylight): `DayEmisK` 0.22 -> ~0.16 (MPC) but it dims S7's lit windows too; test S5 + S7 + S8 together.
4. S3 foreground is near black (lighting), roof plane sparse; S5 red steps are flat pink; Times Square tree guards hold no trees; C3 window depth is judged, not measured.
5. Far field is at the edge of its window because the sky is blown (Y 229): C13 margin 1.3 Y, C15 margin 0.007. Lowering the sky band ~10 Y (P4) widens it; fog / FarGain / FarJit are then free.

### What round 07 changed, root causes (details in round-07/README.md)
- **CITY-SPEC measured once**: `spec_regions.json` (hand-placed boxes, 1080p + 4K per line), `city_spec_check.py` (texture statistics on the 1080p-normalised frame, mean-type statistics on the native frame; `--overlay <dir>` draws the boxes). r06's builder / critic disagreement was different boxes.
- **`M_CityFarMass` never compiled in r06** (`vc.a` on an RGB-only custom-node input): every far-shore block of r03-r06 was the default grey material. New input kind `vca` in `make_material`. Then: per-24 m tone jitter `FarJit` (1.3), floor banding, ~1 block in 6 dark glass,
  window grid never below 18 %; `M_CityFarLand` canopy / lots / street lines; `M_CityCliff` basalt columns; water Fresnel (`WaterSpec` 0.035).
- **Atmosphere of the view maps** (`add_lighting`; `FOG_DENSITY` etc.): fog 0.0008, inscattering (0.76, 0.78, 0.80), aerial scale 0.34. **Trade line** (S4, sweep table in README): fog -1e-4 = C13 -1.7 Y and C15 +0.011; FarGain +1 = C13 +1.8 Y (only +0.8 above ~6) and C15 -0.004; FarJit +0.3 = C13 -1.5 Y, C15 +0.005.
  MPC values (saved asset and script defaults agree): FarGain 7.6, FarJit 1.3, FarLandGain 1.6, WaterSpec 0.035, SunK 0.08.
- **Facade albedo cap `SunK`**: sun-facing base colour luma limited to SunK via `ResolvedView.DirectionalLightDirection` (N.L ramp 0..0.4), faded out over 0.9-2.2 km so the far skyline keeps its albedo; in M_CityFacade / M_CityDetail / M_CityRoof; `AlbKnee/AlbSlope/F0Scale` in the facade.
  C1 10/18 -> 17/18. **Do not put code after a `//` on the same line inside a Custom-node string**: the interrupted WIP did that (the whole cap commented out; the committed 20:20 frames had no cap).
- IP: MTA slogan, racing-franchise key art, sneaker photography replaced by original art (`ip_original_art.py`); 0 OCR hits. Sign atlases `never_stream`; `tsFrames` panelled cladding; 7 shop-interior types.
- Scripts: `run_commandlet.sh` (headless `-nullrhi` commandlet through the GPU slot) is the way to run any editor script; `launch_editor.sh` (`open -n`, not slot-wrapped) should not be used while the lock is in force. Neither `pkill -9`s an engine any more.

### How a round runs now (measured wall times; the queue for the shared GPU took 5-15 min per wait on 2026-09-30)
ONE slot hold for the whole sequence (nested `gpu_slot.sh` calls pass through, so wrapping the driver script once is legal and avoids a queue wait per capture; max hold 40 min, the r07 final was 14 min):
```
cat > final.sh <<'X'   # zsh; strictly sequential, one Unreal process at a time
WT=/Users/midir/sm2-n1/city
$WT/tools/export/ue/run_commandlet.sh $WT/unreal/WebHomage/Scripts/build_city.py steps=mat,map
$WT/tools/export/ue/run_commandlet.sh $WT/tools/export/ue/set_mpc.py FarGain=7.6 FarJit=1.3 SunK=0.08 DebugMode=0
$WT/tools/export/capture_round.sh <raw_dir>            # 8 views x (1080p, 4K), perf window 18-28 s
X
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label city -- zsh final.sh
python3 tools/export/assemble_round.py <raw_dir>/raw docs/night1/city/round-NN NN
python3 tools/export/city_spec_check.py docs/night1/city/round-NN --yolo --ip --json docs/night1/city/round-NN/city_spec_check.json --md docs/night1/city/round-NN/city_spec_check.md
python3 tools/export/builder_crops.py docs/night1/city/round-NN
```
Parameter sweeps: build variant maps with `tools/export/ue/atmo_variants.py` (`src=S4_perch_skyline names=d,e fog_d=.. aerial_d=.. fogc_d=..` -> `City_View_S4vd`) and capture them with `capture_one.sh <dir> S4vd 1920x1080`; MPC values with `set_mpc.py` (no recompile).
Never run two of your own captures at once (one Unreal process per agent: do not queue a second hold while one is waiting; kill the waiting wrapper first). There is no `timeout` command on macOS; poll with a `for` loop.

### New gotchas (r07)
16. Custom-node vertex colour input is RGB; alpha needs the `A` output (`kind 'vca'`). A failed compile = default material in -game, silently: `grep "Failed to compile" <capture>.log`.
17. Editor Python / materials / MPC / maps run fine in a `-nullrhi` commandlet; shaders compile lazily in the -game process.
18. Sun direction in a material: `ResolvedView.DirectionalLightDirection.xyz` (toward the atmosphere sun) compiles in Custom nodes. The material cannot know shadows.
19. After the 2026-09-29 16:43 GPU incident: <= 1 Unreal process per agent, everything through `gpu_slot.sh capture`, `wait_slot.sh` cap 4 (`SM2_MAX_UNREAL`). After the 23:08 kernel panic: never SIGKILL an engine (`stop_ue.sh`), never launch while an UnrealEditor is stuck exiting (the lock refuses). `Scripts/run_game.sh` still `kill -9`s after its `-timeout` (900 s; not P1's file): a normal capture takes ~50 s, so watch and use `stop_ue.sh` first.
20. `S4v?` variant maps (a..r) are scratch in Content/ (not committed, regenerable with atmo_variants.py); the last sweep left S4va..S4ve there.
21. `set_mpc.py` prints the parameter dict to `Saved/Logs/city_cmdlet.log`, not to stdout: `grep -a "'FarGain'" .../city_cmdlet.log | tail -1`.
22. Comment lines in a Custom-node string swallow the rest of their physical line: one statement per line.
23. Lumen bounce: capping near albedo also lowers the far shore Y by ~1 (S4 -1.2) and river by ~0.8: re-measure S4 after any near-field albedo change.
Detailed block = 768 m long (tiles ix -1..1 -> x -256..512); the 30 s route leaves it at ~22.6 s. Not extended.

## State (round 06, still valid)
- Critic rounds: r01-r05 FAIL (r05: facades 5, street 4, skyline 3, Manhattan 4, IQ 5; gap: far skyline, S4 and everything past ~1 km).
  r06 = far field: far-shore blocks with real window grids, coast / far-land materials instead of white slabs, thinner warm-neutral haze, real-water
  Fresnel, IP exclusions (HAUTE UNLIMITED, Hotel Astoria, Madison Arena, Boreal Outdoor, New York Knights).
- **What was wrong (root causes, all found by rendering with fog off and by mask captures):**
  1. `farCityMass` (far-shore blocks, farshore.js) encodes a window flag in vertex colour blue (+10 / +20); the exporter clamped colour to 0..1 and the flag
     became saturated blue for every block (the "lavender boxes"). `export_city.mjs` now decodes the flag into vertex ALPHA (0 / 0.5 / 1) and restores blue.
  2. Coast, far-land, cliff and water were imported with the generic white vertex-colour material (`M_CityVC`): the near-white shoreline / "snow" slabs.
  3. Height fog density 0.006 with blue inscattering + full aerial perspective washed the far field out.
- **New materials** (build_city.py): `M_CityFarMass` (createMassMaterial port: window grid, spandrels, glass towers, night lights; warm push), `M_CityCoast`
  (createCoastMaterial port: atlas granite / riprap / planks / bulkhead, lawn, pavers, ribbed metal, picket cards), `M_CityFarLand` (the browser's baked far-land
  ground map, exported by `export_city.mjs` as `farland_map.png`) and `M_CityCliff`. `far_material(rec)` maps mesh names to them. `M_CityWater` Specular 0.25
  (real water F0 0.02; 0.5 read as milky glass). New build step **`far`** (re-imports `farCityMass` as `SM_*_r06`, retargets the other far meshes, swaps level
  actors); `build_geo_level` prefers `_r06` / `_r04` re-imports, so a `map` step no longer reverts them (before this, round-05 map rebuilds silently restored the
  original tsFrames housing).
- (SUPERSEDED by r07: fog 0.0008, aerial 0.34, inscattering 0.76,0.78,0.80) **Atmosphere of the view maps** (`add_lighting`, args `fog=`, `fogc=`, `aerial=`; variants: `tools/export/ue/atmo_variants.py`): height fog 0.0065, sky-neutral
  inscattering (0.6, 0.62, 0.64) (r05: blue 0.32, 0.40, 0.52), SkyAtmosphere `aerial_pespective_view_distance_scale` 1.0 (sic, UE spells it "pespective").
  History: I first thinned the haze (fog 0.001, aerial 0.25) for the best-looking far field, then CITY-SPEC C11-C15 (added mid-round) asked for the opposite
  (far shore 25-35 luma under the sky, aerial contrast falloff 0.25-0.45): the current values are the spec-driven ones. The sky is blown (Y 229, manual exposure
  +2 EV in the test maps): P4 owns exposure / sky; the far-shore / sky RATIO is what these values fix, so it should survive an exposure change.
- Facade far LOD (`gen_shaders.mjs` uePatch): window-cell box filter 1.8x -> 1.15x (grid readable further out) and a warm-neutral albedo push where lod -> 1.
- **Measurements** (round-06/README.md has the tables; scripts in tools/export): `spec_farfield.py` (CITY-SPEC C11-C15), `far_stats.py` (shore strip vs water, masks =
  MPC_City.DebugMode 3 captured on `City_View_S4vm` = S4 with fog and aerial off, because haze washes the mask colours out), `facade_c1.py` (C1 / C2, facade mask =
  DebugMode 11), `ip_ocr_check.py` (denylist OCR). r06 numbers: C11 6.7x sky Laplacian / flat blocks 22 %, C12 +1.9, C13 -32.6, C15 0.25 pass; **C14 fails** (river 13.5
  brighter than the far shore: the river is veiled by the same haze; fixing it needs a distance-dependent haze model or a lower sky exposure, not more fog tuning);
  shore strip darker than water by 0.104 luma (crop x 0-2800, y 550-700); C1 fails on S2 (sunlit pale stone 30.7 % above Y 204, mean 134) and S2 right glass tower (3.8 %),
  passes on S1 / S8; S1 right tower (canyon-shadowed dark glass, mean Y 20) is under C2's 52. Those are lighting-driven (sun 6, sky fill 1.7, exposure +2 EV): for P4.

## Round 05 (street level; still valid)
- Critic rounds: r01-r03 FAIL; r04 FAILS-improving (facades 5, street 3, skyline 4, Manhattan 4, IQ 5; gap: street level 0-3 storeys unbuilt).
  r05 = street-level kit + crisp shop interiors + supplemental street furniture + sidewalk slabs + two more IP cell exclusions.
- Detailed block: tiles ix -1..1, iz -2..0 (x -256..512, z -512..256). Far: facade-LOD masses for the whole island, far shores, bridges, hinterland
  boxes, land polygon, one water plane at y = -1.6 m, height-fog haze from 400 m. Views: 8 maps `/Game/Tests/City/City_View_<id>` (S1..S8).
- **Street-level kit (r05)**: `tools/export/street_kit.py` reads every ground-floor face of the exported facade meshes (`street_faces.py`: face frame,
  storefront height gH, bay layout of the shader) and builds real geometry in front of the shader wall: stone / brick piers with plinth + capital, a
  stepped stone cornice with dentils (metal canopy on curtain-wall podiums), 3D storefront frames (jambs, head, transom, mullions, door leaves with kick
  plates + pull bars), fascia sign boards, fabric awnings (stripes, lettered valance) or metal marquees, and fire escapes (grated platforms, railings,
  stair flights, drop ladder aligned with a pier) on ~90 % of pre-war faces and on side / deco faces. 578 faces, 2225 bays, ~580 k tris, 9 GLBs
  (`mesh/streetkit/`), Nanite, material `M_CityKit`. Signage = `gen_street_signs.py` (original generic shop names, system fonts).
- **Crisp shop interiors (r05)**: the atlas photos were ~85 px / m and blurry at street distance. `gen_shaders.mjs` `uePatch` list now draws four shop
  types analytically (grocery shelves + produce crates, cafe slat wall + jars + menu boards + pendant lamps, boutique rails + mannequins, pharmacy /
  bank), customers, checker floor, side walls, soffit + ceiling tubes; anti-aliased from the pixel footprint.
- **Street furniture (r05)**: `street_props.py` adds a hydrant, trash can, newspaper box and tree pit every ~20 m of avenue frontage (149 / 151 / 143 / 127
  instances) to the browser pools' ISMs (`streetprops.json`, merged in `build_city.py`). Sidewalk shader patch: 1.5 m slab joints, bevel, per-slab tone,
  hairline cracks, gum spots (`gen_shaders.mjs`, Sidewalk block). S1 corridor street trees thinned (45 %; the deco podium in front of the fire escape is
  cleared: `thin()` in build_city.py) and SkyLight intensity 1.7 in every view map.
- IP: `ip_sanitize.py` also excludes COLTEX SPORT (L27), COLTEX (P27) and COLEXCO (P38) ad cells. See `IP_EXCLUSIONS.md`.

## Round 04 numbers (details: round-04/README.md, window_stats.json, window_crops/)
Share of window pixels above 80 % luminance in 400 px crops of the 4K frames (round 03 -> round 04): S1 right facade 0.0 % -> 0.0 % (median luminance
0.286 -> 0.071: the tower is in canyon shade and now reads near-black glass), S8 brick tower centre-right 11.97 % -> 3.11 %, S8 brick tower left
21.26 % -> 0.0 %, S2 left stone tower 24.13 % -> 0.49 %, S7 right masonry wall 68.93 % -> 0.0 %, S7 left glass wall 0.0 % -> 0.0 % (median 0.388 -> 0.129).
Open: S1's right tower may now be too dark (median 0.07); DayEmisK / InteriorGain are the knobs (MPC, no recompile). Window mask frames
(`_scratch/city/r04/mask4k`, DebugMode 3) were captured once; a rerun after geometry changes needs new masks (set DebugMode=3, capture the 4 views at 4K, reset to 0).

## Commands (all from the worktree root)
```
npx vite --port 5202 --host 127.0.0.1 --strictPort &        # browser city (exporter needs it; only for a full rebuild with export)
tools/export/build_city.sh                                  # FULL: export -> patch_export -> prep textures (IP sanitiser) -> street signs -> street kit -> street props -> gen shaders -> build_city.py (this last step goes through uejob.py = a P1 EDITOR
                                                            # with the job server; on a clean checkout run the last line of that script through tools/export/ue/run_commandlet.sh instead: `run_commandlet.sh unreal/WebHomage/Scripts/build_city.py steps=clean,tex,mat,mesh,proto,kit,map`)
tools/export/ue/run_commandlet.sh <script.py> [k=v ...]     # ANY editor script (build_city.py steps=mat,map | set_mpc.py FarGain=.. | atmo_variants.py ...) headless -nullrhi, through gpu_slot; needs the P1 editor closed
tools/export/ue/launch_editor.sh                            # legacy: `open -n` editor with MCP :8771 + job server; NOT slot-wrapped, do not use while the GPU lock is in force
tools/export/capture_round.sh <raw_dir> [ids...]            # run_game.sh per view, 1080p + 4K, perf + GPU util (waits for a free Unreal slot)
python3 tools/export/assemble_round.py <raw_dir>/raw docs/night1/city/round-NN NN   # JPGs + perf.json + README
python3 tools/export/window_stats_round.py <lit_dir> <mask_dir> out.json [crop_dir]  # window brightness test (mask = DebugMode 3 frames)
node tools/export/browser_views.mjs <out> [ids]             # browser captures from the same cameras (A/B)
python3 tools/export/ue/uejob.py file.py [k=v]  |  -c "code" # run editor Python in the P1 editor (JOB_ARGS dict)
```
Stop an engine of yours: `/Users/midir/sm2-n1/_scratch/gpu/bin/stop_ue.sh "[/]Users/midir/sm2-n1/city/unreal/WebHomage"` (drivers first, SIGTERM, wait; NEVER `kill -9` a rendering engine). **Owner rule 2026-09-29: the editor is
closed whenever it is not needed** (captures use `run_game.sh`, they do not need it) and no Unreal process is started while 3+ are running
(`tools/export/ue/wait_slot.sh`). Typical r04 loop: launch editor -> `uejob.py build_city.py steps=mat` / set MPC -> stop editor -> capture.
Full build ~9 min, export ~2 min, mat step ~15 s (the shader compiles lazily in the game process), one view capture ~70-120 s.

## Job runner (legacy editor route; r07 uses run_commandlet.sh instead)
The official MCP has no Python exec, and `-ExecutePythonScript` QUITS the editor. The editor runs `job_server.py` (slate tick, polls
`_scratch/city/uejobs/*.py`, writes `.out` / `.done`). Jobs run on the game thread; a modal dialog blocks it (deleting referenced maps /
materials / meshes did that) -> build_city.py never deletes referenced assets: maps are opened + emptied, materials reused, and the
`frames` step re-imports a mesh under a new name (`_r04`) and re-points the level actors instead of deleting.
No numpy inside the editor's Python.

## File map
- `tools/export/export_city.mjs` + `collect_page.js`: headless Chrome export. `patch_export.py`: post-export mesh clean-up (r04: removes
  dark hovering tsFrames housings within 25 m of a shot camera). `ip_sanitize.py` + `prep_textures.py`: IP-clean Unreal copies of the
  ads / signs atlases (see `IP_EXCLUSIONS.md`).
- `tools/export/glsl2hlsl.mjs` + `gen_shaders.mjs`: browser GLSL -> `Shaders/City/{Facade,Detail,Roof,Asphalt,Sidewalk}.ush`. **Facade.ush is
  generated: never edit it by hand.** UE-only changes go into the `uePatch(...)` list in gen_shaders.mjs (each patch must match exactly once).
- `unreal/WebHomage/Scripts/build_city.py`: textures, materials (Custom nodes), meshes, protos, maps, `frames` step. `city_shots.json`: the 8 cameras.
- Materials: M_CityFacade/Detail/Roof/Asphalt/Sidewalk (ports), M_CitySignage (signage.js port, r04), M_CityKit (street kit, r05), M_CityFrame (gunmetal billboard housings,
  r04), M_CityProp, M_CityVC, M_CityLeaves, M_CityCrown, M_CityLand, M_CityWater (placeholder, P6), M_CityHinter, MPC_City.

## MPC_City (Content/City/Materials/MPC_City, defaults in build_city.py MPC_DEFAULTS)
NightK, DnTime, InteriorGain 0.5, ShopGain 0.7, EmissiveScale 3.0 (r03) plus r04: **DayEmisK 0.22** (facade interior / sign emission scale in
daylight, 1.0 at night: rooms behind glass are ~10x darker than sunlit masonry), **GlassSpec 0.5** (UE Specular of dielectric sash glass = F0 0.04), r06-r07: **FarGain 7.6, FarJit 1.3, FarLandGain 1.6, WaterSpec 0.035** (far field), **AlbKnee 0.30, AlbSlope 0.48, F0Scale 0.8, SunK 0.08** (facade albedo cap, C1),
**DebugMode**: facade: 1 emissive only, 2 no emissive, 3 window mask (red = glass pixel; used by window_stats), 4/8/9 gLodI, 5/7 raw interior
atlas, 6 interior(), 10 raw signs atlas, 11 facade-only mask (facade_c1.py); r06 far field, mode 3: coast + far land red, water blue, far-shore blocks green; mode 9 (M_CityFarMass): vertex alpha. Change values without recompiling: `run_commandlet.sh tools/export/ue/set_mpc.py Name=value` (or `uejob.py` in an editor) (edits
the MPC defaults and saves; `tools/export/capture_one.sh <dir> <id> [WxH]` = single frame).

## Facade patch layer (gen_shaders.mjs, r04) — what made the windows read as glass
1. `gLodI` -2.5 mips (interior mapping sampled the room atlas 2-4 mips too high because UE renders at 50-73 % internal resolution: every room was
   the atlas average = beige).
2. Rooms 25 bays wide with the back-wall photo wrapping once per bay / per storefront (`gRoomWrap`): at street angles a 3 m room exits through its
   side wall after 1 m, so all windows showed one flat side-wall tint.
3. Lit / dim / dark rooms in ~10 / 30 / 60 %, unlit rooms 0.2x, ceilings 0.42 (was 0.72), shop floor 0.3, blinds albedo x0.5.
4. Material: Emis x DayEmisK; sash glass Specular 0.5 instead of 0.1375 (the old value removed all reflection); curtain glass unchanged (metal mirror).
Result: dark glass with Lumen reflections, visible room interiors (desks, paintings, shelves) in the lit share of windows, blinds and curtains.

## Gotchas (each cost hours)
1. **Nanite keeps only 4 UV channels.** Facade / roof / ground meshes must be non-Nanite AND rebuilt (symptom: facades without windows).
2. **The editor caches shader source files**: edits to `Shaders/City/*.ush` are ignored until `recompileshaders changed` (build_city.py mat step runs it).
3. **Material usage flags must be saved** (Nanite, InstancedStaticMeshes) or -game draws the default material.
4. Custom-node HLSL: `Texture2DSample`/`...SampleGrad` wrappers, float literals with `f`, derivatives (ddx/fwidth) only in uniform control flow, textures
   passed through every function (TEXDECL / TEXPASS).
5. three.js textures are v-flipped: sample at (u, 1 - v) (fl2/fl3 helpers).
6. Glass: coated curtain glass = metal mirror; sash glass = dielectric Specular 0.5 (r04).
7. `EditorAppToolset.CaptureViewport` renders unconverged frames; judge in `-game` (run_game.sh).
8. Interchange glTF: UE = (x, z, y) x 100; per-file subfolders `_in/<name>/StaticMeshes/`.
9. `MPC.scalar_parameters` names are `Name` objects: compare with `str()` or every run appends `NightK1`, `NightK2` ... (fixed in build_city.py).
10. GLB coordinates are tile-local: world = local + manifest `center` (x, z).
11. Handedness: UE is left-handed. A hand-made camera ray needs `right = cross(up, f)` and `up = cross(f, right)` (the first S5 probes were wrong).
12. GPU is shared: every perf number so far was taken at 50-99 % utilization before the run.
13. Mask captures see haze: fog / aerial perspective add a ~75/255 veil to every pixel, so mask colours are detected by channel differences (far_stats.py),
    not absolute levels; set Specular 0 + roughness 1 in the mask branch of a material or reflections leak in.
14. Interchange keeps vertex ALPHA and clamps vertex colour to 0..1 (8-bit): never encode data in colour values > 1 (exporter decodes farshore.js flags into alpha).
15. Debug recipe: replace the return of a Custom node by a debug value scaled by 0.05 (emissive 1.0 saturates at the +2 EV manual exposure), capture
    1080p in `-game`, read pixel values with PIL.

## Known problems / next rounds (round-08 to-do list is at the top; this list is older and partly fixed: items marked FIXED r07)
- Far field (r06 text; r07 added tone jitter, banding, dark-glass blocks, canopy clumps, basalt cliff, see top): the far-shore blocks are boxes with a window grid; no brick / trees / parks colour variety like the browser (the browser bakes park
  greens and lot tones into the far-land map, which is used, but the 2-4 km facade ring stays tone-flat). No bridges texture work, no far water towers.
  Horizon hinterland (> 5 km) is sub-pixel windows only. Hazy sky band stays bright (sky / exposure belong to P4).
- Test-map atmosphere (r07: fog 0.0008, aerial 0.34, inscattering 0.76,0.78,0.80) is mine; if P4's look pass re-lights the maps, re-run `city_spec_check.py` (it supersedes spec_farfield.py / far_stats.py / facade_c1.py, which stay for mask captures).
- The window-brightness numbers of round 04 (window_stats_round.py) were superseded by CITY-SPEC C1 (facade_c1.py); the r04 script still works with DebugMode 3.
- CITY-SPEC (docs/night1/city/SPEC.md on Opus-5.5-Loop-Night-1) lists C4-C10 not yet worked: parked cars / traffic (P6), S3 water towers (>= 2 in frame), street-tree count in S1.
- `frames` / `far` steps leave the previous imports behind as `*_old<ts>` assets; a `clean` rebuild removes them.
- Fire escapes are in the S1 crop x 0-1600, y 800-1700 only at its top-right corner (the lowest platforms of the far deco tower, x ~1525-1600,
  y 800-1000); nearer escapes start above the 6 m cornice, above that crop. If the critic wants them lower in frame: move the camera or add a
  retracted-ladder variant. Drop ladders end at 2.6 m and are aligned with a pier (behind awnings they are hidden at oblique angles).
- Street kit density: every ground-floor bay gets a fascia board; ~38 % of bays get a fabric awning, ~21 % a marquee (curtain-wall podiums: marquee only);
  bays that already carry a browser awning mesh (fabric / marquee bulbs) get no second awning. Awnings are dark-ish (palette in `street_kit.py` AWN).
- Shop interiors are analytic (crisp) but simple: no depth-of-field cues, customers are flat silhouettes, no per-shop signage inside. Upper wall / soffit
  is a dark band; the glass reflects the sky (white panes at grazing angles).
- S5 / S6 (Times Square): the kit also dresses those podiums; tree guards there still hold no trees; red steps flat; white clipping on the curb.
- Sunset (S7) and night: interior emission only follows NightK; a dusk ramp belongs to P4.
- FIXED r07 (lavender boxes, white shoreline slabs); bridges and piers on the far shore still missing (critic secondary issue).
- No traffic or pedestrians (P6); sidewalk joints are visible in sun only (the avenue sidewalks sit in canyon shade).
- Perf r05: see round-05 README; captures ran with other Unreal sessions active, numbers are contaminated (GPU util column).
- Window brightness test (r04 numbers in the section above) was not re-measured in r05 (upper-floor glass unchanged; SkyLight 1.0 -> 1.7 brightens
  reflections slightly): re-run `window_stats_round.py` with fresh DebugMode-3 masks before quoting.
