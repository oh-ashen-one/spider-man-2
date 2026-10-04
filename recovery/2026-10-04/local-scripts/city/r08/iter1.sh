#!/bin/zsh
# r08 iteration 1: build vehicle protos + rebuild maps (headless commandlet), then S1 + S2 at 1080p; strictly sequential, ONE Unreal process at a time
WT=/Users/midir/sm2-n1/city
OUT=/Users/midir/sm2-n1/_scratch/city/r08/it1
mkdir -p $OUT
date "+%H:%M:%S start"
$WT/tools/export/ue/run_commandlet.sh $WT/unreal/WebHomage/Scripts/build_city.py steps=veh,map
RC=$?
date "+%H:%M:%S commandlet rc=$RC"
[ $RC -ne 0 ] && exit 5
grep -a "Failed to compile\|MISSING\|Traceback" $WT/unreal/WebHomage/Saved/Logs/city_cmdlet.log | head -20
while pgrep -f "MacOS/UnrealEditor .*${WT}/unreal" >/dev/null; do sleep 3; done
$WT/tools/export/capture_one.sh $OUT S1_avenue_street 1920x1080
while pgrep -f "MacOS/UnrealEditor .*${WT}/unreal" >/dev/null; do sleep 3; done
$WT/tools/export/capture_one.sh $OUT S2_avenue_swing 1920x1080
date "+%H:%M:%S done"
