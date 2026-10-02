#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06, hold 2: a queued PLACEHOLDER that keeps its place in the GPU queue while the builder analyses the previous hold. It runs the chain script named in
# $SM2_LOOK_SCRATCH/r06/NEXT_HOLD (one absolute path, written by the builder when the next chain is committed and ready) and exits at once, rendering nothing,
# when that file is missing (then the builder queues it again by hand; never re-queue from inside a hold: a nested gpu_slot call passes through).
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
if [ ! -f "$S/NEXT_HOLD" ]; then echo "hold2: no NEXT_HOLD file: exiting without rendering"; exit 0; fi
NEXT=$(cat "$S/NEXT_HOLD"); mv "$S/NEXT_HOLD" "$S/NEXT_HOLD.used.$(date +%H%M)"
[ -x "$NEXT" ] || { echo "hold2: $NEXT is not executable"; exit 0; }
cd "$WT"
echo "hold2: running $NEXT"
exec "$NEXT"
