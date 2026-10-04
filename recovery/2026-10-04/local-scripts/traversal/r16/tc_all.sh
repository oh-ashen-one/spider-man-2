#!/bin/bash
# runs the TC checker on every probed sequence (probe dir) and prints the verdict lines only
D=${D:-/Users/midir/sm2-n1/_scratch/traversal/r16/probe}
cd /Users/midir/sm2-n1/traversal/docs/night1/traversal
for n in "$@"; do
  python3 trickcam_check.py $D/$n/probe_telemetry.csv $n --quiet | cut -c1-${W:-330}
  echo
done
