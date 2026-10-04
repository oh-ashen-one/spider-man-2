#!/bin/bash
# P3 r20: capture batch inside ONE outer gpu_slot capture hold (GPU_OUTER=1). args = sequence names, or "depth"
cd /Users/midir/sm2-n1/traversal
# r20: extra sequences appended from a file (lets a queued batch grow without losing its queue place)
[ -f /Users/midir/sm2-n1/_scratch/traversal/r20/EXTRA_SEQS ] && set -- "$@" $(cat /Users/midir/sm2-n1/_scratch/traversal/r20/EXTRA_SEQS)
while [ -e /Users/midir/sm2-n1/_scratch/traversal/r20/BUILDING ]; do sleep 5; done
RD=docs/night1/traversal/round-20
UE=/Users/midir/sm2-n1/traversal/unreal/WebHomage
SEQ=()
for a in "$@"; do
  if [ "$a" = depth ]; then
    O=/Users/midir/sm2-n1/_scratch/traversal/r20/depth; rm -rf $O; mkdir -p $O
    "$UE/Scripts/run_game.sh" $O -map /Game/Maps/Manhattan -res 1280x720 -quit 6 -name depth -timeout 1200 -- -benchmark -fps=60 \
      -WHTravDepthAudit=$O/depth_audit.csv | tail -1
    grep -E "depth audit|WebTravWorld" $O/depth.log | sed 's/^.*Display: //'
    cp $O/depth_audit.csv $RD/ 2>/dev/null; gzip -c $O/depth_audit_solid_raw.csv > $RD/depth_audit_solid_raw.csv.gz 2>/dev/null
  else SEQ+=("$a"); fi
done
[ ${#SEQ[@]} -gt 0 ] && GPU_OUTER=1 NO_STILLS=${NO_STILLS:-1} SKIP_WARM=${SKIP_WARM:-} docs/night1/traversal/capture_round.sh $RD "${SEQ[@]}"
exit 0
