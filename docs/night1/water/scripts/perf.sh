#!/bin/bash
# exclusive GPU perf runs: water ON / OFF (MPC_Water.Off) x S4 perch / river_low, 3840x2160 output, TSR 67 % (2573x1447 internal), static camera
R=/Users/midir/sm2-n1/water-ab-sonnet/docs/night1/water/round-01
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
RG=/Users/midir/sm2-n1/water-ab-sonnet/unreal/WebHomage/Scripts/run_game.sh
OUTB=/Users/midir/sm2-n1/_scratch/water-sonnet/perf
mkdir -p $OUTB $R/perf_runs
for spec in "$@"; do
  NAME="${spec%%=*}"; MAP="${spec#*=}"
  rm -rf $OUTB/$NAME
  $G perf --label water-sonnet --json $R/perf_runs/${NAME}_gpu.json -- $RG $OUTB/$NAME -map $MAP -res 3840x2160 -perf 20:40 -name $NAME -exec "r.ScreenPercentage 67" -timeout 900 > $OUTB/$NAME.log 2>&1
  echo "$NAME rc=$?" >> $OUTB/status.txt
  cp $OUTB/$NAME/${NAME}_perf.json $R/perf_runs/ 2>/dev/null
done
echo ALLDONE >> $OUTB/status.txt
