#!/bin/zsh
# One view, one resolution, one frame at t = 28 s (no perf window): usage: capture_one.sh <out_dir> <shot id> [WxH]
OUT=$1; ID=$2; RES=${3:-1920x1080}
mkdir -p "$OUT"
/Users/midir/sm2-n1/city/tools/export/ue/wait_slot.sh
cd /Users/midir/sm2-n1/city/unreal/WebHomage
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label city -- Scripts/run_game.sh "$OUT" -map /Game/Tests/City/City_View_$ID -res $RES -shots 28 -quit 30 -name ${ID%%_*}_$RES -timeout 900
