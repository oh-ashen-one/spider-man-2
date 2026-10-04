#!/bin/bash
# r05 shadow-proxy iteration: after the build-4 S+M chain ends, build /Game/TerrainR5b (full, nullrhi, through the lock), then a test hold on it (p4 / p1 / p10 4K stills),
# then the MegaLights diagnostic on V_p4 (1080p). One engine at a time; runs outside any hold.
L=/Users/midir/sm2-n1/_scratch/terrain/r05
for i in $(seq 1 720); do grep -q "chain done" $L/chain_SM.log 2>/dev/null && break; kill -0 $(cat $L/chain_SM.pid) 2>/dev/null || break; sleep 10; done
cd /Users/midir/sm2-n1/terrain || exit 1
SM2_TERRAIN_ROOT=/Game/TerrainR5b /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 7200 -- tools/terrain/run_build.sh > $L/build5b.log 2>&1
grep -q "rc=0" $L/build5b.log || { echo "build5b failed"; exit 3; }
sleep 5
mkdir -p docs/night1/terrain/round-05/test5b && cp docs/night1/terrain/round-05/crops.json docs/night1/terrain/round-05/test5b/
STAGE=T TEST_NAME=test5b TERRAIN_ROOT=/Game/TerrainR5b /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round5.sh > $L/holdT5b.log 2>&1
sleep 5
sed 's#/Game/TerrainR5/#/Game/TerrainR5b/#g' $L/diag5.sh > $L/diag5b.sh; chmod +x $L/diag5b.sh
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 7200 -- $L/diag5b.sh > $L/diag5b.log 2>&1
echo "chain B done $(date +%H:%M:%S)"
