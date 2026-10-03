#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 08: the stitched L23b lapse of the CURRENT baked build into round-08/ (same segments and instrument condition as round 07: x4 day / night, x16 twilights, 960x540, each segment
# 0.3 h early), one GPU hold (budget HOLD_BUDGET s, default 2300; no segment is started that cannot finish before the deadline at LAPSE_SPF s per rendered frame). REUSE=1 keeps segments already rendered.
# usage: [REUSE=1] gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_lapse.sh
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-08
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2300}
cd "$WT"; mkdir -p "$R"
RE=""; [ -n "$REUSE" ] && RE="--reuse"
LAPSE_SPF=${LAPSE_SPF:-0.3} python3 tools/perf_ue/lapse_stitch.py --round "$R" --name tod_lapse_S4 --res 960x540 ${=RE} --timeout 1700 --segments "${SEGMENTS:-3.7:1.8:4:0.3,5.2:4.0:16:0.3,8.9:8.7:4:0.3,17.3:4.1:16:0.3,21.1:6.9:4:0.3}" --deadline $(( T0 + HOLD - 90 ))
echo "hold_lapse done t=$(( $(date +%s) - T0 ))s"
