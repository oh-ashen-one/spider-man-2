#!/bin/zsh
# usage: capx.sh <view name> <WxH> <outdir>   (view map City_View_<name>); waits for a free Unreal slot
NAME=$1; RES=${2:-1920x1080}; OUT=${3:-/Users/midir/sm2-n1/_scratch/city/r05/x}
mkdir -p $OUT; /Users/midir/sm2-n1/city/tools/export/ue/wait_slot.sh
cd /Users/midir/sm2-n1/city/unreal/WebHomage
Scripts/run_game.sh $OUT -map /Game/Tests/City/City_View_$NAME -res $RES -shots 28 -quit 30 -name ${NAME}_$RES -timeout 900 > $OUT/${NAME}_$RES.run.txt 2>&1
ls $OUT/${NAME}_${RES}_00*.png
