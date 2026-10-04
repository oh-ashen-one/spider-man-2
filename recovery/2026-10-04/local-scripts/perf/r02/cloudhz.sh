#!/bin/bash
# horizon-cloud look check: route stills at game t = 38 s and 42 s (last third of the route: hero over the far LOD, looking at the horizon)
S=/Users/midir/sm2-n1/perf/tools/perf_ue2/stills2.sh; O=/Users/midir/sm2-n1/_scratch/perf/r02/cloudhz
export SM2_PERF_ROUTE_SHOTS=38,42
$S $O/ctl "ctl@50+set:perf60" "route"
$S $O/cl6 "cl6@50+set:perf60+variant:Cl6" "route"
$S $O/cl4 "cl4@50+set:perf60+variant:Cl4" "route"
$S $O/cl3 "cl3@50+set:perf60+variant:Cl3" "route"
unset SM2_PERF_ROUTE_SHOTS
HYB="+r.Lumen.HardwareRayTracing=1+r.Lumen.ScreenProbeGather.HardwareRayTracing=0+r.Lumen.Reflections.HardwareRayTracing=1"
O2=/Users/midir/sm2-n1/_scratch/perf/r02/refl1
$S $O2/hybrt2 "hybrt2@50+set:perf60+variant:Cl4RT2$HYB" "S2 S1"
$S $O2/hybrt3 "hybrt3@50+set:perf60+variant:Cl4RT3$HYB" "S2 S1"
echo CLOUDHZ DONE
