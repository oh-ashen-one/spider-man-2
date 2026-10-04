#!/bin/bash
# P3 r13: one capture batch at a time (one engine per agent): wait for batch B's lock process, then C, then D
S=/Users/midir/sm2-n1/_scratch/traversal/r13
while kill -0 12717 2>/dev/null; do sleep 10; done
SKIP_WARM=1 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label traversal -- $S/cap_batch.sh f1_flow_backDouble f2_flow_pikeSwan f3_flow_corkscrew > $S/capC.log 2>&1
SKIP_WARM=1 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label traversal -- $S/cap_batch.sh f4_chain_flips f5_canyon_backDouble > $S/capD.log 2>&1
echo CHAIN_DONE >> $S/capD.log
