#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07 (resume): bake a table (make_v3 knobs + bias file) in place, rebuild the look content, then run a stills plan (run_r06.py format) into <out dir> (NOT into the round folder).
# usage: gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r07/hold_build_stills.sh <knobs.json> <bias.json> <plan.json> <out dir>
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$WT"; T0=$(date +%s)
python3 tools/perf_ue/sweeps/r07/make_v3.py --knobs "$1" --bias-overrides "$2" --in-place || exit 2
tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod
grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
echo "build done t=$(( $(date +%s) - T0 ))s"
mkdir -p "$4"
python3 tools/perf_ue/sweeps/run_r06.py --plan "$3" --out "$4" --timeout 1500; echo "stills rc=$? t=$(( $(date +%s) - T0 ))s"
