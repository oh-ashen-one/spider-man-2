# Third-party code and assets

## three-pinata — MIT, © Daniel Greenheck
- Source: https://github.com/dgreenheck/three-pinata — npm `@dgreenheck/three-pinata@2.0.1` (dependency, not vendored).
- Used for: Voronoi fracture (3D and 2.5D) of breakable props, glass panes, crates and bins
  (`src/game/destruction/fracture.worker.js`, run in a Web Worker).

## ez-tree — MIT, © Daniel Greenheck
- Source: https://github.com/dgreenheck/ez-tree @ v2.0.0 (`dcf309b`, 2026-07-16).
- Vendored: `src/lib/*` -> `src/world/eztree/` (tree generator, options, presets as JS modules, trellis). Local
  changes are marked `(pat)` and listed in the header of `src/world/eztree/tree.js` (instanced wind fix, per-instance
  wind phase, wind in the shadow pass, bark sway, metric bark UVs, Uint32 indices). License: `src/world/eztree/LICENSE`.
- Ported: the instanced wind grass of the demo app (`src/app/grass.js`) -> `src/world/grass.js` (rewritten for
  camera-anchored GPU instancing; its simplex wind code kept).
- Assets: leaf-spray textures of the demo app (`src/app/public/textures/leaves/{ash,oak,pine,aspen}.png`, project
  license, MIT) -> `public/assets/eztree/leaves/`. The ambientCG bark textures of the demo are **not** used (the city's
  own bark array is).
