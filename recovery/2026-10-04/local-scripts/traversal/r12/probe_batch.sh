#!/bin/bash
# P3 r12: several -nullrhi telemetry probes inside ONE gpu_slot capture hold (wrapped by the caller)
UE=/Users/midir/sm2-n1/traversal/unreal/WebHomage
SC=/Users/midir/sm2-n1/traversal/docs/night1/traversal/scripts/city
OUT=/Users/midir/sm2-n1/_scratch/traversal/r12/probe
for spec in "$@"; do
  EXTRA=""; [ "$spec" = "${HMFIRST:-}" ] && EXTRA="-WHTravHeightmap=$OUT/../hm/heightmap_big.csv -WHTravHmExt=-800,-1000,1100,900"
  n=${spec%%:*}; q=${spec##*:}
  mkdir -p $OUT/$n
  "$UE/Scripts/run_game.sh" $OUT/$n -map /Game/Maps/Manhattan -res 1920x1080 -quit $q -name probe -timeout 900 -- -nullrhi -benchmark -fps=60 \
     -WHTravScript=$SC/$n.json -WHTravCsv=$OUT/$n/probe_telemetry.csv $EXTRA | tail -1
  grep -E "sky launch" $OUT/$n/probe.log | sed 's/^.*Display: //' | head -5
done
