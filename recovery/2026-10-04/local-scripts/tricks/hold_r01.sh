#!/bin/bash
# tricks r01 hold: fit the reel's turn keys (nullrhi probes) then capture the reel, all inside one capture slot
cd /Users/midir/sm2-n1/tricks
: clips already rebuilt (13:37)

W=/Users/midir/sm2-n1/_scratch/tricks/route; mkdir -p $W
FIXED_KEYS=12.63:90,29.97:180 python3 tools/tricks/auto_route.py docs/night1/tricks/scripts/t60_trick_reel.json $W/t60_fitted.json $W 2>&1 | grep -v "^run_game\|WH_QUIT"
cp $W/t60_fitted.json docs/night1/tricks/scripts/t60_trick_reel.json
QUIT_t60_trick_reel=60.5 tools/tricks/capture.sh docs/night1/tricks/round-01 t60_trick_reel
