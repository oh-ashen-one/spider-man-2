#!/bin/bash
# P3 r21 batch 2 (one gpu_slot capture hold): the non-wall shot-list clips with the same GO args
R21=/Users/midir/sm2-n1/_scratch/traversal/r21
RD=/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-21
while [ -e $R21/BUILDING ]; do sleep 5; done
GOARGS=$(cat $R21/GO 2>/dev/null)
cd /Users/midir/sm2-n1/traversal
GPU_OUTER=1 NO_STILLS=1 SKIP_WARM=1 EXTRA_ARGS="$GOARGS" docs/night1/traversal/capture_round.sh $RD "$@"
exit 0
