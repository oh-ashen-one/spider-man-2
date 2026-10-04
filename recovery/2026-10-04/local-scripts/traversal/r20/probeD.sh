#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/traversal/r20
for d in c_wallrun_perch w1_wallrun_tall_zip w2_wallrun_side_zip a_swing_chain f4_chain_flips s1_high_swing f1_flow_backDouble x1_rmb_cancel_flip x2_rmb_cancel_wall; do rm -rf probe/$d probe/${d}_*; done
./probe_batch.sh x1_rmb_cancel_flip:4 x2_rmb_cancel_wall:5 c_wallrun_perch:11 w1_wallrun_tall_zip:8 w2_wallrun_side_zip:7 a_swing_chain:15.6 f4_chain_flips:13.5 f1_flow_backDouble:9 s1_high_swing:6 mouse
TAG=_tc0 XARGS="-WHTrickCancel=0 -WHAirSpeedPose=0" ./probe_batch.sh x1_rmb_cancel_flip:4 x2_rmb_cancel_wall:5
TAG=_g1 XARGS="-WHGaitTune=Top=0.62,Bot=0.80,KneeOff=6,KneeOut=0.05" ./probe_batch.sh c_wallrun_perch:11 w1_wallrun_tall_zip:8
TAG=_g2 XARGS="-WHGaitTune=Top=0.66,Bot=0.78,Lift=0.03,KneeOff=4,KneeOut=0.03" ./probe_batch.sh c_wallrun_perch:11 w1_wallrun_tall_zip:8
TAG= XARGS="-WHTravInputTest=mouseLook" ./probe_batch.sh m1_mouse_swing:6
