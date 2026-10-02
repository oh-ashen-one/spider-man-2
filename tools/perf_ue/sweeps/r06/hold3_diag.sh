#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06, hold 3: which temporal accumulation makes the 2 h/s lapse lag? (hold 2: Lumen diffuse indirect off = no wash; surface-cache update factors / force update / radiosity history 1 = no change;
# a 0.5 h/s lapse = no wash; after the clock stops the lighting relaxes in ~35 frames.) Freeze lapses (clock 19 -> 22 h at 2 h/s, then stopped), one candidate per run, 960x540, ~45 s each.
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
cd "$WT"
FAILS=0
step() { local name=$1 need=$2; shift 2; local r=$(rem); if [ $r -lt $need ]; then echo "skipping $name ($r s left, needs $need)"; return 9; fi
  echo "== $name ($r s left)"; "$@"; local rc=$?; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"
  if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; return $rc; }
tmo() { local c=$1; local r=$(( $(rem) - 120 )); [ $r -gt $c ] && r=$c; echo $r; }
KB="$S/plans/keys_base.txt"
LAP="python3 tools/perf_ue/capture_tod_lapse.py --shot S4 --res 960x540 --no-encode"
F() { local n=$1 cmds=$2; step "freeze $n" 150 ${=LAP} --round "$S/diag3/$n" --name $n --from 19.0 --hours 3 --seconds 1.5 --freeze 2.5 --keys "$KB" --cmds "exec wh.ToDLapseLumen 0${cmds:+;$cmds}" --timeout $(tmo 300); }
F T0_native ""
F T1_spg1 "exec r.Lumen.ScreenProbeGather.Temporal.MaxFramesAccumulated 1;exec r.Lumen.ScreenProbeGather.TemporalFilterProbes 0;exec r.LumenScene.Radiosity.Temporal.MaxFramesAccumulated 1"
F T2_spg1_upd "exec r.Lumen.ScreenProbeGather.Temporal.MaxFramesAccumulated 1;exec r.Lumen.ScreenProbeGather.TemporalFilterProbes 0;exec r.LumenScene.Radiosity.Temporal.MaxFramesAccumulated 1;exec r.LumenScene.Radiosity.UpdateFactor 4;exec r.LumenScene.DirectLighting.UpdateFactor 4"
F T3_notemporal "exec r.Lumen.ScreenProbeGather.Temporal 0;exec r.LumenScene.Radiosity.Temporal 0;exec r.Lumen.ScreenProbeGather.TemporalFilterProbes 0"
F T4_skyslice0 "exec r.SkyLight.RealTimeReflectionCapture.TimeSlice 0"
F T5_sky0 "exec wh.ToDSet sky.Intensity 0"
F T6_novolfog "exec r.VolumetricFog 0"
F T7_noaa "exec r.AntiAliasingMethod 0"
F T8_radcache "exec r.Lumen.ScreenProbeGather.RadianceCache 0"
F T9_noclouds "exec wh.ToDSet cloud.Cloud_GlobalCoverage -1"
echo "hold3_diag done t=$(( $(date +%s) - T0 ))s"
