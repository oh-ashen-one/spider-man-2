#!/bin/zsh
# r10 hold 1: (A) regression + exposure / fog response of the far band on the r09 content, (B) rebuild with the far skyline (steps mat,fsky,map) and the same views on the new geometry.
# ONE engine at a time, sequential, inside one gpu_slot hold.
WT=/Users/midir/sm2-n1/city
OUT=/Users/midir/sm2-n1/_scratch/city/r10/h1
mkdir -p $OUT $OUT/new
sick() { ps -axo stat=,comm= | awk '$1 ~ /[ZE]/ && $2 ~ /UnrealEditor/ && $2 !~ /Services/ {f=1} END {exit !f}'; }
waitengine() { while pgrep -f "MacOS/UnrealEditor .*${WT}/unreal" >/dev/null; do sleep 3; done; }
sick && { echo "ABORT: an UnrealEditor is stuck exiting"; exit 6; }
$WT/tools/export/ue/run_commandlet.sh $WT/tools/export/ue/view_variants.py names=e15,e10,e05,f5,f12 exp_e15=1.5 exp_e10=1.0 exp_e05=0.5 exp_f5=1.0 fog_f5=0.0005 exp_f12=1.0 fog_f12=0.0012 > $OUT/variants.txt 2>&1
RC=$?; echo "variants rc=$RC"; [ $RC -ne 0 ] && { echo "VARIANTS FAILED"; exit 5; }
waitengine
cap() { # dir id
  sick && { echo "ABORT: engine stuck exiting before $2"; exit 7; }
  $WT/tools/export/capture_one.sh $1 $2 1920x1080 > $1/cap_$2.txt 2>&1
  echo "capture $1 $2 rc=$?"
  waitengine; sleep 5
}
for id in S4_perch_skyline S4ve10 S4ve05 S4vf12; do cap $OUT $id; done
echo "PART A DONE"
$WT/tools/export/ue/run_commandlet.sh $WT/unreal/WebHomage/Scripts/build_city.py steps=mat,fsky,map > $OUT/build_new.txt 2>&1
RC=$?; echo "build rc=$RC"; [ $RC -ne 0 ] && { echo "BUILD FAILED"; exit 5; }
waitengine
for id in S4_perch_skyline S4ve10 S4ve05 S6_timessq_street S3_rooftop_watertower; do cap $OUT/new $id; done
echo "PART B DONE"
# part C: car prototypes (plates) + clear-coat cars, rebuilt in their own commandlet so a failure here cannot cost the S4 results above
$WT/tools/export/ue/run_commandlet.sh $WT/unreal/WebHomage/Scripts/build_city.py steps=veh,map > $OUT/build_veh.txt 2>&1
RC=$?; echo "build veh rc=$RC"
waitengine
[ $RC -eq 0 ] && cap $OUT/new S1_avenue_street
echo HOLD1_DONE
