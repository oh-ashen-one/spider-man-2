#!/bin/bash
# F round 1, phase A3 (V0 content): TSR / post-process cost at 4K output. Waits for chain_r05.
cd /Users/midir/sm2-n1/perf
L=/Users/midir/sm2-n1/_scratch/perf/logs; R=/Users/midir/sm2-n1/_scratch/perf/r06; mkdir -p $R
until grep -q "chain done" $L/chain_r05.out; do sleep 10; done
Q4="aa2_50@50+sg.AntiAliasingQuality=2,tsrh100_50@50+r.TSR.History.ScreenPercentage=100,pp2_50@50+sg.PostProcessQuality=2,mbhalf_50@50+r.MotionBlur.HalfResGather=1+r.MotionBlur.HalfResInput=1,mpe4_hwrt0_aa2_50@50+set:mpe4+set:hwrt0+sg.AntiAliasingQuality=2,mpe4_hwrt0_aa2_pp2_50@50+set:mpe4+set:hwrt0+sg.AntiAliasingQuality=2+sg.PostProcessQuality=2"
echo "$(date +%T) q4" >> $L/chain_r06.out
python3 tools/perf_ue2/perf_queue.py --out $R --configs "$Q4" --tag q >> $L/chain_r06.out 2>&1
echo "$(date +%T) chain done" >> $L/chain_r06.out
