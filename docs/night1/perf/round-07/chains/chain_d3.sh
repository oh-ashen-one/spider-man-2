#!/bin/bash
# F round 07 session d3: Lumen surface-cache capture budget on top of card refresh off. Exclusive lock via perf_queue.py.
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07
cd $WT
L=+variant:Life; CR=+r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0; C128=+r.LumenScene.SurfaceCache.CardCaptureFactor=128; C256=+r.LumenScene.SurfaceCache.CardCaptureFactor=256
python3 tools/perf_ue2/perf_queue.py --out $R/perf --tag g --configs "lwarm@ini$L,lccf_a@ini$L$CR$C128,lcc256_a@ini$L$CR$C256,lcc256pf@ini$L$CR$C256+r.LumenScene.SurfaceCache.CardCapturesPerFrame=150,lsky4@ini$L$CR$C128+r.SkyLight.RealTimeReflectionCapture.VolumetricCloudResolutionDivider=4,lccf_b@ini$L$CR$C128,lcc256_b@ini$L$CR$C256,sccf@ini$CR$C128,lctl@ini$L,lccf_c@ini$L$CR$C128" -- --budget-s 870
echo "$(date +%T) d3 done"
