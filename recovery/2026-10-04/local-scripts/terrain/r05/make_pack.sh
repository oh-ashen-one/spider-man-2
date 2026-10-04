#!/bin/bash
# r05 blind critic pack: 9 views vs refs + 5 progress pairs (r03-merged vs r05) + 2 movies; every 4K image also as _2048.jpg
set -euo pipefail
C=/Users/midir/sm2-n1/_scratch/critic-E-r05
case "$C" in /Users/midir/sm2-n1/_scratch/*) ;; *) exit 1;; esac
mkdir -p "$C"; [ -d "$C/pack" ] && rm -rf "$C/pack"
cd /Users/midir/sm2-n1/terrain
LAWN_PROGRESS=1 python3 tools/terrain/make_pairs.py docs/night1/terrain/round-05 "$C/pairs.json" docs/night1/terrain/round-03
python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py "$C/pack" "$C/pairs.json"
python3 tools/terrain/pack_small.py "$C/pack"
ls "$C/pack" | wc -l; du -sh "$C/pack"
