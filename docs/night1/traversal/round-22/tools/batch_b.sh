#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P3 r22 hold B (inside one gpu_slot capture hold): the non-wall shot-list clips (SEQS_B) with the GO args of hold A
R=/Users/midir/sm2-n1/_scratch/traversal/r22
RD=/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-22
while [ -e $R/BUILDING ]; do sleep 5; done
GOARGS=$(cat $R/GO 2>/dev/null)
cd /Users/midir/sm2-n1/traversal
echo "== hold B captures $(date +%T) with [$GOARGS]: $(cat $R/SEQS_B)"
GPU_OUTER=1 NO_STILLS=1 SKIP_WARM=1 EXTRA_ARGS="$GOARGS" docs/night1/traversal/capture_round.sh $RD $(cat $R/SEQS_B)
echo "== hold B done $(date +%T)"
exit 0
