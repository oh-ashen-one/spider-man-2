#!/bin/bash
# F round 07 final chain f1 (after content c1 = leaf_area + rt_proxy_cards, ini = perf60_hwl4):
#  1. stills (capture slot, fixed step): final S1 S2 S7 route t20/28/38/42; h3 = same content with the three r07cap cvars back at engine default; life route
#  2. look gates   3. exclusive perf session p1 (perf_queue)   4. R2 / R2-L clips
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd $WT
H3=+r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0.125+r.LumenScene.SurfaceCache.CardCaptureFactor=64+r.SkyLight.RealTimeReflectionCapture.VolumetricCloudResolutionDivider=2
L=+variant:Life
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED present: stop"; exit 3; }
export SM2_PERF_STILL_FIXED=1 SM2_PERF_ROUTE_SHOTS=20,28,38,42
echo "$(date +%T) stills start"
$G capture --label perf -- bash -c "
tools/perf_ue2/stills2.sh $R/st/final 'ship@ini' 'S1 S2 S7 route' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/final_life 'life@ini$L' 'route' 2>&1 | tail -1
tools/perf_ue2/stills2.sh $R/st/h3 'h3@ini$H3' 'S1 S2 S7' 2>&1 | tail -1
" > $R/logs/f1_stills.log 2>&1; echo "$(date +%T) stills rc $?"
for d in final h3; do python3 tools/perf_ue2/look_gate.py $R/st/$d > $R/st/$d.gate.md 2>&1; echo "$d gate rc $?"; done
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED present: stop before perf"; exit 3; }
echo "$(date +%T) perf start; util $(ioreg -r -d 1 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*')"
python3 tools/perf_ue2/perf_queue.py --out $R/perf --tag p --configs "lwarm@ini$L,life_a@ini$L,lh3_a@ini$L$H3,life_b@ini$L,lh3_b@ini$L$H3,life_c@ini$L,ship_a@ini,ship_b@ini,s2@ini+view:S2,life_d@ini$L" -- --budget-s 870
echo "$(date +%T) perf done"
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED present: stop before clips"; exit 3; }
$G capture --label perf -- tools/perf_ue2/route_movie.sh $R/clip_ship "movie@100+set:perf60_hwl4" > $R/logs/clip_ship.log 2>&1; echo "$(date +%T) clip ship rc $?"
$G capture --label perf -- tools/perf_ue2/route_movie.sh $R/clip_life "movie@100+set:perf60_hwl4$L" > $R/logs/clip_life.log 2>&1; echo "$(date +%T) clip life rc $?"
echo "$(date +%T) f1 done"
