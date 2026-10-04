#!/bin/bash
# exploration batch 1: reference looks + software-Lumen reflection probes + diagnostics (one capture slot hold, sequential launches)
S=/Users/midir/sm2-n1/perf/tools/perf_ue2/stills2.sh; O=/Users/midir/sm2-n1/_scratch/perf/r02/refl1
$S $O/before "before@50" "S2 S1"
$S $O/perf60 "perf60@50+set:perf60" "S2 S1"
$S $O/t2_refl_nomesh "t2@50+set:perf60+r.Lumen.Reflections.TraceMeshSDFs=0" "S2 S1"
$S $O/t3_nomesh "t3@50+set:perf60+r.Lumen.TraceMeshSDFs=0" "S2"
$S $O/t1_bias100 "t1@50+set:perf60+r.Lumen.DiffuseIndirect.SurfaceBias=100" "S2"
$S $O/t5_scenecolor "t5@50+set:perf60+r.Lumen.Reflections.SampleSceneColorAtHit=2" "S2"
$S $O/hyb "hyb@50+set:perf60+r.Lumen.HardwareRayTracing=1+r.Lumen.ScreenProbeGather.HardwareRayTracing=0+r.Lumen.Reflections.HardwareRayTracing=1" "S2 S1"
$S $O/dx_lumenscene "dlumen@50+set:perf60+ShowFlag.VisualizeLumenScene=1" "S2"
$S $O/dx_meshdf "dmesh@50+set:perf60+ShowFlag.VisualizeMeshDistanceFields=1" "S2"
echo BATCH1 DONE
# ---- batch 2 (appended while running): hardware-RT reflections with a reduced ray-tracing scene / ray budget
HYB="+r.Lumen.HardwareRayTracing=1+r.Lumen.ScreenProbeGather.HardwareRayTracing=0+r.Lumen.Reflections.HardwareRayTracing=1"
$S $O/hybrt "hybrt@50+set:perf60+variant:Cl6RT$HYB" "S2 S1"
$S $O/hybrt_ds2 "hybrt_ds2@50+set:perf60+variant:Cl6RT$HYB+r.Lumen.Reflections.DownsampleFactor=2" "S2 S1"
$S $O/hybrt_ff0 "hybrt_ff0@50+set:perf60+variant:Cl6RT$HYB+r.Lumen.Reflections.HardwareRayTracing.FarField=0" "S2"
$S $O/hybrt_r25 "hybrt_r25@50+set:perf60+variant:Cl6RT$HYB+r.Lumen.Reflections.MaxRoughnessToTrace=0.25" "S2"
echo BATCH2 DONE
# ---- batch 3 (appended while running): route stills t20 / t28 (4K, TSR 50, perf60 software Lumen) for the cloud tracing distance A/B, and a control repeat for the noise floor
$S $O/route_ctl_a "ctl_a@50+set:perf60" "route"
$S $O/route_ctl_b "ctl_b@50+set:perf60" "route"
$S $O/route_cl6 "cl6@50+set:perf60+variant:Cl6" "route"
$S $O/route_cl4 "cl4@50+set:perf60+variant:Cl4" "route"
$S $O/route_cl3 "cl3@50+set:perf60+variant:Cl3" "route"
$S $O/route_cl15 "cl15@50+set:perf60+variant:Cl15" "route"
echo BATCH3 DONE
