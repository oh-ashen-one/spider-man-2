#!/bin/bash
# F round 1: where does p95 reach 55 fps? perf60_mpe6 at lower TSR percentages. Waits for the native chain.
cd /Users/midir/sm2-n1/perf
L=/Users/midir/sm2-n1/_scratch/perf/logs; R=/Users/midir/sm2-n1/perf/docs/night1/perf/round-01/perf
until grep -q "chain done" $L/chain_r12.out 2>/dev/null; do sleep 10; done
echo "$(date +%T) reserve" >> $L/chain_r13.out
python3 tools/perf_ue2/perf_queue.py --out $R/reserve --configs "f_mpe6_sp46@46+set:perf60_mpe6,f_mpe6_sp42@42+set:perf60_mpe6,f_perf60_sp46@46+set:perf60" --tag s >> $L/chain_r13.out 2>&1
echo "$(date +%T) chain done" >> $L/chain_r13.out
