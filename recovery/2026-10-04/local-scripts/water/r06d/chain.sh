#!/bin/bash
# waits for the previous water hold (pid $1), then runs hold D under the GPU lock (no worktree path on this command line: stop_ue.sh matches it)
while kill -0 $1 2>/dev/null; do sleep 5; done; sleep 5
cd ~/sm2-n1/water
V=/Game/Water/Variants; M=/Game/Water/Maps
export RD=$HOME/sm2-n1/_scratch/water/r06d VJ=$PWD/tools/water/r06/variantsD.json
export SHOTS="$V/Water_Var_K3_river_sun|K3_rs $V/Water_Var_R5_river_low|R5_rl $V/Water_Var_K3SP_river_sun|K3SP_rs $V/Water_Var_K4_river_sun|K4_rs $V/Water_Var_SP3_river_sun|SP3_rs $V/Water_Var_R45_river_low|R45_rl $V/Water_Var_K2_river_sun|K2_rs $V/Water_Var_K3P_river_sun|K3P_rs $M/Water_View_RiverSun|base_rs $M/Water_View_RiverLow|base_rl $V/Water_Var_R5_river_sun|R5_rs"
exec /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash tools/water/r06/holdA.sh
