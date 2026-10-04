#!/bin/bash
# F round 1, phase D: OFFICIAL numbers on the untouched (V0) content, control + presets in the same exclusive sessions.
cd /Users/midir/sm2-n1/perf
L=/Users/midir/sm2-n1/_scratch/perf/logs; R=/Users/midir/sm2-n1/perf/docs/night1/perf/round-01/perf; mkdir -p $R
echo "$(date +%T) official route" >> $L/chain_r10.out
python3 tools/perf_ue2/perf_queue.py --out $R/route --configs "warm@50+set:perf60,f_base50@50,f_perf60_50@50+set:perf60,f_perf60_mpe6_50@50+set:perf60_mpe6,f_cand1_50@50+set:cand1,f_perf60_sp58@58+set:perf60,f_perf60_sp67@67+set:perf60,f_base67@67" --tag s >> $L/chain_r10.out 2>&1
echo "$(date +%T) official s2" >> $L/chain_r10.out
python3 tools/perf_ue2/perf_queue.py --out $R/s2 --configs "f_s2_warm@50+set:perf60,f_s2_base50@50,f_s2_perf60_50@50+set:perf60" --tag s -- --script none --map /Game/Maps/Manhattan_View_S2 >> $L/chain_r10.out 2>&1
echo "$(date +%T) chain done" >> $L/chain_r10.out
