#!/bin/bash
while kill -0 3513 2>/dev/null; do sleep 5; done
cd /Users/midir/sm2-n1/look
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label P4 --timeout 7200 --json /Users/midir/sm2-n1/_scratch/look/r09/holdC/gpu_slot.json -- tools/perf_ue/sweeps/r09/hold_c.sh /Users/midir/sm2-n1/_scratch/look/r09/holdC
