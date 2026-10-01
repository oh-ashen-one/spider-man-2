# Island (piece A) — HANDOFF (round 01, WORK IN PROGRESS — rewritten at the end of the round)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/island` (from integration 690dfa7), worktree `/Users/midir/sm2-n1/island`, scratch `/Users/midir/sm2-n1/_scratch/island`
(a symlink to the exFAT drive `/Volumes/memory/sm2-n1/island`: exFAT writes `._*` AppleDouble files next to every file — skip them in globs).
Dev port 5208 (Vite, only for exports). Owns `tools/export/*`, `Scripts/build_city.py`, `Scripts/build_manhattan.py`, `Shaders/City/`,
`/Game/City`, `/Game/Tests/City`, `/Game/Maps/Manhattan*`, `docs/night1/island/`.

Round 1 status: see `round-01/README.md` once written. In progress at the time of this note: Midtown 7 x 9 build
(`build_manhattan.py --steps city,traversal,characters,look,map`, log `_scratch/island/logs/build_manhattan2.log`).
