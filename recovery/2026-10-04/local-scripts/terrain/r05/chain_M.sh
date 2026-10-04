#!/bin/bash
# waits for the S stills hold to release its slot, then queues the M movies hold (same content, no rebuild in between); runs outside any hold
L=/Users/midir/sm2-n1/_scratch/terrain/r05
for i in $(seq 1 720); do grep -q "release exit" $L/holdS.log && break; sleep 10; done
grep -q "release exit" $L/holdS.log || exit 3
[ -e /Users/midir/sm2-n1/_scratch/terrain/capture/STOPPED ] && { echo "S hold stopped: not chaining"; exit 4; }
cd /Users/midir/sm2-n1/terrain && STAGE=M /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round5.sh > $L/holdM.log 2>&1
