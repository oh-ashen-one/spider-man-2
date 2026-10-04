#!/bin/bash
# F round 1, phase B: candidate-1 control on V0 content (+ Insights trace to explain the periodic late-route hitches), then the content variants (cumulative),
# each measured with candidate 1 at TSR 50.
cd /Users/midir/sm2-n1/perf
L=/Users/midir/sm2-n1/_scratch/perf/logs; R=/Users/midir/sm2-n1/_scratch/perf/r08; mkdir -p $R
until grep -q "chain done" $L/chain_r07.out; do sleep 10; done
echo "$(date +%T) v0" >> $L/chain_r08.out
python3 tools/perf_ue2/perf_queue.py --out $R/v0 --configs "cand1_v0@50+set:cand1,cand1_v0_sp67@67+set:cand1" --tag p >> $L/chain_r08.out 2>&1
python3 tools/perf_ue2/perf_queue.py --out $R/v0s2 --configs "s2_cand1_v0@50+set:cand1" --tag p -- --script none --map /Game/Maps/Manhattan_View_S2 >> $L/chain_r08.out 2>&1
echo "$(date +%T) trace" >> $L/chain_r08.out
python3 tools/perf_ue2/perf_queue.py --out $R/trace --configs "tr_cand1_50@50+set:cand1" --tag t -- --trace cpu,gpu,frame >> $L/chain_r08.out 2>&1
echo "$(date +%T) matrix" >> $L/chain_r08.out
tools/perf_ue2/perf_matrix.sh $R/matrix "cand1_c@50+set:cand1" static far_plain kit_plain tree_lumen >> $L/chain_r08.out 2>&1
echo "$(date +%T) chain done" >> $L/chain_r08.out
