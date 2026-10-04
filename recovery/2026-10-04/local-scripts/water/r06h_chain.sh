#!/bin/bash
# waits for the previous water hold (pid $1), then runs hold E under the GPU lock (no worktree path on this command line)
while kill -0 $1 2>/dev/null; do sleep 5; done; sleep 5
cd ~/sm2-n1/water
V=/Game/Water/Variants; M=/Game/Water/Maps
export RD=$HOME/sm2-n1/_scratch/water/r06h VJ=$PWD/tools/water/r06/variantsH.json
export SHOTS="$M/Water_View_RiverLow|base_rl|8,10,12,14,16 $M/Water_View_RiverSun|base_rs $V/Water_Var_R45CB_river_low|R45CB_rl|8,10,12,14,16 $V/Water_Var_R45CB_river_sun|R45CB_rs $V/Water_Var_R4CB_river_low|R4CB_rl|8,10,12,14,16 $V/Water_Var_R4CB_river_sun|R4CB_rs"
exec /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash tools/water/r06/holdA.sh
