#!/bin/bash
# P3 r20: -nullrhi probes inside ONE gpu_slot capture hold (wrapped by the caller)
UE=/Users/midir/sm2-n1/traversal/unreal/WebHomage
SC=/Users/midir/sm2-n1/traversal/docs/night1/traversal/scripts/city
OUT=/Users/midir/sm2-n1/_scratch/traversal/r20/probe
RD=/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-20
mkdir -p $OUT $RD
for job in "$@"; do
  case $job in
    dump)
      mkdir -p $OUT/dump
      "$UE/Scripts/run_game.sh" $OUT/dump -map /Game/Maps/Manhattan -res 1280x720 -quit 4 -name dump -timeout 900 -- -nullrhi -benchmark -fps=60 \
        -WHTravDumpPrims=$OUT/dump/prims.csv -WHTravHeightmap=$OUT/dump/floor_r20.csv | tail -1
      grep -E "WebTravWorld|heightmap" $OUT/dump/dump.log | sed 's/^.*Display: //' ;;
    mouse)
      mkdir -p $OUT/mouse
      "$UE/Scripts/run_game.sh" $OUT/mouse -map /Game/Maps/Manhattan -res 1280x720 -quit 7 -name mousetest -timeout 600 -- -nullrhi -benchmark -fps=60 \
        -WHTravInputTest=mouseLook -WHTravCsv=$OUT/mouse/mouselook_telemetry.csv | tail -1
      grep -E "WH_INPUTTEST|WH_INPUT " $OUT/mouse/mousetest.log | sed 's/^.*\(WH_INPUT\)/\1/' | tee $RD/inputtest_mouselook.log ;;
    *)
      n=${job%%:*}; q=${job##*:}
      tag=${TAG:-}
      mkdir -p $OUT/$n$tag
      "$UE/Scripts/run_game.sh" $OUT/$n$tag -map /Game/Maps/Manhattan -res 1920x1080 -quit $q -name probe -timeout 900 -- -nullrhi -benchmark -fps=60 \
         -WHTravScript=$SC/$n.json -WHTravCsv=$OUT/$n$tag/${n}_telemetry.csv ${XARGS:-} | tail -1
      grep -E "zip press|setback|top-out|WH_TRAV landing|WebTravWorld: solid" $OUT/$n$tag/probe.log | sed 's/^.*Display: //;s/^.*Warning: //' | head -20 ;;
  esac
done
