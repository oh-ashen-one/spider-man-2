#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06, hold 4 (via hold2.sh / NEXT_HOLD; one gpu_slot hold, strict remaining budget):
#  hold 3 found: sky light real-time capture time slicing + volumetric fog history are the 2 h/s lighting lag (T4 + T6: wash 214 -> ~100; with both off the lapse has p99 2.8 / 3.4, mean <= 119 / 104);
#  remaining: a one-frame -14 step at 18:58 (frame 446) and the dawn rise 6.4-6.6 (+3..+8 per frame).
#  1 freeze lapses: T12 = TimeSlice 0 + VolumetricFog.HistoryWeight 0 (keeps the volumetric fog), T13 = history weight alone
#  2 V2c lapses (keys_v2c) with T12's settings: frames 440-452 and 66-78 kept as jpgs; and with volumetric fog off for comparison
#  3 hero clip at 22:00 with V2c, 4 plan_d stills (settled probes around the steps, twilight hours, mist, golden / night tours, moon variants)
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
cd "$WT"; mkdir -p "$S/plans_d"
python3 tools/perf_ue/sweeps/r06/gen_plans_d.py --out "$S/plans_d" || exit 1
FAILS=0
step() { local name=$1 need=$2; shift 2; local r=$(rem); if [ $r -lt $need ]; then echo "skipping $name ($r s left, needs $need)"; return 9; fi
  echo "== $name ($r s left)"; "$@"; local rc=$?; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"
  if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; return $rc; }
tmo() { local c=$1; local r=$(( $(rem) - 120 )); [ $r -gt $c ] && r=$c; echo $r; }
KB="$S/plans/keys_base.txt"; KC="$S/plans_d/keys_v2c.txt"
LAP="python3 tools/perf_ue/capture_tod_lapse.py --shot S4 --res 960x540 --no-encode"
LC="r.SkyLight.RealTimeReflectionCapture.TimeSlice=0,r.VolumetricFog.HistoryWeight=0"
F() { local n=$1 cmds=$2; step "freeze $n" 150 ${=LAP} --round "$S/diag4/$n" --name $n --from 19.0 --hours 3 --seconds 1.5 --freeze 2.5 --keys "$KB" --cmds "exec wh.ToDLapseLumen 0${cmds:+;$cmds}" --timeout $(tmo 300); }
F T12_slice0_vfhist0 "exec r.SkyLight.RealTimeReflectionCapture.TimeSlice 0;exec r.VolumetricFog.HistoryWeight 0"
F T13_vfhist0 "exec r.VolumetricFog.HistoryWeight 0"
step "lapse V2c (T12 settings)" 250 ${=LAP} --round "$S/lapse_V2c" --name lapse_V2c --from 4.0 --hours 24 --seconds 12 --keys "$KC" --cmds "exec wh.ToDLapseCvars $LC" --save-frames 440:452,66:78 --timeout $(tmo 600)
step "lapse V2c (volumetric fog off)" 250 ${=LAP} --round "$S/lapse_V2c_novf" --name lapse_V2c_novf --from 4.0 --hours 24 --seconds 12 --keys "$KC" --cmds "exec wh.ToDLapseCvars r.SkyLight.RealTimeReflectionCapture.TimeSlice=0,r.VolumetricFog=0" --save-frames 440:452,66:78 --timeout $(tmo 600)
step "hero clip V2c" 330 python3 tools/perf_ue/capture_looks.py --round "$S/clips_d" --presets tod@22 --clips --no-stills --no-warmup --clip-res 960x540 --name-suffix _v2c --keys "$KC" --timeout $(tmo 600)
step "stills plan_d" 600 python3 tools/perf_ue/sweeps/run_r06.py --plan "$S/plans_d/plan_d.json" --out "$S/sweep_d" --timeout $(tmo 1500)
echo "hold4 done t=$(( $(date +%s) - T0 ))s"
