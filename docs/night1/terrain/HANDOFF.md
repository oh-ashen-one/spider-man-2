# Terrain (piece E) — HANDOFF (round 01, WIP)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/terrain` (pushed), worktree `/Users/midir/sm2-n1/terrain`, scratch `/Users/midir/sm2-n1/_scratch/terrain`, dev port 5209 (Vite, exports only),
UE MCP port unused (headless commandlets only). Owns `/Game/Terrain`, `tools/export/{export_terrain.mjs,collect_terrain.js,gen_terrain_shaders.mjs}`,
`tools/terrain/`, `unreal/WebHomage/Scripts/build_terrain.py`, `unreal/WebHomage/Shaders/Terrain/`, `docs/night1/terrain/`.

## State
- Round 1 in progress: exporter / prep / shader generator / UE builder written; first GPU-locked build + captures pending in the lock queue (cap 1).
- Rebuild recipe (CPU steps need no slot): `node tools/export/export_terrain.mjs` (dev server `npx vite --port 5209 --host 127.0.0.1 --strictPort` first),
  `python3 tools/terrain/prep_terrain.py`, `node tools/export/gen_terrain_shaders.mjs`, then `build_terrain.py` as a headless `-run=pythonscript` commandlet
  through `gpu_slot.sh capture --label terrain` (needs the base Manhattan content: `build_manhattan.py` steps city/traversal/look/map).
