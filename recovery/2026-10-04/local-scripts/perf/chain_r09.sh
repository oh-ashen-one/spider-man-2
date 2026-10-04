#!/bin/bash
# F round 1, phase C: restore the untouched content (the content variants gave nothing on top of candidate 1 unless the matrix says otherwise: decided by hand
# before this starts is NOT possible, so this always restores) and run the last cvar probes on top of candidate 1.
cd /Users/midir/sm2-n1/perf
L=/Users/midir/sm2-n1/_scratch/perf/logs; R=/Users/midir/sm2-n1/_scratch/perf/r09; mkdir -p $R
until grep -q "chain done" $L/chain_r08.out; do sleep 10; done
echo "$(date +%T) restore" >> $L/chain_r09.out
tools/perf_ue2/perf_content.sh restore >> $L/chain_r09.out 2>&1
echo "$(date +%T) q7" >> $L/chain_r09.out
Q7="ctlF@50+set:cand1,skyslice@50+set:cand1+r.SkyLight.RealTimeReflectionCapture.TimeSlice=1,mpe6@50+set:cand1+r.Nanite.MaxPixelsPerEdge=6,cld256@50+set:cand1+r.VolumetricCloud.ViewRaySampleMaxCount=256,cldd8@50+set:cand1+r.VolumetricCloud.DistanceToSampleMaxCount=8,vsmmov@50+set:cand1+r.Shadow.Virtual.ResolutionLodBiasDirectionalMoving=1,smrt4@50+set:cand1+r.Shadow.Virtual.SMRT.RayCountDirectional=4,ctlF2@50+set:cand1"
python3 tools/perf_ue2/perf_queue.py --out $R --configs "$Q7" --tag q >> $L/chain_r09.out 2>&1
echo "$(date +%T) chain done" >> $L/chain_r09.out
