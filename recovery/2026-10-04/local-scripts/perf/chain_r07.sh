#!/bin/bash
# F round 1, phase A4 (V0 content): controls for the r06 session, the capture-gate measurement, Lumen probe density, cloud render target.
cd /Users/midir/sm2-n1/perf
L=/Users/midir/sm2-n1/_scratch/perf/logs; R=/Users/midir/sm2-n1/_scratch/perf/r07; mkdir -p $R
Q5="ctl_base50@50,ctl_mpe4_hwrt0_50@50+set:mpe4+set:hwrt0,rep_tsr100_50@50+set:tsr100,rep_mbhalf_50@50+r.MotionBlur.HalfResGather=1,gate_on50@50+flag:-WHTravMask,lpg32_50@50+r.Lumen.ScreenProbeGather.DownsampleFactor=32,oct6_50@50+r.Lumen.ScreenProbeGather.TracingOctahedronResolution=6,vrt2_50@50+r.VolumetricRenderTarget.Mode=2+r.VolumetricRenderTarget.Scale=0.7"
echo "$(date +%T) q5" >> $L/chain_r07.out
python3 tools/perf_ue2/perf_queue.py --out $R --configs "$Q5" --tag q >> $L/chain_r07.out 2>&1
echo "$(date +%T) chain done" >> $L/chain_r07.out
