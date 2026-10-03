# Round 09 perf (S4 perch view, 4K output): NOT MEASURED

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Planned pass: `gpu_slot.sh perf --label P4 --timeout 3600 --json round-09/perf/perf_gpu.json -- tools/perf_ue/sweeps/r09/perf_s4.sh <out>`: `/Game/Maps/Manhattan_View_S4` (integrated map, golden preset, static perch camera), 3840x2160 output, `r.ScreenPercentage 67` (TSR from 2573x1447 internal), frame-time window 15-45 s of game time.

What happened (gpu_slot log, `_scratch/look/r09/perf/perf.log`): queued 2026-10-03 ~18:00 EDT behind one capture holder (island); the exclusive lock was taken after ~830 s; the settle gate (GPU "Device Utilization %" < 15 for 10 consecutive s) was then not met for 180 s: no Unreal process was running, utilization read 19-24 % (one 0 sample) while a Codex (ChatGPT) process and WindowServer were busy. The builder stopped its own waiting perf request (SIGTERM to its gpu_slot process at 1016 s, before any engine started) so the lock did not block the other agents' captures for the rest of the 3600 s timeout. No perf number exists for round 09; the last measured look perf is in earlier rounds (`round-0*/PERF.md`).
