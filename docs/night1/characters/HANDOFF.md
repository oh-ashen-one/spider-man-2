# P2 Characters: handoff after round 02

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203.
Round 02 fixed the critic's single biggest gap (round-01 verdict: hero model 4, hero animation 4, enemies 2, civilians 2, image quality 3; FAILS). Everything not listed under "Round 02" is unchanged from round 01.

## Round 02: the brute

**Cause (measured, not guessed).** `thug.glb` is ONE mesh with ONE material and 19 real UV islands. The brute is that mesh scaled up; the game and UE only swap the base-colour map (`enemy.js tintBrute`, `MI_Brute`). The old `public/assets/enemies/brute_basecolor.webp` was laid out for a different UV packing, so every island sampled the wrong garment. Texel audit on the thug UVs (`paint_brute.py --audit-png`): the old map has 149,841 skin-coloured texels and 97,688 white texels outside the hand/face islands. There was no material-slot problem to fix.

**Decision.** Re-paint the brute base colour ON THE THUG'S OWN UV LAYOUT (not re-project the old map: its layout is unknown and it has no matching mesh; not rebuild the mesh: the thug topology, weights and hero-skeleton fit are all good). Geometry, skeleton, skin weights, thug normal map and ORM are untouched.
- `tools/ue_char/brute/uvgeom.py` (Blender headless): dumps every UV triangle of `thug.glb` with its rest-pose 3D position and dominant skin bone.
- `tools/ue_char/brute/paint_brute.py` (numpy/PIL/scipy): rasterises that into per-texel island, position and bone maps. Island roles come from the bones and positions (torso front/back, head, thigh, shin, upper arm, forearm, hand, boot, sole), not from hard-coded ids. Paints: olive work jacket (chest pockets with flaps, zip, collar, yoke and centre-back seam, hem rib, belt and buckle), same-garment sleeves (elbow patches, cuffs), charcoal cargo trousers (pockets, worn knees, dirty hems), dark work boots (the thug's white sneaker pattern becomes laces), olive knit beanie, plain slate bandana (the red polka-dot pattern becomes a faint paisley), the thug's own skin/eyes/hands kept (brows shadowed). Gutters are filled by nearest island colour so no lavender bleeds into mips.
- Outputs: `public/assets/enemies/brute_basecolor.webp` (committed, 136 KB, same 2048x2048, same path, same loader), `art/night1/characters/thug/tex/brute_basecolor.png` (UE) and `brute_regions.png` (R face skin, G hands, B everything else). Texel audit of the new map: 0 skin-coloured and 0 white texels outside hands/face.
- `tools/ue_char/brute/build_brute.sh` runs both steps; the UE build's `prep` step calls it, so the browser webp and the UE PNG cannot drift apart. Deterministic: rerunning produces the same webp.
- The torso/thigh UV cut is jagged (mesh cut along triangle edges). The waist is designed around it: the torso's lowest part is trouser-coloured, hem rib and belt are on the torso only. Do not paint colour steps on a torso/thigh or torso/sleeve seam.

**UE-only look choices** (`build_characters.py`, ARGS in brackets):
- `MI_Brute`: `Tint` 0.85 [`brute_tint`], `Specular` 0.15, `Cloth` 0.12. The lineup stage renders sRGB albedo about 3x brighter and dark cloth is veiled by spec/sheen; the browser texture is untouched. Palette lessons from four measured iterations: in this stage a khaki/tan beanie, dark-brown hair and warm-grey boots all read as white or skin-coloured in sun (up to hundreds of thousands of hits over a clip), so the final cloth is a darker olive beanie, near-neutral dark hair and near-neutral dark boots.
- Actor scale 1.24 uniform x girth 1.2 [`brute_girth`] on X/Y (heavy-set build, same height). The browser still uses `scale 1.24` only (`enemy.js` not touched); to match, `this.root.scale.set(s * 1.2, s, s * 1.2)`.
- Enemy fill: 4 shadowless directional lights (0.8 lux each [`enemy_fill`], yaw 0/90/180/270, pitch -30) on lighting channel 1 only; only the thug and brute are on channel 1. Without it the shaded flank of a walking enemy is near black.
- Brute side shot: distance 700, aim 105, azimuth 180 [`brute_az`] (was 480/110/0: head cropped at the top of the frame). New shot 10 = brute orbit 360 deg in 6 s.

**Test (4K, brute only).** Two deterministic `-movie` runs of the same shot, 3840x2160:
BEAUTY = `Char_Lineup`; MASK = `Char_Lineup_BruteMask` (built by the same script: identical actors and timing; brute unlit with `T_Brute_Regions`, every other character unlit yellow so it still occludes, black background, no lights).
`measure_frames.py` classifies only pure-blue mask pixels (the brute's cloth), eroded 6 px, >= 14 px from face/hands and >= 30 px from any contaminated mask pixel (edge blends, other characters and their motion blur), then counts skin-like (hue 8-38, sat 0.22-0.65, value >= 0.42) and white-like (value >= 0.80, sat <= 0.18) pixels on the beauty frame. Control: the same detector on hand/face pixels fires on 24% (side) and 92% (orbit) of them, so it is not blind.

| Run | Frames analysed (every 3rd from frame 30) | Cloth px judged | Skin-like (strict) | White-like | Largest flagged region |
|---|---|---|---|---|---|
| Side span (shot 5, 3.3 s) | 51 | 18,692,093 | 0 (loose threshold value >= 0.30: 0) | 10 px in 1 frame | 7 px |
| Orbit 360 (shot 10, 6.3 s) | 111 | 50,134,901 | 0 (loose: 0) | 0 | 0 |

Frames skipped: 6 of 57 side candidates and 6 of 117 orbit candidates (brute not in frame). Before the detector excluded other characters' blur, a hero motion-blur crossing in front of the brute produced thousands of false hits; that is why the mask run paints them yellow. Evidence: `round-02/captures/brute_test/` (3 side + 5 orbit 4K frames, both JSONs with per-frame counts, worst-frame overlays, a 4K side clip). Earlier iterations of this round failed the same test (earlier detector versions, so the counts are not comparable): a lighter olive beanie at tint 1.0 flagged white in the sun (795,049 px over the side span), brown hair flagged skin-like (9,590 px), a warm-grey boot heel flagged skin-like (a 535 px blob on the orbit). Each was fixed in the texture and the test re-run on the final assets above.
Old map for comparison, texel level on the thug UVs: 149,841 skin-like and 97,688 white texels outside hands/face; new map 0 and 0. The round-01 clip itself was not re-measured (no mask exists for it).
Internal render resolution of the 4K movie runs was not printed (`-perf` was off); per CAPTURE.md 2160p output renders at 1920x1080 internal, and the 4K stills run confirms `internal=1920x1080 (auto_display)`.

**Browser.** `npm test` 15/15, `npx vite build` OK, `node tools/ue_char/brute/browser_check.mjs` (headless Chrome, port 5203) spawns `__cmb.debug.fight('b')`, confirms the brute mesh samples `brute_basecolor.webp` (2048x2048) and logs no console errors (screenshot in `round-02/captures/browser_brute_game.jpg`).

## State after round 02 (all else as round 01)

- **UE** (`/Game/Characters`, `/Game/Tests/Characters`, rebuilt from scratch by script, about 40 s headless): hero SK + 79 clips, thug + 5 suits + brute on the hero skeleton, 4 citizens, `M_Char_Suit` (+ lens materials), `ABP_*_Lineup`, plus new `T_Brute_Regions`, `M_Char_IDMask`, `MI_BruteMask`, `M_Char_MaskOther`, `MI_MaskOther`, maps `Char_Lineup` and `Char_Lineup_BruteMask` (test only).
- **Lineup map** `/Game/Tests/Characters/Char_Lineup`: `AWHCharShowDirector` now has 11 shots, 51 s (0 hero turntable 6 s, 1 hero side 5, 2 hero 3/4 5, 3 suit close-up 4, 4 thug 4, 5 brute side 3, 6 citizens wide 5, 7 citizen side 4, 8 citizen 3/4 4, 9 AI suits 5, 10 brute orbit 6).
- **Captures:** `round-02/captures/` (see `round-02/CAPTURES.md`).
- **Not touched in round 02:** hero model/animation, AI suits, citizens, fauna, thug (still the round-01 hoodie/red-bandana texture on the same mesh), all C++.

## Commands

```
# UE content (wipes + rebuilds /Game/Characters and /Game/Tests/Characters; runs the brute painter in 'prep')
tools/ue_char/build_characters_headless.sh                 # all steps, waits while 3+ Unreal instances run
tools/ue_char/build_characters_headless.sh '{"steps":"map","brute_girth":1.2}'   # map only (materials must exist)
unreal/WebHomage/Scripts/build_editor.sh                   # after C++ changes (or after merging the integration branch)
# brute texture alone
tools/ue_char/brute/build_brute.sh                         # webp + PNG + region mask; add --audit-png X.png to audit any map on the thug UVs
python3 tools/ue_char/brute/paint_brute.py --audit-png art/night1/characters/thug/tex/thug_basecolor.png
blender -b -P tools/ue_char/brute/preview_brute.py -- /tmp/pv art/night1/characters/thug/tex/brute_basecolor.png --scale 1.24 --xy 1.2   # Blender stills (Blender's lighting differs from UE)
# captures of the running game (offscreen, every launch waits for < 3 Unreal instances)
tools/ue_char/capture_lineup.sh <out>                      # ONE 51 s 1080p60 -movie run, ffmpeg cuts 7 clips + 4 stills
tools/ue_char/capture_4k_stills.sh <out>                   # 4K stills at 3,8,13,18,21 s + perf json (internal resolution)
# 4K brute test: run_game.sh ... -res 3840x2160 -quit 3.3 -movie -- -WHCharShot=5   on Char_Lineup and on Char_Lineup_BruteMask, then
python3 tools/ue_char/brute/measure_frames.py <beauty_frames> <mask_frames> out.json --step 3 --start 30 --overlay worst.jpg
node tools/ue_char/brute/browser_check.mjs                 # browser brute load check (port 5203)
# live editor (own instance, MCP :8772, python mailbox: tools/ue_char/uebox.py file.py | -c "code"); close it when idle
tools/ue_char/launch_editor.sh ; pkill -9 -f "[c]haracters/unreal/WebHomage/WebHomage.uproject"
# derived sources (git-ignored, regenerated by the build 'prep' step)
python3 tools/ue_char/prep_glbs.py ; python3 tools/ue_char/extract_textures.py ; tools/ue_char/eval/export_citizens.sh
python3 tools/ue_char/suitmaps/run.py --all [--from geom]  # suit PBR bake (Blender, ~2 min/suit)
```

## File map (what P2 owns)

| Path | What |
|---|---|
| `unreal/WebHomage/Scripts/build_characters.py` | Idempotent UE build (steps prep, clean, tex, mat, mesh, citizens, rename, abp, map). Round 02: brute regions texture + mask materials, MI_Brute tint/spec, girth, enemy fill lights, brute orbit shot, mask map (built in the same loop as the lineup map) |
| `unreal/WebHomage/Source/WebHomage/Characters/` | `WHCharAnimInstance`, `WHCharLoopWalker`, `WHCharShowDirector` (unchanged in round 02) |
| `tools/ue_char/brute/` | `uvgeom.py`, `paint_brute.py`, `build_brute.sh`, `preview_brute.py`, `measure_frames.py`, `browser_check.mjs` |
| `tools/ue_char/ue_wait.sh` | Polls every 60 s until fewer than 3 UnrealEditor processes run (owner rule); called by every launcher of mine |
| `tools/ue_char/` | prep/strip GLB, texture extraction, normal convention test, mailbox, launch, headless build, capture scripts |
| `tools/ue_char/eval/`, `tools/ue_char/suitmaps/` | Asset-eval renders, citizen rig/FBX, suit PBR bake |
| `art/night1/characters/` | Derived PNG/FBX only (git-ignored `*.png *.fbx`) |
| `public/assets/enemies/brute_basecolor.webp` | The brute map, now painted on the thug UVs (browser + UE) |
| `docs/night1/characters/` | This file, `round-01/`, `round-02/` |

## Local-only binaries (MANIFEST)

Nothing below is committed. Everything is regenerable.
- `unreal/WebHomage/Content/{Characters,Tests/Characters}`: UE assets (no LFS budget), rebuilt by the headless build. `DerivedDataCache/`, `Intermediate/` and `dist/` were deleted at the end of round 02.
- `art/night1/characters/**/*.png, *.fbx` (about 60 MB).
- `/Users/midir/sm2-n1/_scratch/characters/`: `ueimport/` (webp-free GLBs), `uebox/` (mailbox), `eval/`, `suits/`, `r2/` (round 02: `uvgeom.npz`, previews, 4K measurement frames, capture frames).
- No `.blend` kept.

## Gotchas

Round 01 (still true): UE rejects `EXT_texture_webp`; Interchange scripting needs `AssetImportTask` + `InterchangePipelineStackOverride`; asset names come from the source file; skeletal material arrays come back as copies; skinned materials need `used_with_skeletal_mesh`; `VectorParameter` output is float4; `unreal.Rotator` is (roll, pitch, yaw) and the build's `spawn()` takes `rot = (yaw, pitch, roll)`; `-ExecutePythonScript` quits the editor; zsh does not word-split; below 60 fps the director clock drifts (use `-movie`); round-01 perf is not valid (GPU 91 % busy).

Round 02:
1. **Material sampler types must match the texture.** A texture imported as `linear` (srgb off, character LOD group) is a *Masks* texture: `SAMPLERTYPE_COLOR` and `SAMPLERTYPE_LINEAR_COLOR` both fail to compile and UE silently draws WorldGridMaterial (log line "Failed to compile Material ... Sampler type is X, should be Masks"). Check `-abslog` for that line whenever a material looks grey.
2. **Duplicating a map asset and editing it did not render (black).** Build the twin map in the same loop instead (`for MAP, MASK in variants`).
3. **`unreal.LightingChannels` fields are read-only attributes**: use `chan.set_editor_property('channel1', True)`.
4. **Post-process manual exposure** needs a large `auto_exposure_bias` (about +10 EV or more) for unlit emissive to show; the mask map now uses auto exposure with a black scene and unlit emissive (works).
5. **`pkill -f` matches your own shell** if the pattern is in the command line: use `pkill -f "[c]haracters/..."`.
6. **Movie mode looks brighter than real-time stills** (different exposure convergence); judge colours on the movie frames the critic sees.
7. **Blender headless loads the BlenderMCP add-on** (harmless "unregister" traceback in the log); it does not open port 19891.
8. **Owner rule 2026-09-29:** every Unreal launch `-RenderOffScreen -NoSound`; before launching, count `pgrep -fl "MacOS/UnrealEditor( |$)"` and wait (poll 60 s) while 3 or more run (`tools/ue_char/ue_wait.sh`); close the editor when idle. `capture_lineup.sh` therefore does one launch for all clips.

## Known problems (carried + new)

- **Brute:** face is still the thug's flat painted mask (cartoon eyes, no folds); walks with the hero's walk clip (stiff, wide knees); girth is a uniform X/Y scale (head widens too); browser has no girth.
- **Thug:** unchanged (round-01 critic: flat cartoon eye decals, mitten hands, stiff walk). The painter can be reused for thug variants B/C.
- **Hero:** browser GLB has no TANGENT; lens material is a flat placeholder; no turn lean; the 5.6 m/s loop has no stride warping; the hop is a flat dive. The critic's suit-read notes (coarse weave, painted web lines, flat lenses) are open.
- **Suits:** Qwen faint carved back-logo outline; Tripo UV fragmentation with seam dashes; all five walk in phase.
- **Citizens:** glide in a stand pose in the lineup, long coats stretch, shard/white artifacts on the construction worker and businesswoman, accessories missing in UE.
- **Perf:** one indicative run only: the 4K stills run (`round-02/captures/lineup4k_perf.json`, 18.98 s, 1094 frames, 3840x2160 output, internal 1920x1080): avg 17.35 ms (57.6 fps), p95 21.76 ms, p99 24.65 ms, one 2018 ms hitch, GPU avg 11.8 ms. `ioreg` Device Utilization was 69 % from other sessions right before it, so treat it as an upper bound on frame time, not a measurement of this piece.

## Round 03 should look at

1. The next critic's single biggest gap. Likely candidates from round 01: civilians (real walk cycle with foot lock, kill the shard artifacts), then hero suit read (lenses, web lines, weave scale) and hero run (lean, arm swing, replace the dive hop, desync suit phases).
2. Thug: apply the same UV-role painter approach (new palette, beanie/hood, bandana) and a real face (paint or a sculpted head).
3. Give the brute its own walk (hero walk is used) and, if wanted, mirror girth in `enemy.js`.
4. A perf pass on an idle GPU.
