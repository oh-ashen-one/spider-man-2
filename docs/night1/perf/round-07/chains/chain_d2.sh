#!/bin/bash
# F round 07 session d2: life-route candidates (no extra CSV categories). Exclusive lock via perf_queue.py.
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07
cd $WT
L=+variant:Life; CR=+r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0; BT=+r.GPUSkin.BoneTransformAllocationMode=0
echo "$(date +%T) start; util $(ioreg -r -d 1 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*')"
python3 tools/perf_ue2/perf_queue.py --out $R/perf --tag e --configs "lwarm@ini$L,lctl_a@ini$L,lcr0_a@ini$L$CR,lbt0@ini$L$BT,lcrbt@ini$L$CR$BT,lsk300@ini$L+r.Lumen.HardwareRayTracing.SkipTwoSidedHitDistance=300,lctl_b@ini$L,lcr0_b@ini$L$CR,lccf@ini$L$CR+r.LumenScene.SurfaceCache.CardCaptureFactor=128,lcrbt_b@ini$L$CR$BT" -- --budget-s 870
echo "$(date +%T) d2 done"
