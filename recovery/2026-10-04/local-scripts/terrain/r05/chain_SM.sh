#!/bin/bash
# r05 final: waits for the mat build 4, then the S stills hold, then the M movies hold (same content, nothing rebuilt in between); runs outside any hold, one hold at a time
L=/Users/midir/sm2-n1/_scratch/terrain/r05
for i in $(seq 1 360); do grep -q "release exit" $L/build4.log 2>/dev/null && break; sleep 5; done
grep -q "rc=0" $L/build4.log || { echo "build4 failed"; exit 3; }
sleep 5
cd /Users/midir/sm2-n1/terrain || exit 1
STAGE=S /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round5.sh > $L/holdS2.log 2>&1
[ -e /Users/midir/sm2-n1/_scratch/terrain/capture/STOPPED ] && { echo "S hold stopped: no movies"; exit 4; }
sleep 5
STAGE=M /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round5.sh > $L/holdM.log 2>&1
echo "chain done $(date +%H:%M:%S)"
