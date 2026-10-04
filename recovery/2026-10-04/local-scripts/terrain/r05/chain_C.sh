#!/bin/bash
# r05 final on /Game/TerrainR5b (build of 05:37: build 4 + olive reeds + furniture vertex colours + conifer shadow proxies): S stills hold, then M movies hold (same content)
L=/Users/midir/sm2-n1/_scratch/terrain/r05
cd /Users/midir/sm2-n1/terrain || exit 1
STAGE=S TERRAIN_ROOT=/Game/TerrainR5b /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round5.sh > $L/holdS3.log 2>&1
[ -e /Users/midir/sm2-n1/_scratch/terrain/capture/STOPPED ] && { echo "S hold stopped: no movies"; exit 4; }
sleep 5
STAGE=M TERRAIN_ROOT=/Game/TerrainR5b /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round5.sh > $L/holdM3.log 2>&1
echo "chain C done $(date +%H:%M:%S)"
