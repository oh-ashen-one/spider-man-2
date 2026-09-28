# Water Effects — branch README

> Homage fan project — not an official Marvel game and not affiliated with Marvel, Disney, Sony or Insomniac. We are not trying to make anything copyrighted.

Branch: `water-effects` (cut from `main` @ `4361e15`, 2026-09-28). All water work happens here. **Never merge to `main` without the owner's OK.** Other sessions are active in this repo on other branches (`flight-dynamics`, `3d-assets`) — don't touch them.

Goal: take the river / harbour water from "pretty flat mirror" to interactive, living water — waves, splashes, swimming/diving, underwater — by porting techniques from Dan Greenheck's open-source repos (github.com/dgreenheck).

---

## 1. Where our water is today

Renderer: Three.js r186 **`WebGLRenderer`** (not WebGPU) with a custom multi-pass pipeline (`src/render/pipeline.js`). Anything WebGPU/TSL/WGSL must be ported to GLSL.

| Area | Current state | Files |
|---|---|---|
| Surface | One flat 300 km plane at `WATER_Y = -1.6`, 16×16 segs, **no vertex waves** | `src/world/water.js` |
| Shading | `MeshStandardMaterial` + `onBeforeCompile`: scrolling normal map (4 near + 2 far scales), calm patches/gusts/current streaks, distance roughness, sun glitter, grazing-angle sky refetch | `water.js:19-178` |
| Reflections | Planar mirror @ 1/3 res, only layers 27/28, 8-tap ripple blur + haze; skipped at street level >260 m from shore; river opts out of SSR (`NO_SSR`) | `water.js:181-226` |
| Shoreline | Baked distance-to-shore texture → silty tint, pale wash line, calmer edges. No real foam. Wet/algae bands on seawalls | `water.js:231-360` |
| Park ponds | Same material, SSR enabled | `src/world/ground.js:1382`, `layout.js:177` |
| Boats | 5 box-hull `InstancedMesh`es, sine bob, flat textured Kelvin-V wake quads | `src/world/boats.js` |
| Player + water | **Can't swim/dive.** Below y=-1.0 `waterBounce()` web-yanks him to dry land; `waterSplash` event only shakes the camera. No splash VFX, no sound, no underwater | `src/player/traversal/traversal.js:512-541`, `src/player/player.js:170` |
| Particles | Only system is combat billboards (900 additive + 300 alpha pools, canvas atlas) — **reusable for splashes** | `src/game/combat/fx.js:78` |
| Birds | Pigeon flocks only, no gulls | `src/world/npc/pigeons.js` |
| Shots harness | `?shot=<name>` = 90 fixed frames then `window.__shotReady`. **No water shot exists yet** | `src/main.js:86-99`, `src/shots.js` |
| Quality | `?q=low|med|high`, `?qset=k:v`, `?prof=1` per-pass GPU ms | `src/render/quality.js` |

Geography: Manhattan ~6.8 × 1.45 km; Hudson west, East River east, harbour south; rivers ~0.5–1 km wide.

---

## 2. Research: what we can use from dgreenheck's repos

Licenses verified by reading the LICENSE files (2026-09-28).

### Integrate fully (MIT, works on WebGL r186)
- **three-pinata** — `npm i @dgreenheck/three-pinata` (2.0.1, MIT, peer `three >=0.158`). Real-time Voronoi fracture/slicing (2.5D glass shatter, impact-point concentration). → Breakable glass/props/cars. **Not water — do it on its own branch.** ~2–3 days prototype.
- **ez-tree** — MIT, 16 presets, CC0 bark. Use the unpublished **v2.0** from GitHub (`src/lib/`, has LODs); npm is still 1.1.0. Bug: its leaf wind patch drops `instanceMatrix` (`tree.js:1051-1066`) — one-line fix for `InstancedMesh`. We already have procedural trees (`src/world/trees.js`), so this is a quality upgrade + blade grass (`src/app/grass.js`). **Own branch.** ~3–5 days.

### Port the techniques (MIT) — the water plan
**tidewater** (MIT) has the best water, but it is a custom **raw WebGPU/WGSL engine, not Three.js** — nothing drops in. Port the math to GLSL:

