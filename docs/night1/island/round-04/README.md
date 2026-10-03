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

## 1. Fire escapes: collision = the drawn landings (round-03 critic's biggest gap)
Round 03: each fire escape was ONE solid (QueryOnly, cooked triangles): landings, 1.05 m railing planes, stair flights, drop / roof ladders.
On r3 the hero swung into the escape at x -235.5 / y 616.4 (west facade of the block x -234 .. -206, roof 37.8 m, cornice 37.9-39.05 m,
belt course 33.84-34.20 m; landings every 3.7 m from 6.1 to 35.7 m): 6 top-out loops from t = 2.4 s, stuck to 8.5 s.
Round 04 (`tools/export/street_kit.py` `fire_escape`, 8,562 fire escapes / 58,770 landings island-wide):
* **solid** (`fireescape__t*` tiles, traversal solids with their own triangles): ONLY the landings: grating top + underside, front lip beam
  and side beams; every landing has an **open well**: the flight arriving from below comes up through a 1.5 m x 0.70 m opening, the lowest
  landing has a 0.6 m x 0.5 m **drop-ladder hatch** (58,770 wells / hatches);
* **visual only** (moved into the `streetkit__t*` tiles, which are on the traversal's exclusion list): railings, brackets, stair flights,
  stringers, drop and roof ladders, and a wall angle + inner frame rail;
* the landing grating (drawn and solid alike) starts **0.40 m off the wall** (r03: 0.02 m): a 0.38 m slot along the facade. Reason, measured
  below: the traversal's wall-run "wall top ahead" probe looks ~0.6 m inward of the hero; a landing reaching the wall is a "wall top" for a hero
  running up the facade under it, and the run top-out (fixed 11.5 m/s hop, ~3.5 m) cannot clear the landing 3.7 m above.

Sim evidence (telemetry-only, `-nullrhi`, fixed 1/60 s step, merged C++; tiles -2_2 / -1_2 / 0_2 patched with `build_manhattan.py --steps fepatch`
on the round-03 map), checker `tools/export/island_fe_check.py` (from t = 2.4 s):

| variant | top-outs at the r03 spot | 1 s windows < 3 m at the spot | hero at t = 3.5 s | free of the spot |
|---|---|---|---|---|
| r03 layout, merged C++ (`sim_base`) | 6 loops | 2.4-8.5 s | x -235.44, z 33.5 | 8.7 s |
| r04a: landings solid to the wall, railings / stairs visual-only | 3 (loops 2) | 2.4-4.4 s | x -235.01, z 34.0 | 4.9 s |
| V1 diagnostic: whole escape visual-only | 2 (belt course 34.2 m, then cornice) | none | x -234.5, z 37.4 | 3.9 s |
| **r04 final: landings solid from 0.40 m off the wall** | **0** | **none** | **x -218.1, z 46.1 (swinging east)** | **2.7 s (wall kick + release)** |
