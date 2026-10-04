#!/bin/bash
# final capture hold of round 06 from the hold-G build (SKIP_BUILD; no worktree path on this command line)
while kill -0 $1 2>/dev/null; do sleep 5; done; sleep 3
cd ~/sm2-n1/water
export SKIP_BUILD=1
exec /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash tools/water/r06/final_g.sh
