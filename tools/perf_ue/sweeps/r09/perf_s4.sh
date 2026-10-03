#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 09: ONE exclusive perf pass of the S4 perch view (/Game/Maps/Manhattan_View_S4: the integrated map, golden preset, static perch camera), 3840x2160 output,
# r.ScreenPercentage 67 (TSR, internal 2573x1447), frame-time window 15-45 s of game time. Run it ONLY through the exclusive lock:
#   gpu_slot.sh perf --label P4 --json <out>/perf_gpu.json -- tools/perf_ue/sweeps/r09/perf_s4.sh <out>
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"; cd "$WT"; OUT="$1"; mkdir -p "$OUT"
ioreg -r -d 1 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1 > "$OUT/gpu_util_before.txt"
unreal/WebHomage/Scripts/run_game.sh "$OUT" -map /Game/Maps/Manhattan_View_S4 -res 3840x2160 -perf 15:45 -shots 44 -name perf_s4_4k -timeout 400 -exec "r.ScreenPercentage 67"
ioreg -r -d 1 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1 > "$OUT/gpu_util_after.txt"
