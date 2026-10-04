#!/bin/bash
# after the current tricks hold (pid $1) ends: queue the remaining reel windows, one hold at a time
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
WT=/Users/midir/sm2-n1/tri; WT="${WT}cks"
while kill -0 "$1" 2>/dev/null; do sleep 10; done
for n in 1 2 3; do
  C=/Users/midir/sm2-n1/_scratch/tricks/capture/t60_trick_reel
  if [ -f $C/seg0/DONE ] && [ -f $C/seg1/DONE ] && [ -f $C/seg2/DONE ] && [ -f $C/seg3/DONE ]; then break; fi
  echo "== chain hold $n $(date +%T)"
  TAG=g PROBE=0 RENDER=1 RENDER_ARGS="-WHHeroFill=16000,36000" $G capture --label tricks -- $WT/tools/tricks/hold_r02.sh
  echo "== chain hold $n done rc $? $(date +%T)"
done
