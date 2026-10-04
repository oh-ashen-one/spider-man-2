#!/bin/bash
# waits for the previous water hold (pid $1), then runs hold E under the GPU lock (no worktree path on this command line)
while kill -0 $1 2>/dev/null; do sleep 5; done; sleep 5
cd ~/sm2-n1/water
V=/Game/Water/Variants; M=/Game/Water/Maps
export RD=$HOME/sm2-n1/_scratch/water/r06g2 VJ=$PWD/tools/water/r06/variantsG.json
export SHOTS="$V/Water_Var_DBG12_river_sun|DBG12_rs $V/Water_Var_E80_river_sun|E80_rs $V/Water_Var_E20_river_sun|E20_rs $V/Water_Var_E300_river_sun|E300_rs $V/Water_Var_E80P_river_sun|E80P_rs $V/Water_Var_E80K_river_sun|E80K_rs $M/Water_View_RiverSun|base_rs"
exec /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash tools/water/r06/holdA.sh
