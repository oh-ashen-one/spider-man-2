#!/bin/bash
# P3 r20 capture batch A (inside ONE gpu_slot capture hold): warm-up + wall / zip / RMB sequences
cd /Users/midir/sm2-n1/traversal
GPU_OUTER=1 NO_STILLS=1 docs/night1/traversal/capture_round.sh docs/night1/traversal/round-20 w1_wallrun_tall_zip w2_wallrun_side_zip c_wallrun_perch x2_rmb_cancel_wall r1_roofrun_zip x1_rmb_cancel_flip
