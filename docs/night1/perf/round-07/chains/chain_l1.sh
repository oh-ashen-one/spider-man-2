#!/bin/bash
# F round 07 look probes l1 (capture slot): why the S2 tree line / S7 reflected foliage / S1 canopy lost their green. Stills S1 S2 S7 per config.
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd $WT
$G capture --label perf -- bash -c "
tools/perf_ue2/stills2.sh $R/st/base 'ship@ini' 'S1 S2 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/lm2 'lm2@ini+r.Lumen.HardwareRayTracing.LightingMode=2' 'S1 S2 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/lm1 'lm1@ini+r.Lumen.HardwareRayTracing.LightingMode=1' 'S1 S2 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/r4 'r4@ini+variant:RTvRk20' 'S1 S2 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/lk 'lk@ini+variant:RTvLk20' 'S1 S2 S7' 2>&1 | tail -1
" > $R/logs/l1.log 2>&1; echo "$(date +%T) l1 rc $?"
for d in base lm2 lm1 r4 lk; do python3 tools/perf_ue2/look_gate.py $R/st/$d > $R/st/$d.gate.md 2>&1; echo "$d gate rc $?"; done
