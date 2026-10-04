#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/traversal/r20
for d in f4_chain_flips x2_rmb_cancel_wall s1_high_swing c_wallrun_perch w1_wallrun_tall_zip w2_wallrun_side_zip a_swing_chain x1_rmb_cancel_flip m1_mouse_swing; do rm -rf probe/$d; done
./probe_batch.sh f4_chain_flips:13.5 x2_rmb_cancel_wall:5 s1_high_swing:7 c_wallrun_perch:11 w1_wallrun_tall_zip:8 w2_wallrun_side_zip:7 a_swing_chain:15.6 x1_rmb_cancel_flip:4 m1_mouse_swing:6 mouse
