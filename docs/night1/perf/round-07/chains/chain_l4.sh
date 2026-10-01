#!/bin/bash
# F round 07 look probes l4 (capture slot): which preset cvar removed the S2 tree-line / S1 canopy / S7 reflected foliage. Fixed-step stills S1 S2 S7.
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd $WT
export SM2_PERF_STILL_FIXED=1
$G capture --label perf -- bash -c "
tools/perf_ue2/stills2.sh $R/st/ca1 'ca1@ini+r.RayTracing.Culling.Angle=1' 'S7 S2 S1' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/npe1 'npe1@ini+r.Nanite.MaxPixelsPerEdge=1' 'S2 S1 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/npe2 'npe2@ini+r.Nanite.MaxPixelsPerEdge=2' 'S2 S1 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/npe4 'npe4@ini+r.Nanite.MaxPixelsPerEdge=4' 'S2 S1 S7' 2>&1 | tail -1
" > $R/logs/l4.log 2>&1; echo "$(date +%T) l4 rc $?"
for d in ca1 npe1 npe2 npe4; do python3 tools/perf_ue2/look_gate.py $R/st/$d > $R/st/$d.gate.md 2>&1; echo "$d gate rc $?"; done
