#!/bin/bash
# F round 1, phase E: after stills (perf60 and perf60_mpe6, both TSR 50) + the route clip, all under capture slots. Waits for the official perf chain.
cd /Users/midir/sm2-n1/perf
L=/Users/midir/sm2-n1/_scratch/perf/logs; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh; R=/Users/midir/sm2-n1/perf/docs/night1/perf/round-01
until grep -q "chain done" $L/chain_r10.out 2>/dev/null; do sleep 10; done
echo "$(date +%T) stills perf60" >> $L/chain_r11.out
$G capture --label perf -- tools/perf_ue2/stills.sh /Users/midir/sm2-n1/_scratch/perf/stills_perf60_sp50 50 "set:perf60" >> $L/chain_r11.out 2>&1
echo "$(date +%T) stills perf60_mpe6" >> $L/chain_r11.out
$G capture --label perf -- tools/perf_ue2/stills.sh /Users/midir/sm2-n1/_scratch/perf/stills_perf60mpe6_sp50 50 "set:perf60_mpe6" >> $L/chain_r11.out 2>&1
echo "$(date +%T) movie" >> $L/chain_r11.out
$G capture --label perf -- tools/perf_ue2/route_movie.sh $R "set:perf60" >> $L/chain_r11.out 2>&1
echo "$(date +%T) chain done" >> $L/chain_r11.out
