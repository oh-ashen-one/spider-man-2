# P6 City life: shot list (rounds 02+)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Every capture is the REAL game (`-game`, offscreen, `Scripts/run_game.sh`) inside the GPU lock (`gpu_slot.sh capture`), one map per shot, driven by `docs/night1/life/capture_round.sh <round dir> [warm|stills|clips|detect|perf]`.
Output is 1920x1080 (1080p60 clips, 1080p stills) or true 3840x2160 (4K stills) at `r.ScreenPercentage 100` (native internal resolution, disclosed in `<round>/capture_settings.json`).

| id | what | map | length / time | reference the critic compares with | spec lines |
|---|---|---|---|---|---|
| `S1_street_{1080p,4k}.jpg` | street level in the traffic lanes of the avenue (P1 `city_shots.json` S1 camera), looking along the storefront stretch | `Life_View_S1` | still at game t = 28 s | `refs/streets/street-avenue-hero-taxis`, `street-sidewalk-pedestrians` | C4 cars 5-19, C4 / CH16 people (>= 16 by the brief), CH17 >= 6 looks and no twin heads, C4 traffic light >= 1 |
| `S2_avenue_{1080p,4k}.jpg` | avenue from swing height (P1 S2 camera) | `Life_View_S2` | still at t = 28 s | `refs/streets/street-midtown-high` | C6 vehicles median 14-22 |
| `street_clip_1080p60.mp4` | walking camera (1.8 m eye, 1.5 m/s) in the curb lane of the avenue, sidewalk crowd on the left, oncoming traffic on the right | `Life_Street_Clip` | 18 s (+ 2.5 s warm-up hold, trimmed) | `refs/characters/clips/street-npcs-idle` | CH16 people 8-25 (>= 16 by the brief), CH17, CH19 gait phases, feet |
| `swing_clip_1080p60.mp4` | swing height: camera 30 m over the avenue centre line at 25 m/s heading north, aimed down the avenue | `Life_Swing_Clip` | 10 s (+ hold) | `refs/traversal/clips/swing-avenue-traffic` | C6 vehicles median >= 14 with moving flow in every through-lane |
| `signal_clip_1080p60.mp4` | fixed camera 7.5 m up on the avenue, queue of the two southbound lanes at the signal of street 160: red until clip t = 4 s, then green; lit lenses on the P1 masts | `Life_Signal_Clip` | 10 s (+ hold) | (critic gap 3: queue of >= 3 cars stops at red, pulls away on green, nobody stopped in the box) | signals lit, queue, `junction-box stops` in the probe |

Also written per run: `probe_*.txt` (engine counts, lane motion, queue, box stops, sim ms), `feet_*.csv` (planted-stance ankle displacement), `detector.json` / `detector.txt` (YOLO11x-seg on the stills and every clip frame at 0.5 s, spec instrument settings), `SPEC_TABLE.md`, `PERF_TABLE.md`.
