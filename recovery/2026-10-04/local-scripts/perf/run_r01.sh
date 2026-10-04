#!/bin/bash
cd /Users/midir/sm2-n1/perf
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label perf -- tools/perf_ue2/vsm_diag.sh /Users/midir/sm2-n1/_scratch/perf/diag/vsm > /Users/midir/sm2-n1/_scratch/perf/logs/vsm_diag.out 2>&1
echo "diag exit $?" >> /Users/midir/sm2-n1/_scratch/perf/logs/vsm_diag.out
python3 tools/perf_ue2/perf_queue.py --out /Users/midir/sm2-n1/_scratch/perf/r01 --configs "$(cat /Users/midir/sm2-n1/_scratch/perf/r01/configs.txt)" > /Users/midir/sm2-n1/_scratch/perf/logs/queue_r01.out 2>&1
