#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Round-04 capture phases inside ONE GPU-slot hold each (slot hold max 2400 s):
#   gpu_slot.sh capture --label look -- tools/perf_ue/sweeps/run_r04.sh A     # rebuild golden rig (nullrhi) + golden stills 1080p and 4K
#   gpu_slot.sh capture --label look -- tools/perf_ue/sweeps/run_r04.sh B     # golden swing clip
#   gpu_slot.sh capture --label look -- tools/perf_ue/sweeps/run_r04.sh C     # midday + night stills (1080p, 4K) of the unchanged presets
#   gpu_slot.sh capture --label look -- tools/perf_ue/sweeps/run_r04.sh D     # midday + night swing clips
# Every tool below wraps its own game launch in gpu_slot too (nesting passes through). A failed step stops the phase (no relaunch loops).
WT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCR=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}
RND=${R04_ROUND:-$WT/docs/night1/look/round-04}
mkdir -p "$RND"
case "$1" in
  A) "$WT/tools/perf_ue/rebuild_look.sh" rigs golden || exit $?
     python3 "$WT/tools/perf_ue/capture_tour.py" --round "$RND" --presets golden --res 1920x1080,3840x2160 --timeout 6000 --work "$SCR/tour_r04" ;;
  B) python3 "$WT/tools/perf_ue/capture_looks.py" --round "$RND" --presets golden --clips --no-stills --no-warmup ;;
  C) python3 "$WT/tools/perf_ue/capture_tour.py" --round "$RND" --presets midday,night --res 1920x1080,3840x2160 --timeout 6000 --work "$SCR/tour_r04" ;;
  D) python3 "$WT/tools/perf_ue/capture_looks.py" --round "$RND" --presets midday,night --clips --no-stills --no-warmup ;;
  *) echo "usage: run_r04.sh A|B|C|D"; exit 2 ;;
esac
