#!/bin/bash
# tricks r01: render window $1 of the reel (one engine run inside the caller's hold)
cd /Users/midir/sm2-n1/tricks
while pgrep -f "[/]Users/midir/sm2-n1/tricks/unreal/WebHomage/WebHomage.uproject" >/dev/null; do sleep 5; done
NOHOLD=1 SEGS="0:20,20:40,40:60.5" SEG_ONLY=$1 tools/tricks/capture.sh docs/night1/tricks/round-01 t60_trick_reel
