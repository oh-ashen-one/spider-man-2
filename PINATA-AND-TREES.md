# Pinata & Trees — branch README

> Homage fan project — not an official Marvel game and not affiliated with Marvel, Disney, Sony or Insomniac. We are not trying to make anything copyrighted.

Branch: `pinata-and-trees` (cut from `main` @ `4361e15`, 2026-09-28). Two features from Dan Greenheck's MIT repos (github.com/dgreenheck):

1. **Destruction** with [three-pinata](https://github.com/dgreenheck/three-pinata) — breakable glass, props and car panels.
2. **Better trees + real grass** with [ez-tree](https://github.com/dgreenheck/ez-tree).

## House rules (read first)
- **Never merge to `main`** without the owner's explicit OK. Push this branch; leave merging alone.
- Other sessions are active in this repo on other branches (`water-effects`, `flight-dynamics`, `3d-assets`) — don't touch their worktrees, branches or dev-server ports. Use your own port (e.g. 5193+).
- Renderer is Three.js **r186 `WebGLRenderer`** with a custom multi-pass pipeline (`src/render/pipeline.js`) — no WebGPU/TSL.
- The game has **no physics engine** (deps: `three`, `postprocessing`, `n8ao`). Collision is a custom grid (`src/world/collision.js`) with `world.raycast` / `world.groundHeight`.
- Target: 60 fps on the Mac Studio (M3 Ultra) at `?q=high`; `?q=low` must stay playable. `?prof=1` shows per-pass GPU ms.
- Keep MIT attribution: header comment `// Adapted from dgreenheck/<repo> (MIT, © Daniel Greenheck)` on vendored/ported files + a `THIRD_PARTY.md` entry.

## Screenshot harness
`?shot=<name>` renders a deterministic composition (`src/shots.js`, 90 fixed frames then `window.__shotReady`). The `water-effects` branch added a headless capture tool — copy it over rather than rewriting:
```bash
git checkout origin/water-effects -- tools/shot.mjs      # + npm i -D playwright-core
node tools/shot.mjs street swing    # -> shots/<name>.png (starts its own Vite on a free port, headless installed Chrome)
```
Add your own shots (e.g. `parkHigh`, `parkLow`, `glassBreak`) and commit before/after captures in `docs/pinata/` and `docs/trees/`.

---

## Part 1 — Destruction (three-pinata)

**Library:** `npm i @dgreenheck/three-pinata` (2.0.1, MIT, peer `three >=0.158` → fine on r186). Plain CPU three.js.
- Voronoi fracture in 3D and **2.5D** (fast; best for flat things like glass panes, signs, panels), impact-point concentration, re-fracture, plane slicing, separate interior-face material.
- Limits: meshes must be **watertight**; full 3D Voronoi is slow and synchronous → pre-fracture at load/idle time or run in a Web Worker; pool fragments.
- Reference: `demo/src/scenes/GlassShatterScene.ts` in the repo (the demo uses Rapier physics — we don't have to).

**Where it fits in our game**
- Combat props already exist: `src/game/combat/props.js` (litter bin, crate, oil drum thrown at enemies). → Shatter crates/bins on impact instead of just disappearing.
- Street props are procedural in `src/world/props.js` (lamppost, hydrant, trash can, bench, newsstand, planter, mailbox, bus-stop sign, hotdog cart…). → Pick a few "breakable" kinds; swap the instanced prop for a pre-fractured copy on a hard hit.
- Glass: facades are a shader (`src/world/facade.js`), not real panes — don't fracture buildings. Instead: storefront/bus-shelter/phone-booth panes and car windows as separate quads → 2.5D shatter on web-zip impact / hard landing / thrown prop.
- Cars: `src/world/vehicles.js` + `vehinst.js` (instanced). → Door/hood/window pieces break off on a thrown-car/prop hit.
- Particles for dust/sparks already exist: `src/game/combat/fx.js` (`class Particles`, pooled GPU billboards). Reuse for glass glitter + debris dust.

**Suggested steps**
1. Install, prototype one breakable crate in combat (`props.js`): pre-fracture 12–20 pieces at load, swap on impact, simple custom physics (gravity + ground via `world.groundHeight` + damping + spin), fade/despawn after ~6 s, pool.
2. Glass: bus-shelter / storefront pane quads → 2.5D shatter at the impact point, glitter particles, glass SFX.
3. Street props: 3–4 breakable kinds (hydrant → also a water jet later, bench, newsstand, sign).
4. Cars: detachable panels/windows on heavy hits.
5. Budget: cap live fragments (~300), instanced where possible, no allocations per frame. Verify `?prof=1` in a big fight.

---

## Part 2 — Trees + grass (ez-tree)

**Library:** `@dgreenheck/ez-tree` — **use the GitHub v2.0 source**, not npm (npm is still 1.1.0; v2 adds LODs, `createGeometry(detail)`, PBR, bring-your-own textures). Vendor `src/lib/` (~1.6k lines) into e.g. `src/world/eztree/`.
- WebGL, GLSL via `onBeforeCompile` on `MeshStandardMaterial` — plays fine with our pipeline/n8ao.
- 16 presets (`src/lib/presets/`): ash/aspen/oak/pine S/M/L, 3 bushes, trellis. Seeded = deterministic.
- Assets: bark = CC0 (ambientCG), leaf PNGs = MIT (`src/app/public/textures/LICENSE.md`).
- Measured (r186): 3.6k–22k tris/tree full detail, far LOD 0.6k–5.4k; 1–9 ms to generate; 2 draw calls/tree (4 with shadows).
- **Bugs to fix when vendoring:**
  - Leaf wind patch replaces `#include <project_vertex>` and **drops `instanceMatrix`** (`tree.js:1051-1066`) → every `InstancedMesh` instance lands at the origin. Re-add the instance transform.
  - Wind noise is sampled in local space → all instances sway in sync. Add a per-instance phase (instance attribute or hash of instance position).
  - Wind isn't in the shadow pass (no `customDepthMaterial`) → add one with the same vertex wind.
  - Bark doesn't sway.
- Bonus in the demo app (MIT): instanced wind grass `src/app/grass.js` (5k–25k instances), skybox gradient — grass is the valuable part.

**What we have today (don't lose it)**
- `src/world/trees.js` (822 lines): procedural instanced trees — kinds `street`, `park`, `elm`, `small`, `conifer`; swept-tube trunks with bark array (`treetrunk.js`), alpha-tested leaf-cluster cards with sway, autumn two-tone tint, canopy self-occlusion, 3 LODs (cards <~130 m → lumpy crown → blob), distance `Pool`s, trunk collision (`addSolids`).
- Far shores use cheap icosahedron canopy blobs (`canopy.js`); roof gardens are atlas cards (`roofplants.js`).
- Grass = shader-only lawn (`createGrassMaterial` in `src/world/ground.js` ~line 685). No blades.
- Park layout: `G.PARK` in `src/world/layout.js`, `PARK_SITES`/`PARK_ROCKS` in `park.js`, ponds `PARK_WATER`.

**Suggested steps**
1. Vendor ez-tree v2, fix the 3 bugs, write a tiny test scene/shot comparing an ez-tree oak vs our `park` tree at the same camera.
2. Archetypes: at load (or baked to GLB offline via its exporter), generate ~12–20 trees — street trees (London plane / honey locust look: use ash/oak presets tuned), park oak/elm, conifers — a few seeds each. Autumn tint like today.
3. Instancing: one `InstancedMesh` per archetype × material × LOD band, per-instance wind phase + tint; plug into the existing `Pool` distance system and trunk colliders so gameplay/collision doesn't change. Beyond ~400 m keep our cheap crowns/blobs (or octahedral impostors).
4. Budget: ~1,000 street trees would be 3–4 M tris if all drawn at LOD1/2 → per-block frustum culling or `BatchedMesh` is required. Central Park: ~300–600 trees.
5. Grass: port `grass.js` blades for Central Park lawns near the camera (fade to the existing shader lawn with distance), wind matched to the trees.
6. Before/after shots from swing height and street level, `?prof=1` on high + low.

---

## Deliverables
- Pushed branch with both features behind quality gates (`src/render/quality.js`, `?qset=`), before/after captures, perf notes, THIRD_PARTY attribution, and this README updated with what was done + known issues.
