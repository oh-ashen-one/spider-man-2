#!/bin/bash
# scratch: start hold D (hold4.sh) once hold C has ended (my own shell, not inside a hold)
R=/Users/midir/sm2-n1/_scratch/traversal/r25
while [ ! -f $R/hold_C.done ]; do sleep 15; done
sleep 5
exec /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label traversal -- /Users/midir/sm2-n1/traversal/docs/night1/traversal/round-25/tools/hold4.sh D
