# P1 City — handoff after round 05 (for the next builder)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Branch `night1/city`, worktree `/Users/midir/sm2-n1/city`. UE MCP port **8771**, browser dev port **5202**.
Owned: `tools/export/`, `/Game/City`, `/Game/Tests/City`, `docs/night1/city/`, plus (flagged to the integrator)
`unreal/WebHomage/Shaders/City/` and `unreal/WebHomage/Scripts/{build_city.py,city_shots.json}`.
Content/ is NOT committed (public fork, no LFS): everything is rebuilt by scripts from the browser city.

## State (round 05)
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
npx vite --port 5202 --host 127.0.0.1 --strictPort &        # browser city (exporter needs it)
tools/export/ue/launch_editor.sh                            # P1 editor, OFFSCREEN (-RenderOffScreen -NoSound), MCP :8771, job server; waits while 3+ Unreal run
tools/export/build_city.sh                                  # export -> patch_export -> prep textures (IP sanitiser) -> street signs -> street kit -> street props -> gen shaders -> build_city.py
SKIP_EXPORT=1 STEPS=mat,map tools/export/build_city.sh      # partial rebuild (steps: clean,tex,mat,mesh,proto,map,frames,kit)
tools/export/capture_round.sh <raw_dir> [ids...]            # run_game.sh per view, 1080p + 4K, perf + GPU util (waits for a free Unreal slot)
python3 tools/export/assemble_round.py <raw_dir>/raw docs/night1/city/round-NN NN   # JPGs + perf.json + README
python3 tools/export/window_stats_round.py <lit_dir> <mask_dir> out.json [crop_dir]  # window brightness test (mask = DebugMode 3 frames)
node tools/export/browser_views.mjs <out> [ids]             # browser captures from the same cameras (A/B)
python3 tools/export/ue/uejob.py file.py [k=v]  |  -c "code" # run editor Python in the P1 editor (JOB_ARGS dict)
```
Stop editor: `pkill -9 -f "/Users/midir/sm2-n1/city/unreal/WebHomage/WebHomage.uproject"` (only yours). **Owner rule 2026-09-29: the editor is
closed whenever it is not needed** (captures use `run_game.sh`, they do not need it) and no Unreal process is started while 3+ are running
(`tools/export/ue/wait_slot.sh`). Typical r04 loop: launch editor -> `uejob.py build_city.py steps=mat` / set MPC -> stop editor -> capture.
Full build ~9 min, export ~2 min, mat step ~15 s (the shader compiles lazily in the game process), one view capture ~70-120 s.

## Job runner
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
daylight, 1.0 at night: rooms behind glass are ~10x darker than sunlit masonry), **GlassSpec 0.5** (UE Specular of dielectric sash glass = F0 0.04),
**DebugMode** (facade only): 1 emissive only, 2 no emissive, 3 window mask (red = glass pixel; used by window_stats), 4/8/9 gLodI, 5/7 raw interior
atlas, 6 interior(), 10 raw signs atlas. Change values without recompiling: `uejob.py tools/export/ue/set_mpc.py Name=value` (edits
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
13. Debug recipe: replace the return of a Custom node by a debug value scaled by 0.05 (emissive 1.0 saturates at the +2 EV manual exposure), capture
    1080p in `-game`, read pixel values with PIL.

## Known problems / next rounds
- Fire escapes are in the S1 crop x 0-1600, y 800-1700 only at its top-right corner (the lowest platforms of the far deco tower, x ~1525-1600,
  y 800-1000); nearer escapes start above the 6 m cornice, above that crop. If the critic wants them lower in frame: move the camera or add a
  retracted-ladder variant. Drop ladders end at 2.6 m and are aligned with a pier (behind awnings they are hidden at oblique angles).
- Street kit density: every ground-floor bay gets a fascia board; ~38 % of bays get a fabric awning, ~21 % a marquee (curtain-wall podiums: marquee only);
  bays that already carry a browser awning mesh (fabric / marquee bulbs) get no second awning. Awnings are dark-ish (palette in `street_kit.py` AWN).
- Shop interiors are analytic (crisp) but simple: no depth-of-field cues, customers are flat silhouettes, no per-shop signage inside. Upper wall / soffit
  is a dark band; the glass reflects the sky (white panes at grazing angles).
- S5 / S6 (Times Square): the kit also dresses those podiums; tree guards there still hold no trees; red steps flat; white clipping on the curb.
- Sunset (S7) and night: interior emission only follows NightK; a dusk ramp belongs to P4.
- Far shore / coast (S4): lavender untextured boxes and a white shoreline band; bridges and piers missing (critic secondary issue).
- No traffic or pedestrians (P6); sidewalk joints are visible in sun only (the avenue sidewalks sit in canyon shade).
- Perf r05: see round-05 README; captures ran with other Unreal sessions active, numbers are contaminated (GPU util column).
- Window brightness test (r04 numbers in the section above) was not re-measured in r05 (upper-floor glass unchanged; SkyLight 1.0 -> 1.7 brightens
  reflections slightly): re-run `window_stats_round.py` with fresh DebugMode-3 masks before quoting.
