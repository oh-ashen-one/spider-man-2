#!/bin/zsh
# usage: cap1.sh <tag> <shotid> [res] [extra run_game args...]
TAG=$1; ID=$2; RES=${3:-1920x1080}; shift 3 2>/dev/null
OUT=/Users/midir/sm2-n1/_scratch/city/r04/$TAG; mkdir -p $OUT
cd /Users/midir/sm2-n1/city/unreal/WebHomage
Scripts/run_game.sh $OUT -map /Game/Tests/City/City_View_$ID -res $RES -shots 28 -quit 30 -name ${ID%%_*}_$RES -timeout 900 "$@" > $OUT/${ID%%_*}_$RES.run.txt 2>&1
ls $OUT/*.png
