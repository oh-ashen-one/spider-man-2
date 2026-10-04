#!/bin/bash
# F round 1, phase A2 (V0 content still): floor test, cheap-set on top, other TSR percentages, S2 static heavy view. Waits for chain_r03.
cd /Users/midir/sm2-n1/perf
L=/Users/midir/sm2-n1/_scratch/perf/logs; R=/Users/midir/sm2-n1/_scratch/perf/r04; mkdir -p $R
until grep -q "chain done" $L/chain_r03.out; do sleep 10; done
Q3="floor25_50@25+set:mpe4+set:hwrt0,mpe4_hwrt0_cheap_50@50+set:mpe4+set:hwrt0+set:cheap,mpe4_hwrt0_sp58@58+set:mpe4+set:hwrt0,mpe4_hwrt0_sp67@67+set:mpe4+set:hwrt0,base67@67"
echo "$(date +%T) q3" >> $L/chain_r04.out
python3 tools/perf_ue2/perf_queue.py --out $R --configs "$Q3" --tag q >> $L/chain_r04.out 2>&1
echo "$(date +%T) s2" >> $L/chain_r04.out
python3 tools/perf_ue2/perf_queue.py --out $R --configs "s2_base50@50,s2_mpe4_hwrt0_50@50+set:mpe4+set:hwrt0" --tag s -- --script none --map /Game/Maps/Manhattan_View_S2 >> $L/chain_r04.out 2>&1
echo "$(date +%T) chain done" >> $L/chain_r04.out
