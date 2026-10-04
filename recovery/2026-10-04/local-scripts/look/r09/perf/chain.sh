#!/bin/bash
while kill -0 40797 2>/dev/null; do sleep 5; done
cd /Users/midir/sm2-n1/look
mkdir -p /Users/midir/sm2-n1/look/docs/night1/look/round-09/perf
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh perf --label P4 --timeout 3600 --json /Users/midir/sm2-n1/look/docs/night1/look/round-09/perf/perf_gpu.json -- tools/perf_ue/sweeps/r09/perf_s4.sh /Users/midir/sm2-n1/_scratch/look/r09/perf/run
