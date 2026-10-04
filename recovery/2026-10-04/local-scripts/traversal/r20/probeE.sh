#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/traversal/r20
for d in f4_chain_flips x2_rmb_cancel_wall s1_high_swing c_wallrun_perch w1_wallrun_tall_zip a_swing_chain f1_flow_backDouble; do rm -rf probe/$d probe/${d}_ism probe/${d}_rg0; done
./probe_batch.sh f4_chain_flips:13.5 f1_flow_backDouble:9 a_swing_chain:15.6 x2_rmb_cancel_wall:5 s1_high_swing:6 c_wallrun_perch:11 w1_wallrun_tall_zip:8
TAG=_ism XARGS="-WHTravIsmSolid=1" ./probe_batch.sh f4_chain_flips:13.5 a_swing_chain:15.6
TAG=_rg0 XARGS="-WHRopeGuard=0" ./probe_batch.sh f4_chain_flips:13.5
