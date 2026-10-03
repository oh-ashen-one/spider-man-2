# Island (piece A) — round 04: merged branch, fire-escape collision, fresh rebuild

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Builder: Claude Opus 5.5 high via Devin, 2026-10-03. Branch `night1/island` (pushed). All captures: REAL game (`-game`, offscreen,
`Scripts/run_game.sh`), map `/Game/Maps/Manhattan_WP`, every Unreal process (commandlets included) inside `gpu_slot.sh capture --label island`.

(sections below are filled in as the round's measurements land)

## 0. Integration merge
`git merge origin/Opus-5.5-Loop-Night-1` at 8b7a8301 (352 commits since aad3ac3: traversal r25 / r26 — new camera, rope material, original
default suit — city r11, terrain r05, characters r17): **no conflicts** (merge commit 70ce4f12). Island-owned files the merge changed:
`Scripts/build_city.py` (city r11: facade F0Scale 0.8 -> 0.25, grazing-angle curtain glass, far-LOD tower / hinterland panel structure,
FarLitK / FarFill, fog start per shot, fabric without distance fields) and `tools/export/far_skyline.py` / `bake_sunmask.py`; the browser
sources (`src/`, `public/`) are unchanged, so the island export is unchanged.
C++ rebuilt with `Scripts/build_editor.sh`: 15.7 s (UBA, 20 actions), `UnrealEditor.modules -> libUnrealEditor-WebHomage.dylib`.

Merged C++ on the round-03 map (telemetry-only sim, same r3 script): identical to the round-03 capture for 648 frames (0.000 m), first
deviation at t = 10.8 s (new traversal); the fire-escape loop at x -235.5 is unchanged by the merge (6 top-out loops, stuck 2.4-8.5 s).
