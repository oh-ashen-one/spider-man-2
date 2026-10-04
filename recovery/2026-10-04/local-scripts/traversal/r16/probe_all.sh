#!/bin/bash
# probes every sequence (nullrhi) in ONE gpu hold; usage: gpu_slot.sh capture --label traversal -- probe_all.sh [names...]
B=/Users/midir/sm2-n1/_scratch/traversal/r16/batch_probe.sh
ARGS=("$@")
[ ${#ARGS[@]} -eq 0 ] && ARGS=(a_swing_chain:15.6 b_release_trick_dive_zip:7.0 c_wallrun_perch:10.5 d_sprint_jump_first_swing:12.0 f1_flow_backDouble:8.0 f2_flow_pikeSwan:8.0 f3_flow_corkscrew:8.0 f4_chain_flips:11.6 f5_canyon_backDouble:8.0)
$B "${ARGS[@]}" 2>&1 | grep -E "trick camera choice" | cut -c1-600
