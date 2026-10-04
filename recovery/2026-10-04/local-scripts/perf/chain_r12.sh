#!/bin/bash
# F round 1: native (SP 100 = 3840x2160 internal) rows of the official table. Waits for the official route chain.
cd /Users/midir/sm2-n1/perf
L=/Users/midir/sm2-n1/_scratch/perf/logs; R=/Users/midir/sm2-n1/perf/docs/night1/perf/round-01/perf
until grep -q "chain done" $L/chain_r10.out 2>/dev/null; do sleep 10; done
echo "$(date +%T) official native" >> $L/chain_r12.out
python3 tools/perf_ue2/perf_queue.py --out $R/native --configs "f_base100@100,f_perf60_100@100+set:perf60" --tag s >> $L/chain_r12.out 2>&1
echo "$(date +%T) chain done" >> $L/chain_r12.out
