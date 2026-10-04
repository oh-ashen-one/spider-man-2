#!/bin/zsh
# summarise every S4-type frame under the given dirs with s4_far_check
cd /Users/midir/sm2-n1/city
for f in "$@"; do python3 tools/export/s4_far_check.py $f 2>&1 | sed 's/^== /== /'; done
