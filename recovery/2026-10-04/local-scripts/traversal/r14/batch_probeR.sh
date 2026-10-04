#!/bin/bash
# P3 r13: content build (commandlet, -nullrhi) + -nullrhi telemetry probes inside ONE gpu_slot capture hold (wrapped by the caller)
UE=/Users/midir/sm2-n1/traversal/unreal/WebHomage
SC=/Users/midir/sm2-n1/traversal/docs/night1/traversal/scripts/city
OUT=/Users/midir/sm2-n1/_scratch/traversal/r14/probeR
if [ -n "${BUILD:-}" ]; then
  echo "== build_traversal"
  "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$UE/WebHomage.uproject" -run=pythonscript \
    -script="$UE/Scripts/build_traversal.py" -unattended -nullrhi -NoSound -abslog="$OUT/../build_traversal.log" > /dev/null 2>&1
  echo "build rc $?"; grep -E "flip|Flip|ERROR|Error:" "$OUT/../build_traversal.log" | tail -8
fi
for spec in "$@"; do
  n=${spec%%:*}; q=${spec##*:}
  mkdir -p $OUT/$n
  "$UE/Scripts/run_game.sh" $OUT/$n -map /Game/Maps/Manhattan -res 1920x1080 -quit $q -name probe -timeout 900 -- -nullrhi -benchmark -fps=60 \
     -WHTravScript=${SCD:-$SC}/$n.json -WHTravCsv=$OUT/$n/probe_telemetry.csv ${TUNE:-} | tail -1
  grep -E "flow flip|WebTravAnimInstance" $OUT/$n/probe.log | sed 's/^.*Display: //' | head -6
done
