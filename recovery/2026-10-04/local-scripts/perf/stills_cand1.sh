#!/bin/bash
cd /Users/midir/sm2-n1/perf
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label perf -- tools/perf_ue2/stills.sh /Users/midir/sm2-n1/_scratch/perf/stills_cand1_sp50 50 "set:cand1" >> /Users/midir/sm2-n1/_scratch/perf/logs/stills_cand1.out 2>&1
echo "stills cand1 done" >> /Users/midir/sm2-n1/_scratch/perf/logs/stills_cand1.out
