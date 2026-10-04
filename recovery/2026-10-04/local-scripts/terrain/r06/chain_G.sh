#!/bin/bash
# r06 chain G: mat rebuild -> T hold with p10 only (round-06/test3) -> chain_F without a build (S stills, M movies, perf attempt), all on the same content
L=/Users/midir/sm2-n1/_scratch/terrain/r06; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd /Users/midir/sm2-n1/terrain || exit 1
echo "build mat start $(date +%H:%M:%S)"
SM2_TERRAIN_ROOT=/Game/TerrainR6 $G capture --label terrain --timeout 28800 -- tools/terrain/run_build.sh mat > $L/buildG.log 2>&1
echo "build rc=$? $(date +%H:%M:%S)"
sleep 3
STAGE=T TEST_NAME=test3 ONLY_IDS=p10_lawn_eye TERRAIN_ROOT=/Game/TerrainR6 $G capture --label terrain --timeout 28800 -- docs/night1/terrain/round6.sh > $L/holdT3.log 2>&1
echo "T3 rc=$? $(date +%H:%M:%S)"
[ -e /Users/midir/sm2-n1/_scratch/terrain/capture/STOPPED ] && { echo "T3 stopped"; exit 4; }
sleep 3
$L/chain_F.sh
echo "chain G done $(date +%H:%M:%S)"
