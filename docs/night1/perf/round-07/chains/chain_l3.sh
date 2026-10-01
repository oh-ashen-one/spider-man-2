#!/bin/bash
# F round 07 look probes l3: card-capture budget candidates incl. route stills (moving camera = where a smaller capture budget would show).
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd $WT
export SM2_PERF_STILL_FIXED=1 SM2_PERF_ROUTE_SHOTS=20,28,42
CR=+r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0
$G capture --label perf -- bash -c "
tools/perf_ue2/stills2.sh $R/st/cr0 'cr0@ini$CR' 'S1 S2 S7 route' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/ccf128 'ccf128@ini$CR+r.LumenScene.SurfaceCache.CardCaptureFactor=128' 'S1 S2 S7 route' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/ccf256 'ccf256@ini$CR+r.LumenScene.SurfaceCache.CardCaptureFactor=256' 'S1 S2 S7 route' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/fship 'ship@ini' 'route' 2>&1 | tail -1
" > $R/logs/l3.log 2>&1; echo "$(date +%T) l3 rc $?"
