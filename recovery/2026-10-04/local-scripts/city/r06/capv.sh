#!/bin/zsh
# usage: capv.sh <map name> <WxH> <outdir>  -- GPU-lock wrapped single-frame capture of City_View_<map>
NAME=$1; RES=$2; OUT=$3; mkdir -p $OUT
/Users/midir/sm2-n1/city/tools/export/ue/wait_slot.sh
cd /Users/midir/sm2-n1/city/unreal/WebHomage
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label city -- Scripts/run_game.sh $OUT -map /Game/Tests/City/City_View_$NAME -res $RES -shots 28 -quit 30 -name ${NAME}_$RES -timeout 900 > $OUT/${NAME}_$RES.run.txt 2>&1
ls $OUT/${NAME}_${RES}_00*.png
