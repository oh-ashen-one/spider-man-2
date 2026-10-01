# tools/perf_ue: P4 look / perf / capture tooling

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

| file | what |
|---|---|
| `run_perf.py` | real-gameplay perf at 3840x2160: one run per config (`tsr50`, `tsr67`, `native100`, or `name=SP+cvar=val`), CSV profiler + WH_PERF + top GPU passes + GPU utilisation before / during + contamination flag; `--fixed-step` = deterministic hero route; `--reanalyze` recomputes an existing directory |
| `sweep_views.sh` | perf of every static city view under one preset (finds the heaviest view) |
| `make_perf_md.py` | writes `PERF.md` of a round from the run directories |
| `capture_looks.py` | stills (S1..S8 x presets x 4K / 1080p), 60 fps clips (shader warm-up render, 0.8 s pre-roll trimmed), `NOTES.md` (neutral facts) for the critic; runs `night_tests.py` on the night S1 / S6 stills and the night swing |
| `night_tests.py` | night numbers: mean luma / share of pixels < 10 (`still`), light pools in the bottom third (`pools`), hero pixel-box mean luma per frame from the P3 hero-only depth mask (`hero`) |
| `scripts/city_swing_avenue.json` | traversal driver for perf (14 s warm-up, then a swing chain up the avenue) |
| `scripts/city_swing_clip.json` | traversal driver for clips (airborne start, swing chain) |
| `rebuild_city.sh` | P1's city pipeline on P4's own dev port / scratch / editor (never touches P1's) |
| `rebuild_look.sh` | headless `Scripts/build_look.py` (editor closed) |
| `launch_editor.sh`, `job_server.py`, `uejob.py` | P4 editor (MCP 8774, `-RenderOffScreen -NoSound`, waits while 3+ editors run) with a file-based job server; `uejob.py <script.py> [k=v]` runs a Python file in it |

Scratch (never committed): `/Users/midir/sm2-n1/_scratch/look/` (export, textures, job dir, captures). See `docs/night1/look/HANDOFF.md`.
