#!/bin/bash
# wait (CPU side, outside any GPU hold) for my previous hold to finish, carry its unfinished queue items to the front of the next queue,
# then queue the next hold (one gpu_slot acquisition)
R=/Users/midir/sm2-n1/_scratch/traversal/r26; PREV=$1; NEXT=$2
while [ ! -f $R/hold_$PREV.done ]; do sleep 20; done
[ -f $R/STOP_CHAIN ] && exit 0
if [ -s $R/queue_$PREV.txt ]; then cat $R/queue_$PREV.txt $R/queue_$NEXT.txt 2>/dev/null > $R/queue_$NEXT.tmp; mv $R/queue_$NEXT.tmp $R/queue_$NEXT.txt; : > $R/queue_$PREV.txt; fi
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label traversal -- /Users/midir/sm2-n1/traversal/docs/night1/traversal/round-26/tools/hold.sh $NEXT > $R/hold_$NEXT.out 2>&1
