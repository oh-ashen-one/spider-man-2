#!/bin/bash
# waits for the previous water hold (pid $1), then runs hold E under the GPU lock (no worktree path on this command line)
while kill -0 $1 2>/dev/null; do sleep 5; done; sleep 5
cd ~/sm2-n1/water
V=/Game/Water/Variants; M=/Game/Water/Maps
export RD=$HOME/sm2-n1/_scratch/water/r06f VJ=$PWD/tools/water/r06/variantsF.json
export SHOTS="$M/Water_View_RiverSun|base_rs $V/Water_Var_GR6_river_sun|GR6_rs $V/Water_Var_GR15_river_sun|GR15_rs $V/Water_Var_GP60_river_sun|GP60_rs $M/Water_View_RiverLow|base_rl $V/Water_Var_GP3_river_sun|GP3_rs $V/Water_Var_GR4_river_sun|GR4_rs $V/Water_Var_NG_river_sun|NG_rs"
exec /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash tools/water/r06/holdA.sh