| Take | File (tidewater `src/`) | Gives us | Port |
|---|---|---|---|
| Water shading | `ocean/WaterMaterial.js` (741) | Exact Fresnel, GGX sun glint, Cox-Munk distance roughness, refraction to riverbed + Beer-Lambert absorption, horizon-limited SSR | Moderate — pure fragment math |
| Sea variation | `ocean/SeaDetail.js` (173) | Gust patches, calm slicks, wind foam lines — texture-free, reads great from swing height | Near drop-in |
| Underwater | `post/Underwater.js` (434) | Waterline split-screen, meniscus, absorption, light shafts | Moderate (post pass) |
| Lens drops | `post/LensDroplets.js` (158) | Droplets on camera after surfacing | Easy |
| Caustics | `ocean/Caustics.js` (303) | Photon-splat caustics on riverbed/pilings | Moderate (vert/frag, WebGL OK) |
| Spray look | `fx/Spray.js` (827) | Spray sprite shading (sim itself uses compute → rewrite) | Take shading only |
| Water LOD | `core/CDLOD.js` (318) | Crack-free morphing instanced grid for a far-reaching wave mesh | Moderate |
| Gulls | `world/Gulls.js` (118) | Vertex-shader-animated gulls | Easy |

**Skip:** `OceanFFT` / `WakeSim` (compute-heavy, hard rewrite), beach surf systems (`ShoreWaves`, `Breakers`, `SurfFoam` — NYC is seawalls), clouds/atmosphere (compute LUTs).

### Can't use
- **threejs-particle-fluids** — MIT but WebGPU-only (atomics, storage textures), no WebGL fallback, pins three `<0.185`. Revisit only if the game ever moves to `WebGPURenderer`.
- **No license (learn only, don't copy code):** threejs-boids, minecraft-threejs-clone, moonshot, spooky-eyeball.
- **simcity-threejs-clone** — MIT code, but its models have no provenance; borrow the traffic-graph idea only.

Get the source locally to read:
```bash
mkdir -p ~/dg && cd ~/dg
for r in tidewater ez-tree three-pinata threejs-particle-fluids; do git clone --depth 1 https://github.com/dgreenheck/$r.git; done
```

When porting MIT code, keep attribution: add a header comment `// Adapted from dgreenheck/tidewater (MIT, © 2026 DRG Software Solutions LLC)` and list it in a THIRD_PARTY notes file.

---

## 3. Next steps (in order)

Each step: add/extend a `?shot=` water preset first, capture a **before**, build, capture an **after**, check `?prof=1` cost on `high` and `low`.

0. **Water shots harness.** Add `?shot=riverHigh` (swinging height over Hudson), `?shot=riverLow` (street-level at seawall), `?shot=riverSunset` (glint) to `src/shots.js`. Baseline screenshots before touching anything.
1. **Waves + shading.** Add Gerstner waves (4–6 summed, displaced in vertex shader, analytic normals) to the plane in `water.js`; needs a denser near-camera grid (start with a camera-following ring grid, CDLOD later). Port `WaterMaterial.js` Fresnel / GGX glint / roughness / absorption into our `onBeforeCompile`. Keep the planar mirror; sample it with wave-perturbed UVs.
2. **Sea detail.** Port `SeaDetail.js` gusts/slicks/foam lines; merge with our existing calm-patch/streak noise instead of stacking both.
3. **Splashes + ripples.** On `waterSplash`: crown-splash burst + spray using `combat/fx.js` Particles (spray shading from `Spray.js`), splash SFX, and a small ripple heightfield (ping-pong render target around the player) that perturbs water normals. Boats get the same ripple stamp.
4. **Swim / dive / underwater.** Replace `waterBounce()` yank with a swim state (surface swim + dive). Port `Underwater.js` as a pass in `pipeline.js`, `Caustics.js` on riverbed/pilings, `LensDroplets.js` on surfacing. Needs a riverbed mesh (currently none) — simple dark-silt plane + a few props.
5. **Shore foam + wakes.** Real foam at seawalls using the distance-to-shore texture + wave crests; upgrade boat wakes from flat quads to analytic Kelvin wake displacement.
6. **Gulls.** Port `Gulls.js`, spawn over rivers/harbour.
7. **Quality tiers.** Gate waves density, SSR, caustics, underwater shafts per `quality.js` tier; verify `low` still hits 60 fps.

Out of scope for this branch (own branches later): three-pinata destruction, ez-tree trees + grass, flocking birds rewrite, traffic.

---

## 4. Running it

```bash
git fetch origin && git switch water-effects   # or: git clone https://github.com/oh-ashen-one/spider-man-2.git && git switch water-effects
npm install
npx vite --port 5192 --host 127.0.0.1   # 5173/5191 may be taken by other sessions on the Studio
# open http://127.0.0.1:5192/?shot=street   (add &prof=1 for GPU timings, &q=low to test low tier)
```
