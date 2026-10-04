#!/bin/zsh
WT=/Users/midir/sm2-n1/city
OUT=/Users/midir/sm2-n1/_scratch/city/r08/it2
mkdir -p $OUT
date "+%H:%M:%S start"
$WT/tools/export/ue/run_commandlet.sh $WT/unreal/WebHomage/Scripts/build_city.py steps=veh,leaves,map
RC=$?
date "+%H:%M:%S commandlet rc=$RC"
[ $RC -ne 0 ] && exit 5
grep -a "Failed to compile\|MISSING\|Traceback" $WT/unreal/WebHomage/Saved/Logs/city_cmdlet.log | head -20
for v in S1_avenue_street S2_avenue_swing S6_timessq_street S8_aerial_midtown; do
  while pgrep -f "MacOS/UnrealEditor .*${WT}/unreal" >/dev/null; do sleep 3; done
  $WT/tools/export/capture_one.sh $OUT $v 1920x1080
done
date "+%H:%M:%S ITER2DONE"
