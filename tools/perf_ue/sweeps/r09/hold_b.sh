#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 09 hold B (inside ONE gpu_slot.sh capture hold): the time-of-day stills (round-08 'full' plan: golden 18.4 S1-S8, night 22 S1-S8 + S4m,
# the L27 twilight verdict stills, mist 07:36, clear / overcast 13:00) on the baked Look_Midtown_tod with the round-09 city, then dome_check / r08_check.
# The key table is the round-08 table (unchanged in round 09).
# usage: gpu_slot.sh capture --label P4 --timeout 7200 -- tools/perf_ue/sweeps/r09/hold_b.sh <out dir>
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"; cd "$WT"; T0=$(date +%s); OUT="$1"; mkdir -p "$OUT"
python3 tools/perf_ue/sweeps/r08/gen_plans_r08.py --out "$OUT" --set full
python3 tools/perf_ue/sweeps/run_r06.py --plan "$OUT/plan_full.json" --out "$OUT" --timeout ${STILLS_TMO:-2000}; echo "stills rc=$? t=$(( $(date +%s) - T0 ))s"
python3 tools/perf_ue/dome_check.py --dir "$OUT" --out "$OUT/DOME" > /dev/null
python3 tools/perf_ue/r08_check.py --dir "$OUT" --out "$OUT/R08" > /dev/null
echo "hold_b done t=$(( $(date +%s) - T0 ))s"
