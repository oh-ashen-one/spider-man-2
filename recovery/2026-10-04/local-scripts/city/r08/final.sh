#!/bin/zsh
# r08 final: rebuild leaves material + maps, then 8 views x (1080p, 4K); ONE slot hold, strictly sequential, one Unreal process at a time
WT=/Users/midir/sm2-n1/city
RAW=/Users/midir/sm2-n1/_scratch/city/r08/final
mkdir -p $RAW
date "+%H:%M:%S start"
$WT/tools/export/ue/run_commandlet.sh $WT/unreal/WebHomage/Scripts/build_city.py steps=leaves,map
RC=$?
date "+%H:%M:%S commandlet rc=$RC"
[ $RC -ne 0 ] && exit 5
grep -a "Failed to compile\|MISSING\|Traceback" $WT/unreal/WebHomage/Saved/Logs/city_cmdlet.log | head -20
while pgrep -f "MacOS/UnrealEditor .*${WT}/unreal" >/dev/null; do sleep 3; done
$WT/tools/export/capture_round.sh $RAW
date "+%H:%M:%S FINALDONE"
