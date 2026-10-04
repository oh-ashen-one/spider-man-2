#!/bin/bash
# P3 r12 capture batch inside ONE gpu_slot capture hold (GPU_OUTER=1: capture_round.sh runs run_game.sh directly)
T=/Users/midir/sm2-n1/traversal/docs/night1/traversal
export GPU_OUTER=1
"$T/capture_round.sh" "$T/round-12" f1_sky_backDouble f2_sky_pikeSwan
SKIP_WARM=1 NO_STILLS=1 "$T/capture_round.sh" "$T/round-12" f3_sky_corkscrew f4_chain_flips f5_canyon_backDouble c_wallrun_perch
