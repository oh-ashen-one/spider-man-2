#!/bin/bash
# P3 r20 capture batch B: swing chain, flips, mouse injection, high swing
cd /Users/midir/sm2-n1/traversal
GPU_OUTER=1 NO_STILLS=1 SKIP_WARM=1 docs/night1/traversal/capture_round.sh docs/night1/traversal/round-20 a_swing_chain f1_flow_backDouble f4_chain_flips m1_mouse_swing s1_high_swing
