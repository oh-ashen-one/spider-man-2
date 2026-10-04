#!/bin/bash
# gait sweep: knee gap <= .35 m target (c + w1), nullrhi
cd /Users/midir/sm2-n1/_scratch/traversal/r20
while [ -e BUILDING ]; do sleep 5; done
for v in "g3:Top=0.80,Bot=0.90,Lift=0.02,KneeOff=2,Lat=-2,KneeOut=0" "g4:Top=0.74,Bot=0.86,Lift=0.03,KneeOff=3,Lat=-1,KneeOut=0" "g5:Top=0.84,Bot=0.93,Lift=0.02,KneeOff=1,Lat=-4,KneeOut=-0.1"; do
  tag=${v%%:*}; tune=${v#*:}
  for d in c_wallrun_perch w1_wallrun_tall_zip; do rm -rf probe/${d}_$tag; done
  TAG=_$tag XARGS="-WHGaitTune=$tune" ./probe_batch.sh c_wallrun_perch:6 w1_wallrun_tall_zip:4
done
rm -rf probe/x2_rmb_cancel_wall probe/s1_high_swing; ./probe_batch.sh x2_rmb_cancel_wall:5 s1_high_swing:7
