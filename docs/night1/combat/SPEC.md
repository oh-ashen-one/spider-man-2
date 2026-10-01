# P5 Combat: numeric spec and checkers (r03)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Source: the round-01 blind critic (`critic/round-01-CRITIC.md`, pixels only, against the private reference clips
`refs/combat/clips/*` and stills `refs/combat/*.jpg`) plus `CH11` in `docs/night1/characters/SPEC.md`. Every line names the script that measures it. Numbers are
written into the round folder (`round-NN/measure.md`, `measure.json`, `sim_metrics.json`).

| id | axis | target | checker | reference evidence |
|---|---|---|---|---|
| CB1 | local hit-stop on every hero blow (r03) | freeze ONLY the hero and the victim for 5 frames (3-5 allowed) at 60 fps, the camera keeps a 2-4 px shake and the world keeps running: the victim crop (fixed box of the contact frame + 25 %, 480x270 gray) changes by < 1.0 for >= 3 consecutive frames after each contact **while the whole-frame diff is >= 1.0**; whole-frame frozen frames (diff < 0.3) <= 3 % (r02: 7.3 %) | `measure_r03.py` (`good_run_ge3` / `hero_blows_measured`, `whole_frozen_pct_30fps`, `whole_diff_in_hold_min`) | critic r02 "biggest gap"; street-combo (refs hold 0.3-2.7 % of frames below diff 0.3) |
| CB2 | victim reaction (r03) | victim rotates >= 30 deg (visual yaw = actor yaw + hit twist) and its root moves >= 0.5 m (3D) within 0.3 s of every hero blow; heavy / finisher / launcher blows on a non-armoured victim throw it >= 2 m (within 1 s); flinch pose already in the contact frame | `react_metrics.py` (per blow: `push03`, `rot03`, `dmax1`), `measure_r03.py` (`flinch_diff`) | critic r02: "the victim @13.25-13.65 barely moves over 24 frames" |
| CB3 | impact flare (r03) | additive red-orange flare covering 1-3 % of the frame at its peak, static through the hit-stop, gone by frame 8 (area <= max(0.5 %, 20 % of the peak) 8 frames after the contact frame) | `measure_r03.py` (`flare_peak`, `flare_f8`: pixels with dR >= 45, dR - dB >= 35, dR >= dG against the frame before the contact, in a window around the victim) | critic r02: "the sparks are 2-px ticks"; r01 disc was ~12 % of frame width |
| CB4 | aggression | longest gap between attack starts (melee / brute wind-up, gun aim) <= 1.0 s in a 30 s fight | `sim_metrics.py`, `measure_r03.py` (`max_attack_gap_s`) | plaza-fight, night-street-fight |
| CB5 | telegraph | every attack shows an indicator >= 0.4 s before the blow; gunmen show an aim line before they fire | `measure_r03.py` (`min_warning_lead_s`), stills | r01: none over any attacker |
| CB6 | enemies in frame | >= 5 standing enemies (>= 5 % of frame height, centre inside the frame) on screen in >= 80 % of frames (CH11) | `sim_metrics.py`, `measure_r03.py` (`enemies_ge5_frac`) | street-combo median 7, street-fight-cars 8 |
| CB7 | combat camera | mid-high, 4-6 m back, pitched down 15-25 deg; hero box >= 5 % from every frame edge in 100 % of frames | `sim_metrics.py`, `measure_r03.py` (`hero_margin_ge5_frac`) | group-fight-nm, street-fight-cars |
| CB8 | occlusion | no prop or enemy occludes more than 15 % of the frame (hero box overlap, nearer than the hero) | `measure_r03.py` (`occluder_max_pct`) | - |
| CB9 | camera continuity | no snaps: whole-frame diff <= 25 between two frames | `measure_r03.py` (`snaps`) | r01 had one at 25.8 |
| CB10 | move set | jab combo, dodge (flip), launcher + air juggle >= 3 hits, web shots, web strike to the enemy, web-pin, finisher with a camera beat | `fight_events.jsonl` (`summary.json`: `air_hits`, `finishers`, `web_hits`, `launches`) | critic r01 "missing" list |
| CB11 | brute silhouette | the brute reads as bulkier than a thug at a glance (>= 1.3x shoulder width in the frame) | stills (hand read); CH15 is a design choice, not a ref line | - |
| CB13 | camera hit shake (r03) | 2-4 px (1080p) displacement during the hold: a roll + zoom pulse, proportional to the distance from the frame centre (so the bodies near the middle stay still); the shake is logged per frame (`shk`) | `measure_r03.py` (`shake_px_max`) | critic r02: "keep the camera shaking by 2-4 px" |
| CB12 | throughput | fixed-step replay is deterministic: the frozen script's event log equals the record run's | `compare_logs.py` / event diff | - |

Not measured here (owned elsewhere or not ported): frame time (F, `gpu_slot.sh perf` only), audio, HUD, throwables, the Space jump-evade.
