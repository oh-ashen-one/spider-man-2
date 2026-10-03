#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07 (resume): run one live-pin sweep plan (run_r06.py format) against the BAKED table + dome_check.py. Run inside gpu_slot.sh capture.
# usage: gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r07/hold_sweep.sh <plan.json> <out dir>
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$WT"; T0=$(date +%s)
mkdir -p "$2"
python3 tools/perf_ue/sweeps/run_r06.py --plan "$1" --out "$2" --timeout ${SWEEP_TMO:-2000}; echo "sweep rc=$? t=$(( $(date +%s) - T0 ))s"
python3 tools/perf_ue/dome_check.py --dir "$2" --out "$2/DOME" > /dev/null; echo "hold_sweep done t=$(( $(date +%s) - T0 ))s"
