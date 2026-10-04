# F perf round 07, re-baseline on integration cd42c1f2 (2026-10-03 18:49-20:16)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Builder: Claude Opus 5.5 high via Devin.

## Result
No measurement was taken. No perf CSV, no gpu_slot perf sidecar and no 3840 still exists for this integration. Every round-07 pass line is unmeasured.

## Timeline
| time | event |
|---|---|
| 18:47 | health_monitor PAUSED + DEMOTED (GPU pinned >= 98 % for 90 s with 2 engines; it stopped the owner-play wrapper pid 22174). Not F's. |
| 18:49 | merge origin/Opus-5.5-Loop-Night-1 cd42c1f2 -> ac87bc4b (clean) |
| 18:50 | `build_editor.sh`: Succeeded, `UnrealEditor.modules -> libUnrealEditor-WebHomage.dylib` |
| 18:52-18:54 | `build_map.py --preset-off` (MacEngine.ini preset block removed = as-found), city_export (F vite 5209) / city_prep / city_extra (incl. far_skyline) in 96 s |
| 18:58 | PAUSED lifted |
| 18:59:38-19:39:38 | `city_pass1` (one-pass build_city `clean,tex,mat,mesh,proto,kit,fsky,map`) in a capture hold: clean 253 s, materials 274 s, meshes 449 at 1710 s, protos 99 at 2189 s, kit actors 9 at 2295 s; then killed by the 40-min max hold (exit 124). The integrator's warm-DDC run of the same step took 426 s. |
| 19:51:39-19:58:08 | `city_rest.py kit,fsky,map`: rc 0, 389 s, 0 python errors (farsky + 9 maps) |
| 20:01 | life prep: 45 vehicle GLBs, 20 citizen FBX (49 s, CPU only) |
| 20:01 | steps 4-11 queued as one outer capture hold (both slots held by other builders) |
| 20:05 | health_monitor: `WS-STARVE-WARN(gpu 100% ws 0%) probe=FAIL STOP(TERM) newest -game pid=33556`; WindowServer + loginwindow restarted (~20:05:30); GPU Device / Renderer / Tiler utilization 100 % with no Unreal render process; PAUSED again (20:05, 20:13, 20:15) |
| 20:15 | F withdrew its queued capture job (own PIDs 31747, 31745; nothing had launched) and stopped (house rule: dead desktop session = pause, push WIP, notify) |

Evidence: `desktop_reset_2005.txt` (health.log 20:02-20:16, ps, ioreg), `chain_build.log`, `chain_build2.log`, `life_prep.log`.

## Observed during the session (for the next run)
- Desktop GPU use without any Unreal render (gpu_procs watch 8 s, 18:59): WindowServer 9.7 %, Codex (Service) 6.6 %, a Chrome helper 6.3 %, ghostty 2.7 %. gpu_procs.py's VOID thresholds (2 % / WindowServer 8 %) are exceeded by the desktop alone.
- Capture holds run under `taskpolicy -b`; a cold-DDC city build in one hold exceeds 40 min.
- `unreal/WebHomage/Config/Mac/MacEngine.ini` is tracked on this branch since ccb13d2d; deleted in the working tree by `--preset-off`, not staged.
