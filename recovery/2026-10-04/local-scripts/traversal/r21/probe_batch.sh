#!/bin/bash
# P3 r21: -nullrhi probes inside ONE gpu_slot capture hold, then (same hold) the movie batch once GO exists:
#   GO = one line of extra game args (-WHGaitTune=... -WHTravTune=...), empty = defaults; SEQS = sequence names; NOGO = skip captures
UE=/Users/midir/sm2-n1/traversal/unreal/WebHomage
SC=/Users/midir/sm2-n1/traversal/docs/night1/traversal/scripts/city
R21=/Users/midir/sm2-n1/_scratch/traversal/r21
OUT=$R21/probe
RD=/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-21
mkdir -p $OUT $RD
while [ -e $R21/BUILDING ]; do sleep 5; done
for job in "$@"; do
  n=${job%%:*}; q=${job##*:}
  tag=${TAG:-}
  rm -rf $OUT/$n$tag; mkdir -p $OUT/$n$tag
  "$UE/Scripts/run_game.sh" $OUT/$n$tag -map /Game/Maps/Manhattan -res 1920x1080 -quit $q -name probe -timeout 900 -- -nullrhi -benchmark -fps=60 \
     -WHTravScript=$SC/$n.json -WHTravCsv=$OUT/$n$tag/${n}_telemetry.csv ${XARGS:-} | tail -1
  grep -E "zip press|setback|step|top-out|WebTravWorld: solid" $OUT/$n$tag/probe.log | sed 's/^.*Display: //;s/^.*Warning: //' | head -20
done
[ -n "${INNER:-}" ] && exit 0
touch $R21/PROBES_DONE
# variant probes requested while waiting (file VARS: lines "tag|args|jobs")
end=$(( $(date +%s) + 600 ))
while [ ! -e $R21/GO ] && [ ! -e $R21/NOGO ] && [ $(date +%s) -lt $end ]; do
  if [ -s $R21/VARS ]; then
    mv $R21/VARS $R21/VARS.run
    while IFS='|' read -r tg xa jobs; do [ -z "$tg" ] && continue; INNER=1 TAG=_$tg XARGS="$xa" $0 $jobs; done < $R21/VARS.run
    touch $R21/VARS_DONE
  fi
  sleep 3
done
[ -e $R21/NOGO ] && exit 0
GOARGS=$(cat $R21/GO 2>/dev/null)
SEQS=$(cat $R21/SEQS 2>/dev/null)
echo "== captures with [$GOARGS]: $SEQS"
cd /Users/midir/sm2-n1/traversal
GPU_OUTER=1 NO_STILLS=1 SKIP_WARM=${SKIP_WARM:-1} EXTRA_ARGS="$GOARGS" docs/night1/traversal/capture_round.sh $RD $SEQS
exit 0
