#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 08: write the round-08 table (make_v4.py <knobs>) in place, rebuild the look content headless, then run a stills plan (gen_plans_r08.py --set full|check) into <out dir>.
# usage: gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_build_stills.sh <knobs.json> <out dir> [set]
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$WT"; T0=$(date +%s)
BI=(); [ -n "$R07_BIAS" ] && BI=(--r07-bias "$R07_BIAS")   # R07_BIAS: lapse bias overrides (default: round-07/lapse_bias_overrides.json)
python3 tools/perf_ue/sweeps/r08/make_v4.py --knobs "$1" "${BI[@]}" --in-place || exit 2
if [ -z "$NOBUILD" ]; then
  tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod
  grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
  echo "build done t=$(( $(date +%s) - T0 ))s"
fi
mkdir -p "$2"
python3 tools/perf_ue/sweeps/r08/gen_plans_r08.py --out "$2" --set ${3:-full}
python3 tools/perf_ue/sweeps/run_r06.py --plan "$2/plan_${3:-full}.json" --out "$2" --timeout ${STILLS_TMO:-1800}; echo "stills rc=$? t=$(( $(date +%s) - T0 ))s"
if [ -n "$MIDDAY" ]; then   # the r03 midday floor on the fixed midday preset map (Look_Midtown, the merged round-03 look): S1-S8, one session
  python3 tools/perf_ue/capture_tour.py --round "$2/midday_round" --presets midday --res 1920x1080 --timeout 900; echo "midday rc=$? t=$(( $(date +%s) - T0 ))s"
fi
python3 tools/perf_ue/dome_check.py --dir "$2" --out "$2/DOME" > /dev/null
python3 tools/perf_ue/r08_check.py --dir "$2" --out "$2/R08" > /dev/null
echo "hold_build_stills done t=$(( $(date +%s) - T0 ))s"
