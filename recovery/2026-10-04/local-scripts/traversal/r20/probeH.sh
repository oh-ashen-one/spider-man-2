#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/traversal/r20
while [ -e BUILDING ]; do sleep 5; done
rm -rf probe/x2_rmb_cancel_wall probe/s1_high_swing; ./probe_batch.sh x2_rmb_cancel_wall:5 s1_high_swing:7
for v in "g6:Top=0.76,Bot=0.90,Lift=0.04,KneeOff=2,Lat=-2,KneeOut=0" "g7:Top=0.78,Bot=0.90,Lift=0.03,KneeOff=2.5,Lat=-2,KneeOut=0"; do
  tag=${v%%:*}; tune=${v#*:}
  for d in c_wallrun_perch w1_wallrun_tall_zip x2_rmb_cancel_wall; do rm -rf probe/${d}_$tag; done
  TAG=_$tag XARGS="-WHGaitTune=$tune" ./probe_batch.sh c_wallrun_perch:6 w1_wallrun_tall_zip:4 x2_rmb_cancel_wall:3.5
done
