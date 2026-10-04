#!/bin/bash
# P3 r13: capture batch inside ONE outer gpu_slot capture hold (GPU_OUTER=1: no per-run queueing). args = sequence names
cd /Users/midir/sm2-n1/traversal
GPU_OUTER=1 NO_STILLS=${NO_STILLS:-1} SKIP_WARM=${SKIP_WARM:-} docs/night1/traversal/capture_round.sh docs/night1/traversal/round-14 "$@"
