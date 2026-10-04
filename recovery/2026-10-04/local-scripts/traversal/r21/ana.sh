#!/bin/bash
# ana.sh <tag>  (empty tag = defaults)
cd /Users/midir/sm2-n1/_scratch/traversal/r21; t=$1; d=pa$t; rm -rf $d; mkdir -p $d
for n in c_wallrun_perch w1_wallrun_tall_zip w2_wallrun_side_zip; do f=probe/$n$t/${n}_telemetry.csv; [ -f $f ] && ln -sf $PWD/$f $d/${n}_telemetry.csv; done
python3 /Users/midir/sm2-n1/traversal/docs/night1/traversal/r21_checks.py $d | grep -E "wallRun|8|c 3.4|PASS|FAIL" | cut -c1-400
