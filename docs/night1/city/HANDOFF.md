# P1 City — handoff after round 03 (for the next builder)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Branch `night1/city`, worktree `/Users/midir/sm2-n1/city`. UE MCP port **8771**, browser dev port **5202**.
Owned: `tools/export/`, `/Game/City`, `/Game/Tests/City`, `docs/night1/city/`, plus (flagged to the integrator)
`unreal/WebHomage/Shaders/City/` and `unreal/WebHomage/Scripts/{build_city.py,city_shots.json}`.
Content/ is NOT committed (public fork, no LFS): everything is rebuilt by scripts from the browser city.

## State (round 03)
- Critic rounds: r01 FAILS (city ended at 1 km), r02 FAILS-improving (facades 5, street dressing 2, skyline 4,
  Manhattan 4, IQ 3). r03 = foliage replacement: ez-tree geometry everywhere (LOD0 inside the 3x3 block, LOD1 for
  ~35 k trees island-wide), leaf-alpha cards with two-sided-foliage shading, opaque canopy masses in the park.
- Detailed block: tiles ix -1..1, iz -2..0 (x -256..512, z -512..256; 8th / 6th / 5th Av, Times-Square-like bowtie).
- Far: facade-LOD masses for the whole island, far shores (farCity*, farLand, coast, cliffs), bridges, 28,965
  hinterland boxes, land polygon, one water plane at y = -1.6 m, height-fog haze from 400 m.
- Views: 8 maps `/Game/Tests/City/City_View_<id>` (streamed geometry level `City_Midtown_Geo` + light + auto-activated
  CameraActor). Playable map `City_Midtown` (PlayerStart on the 5th-Av-like crosswalk).

## Commands (all from the worktree root)
```
npx vite --port 5202 --host 127.0.0.1 --strictPort &        # browser city (exporter needs it)
tools/export/ue/launch_editor.sh                            # P1 editor: MCP :8771, -unattended, abslog Saved/Logs/city.log,
                                                            # runs tools/export/ue/job_server.py via -ExecCmds "py ..."
tools/export/build_city.sh                                  # export -> prep textures -> gen shaders -> build_city.py (all steps)
SKIP_EXPORT=1 STEPS=mat,map tools/export/build_city.sh      # partial rebuild (steps: clean,tex,mat,mesh,proto,map)
tools/export/capture_round.sh <raw_dir> [ids...]            # run_game.sh per view, 1080p + 4K, perf + GPU util
python3 tools/export/assemble_round.py <raw_dir>/raw docs/night1/city/round-NN NN   # JPGs + perf.json + README
node tools/export/browser_views.mjs <out> [ids]             # browser captures from the same cameras (A/B)
python3 tools/export/ue/uejob.py file.py [k=v]  |  -c "code" # run editor Python in the P1 editor (JOB_ARGS dict)
```
Stop editor: `pkill -9 -f "/Users/midir/sm2-n1/city/unreal/WebHomage/WebHomage.uproject"` (only yours). Full build
~9 min, export ~2 min, one view capture ~70 s per resolution. Export output: `_scratch/city/export/midtown3x3/`,
textures: `_scratch/city/tex/` (prep_textures.py).

## Job runner
The official MCP has no Python exec, and `-ExecutePythonScript` QUITS the editor after the script. The editor
therefore runs `job_server.py` (slate tick, polls `_scratch/city/uejobs/*.py`, writes `.out` / `.done`). Jobs run
on the game thread; a modal dialog blocks it (deleting referenced maps / materials did that) -> build_city.py never
deletes maps (it opens + empties them) and reuses materials (clears the graph). Launch has `-unattended`.

## File map
- `tools/export/export_city.mjs` + `collect_page.js`: headless Chrome export (tiles, far ring, far meshes in 2 km /
  60 km tiles, land polygon, hinterland.json, pools -> layout.json instances, collision.json, manifest.json).
