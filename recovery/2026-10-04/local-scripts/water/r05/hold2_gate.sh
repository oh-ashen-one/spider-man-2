#!/bin/bash
R5=/Users/midir/sm2-n1/_scratch/water/r05
[ -f $R5/READY2 ] || { echo "HOLD2: not ready, releasing slot"; exit 3; }
exec bash $R5/hold2.sh
