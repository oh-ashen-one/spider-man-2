# P5 combat, round 04: notes (NO CAPTURE: the GPU was wedged for the whole session)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Builder: Claude Sonnet 5.5. Branch `night1/combat`. Target of the round (critic r03 "biggest gap"): replace the opaque orange hit disc with an additive burst that keeps the victim readable
(4-8 radial streaks, each >= 8 % of the frame width, <= 35 % of the bounding circle filled, victim keeps >= 60 % of its Sobel energy over contact frames 1-5) and make every blow move the victim
(>= 0.5 m or >= 30 deg within 0.3 s, all 33-34 hero blows of fight30, victim visible).

**Nothing in this round has been rendered.** Code and tools are built (C++ compiles, `build_editor.sh` OK), `measure_r04.py --selftest` passes on synthetic frames, and the capture chain is written and
was queued, but `gpu_slot.sh` refused every launch from 07:29 to the end of my session: two other agents' engines (pids 17555 and 17831) sat in state `?E` (stuck exiting inside the GPU driver) since 06:54, the GPU
read 100 % with no engine running, and the lock does not start an engine while one is stuck exiting (RULES.md, 23:08 kernel panic). I did not bypass it. See "Hazards".

## What was implemented (unverified on screen)

| item | where | what |
|---|---|---|
| starburst | `WHCombatFx::Impact` | No disc, no halo sphere, no `Hit()` sparks. N = 6 (7 for Heavy >= 0.25, 8 for >= 0.55) streaks, random phase, +-18 % angular jitter, each lying in the camera's image plane (`SetCam(P, fov, rot)`), from 0.030 U to 0.128-0.16 U where U = the frame width in metres at the contact's depth (streak length 0.098-0.127 U = 9.8-12.7 % of the frame width), 6 stacked cylinders per streak (width 0.0094 U -> 0.0036 U, orange -> red-orange, HDR 2.4 -> 1.5), material `M_CmbFlare` (additive, unlit, no depth test), hot core 0.035 U. Hollow centre: only the small core sits on the victim's chest. Own RNG, so `-WHCmbFlare=0` removes the starburst and changes nothing else. Static for the 5-frame hold, faded over 2.3 frames (gone by frame 8), as r03. Expected: fill of the bounding circle ~8 %, share of the frame ~0.5 %. I projected the geometry with the recorded r03 cameras (numpy): every streak is 10.0 % of the frame width at L = 0.1 U. |
| victim recoil | `WHEnemy` (`StartTwist`, `SyncActor`) | Every blow (all paths of `Hit()`) also starts a lean of the whole body about the knees (0.45 m): `RecAmp` = max(0.62, 0.7 x twist) rad = 35-50 deg, 65 % of it in the contact frame, peak at 0.1 s, upright again by 0.56 s, direction = the blow's, biased 45 deg towards the screen side the blow points to (the camera's right axis is passed in `FWHHitIn::CamRight`) so it reads from the game camera. Composition `Rec * Twist * Tilt`; the transform was checked numerically (head moves along the lean direction, feet swing the other way by ~0.3 m). `TiltNow` (deg) is logged per enemy in `fight_frames.jsonl`. |
| logs | `WHCombatDirector` | `WH_CMB_RES` (output size, `r.ScreenPercentage`, internal resolution) at frame 40; `WH_CMB_FLARE` per starburst (streaks, depth, frame width, fov). Flags: `-WHCmbFlare=0`. |
| sim | unchanged | Recoil, starburst and logging are visual only. The frozen script `scripts/fight30.json` must still replay `round-03/ue/record` event for event (381 / 381): `final_r04.sh` checks it for both movies and the stills. |

## Tools written this round

- `measure_r04.py`: streak count / length / fill of the flare from the exact pixel difference against a no-flare rerun (`-WHCmbFlare=0`), Sobel retention of the victim box (total energy vs the frame before the
  contact, and edges retained against the same frame without the flare), fade and stillness of the flare, CB2 (`push03`, `turn03` = max(yaw change, tilt change) within 0.3 s). Self-test: `--selftest`.
  On the r03 footage (heuristic red-orange mask, no rerun) it gives the baseline in the last section.
- `react_metrics.py`: `tilt03`, `turn03`, `move_or_turn`. `final_r04.sh` (ONE gpu hold: map, movie A, movie B, 15 native stills), `package_r04.sh`, `critic_pack_r04.sh`, `run_fight.sh` (`WHCMB_EXEC`, run timeout 5400 s).
- `SPEC.md`: CB2 / CB3 rewritten, CB14 (victim readability) added. `SHOTLIST.md`: r04 stills and the no-flare rerun.

## Baseline of the r03 disc with the r04 method (published mp4, heuristic mask; `measure_r04.py` on `round-03/`)

43 contacts (34 hero blows + 9 hits on the hero). Victim Sobel energy in contact frames 1-5 against the frame before the contact: 35 / 43 keep >= 60 % (min 0.40); flare share of the frame median 2.3 %; bounding-circle
fill up to 0.62 (the disc); victim box covered by the flare up to 80 % of its pixels. CB2 from the sim record: 34 / 34 (push min 0.52 m, yaw min 36.8 deg), body tilt not yet logged in r03.

## Hazards (for the orchestrator)

- At 07:27 my r03 engine (pid 10060, SIGTERMed at 07:09) was still blocked in `FMetalSyncPoint::Wait` (a screenshot read-back) inside the wedged GPU; it finally exited at ~07:30 and produced its mp4. I killed only my own stopped
  `gpu_slot.py` (49574) and chain bash (9165) afterwards, as the r03 handoff said.
- Pids 17555 / 17831 (`UnrealEditor`, other agents) are `?E` since 06:54 (>= 2 h 40 min) and the GPU has read 100 % the whole time with 0 live engines. `gpu_slot.sh` waiters (traversal, look, perf, city, characters) gave up or kept waiting.
  Probably only a reboot clears it. I did not launch anything, did not probe the GPU (a probe killed mid-work could become another `?E`), and did not touch anyone's process.
