#!/bin/bash
# stop the matrix after variant 3 (kit_plain): tree_lumen alters the GI look and the earlier variants showed no gain
M=/Users/midir/sm2-n1/_scratch/perf/r08/matrix/matrix.log
until [ "$(grep -cE '^cand1_c +sp' $M)" -ge 3 ]; do sleep 2; done
pkill -f "[p]erf_matrix.sh"
echo "$(date +%T) matrix stopped after variant 3 (kit_plain); tree_lumen skipped" >> $M
