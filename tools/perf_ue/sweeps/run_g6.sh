#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Runs the round-04 golden key/fill sweep (gen_g6.py -> v_g6a.json / v_g6b.json / v_g6c.json) as up to three game sessions inside ONE GPU-slot hold:
#   tools/perf_ue/sweeps/run_g6.sh            (wrap it: gpu_slot.sh capture --label look -- tools/perf_ue/sweeps/run_g6.sh)
# A later session is skipped when the sessions before it took more than 1500 s (the slot hold ends at 2400 s). Stills land in $SCR/eval4/stills (1080p, native internal res).
WT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCR=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}
python3 "$WT/tools/perf_ue/sweeps/gen_g6.py" "$SCR/eval/v_g6.json" || exit 1
T0=$SECONDS
python3 "$WT/tools/perf_ue/capture_tour.py" --round "$SCR/eval4" --presets golden --res 1920x1080 --variants "$SCR/eval/v_g6a.json" --timeout 6000 --work "$SCR/tour4a" || exit $?
for c in b c; do
  if [ $((SECONDS - T0)) -lt 1500 ]; then
    python3 "$WT/tools/perf_ue/capture_tour.py" --round "$SCR/eval4" --presets golden --res 1920x1080 --variants "$SCR/eval/v_g6$c.json" --timeout 6000 --work "$SCR/tour4$c"
  else echo "session $c skipped: $((SECONDS - T0)) s used"; fi
done
