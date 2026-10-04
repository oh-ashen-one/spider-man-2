#!/bin/bash
# backup queue place for batch 1: runs only if batch 1 has not run yet
cd /Users/midir/sm2-n1/_scratch/traversal/r21
[ -e PROBES_DONE ] && exit 0
exec ./probe_batch.sh c_wallrun_perch:5.5 w1_wallrun_tall_zip:4.2 w2_wallrun_side_zip:4.5
