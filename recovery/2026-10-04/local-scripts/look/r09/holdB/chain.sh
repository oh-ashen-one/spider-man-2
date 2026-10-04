#!/bin/bash
while kill -0 24471 2>/dev/null; do sleep 5; done
cd /Users/midir/sm2-n1/look
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label P4 --timeout 7200 --json /Users/midir/sm2-n1/_scratch/look/r09/holdB/gpu_slot.json -- tools/perf_ue/sweeps/r09/hold_b.sh /Users/midir/sm2-n1/_scratch/look/r09/holdB/stills
