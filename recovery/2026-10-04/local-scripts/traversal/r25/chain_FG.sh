#!/bin/bash
# scratch: start hold F after hold E, hold G after hold F (my own shell, never inside a hold)
R=/Users/midir/sm2-n1/_scratch/traversal/r25
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
H=/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-25/tools/hold4.sh
while [ ! -f $R/hold_E.done ]; do sleep 15; done; sleep 5
[ -f $R/STOP_CHAIN ] && exit 0
$G capture --label traversal -- $H F > $R/holdF.log 2>&1
while [ ! -f $R/hold_F.done ]; do sleep 15; done; sleep 5
[ -f $R/STOP_CHAIN ] && exit 0
$G capture --label traversal -- $H G > $R/holdG.log 2>&1
