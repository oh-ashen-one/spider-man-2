#!/bin/bash
# r06 chain A: full content build into /Game/TerrainR6 (nullrhi, through the lock), then the T test hold (warm + p4 p1 p10 4K stills -> round-06/test)
L=/Users/midir/sm2-n1/_scratch/terrain/r06
cd /Users/midir/sm2-n1/terrain || exit 1
echo "build start $(date +%H:%M:%S)"
SM2_TERRAIN_ROOT=/Game/TerrainR6 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- tools/terrain/run_build.sh > $L/buildA.log 2>&1
echo "build rc=$? $(date +%H:%M:%S)"
grep -c "FAILED\|Traceback" /Users/midir/sm2-n1/_scratch/terrain/manhattan/logs/terrain_build.log
[ -f /Users/midir/sm2-n1/terrain/unreal/WebHomage/Content/TerrainR6/Maps/V_p4_greatlawn.umap ] || { echo "no maps: stop"; exit 3; }
sleep 3
STAGE=T TEST_NAME=${TEST_NAME:-test} TERRAIN_ROOT=/Game/TerrainR6 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round6.sh > $L/holdT.log 2>&1
echo "chain A done $(date +%H:%M:%S)"
