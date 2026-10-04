#!/bin/bash
# waits for the previous water hold (pid $1), then runs hold E under the GPU lock (no worktree path on this command line)
while [ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ]; do sleep 20; done; sleep 30
export SKIP_BUILD=1
cd ~/sm2-n1/water
V=/Game/Water/Variants; M=/Game/Water/Maps
export RD=$HOME/sm2-n1/_scratch/water/r06i VJ=$PWD/tools/water/r06/variantsI.json
export SHOTS="$V/Water_Var_V5_river_low|V5_rl|8,10,12,14,16 $V/Water_Var_V9_river_low|V9_rl|8,10,12,14,16 $M/Water_View_RiverLow|base_rl|8,10,12,14,16 $V/Water_Var_V5_river_sun|V5_rs $V/Water_Var_V9_river_sun|V9_rs $M/Water_View_RiverSun|base_rs"
exec /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash tools/water/r06/holdA.sh
