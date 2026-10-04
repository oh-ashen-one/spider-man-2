#!/bin/zsh
# P4 r04: after the city hold (pid in city_ue.pid) ends OK, queue the sweep hold
P=$(cat /Users/midir/sm2-n1/_scratch/look/r04b/city_ue.pid)
while kill -0 $P 2>/dev/null; do sleep 20; done
grep -q "build_look.*DONE" /Users/midir/sm2-n1/_scratch/look/build_look_headless.log 2>/dev/null && [ /Users/midir/sm2-n1/_scratch/look/build_look_headless.log -nt /Users/midir/sm2-n1/_scratch/look/r04b/city_ue.pid ] || { echo "city/look rebuild not confirmed; not queueing S"; exit 1; }
cd /Users/midir/sm2-n1/look
GPU_SLOT_CAPTURE_WAIT_TIMEOUT=14400 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label look -- /Users/midir/sm2-n1/look/tools/perf_ue/sweeps/run_r04b.sh S
echo "S rc=$?"
