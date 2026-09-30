# P5 Combat: numeric spec and checkers (r02)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Source: the round-01 blind critic (`critic/round-01-CRITIC.md`, pixels only, against the private reference clips
`refs/combat/clips/*` and stills `refs/combat/*.jpg`) plus `CH11` in `docs/night1/characters/SPEC.md`. Every line names the script that measures it. Numbers are
written into the round folder (`round-NN/measure.md`, `measure.json`, `sim_metrics.json`).

| id | axis | target | checker | reference evidence |
|---|---|---|---|---|
| CB1 | hit-stop on every contact | the victim crop changes by < 1.0 (mean abs gray diff, 480x270) for >= 3 consecutive frames at 60 fps after each contact | `measure_r02.py` (`contacts_frozen_ge3` / `contacts`) | street-combo: refs hold frames on hits (0.3-2.7 % of frames below diff 0.3) |
| CB2 | victim reaction | victim feet displaced >= 0.3 m within 0.5 s of every hero blow; flinch pose already in the contact frame | `measure_r02.py` (`push_m`, `flinch_diff`) | street-combo @0.5-1.5 |
| CB3 | impact flash | new near-white area in the contact frame <= 3 % of the frame; ~0 six frames later | `measure_r02.py` (`spark_area`, `spark_area_f6`) | r01 disc was ~12 % of frame width |
| CB4 | aggression | longest gap between attack starts (melee / brute wind-up, gun aim) <= 1.0 s in a 30 s fight | `sim_metrics.py`, `measure_r02.py` (`max_attack_gap_s`) | plaza-fight, night-street-fight |
| CB5 | telegraph | every attack shows an indicator >= 0.4 s before the blow; gunmen show an aim line before they fire | `measure_r02.py` (`min_warning_lead_s`), stills | r01: none over any attacker |
| CB6 | enemies in frame | >= 5 standing enemies (>= 5 % of frame height, centre inside the frame) on screen in >= 80 % of frames (CH11) | `sim_metrics.py`, `measure_r02.py` (`enemies_ge5_frac`) | street-combo median 7, street-fight-cars 8 |
| CB7 | combat camera | mid-high, 4-6 m back, pitched down 15-25 deg; hero box >= 5 % from every frame edge in 100 % of frames | `sim_metrics.py`, `measure_r02.py` (`hero_margin_ge5_frac`) | group-fight-nm, street-fight-cars |
| CB8 | occlusion | no prop or enemy occludes more than 15 % of the frame (hero box overlap, nearer than the hero) | `measure_r02.py` (`occluder_max_pct`) | - |
| CB9 | camera continuity | no snaps: whole-frame diff <= 25 between two frames | `measure_r02.py` (`snaps`) | r01 had one at 25.8 |
| CB10 | move set | jab combo, dodge (flip), launcher + air juggle >= 3 hits, web shots, web strike to the enemy, web-pin, finisher with a camera beat | `fight_events.jsonl` (`summary.json`: `air_hits`, `finishers`, `web_hits`, `launches`) | critic r01 "missing" list |
| CB11 | brute silhouette | the brute reads as bulkier than a thug at a glance (>= 1.3x shoulder width in the frame) | stills (hand read); CH15 is a design choice, not a ref line | - |
| CB12 | throughput | fixed-step replay is deterministic: the frozen script's event log equals the record run's | `compare_logs.py` / event diff | - |

Not measured here (owned elsewhere or not ported): frame time (F, `gpu_slot.sh perf` only), audio, HUD, throwables, the Space jump-evade.
