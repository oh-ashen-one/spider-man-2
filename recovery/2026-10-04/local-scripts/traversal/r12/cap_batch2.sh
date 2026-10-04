#!/bin/bash
T=/Users/midir/sm2-n1/traversal/docs/night1/traversal
export GPU_OUTER=1
SKIP_WARM=1 NO_STILLS=1 "$T/capture_round.sh" "$T/round-12" f1_sky_backDouble
SKIP_WARM=1 NO_STILLS=1 "$T/capture_round.sh" "$T/round-12" f2_sky_pikeSwan f3_sky_corkscrew f4_chain_flips
