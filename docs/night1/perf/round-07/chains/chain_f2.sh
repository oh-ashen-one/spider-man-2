#!/bin/bash
# F round 07 chain f2: content c2 (proxy Lumen cards back to the engine default 12: rt_proxy_cards rejected, it fixed neither S7 nor S1 and with r07cap
# it left the 25.7 k cards under-captured: S7 glass SSIM 0.889), keep leaf_area. Then stills + look gates, then the exclusive perf session p2.
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd $WT
H3=+r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0.125+r.LumenScene.SurfaceCache.CardCaptureFactor=64+r.SkyLight.RealTimeReflectionCapture.VolumetricCloudResolutionDivider=2
L=+variant:Life
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED present: stop"; exit 3; }
SM2_PERF_APPLY_STEPS=rt_proxy_cards SM2_PERF_PROXY_CARDS=12 $G capture --label perf -- python3 tools/perf_ue2/build_map.py --steps perf_apply > $R/logs/c2.log 2>&1; echo "$(date +%T) c2 rc $?"
cp /Users/midir/sm2-n1/_scratch/perf/perf_apply.json $R/c2_perf_apply.json
export SM2_PERF_STILL_FIXED=1 SM2_PERF_ROUTE_SHOTS=20,28,38,42
$G capture --label perf -- bash -c "
tools/perf_ue2/stills2.sh $R/st/final2 'ship@ini' 'S1 S2 S7 route' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/h3b 'h3@ini$H3' 'S1 S2 S7' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/n6 'n6@ini+r.Nanite.MaxPixelsPerEdge=6' 'S2 S1' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/final2_life 'life@ini$L' 'route' 2>&1 | tail -1
" > $R/logs/f2_stills.log 2>&1; echo "$(date +%T) stills rc $?"
for d in final2 h3b n6; do python3 tools/perf_ue2/look_gate.py $R/st/$d > $R/st/$d.gate.md 2>&1; echo "$d gate rc $?"; done
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED present: stop before perf"; exit 3; }
echo "$(date +%T) perf start; util $(ioreg -r -d 1 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*')"
python3 tools/perf_ue2/perf_queue.py --out $R/perf --tag p --start 2 --configs "lwarm@ini$L,life_a@ini$L,lh3_a@ini$L$H3,life_b@ini$L,lh3_b@ini$L$H3,life_c@ini$L,ship_a@ini,ship_b@ini,s2@ini+view:S2,life_d@ini$L" -- --budget-s 870
echo "$(date +%T) f2 done"
