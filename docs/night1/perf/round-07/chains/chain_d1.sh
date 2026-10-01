#!/bin/bash
# F round 07 session d1: life-route diagnosis with the RHI-thread stall / flush CSV categories (no Insights), + first candidate levers. Exclusive lock via perf_queue.py.
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07
cd $WT
L=+variant:Life
echo "$(date +%T) start; util $(ioreg -r -d 1 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*')"
python3 tools/perf_ue2/gpu_procs.py snap $R/logs/d1_procs_before.json
python3 tools/perf_ue2/perf_queue.py --out $R/perf --tag d --configs "dwarm@ini$L,dlife_a@ini$L,dship_a@ini,dcr0@ini$L+r.LumenScene.SurfaceCache.CardCaptureRefreshFraction=0,dsky1@ini$L+r.SkyLight.RealTimeReflectionCapture.TimeSlice.SkyCloudCubeFacePerFrame=1,dasync@ini$L+r.RayTracing.AsyncBuild=1,dgts1@ini$L+r.GTSyncType=1,dlife_b@ini$L,ds2@ini+view:S2" -- --budget-s 870 --game-args=-csvCategories=RHITStalls,RHITFlushes,VSM,GPUScene
python3 tools/perf_ue2/gpu_procs.py snap $R/logs/d1_procs_after.json
python3 tools/perf_ue2/gpu_procs.py diff $R/logs/d1_procs_before.json $R/logs/d1_procs_after.json > $R/logs/d1_procs_diff.json
echo "$(date +%T) d1 done"
