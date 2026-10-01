#!/bin/bash
# F round 07 look probes l2 (capture slot): fixed-step stills (noise), Lumen two-sided first-hit skip on the tree proxies.
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd $WT
export SM2_PERF_STILL_FIXED=1
$G capture --label perf -- bash -c "
tools/perf_ue2/stills2.sh $R/st/fbase 'ship@ini' 'S1 S2 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/fbase2 'ship@ini' 'S1 S2 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/sk100 'sk100@ini+r.Lumen.HardwareRayTracing.SkipTwoSidedHitDistance=100' 'S1 S2 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/sk300 'sk300@ini+r.Lumen.HardwareRayTracing.SkipTwoSidedHitDistance=300' 'S1 S2 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/sk1000 'sk1000@ini+r.Lumen.HardwareRayTracing.SkipTwoSidedHitDistance=1000' 'S1 S2 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/r4sk300 'r4sk300@ini+variant:RTvRk20+r.Lumen.HardwareRayTracing.SkipTwoSidedHitDistance=300' 'S1 S2 S7' 2>&1 | tail -1
" > $R/logs/l2.log 2>&1; echo "$(date +%T) l2 rc $?"
