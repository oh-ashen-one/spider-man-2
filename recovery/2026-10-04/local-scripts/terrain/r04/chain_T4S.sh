#!/bin/bash
# t4 movie hold, then (after the marker file GO_S appears) the stills hold; STOP_CHAIN cancels the second
cd /Users/midir/sm2-n1/terrain
STAGE=M MOVIES=t4_lawn_sprint /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round4.sh
echo "t4 hold rc=$?"
for i in $(seq 1 720); do [ -e /Users/midir/sm2-n1/_scratch/terrain/r04/GO_S ] && break; [ -e /Users/midir/sm2-n1/_scratch/terrain/r04/STOP_CHAIN ] && { echo "chain cancelled"; exit 0; }; sleep 10; done
[ -e /Users/midir/sm2-n1/_scratch/terrain/r04/GO_S ] || { echo "no GO_S"; exit 0; }
STAGE=S /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round4.sh
echo "stills hold rc=$?"
