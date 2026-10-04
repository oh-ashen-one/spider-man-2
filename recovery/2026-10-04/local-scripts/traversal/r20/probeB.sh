#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/traversal/r20
./probe_batch.sh c_wallrun_perch:11 w1_wallrun_tall_zip:8 w2_wallrun_side_zip:7 a_swing_chain:15.6
TAG=_g0 XARGS="-WHWallGait=0" ./probe_batch.sh c_wallrun_perch:11 w1_wallrun_tall_zip:8 w2_wallrun_side_zip:7
