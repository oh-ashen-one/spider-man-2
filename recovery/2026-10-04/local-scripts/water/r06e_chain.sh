#!/bin/bash
# waits for the previous water hold (pid $1), then runs hold E under the GPU lock (no worktree path on this command line)
while kill -0 $1 2>/dev/null; do sleep 5; done; sleep 5
cd ~/sm2-n1/water
V=/Game/Water/Variants; M=/Game/Water/Maps
export RD=$HOME/sm2-n1/_scratch/water/r06e VJ=$PWD/tools/water/r06/variantsE.json
export SHOTS="$M/Water_View_RiverSun|base_rs $V/Water_Var_GC_river_sun|GC_rs $M/Water_View_RiverLow|base_rl $V/Water_Var_GA_river_sun|GA_rs $V/Water_Var_GD_river_sun|GD_rs $V/Water_Var_NG_river_sun|NG_rs $V/Water_Var_CB_river_low|CB_rl $V/Water_Var_CB_river_sun|CB_rs $M/Water_View_HarbourHigh|base_hh"
exec /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash tools/water/r06/holdA.sh