- `tools/export/glsl2hlsl.mjs` + `gen_shaders.mjs`: browser GLSL -> `Shaders/City/{Facade,Detail,Roof,Asphalt,Sidewalk}.ush`.
- `unreal/WebHomage/Scripts/build_city.py`: textures (+ Texture2DArrays), materials (Custom nodes), mesh/proto import,
  maps. `city_shots.json`: the 8 shot cameras (browser metres). `docs/night1/city/{SHOTLIST,EXPORT}.md`.
- Materials: M_CityFacade/Detail/Roof/Asphalt/Sidewalk (ports), M_CityProp (partmat port), M_CityVC (generic),
  M_CityLeaves (foliage), M_CityCrown (park canopy mass), M_CityLand, M_CityWater (placeholder; P6 owns water),
  M_CityHinter, MPC_City (NightK, DnTime, InteriorGain, ShopGain, EmissiveScale).

## Gotchas (each cost hours)
1. **Nanite keeps only 4 UV channels.** The facade needs 8 (all browser attributes are packed into UV0-7 + vertex
   colour). Facade / roof / ground meshes must be non-Nanite AND rebuilt after switching (set_lod_build_settings);
   symptom: facades without windows (UV4+ read UV3). Only detail + props + trees are Nanite.
2. **The editor caches shader source files**: edits to `Shaders/City/*.ush` are ignored until
   `recompileshaders changed` (build_city.py mat step runs it).
3. **Material usage flags must be saved** (Nanite, InstancedStaticMeshes) or -game draws the default material on
   HISM / Nanite meshes (grey squares). make_material sets them.
4. Custom-node HLSL: use `Texture2DSample`/`...SampleGrad` wrappers (plain `.Sample` breaks HW-RT hit shaders),
   suffix float literals with `f` (bare literals in ternaries -> FP64 -> Metal compile failure), textures are
   passed through every function (TEXDECL / TEXPASS macros).
5. three.js textures are v-flipped: sample at (u, 1 - v) (fl2/fl3 helpers).
6. Glass: coated curtain glass = metallic mirror (BaseColor = F0 x tint); old sash glass = dielectric Specular
   0.1375 (F0 0.011 -> UE F90 = 0.55, matching the browser's specularF90), else masonry windows turn into mirrors.
7. `EditorAppToolset.CaptureViewport` renders unconverged frames and lit debug values are not trustworthy; debug with
   emissive and judge in `-game` (run_game.sh).
8. Interchange glTF: UE = (x, z, y) x 100; per-file subfolders `_in/<name>/StaticMeshes/` are renamed by the script.
9. Transient "Requires valid texture" warnings during the clean step are harmless; check failures after the mat step.
10. GPU is shared: every perf number so far was taken at 99-100 % utilization before the run.

## Known problems / next rounds
- Round 03 foliage: S1 canopy green with clusters but mean canopy luminance 0.153 (target 0.25): the canopy is
  in canyon shade under a manual-exposure test light (P4 owns lighting); park LOD1 trees thin out at 1-2 km (crown
  masses help, still reads partly as lawn). Near trees use one ez-tree texture per variant, no instance tints
  (browser aTintA/aTintB are ignored).
- Street dressing (critic 2/10): no traffic, no pedestrians (P6), props are low-detail vertex colour, trunks flat.
  Next: port props textures (props_hq_atlas works for some), add parked cars from the browser vehicle atlas.
- Far shore: some coast / quay meshes still flat white; hinterland reads bluish through the atmosphere.
- Times Square screens: ad atlas works, no emissive bloom/night pass; transparent overlays (spill, halos,
  grime, roof AO) are not exported.
- Perf r03: avg 26-66 ms at 1080p and 34-67 ms at 4K (GPU 51-95 % busy before runs, contaminated). Big costs: 35 k Nanite masked trees, Lumen with far city,
  Lumen surface cache oversubscribed (~31 %). Consider HLOD / impostors for far trees and far city.
- S3 has a large billboard back in frame; S7 sunset uses the generic fog colour.
