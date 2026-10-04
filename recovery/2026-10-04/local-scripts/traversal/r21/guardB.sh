#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/traversal/r21
[ -f /Users/midir/sm2-n1/traversal/docs/night1/traversal/round-21/m1_mouse_swing.mp4 ] && exit 0
exec ./cap_batch2.sh a_swing_chain f1_flow_backDouble f4_chain_flips x1_rmb_cancel_flip m1_mouse_swing
