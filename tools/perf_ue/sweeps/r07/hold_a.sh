#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07, hold A: the twilight dome sweep (gen_sweep_a.py plan, baked table + live pins, ONE game session, ~120 stills) + dome_check.py. Run inside gpu_slot.sh capture (the inner slot call passes through).
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r07/sweepA
cd "$WT"; mkdir -p "$S"
T0=$(date +%s)
python3 tools/perf_ue/sweeps/r07/gen_sweep_a.py --out "$S" || exit 2
python3 tools/perf_ue/sweeps/run_r06.py --plan "$S/plan_a.json" --out "$S" --timeout 2100; echo "sweep rc=$? t=$(( $(date +%s) - T0 ))s"
python3 tools/perf_ue/dome_check.py --dir "$S" --out "$S/DOME_A" > /dev/null; echo "hold_a done t=$(( $(date +%s) - T0 ))s"
