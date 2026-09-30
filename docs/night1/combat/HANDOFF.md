# P5 Combat: handoff after round 04 (PROVISIONAL: written while the capture was still waiting for the GPU; the final version replaces it)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/combat`, worktree `~/sm2-n1/combat`. UE MCP port 8775, dev port 5206; nothing here uses the editor or MCP: everything is headless commandlets plus `-game`. P5 owns
`Source/WebHomage/Combat`, `/Game/Combat`, `/Game/Tests/Combat`, `Scripts/build_combat.py`, `docs/night1/combat/`. Scratch: `/Users/midir/sm2-n1/_scratch/combat/` (r04 work: `r04/final1`).

## State when this text was written (07:57 EDT)

- Round 04 code is built and pushed (branch `night1/combat`): starburst flare + victim recoil lean + `WH_CMB_RES` / `WH_CMB_FLARE` log lines + `measure_r04.py` + `final_r04.sh` + `package_r04.sh` + `critic_pack_r04.sh`.
- **No round-04 capture exists yet**: the GPU has been wedged since 06:54 (two other agents' `UnrealEditor` pids 17555 / 17831 stuck exiting in the driver, `?E`, GPU at 100 % with no engine running), so `gpu_slot.sh`
  refuses every launch ("UnrealEditor pid 17555 stuck exiting"). My capture chain `final_r04.sh` is queued behind the lock (see below for how to run / cancel it).

## What round 04 changed (all untested on screen until the capture exists)

See `round-04/NOTES.md` when it exists; the code map is unchanged from r03 except:
- `WHCombatFx::Impact`: no disc, no halo sphere, no `Hit()` sparks. N = 6 / 7 / 8 tapered streaks (6 stacked cylinders each, `M_CmbFlare`, additive, no depth test) in the camera image plane, hollow centre (start 0.03 frame widths out),
  length 0.098-0.127 frame widths, hot core 3.5 % of the frame width. `SetCam(P, fov, rot)`; own RNG (`-WHCmbFlare=0` = no starburst, everything else identical: the A/B rerun for `measure_r04.py`).
- `WHEnemy`: `StartTwist` also starts a recoil lean about the knees (`RecAmp` 0.62-0.88 rad = 35-50 deg, 65 % in the contact frame, gone by 0.56 s, biased sideways on the screen by the camera's right axis, passed in `FWHHitIn::CamRight`).
  `SyncActor` composes `Rec * Twist * Tilt`. `TiltNow` is logged per enemy in `fight_frames.jsonl` (16th field).
- `WHCombatDirector::LogRenderRes` (`WH_CMB_RES` log line at frame 40), `WH_CMB_FLARE` per starburst.
- The sim is unchanged since r03 (frozen script `scripts/fight30.json`, record `round-03/ue/record`): the movie must replay 381 / 381 events.

## Run the capture (one hold, ~15-20 min once it has the slot)

```
docs/night1/combat/final_r04.sh /Users/midir/sm2-n1/_scratch/combat/r04/final1 1.87,2.66,3.05,4.34,7.01,7.78,8.22,9.37,10.25,12.52,15.42,15.65,20.04,22.14,26.68   # map rebuild, movie A (starburst), movie B (-WHCmbFlare=0), 15 native 4K stills
docs/night1/combat/package_r04.sh /Users/midir/sm2-n1/_scratch/combat/r04/final1     # -> round-04/ (mp4 <= 15 MB, measurements, stills, strips)
docs/night1/combat/critic_pack_r04.sh /Users/midir/sm2-n1/_scratch/critic-P5-r04     # blind pack
```
Rules that bit (RULES.md): never SIGKILL a rendering engine; `stop_ue.sh` only; one engine at a time; the wrapper's max hold is raised to 5400 s in `final_r04.sh` so that it never SIGKILLs an engine on a timer; watch the movie and
`SIGSTOP` the wrapper before `SIGTERM`-ing a wedged engine (r03 recipe).
