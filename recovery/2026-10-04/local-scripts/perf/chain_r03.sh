#!/bin/bash
# F round 1, phase A (untouched V0 content): cvar probes q2, 1080p-output control, Insights trace, before-stills. Nothing here edits Content.
cd /Users/midir/sm2-n1/perf
L=/Users/midir/sm2-n1/_scratch/perf/logs
R=/Users/midir/sm2-n1/_scratch/perf/r03
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
mkdir -p $R
Q2="mpe3_50@50+r.Nanite.MaxPixelsPerEdge=3,mpe6_50@50+r.Nanite.MaxPixelsPerEdge=6,hwrtgi0_50@50+r.Lumen.ScreenProbeGather.HardwareRayTracing=0,hwrtrefl0_50@50+r.Lumen.Reflections.HardwareRayTracing=0,mpe4_hwrt0_50@50+set:mpe4+r.Lumen.HardwareRayTracing=0,mpe4_cheap_50@50+set:mpe4+set:cheap"
echo "$(date +%T) q2" >> $L/chain_r03.out
python3 tools/perf_ue2/perf_queue.py --out $R --configs "$Q2" --tag q >> $L/chain_r03.out 2>&1
echo "$(date +%T) ctl1080" >> $L/chain_r03.out
python3 tools/perf_ue2/perf_queue.py --out $R --configs "ctl1080_100@100" --tag c -- --res 1920x1080 >> $L/chain_r03.out 2>&1
echo "$(date +%T) trace" >> $L/chain_r03.out
python3 tools/perf_ue2/perf_queue.py --out $R --configs "tr_base50@50,tr_mpe4_50@50+set:mpe4" --tag t -- --trace cpu,gpu,frame,log >> $L/chain_r03.out 2>&1
echo "$(date +%T) stills before" >> $L/chain_r03.out
$G capture --label perf -- tools/perf_ue2/stills.sh /Users/midir/sm2-n1/perf/docs/night1/perf/round-01/stills_before_sp50 50 >> $L/chain_r03.out 2>&1
echo "$(date +%T) stills mpe4" >> $L/chain_r03.out
$G capture --label perf -- tools/perf_ue2/stills.sh /Users/midir/sm2-n1/_scratch/perf/stills_mpe4_sp50 50 "set:mpe4" >> $L/chain_r03.out 2>&1
echo "$(date +%T) chain done" >> $L/chain_r03.out
