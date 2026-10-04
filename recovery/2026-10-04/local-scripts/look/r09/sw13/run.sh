#!/bin/bash
# waits for the given PID (my previous hold) then runs the S4 sweep tour on the integrated Manhattan map
while kill -0 "$1" 2>/dev/null; do sleep 5; done
cd /Users/midir/sm2-n1/look
python3 tools/perf_ue/capture_tour.py --round /Users/midir/sm2-n1/_scratch/look/r09/sw13/out --presets golden --res 1920x1080 --map /Game/Maps/Manhattan \
  --variants /Users/midir/sm2-n1/_scratch/look/r09/sw13/v.json --settle 5 --first-settle 14 --timeout 2000 --work /Users/midir/sm2-n1/_scratch/look/r09/sw13/work
echo "sweep rc $?"
