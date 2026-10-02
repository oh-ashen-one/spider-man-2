#!/bin/bash
# water r05 hold 1 gate: runs hold1.sh only if the builder marked it READY (else releases the slot at once)
R5=/Users/midir/sm2-n1/_scratch/water/r05
[ -f $R5/READY1 ] || { echo "HOLD1: not ready, releasing slot"; exit 3; }
exec bash $R5/hold1.sh
