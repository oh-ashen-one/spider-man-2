#!/bin/bash
S=/Users/midir/sm2-n1/_scratch/traversal/r13
while kill -0 75595 2>/dev/null; do sleep 10; done
SKIP_WARM=1 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label traversal -- $S/cap_batch.sh a_swing_chain b_release_trick_dive_zip c_wallrun_perch d_sprint_jump_first_swing > $S/capB2.log 2>&1
echo CHAIN2_DONE >> $S/capB2.log
