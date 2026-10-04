#!/bin/bash
cd /Users/midir/sm2-n1/tricks
for v in v1 v2 v3; do
  unreal/WebHomage/Scripts/run_game.sh /Users/midir/sm2-n1/_scratch/tricks/probe/$v -map /Game/Maps/Manhattan -res 1920x1080 -quit 46 -name probe -timeout 600 -- -nullrhi -benchmark -fps=60 -WHTravScript=/Users/midir/sm2-n1/_scratch/tricks/probe/$v.json -WHTravCsv=/Users/midir/sm2-n1/_scratch/tricks/probe/$v/probe_telemetry.csv | tail -1
done
