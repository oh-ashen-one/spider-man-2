#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 08: second capture of the pass stills of the SAME build (no bake: the volumetric cloud pattern differs between sessions, L27 rows 0-150 / 8-row steps move by
# a few Y) + the fixed night preset map S1-S8 (the round-03 night floor L3 / L8 / L13 is a fixed-preset number). One GPU hold.
# usage: gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_extra.sh <out dir>
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$WT"; T0=$(date +%s); mkdir -p "$1"
python3 tools/perf_ue/sweeps/r08/gen_plans_r08.py --out "$1" --set check
python3 tools/perf_ue/sweeps/run_r06.py --plan "$1/plan_check.json" --out "$1" --timeout 1200; echo "check rc=$? t=$(( $(date +%s) - T0 ))s"
python3 tools/perf_ue/capture_tour.py --round "$1/night_round" --presets night --res 1920x1080 --timeout 900; echo "night rc=$? t=$(( $(date +%s) - T0 ))s"
python3 tools/perf_ue/dome_check.py --dir "$1" --out "$1/DOME" > /dev/null; python3 tools/perf_ue/r08_check.py --dir "$1" --out "$1/R08" > /dev/null
echo "hold_extra done t=$(( $(date +%s) - T0 ))s"
