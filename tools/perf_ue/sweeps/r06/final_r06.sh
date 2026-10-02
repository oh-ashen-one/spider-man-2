#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06 final captures. ONE gpu_slot hold per call (max 40 min = 2400 s; remaining-budget guard as in hold1.sh):
#   gpu_slot.sh capture --label look --timeout 21600 -- tools/perf_ue/sweeps/r06/final_r06.sh <steps>      steps = diag,build,stills,lapse,clips (comma separated, default all)
# diag    two freeze lapses (T12 = sky capture time slice 0 + volumetric fog history weight 0, T13 = history alone, 960x540, base keys) decide the render settings of the fast clock (LC below)
# build   headless rebuild of the rigs + maps from Scripts/look_presets.json (the committed table is baked into Look_Rig_tod), confirmed in the log
# stills  ONE session of the rebuilt Look_Midtown_tod (no key override) -> $S/final/ -> round-06/stills/*.jpg
# lapse   24 h lapse from the S4 perch, 1920x1080, metering pinned + the render settings of LC (the instrument condition is written into the json) -> round-06/tod_lapse_S4.{mp4,json,_sheet.jpg}
# clips   swing_tod_18h4 / swing_tod_22 at 1920x1080 (+ -WHTravMask hero box telemetry) -> round-06/
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-06
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
STEPS=${1:-diag,build,stills,lapse,clips}
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
cd "$WT"; mkdir -p "$R/stills" "$S/final" "$S/diag4"
FAILS=0
chk() { local rc=$1 name=$2; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"; if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; }
tmo() { local c=$1; local r=$(( $(rem) - 120 )); [ $r -gt $c ] && r=$c; echo $r; }
LC="r.SkyLight.RealTimeReflectionCapture.TimeSlice=0,r.VolumetricFog.HistoryWeight=0"
KB="$S/plans/keys_base.txt"
LAP="python3 tools/perf_ue/capture_tod_lapse.py --shot S4 --res 960x540 --no-encode"
if [[ $STEPS == *diag* ]]; then
  for T in "T12_slice0_vfhist0|exec r.SkyLight.RealTimeReflectionCapture.TimeSlice 0;exec r.VolumetricFog.HistoryWeight 0" "T13_vfhist0|exec r.VolumetricFog.HistoryWeight 0"; do
    n=${T%%|*}; c=${T#*|}
    [ $(rem) -gt 200 ] && { ${=LAP} --round "$S/diag4/$n" --name $n --from 19.0 --hours 3 --seconds 1.5 --freeze 2.5 --keys "$KB" --cmds "exec wh.ToDLapseLumen 0;$c" --timeout $(tmo 300); chk $? "freeze $n"; }
  done
  W=$(python3 - "$S/diag4/T12_slice0_vfhist0/T12_slice0_vfhist0.json" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1])); h = d['hours_per_frame']; y = d['mean_y_per_frame']
    print('%.1f' % max(v for v, hh in zip(y, h) if 19.8 <= hh <= 22.0))
except Exception: print('999')
PY
)
  echo "T12 wash $W (settled night ~42, native lag 214, hold-3 T10 [slice 0 + volumetric fog off] 104-119)"
  if [ "${W%.*}" -gt 110 ]; then LC="r.SkyLight.RealTimeReflectionCapture.TimeSlice=0,r.VolumetricFog=0"; echo "T12 not enough: lapse render settings fall back to $LC (volumetric fog off during the lapse; disclosed)"; fi
  echo "$LC" > "$S/final/lapse_cvars.txt"
fi
[ -f "$S/final/lapse_cvars.txt" ] && LC=$(cat "$S/final/lapse_cvars.txt")
if [[ $STEPS == *build* ]]; then
  tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod; chk $? build
  grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
fi
if [[ $STEPS == *stills* ]]; then
  python3 tools/perf_ue/sweeps/r06/gen_plans_d.py --out "$S/final" --final
  [ $(rem) -gt 700 ] && { python3 tools/perf_ue/sweeps/run_r06.py --plan "$S/final/plan_final.json" --out "$S/final/stills" --timeout $(tmo 1500); chk $? stills; cp "$S"/final/stills/tod_*.jpg "$R/stills/" 2>/dev/null; cp "$S/final/stills/session.json" "$R/stills_session.json"; } || echo "skipping stills (budget)"
fi
if [[ $STEPS == *lapse* ]]; then
  [ $(rem) -gt 420 ] && { python3 tools/perf_ue/capture_tod_lapse.py --round "$R" --shot S4 --from 4.0 --hours 24 --seconds 12 --cmds "exec wh.ToDLapseCvars $LC" --save-frames 440:452,66:78 --timeout $(tmo 1400); chk $? lapse; rm -rf "$S/final/tod_lapse_S4_frames_kept"; mv "$R/tod_lapse_S4_frames_kept" "$S/final/" 2>/dev/null; } || echo "skipping lapse (budget)"
fi
if [[ $STEPS == *clips* ]]; then
  [ $(rem) -gt 500 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@22 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(tmo 1000); chk $? clip22; } || echo "skipping night clip (budget)"
  [ $(rem) -gt 500 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@18.4 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(tmo 1000); chk $? clip18; } || echo "skipping golden clip (budget)"
fi
echo "final_r06 $STEPS done t=$(( $(date +%s) - T0 ))s"
