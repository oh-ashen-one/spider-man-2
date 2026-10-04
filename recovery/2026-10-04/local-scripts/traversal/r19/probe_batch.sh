#!/bin/bash
# P3 r19: -nullrhi probes inside ONE gpu_slot capture hold (wrapped by the caller): live-input repro A/B, floor audit A/B, script probes
UE=/Users/midir/sm2-n1/traversal/unreal/WebHomage
SC=/Users/midir/sm2-n1/traversal/docs/night1/traversal/scripts/city
OUT=/Users/midir/sm2-n1/_scratch/traversal/r19/probe
RD=/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-19
mkdir -p $OUT $RD
for job in "$@"; do
  case $job in
    input)
      for v in polled latched; do
        X=""; [ $v = latched ] && X="-WHTravLatchInput"
        mkdir -p $OUT/in_$v
        "$UE/Scripts/run_game.sh" $OUT/in_$v -map /Game/Maps/Manhattan -res 1280x720 -quit 16 -name inputtest -timeout 600 -- -nullrhi -benchmark -fps=60 \
          -WHTravInputTest=pauseRelease $X -WHTravCsv=$OUT/in_$v/inputtest_telemetry.csv | tail -1
        grep -E "WH_INPUTTEST|WH_INPUT " $OUT/in_$v/inputtest.log > $RD/inputtest_$v.log
        grep -E "RESULT|NO SWING|-> swing" $RD/inputtest_$v.log | sed 's/^.*WH_INPUTTEST/WH_INPUTTEST/'
      done ;;
    floor)
      for v in on off; do
        F=1; [ $v = off ] && F=0
        mkdir -p $OUT/floor_$v
        "$UE/Scripts/run_game.sh" $OUT/floor_$v -map /Game/Maps/Manhattan -res 1280x720 -quit 4 -name floor -timeout 900 -- -nullrhi -benchmark -fps=60 \
          -WHTravSolidFilter=$F -WHTravHeightmap=$RD/floor_$v.csv | tail -1
        grep -E "WebTravWorld|heightmap" $OUT/floor_$v/floor.log | sed 's/^.*Display: //'
      done
      gzip -f $RD/floor_on.csv $RD/floor_off.csv 2>/dev/null; gunzip -k -f $RD/floor_on.csv.gz $RD/floor_off.csv.gz ;;
    s1old)
      mkdir -p $OUT/s1old
      "$UE/Scripts/run_game.sh" $OUT/s1old -map /Game/Maps/Manhattan -res 1920x1080 -quit 6 -name probe -timeout 900 -- -nullrhi -benchmark -fps=60 \
         -WHTravScript=$SC/s1_high_swing.json -WHTravCsv=$OUT/s1old/s1_high_swing_r18_telemetry.csv -WHTravHighFix=0 | tail -1 ;;
    *)
      n=${job%%:*}; q=${job##*:}
      mkdir -p $OUT/$n
      "$UE/Scripts/run_game.sh" $OUT/$n -map /Game/Maps/Manhattan -res 1920x1080 -quit $q -name probe -timeout 900 -- -nullrhi -benchmark -fps=60 \
         -WHTravScript=$SC/$n.json -WHTravCsv=$OUT/$n/${n}_telemetry.csv ${TUNE:-} | tail -1
      grep -E "zip press|flip variant|WH_TRAV landing|catch guard" $OUT/$n/probe.log | sed 's/^.*Display: //;s/^.*Warning: //' | head -20 ;;
  esac
done
