#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07, hold B (ONE gpu_slot hold, budget 2250 s, a step only starts when it can finish):
#   0 (CPU)  doc_pre.json = make_v3.py --knobs $F/knobs_r07.json (+ $F/bias_in.json if present)
#   1 LOOP   lapse_loop_w.py: the twilight windows at x16 -> exposure-bias overrides of the twilight keys (LOOP_ITERS, default 2)
#   2 (CPU)  make_v3.py --bias-overrides --in-place -> Scripts/look_presets.json (the committed table of the round)
#   3 BUILD  rebuild_look.sh rigs,maps (headless, the baked table)
#   4 STILLS gen_plans_r07.py --set dome (17 poses) -> $F/stills_dome
#   5 LAPSE  lapse_stitch.py -> round-07/tod_lapse_S4.{mp4,json,_sheet.jpg}
# usage: gpu_slot.sh capture --label look --timeout 21600 -- tools/perf_ue/sweeps/r07/hold_b.sh [steps]   (steps = loop,build,stills,lapse)
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-07
F=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r07/${HOLD_DIR:-holdB}
STEPS=${1:-loop,build,stills,lapse}
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
cd "$WT"; mkdir -p "$R" "$F"
FAILS=0
chk() { local rc=$1 name=$2; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"; if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; return 0; }
KN=$F/knobs_r07.json
[ -f "$KN" ] || { echo "no $KN: nothing to do"; exit 2; }
BI=""; [ -f "$F/bias_in.json" ] && BI="--bias-overrides $F/bias_in.json"
python3 tools/perf_ue/sweeps/r07/make_v3.py --knobs "$KN" ${=BI} --out "$F/doc_pre.json" || exit 2
if [[ $STEPS == *loop* ]]; then
  python3 tools/perf_ue/lapse_loop_w.py --out "$F/loop" --doc "$F/doc_pre.json" --substeps ${WSUB:-16} --iters ${LOOP_ITERS:-2} --max-delta ${MAXD:-2.5} --gain ${GAIN:-0.9} --keys-hours ${KEYS_H:-5.6,6.1,6.35,6.5,6.6,6.7,6.8,6.9,7.0,7.1,7.2,7.3,7.4,7.6,7.8,8.0,8.4,18.6,18.7,18.8,18.9,19.0,19.1,19.2,19.3,19.4,19.5,19.6,19.7,19.8,19.9,20.2,20.4,20.6,21.0} --deadline $(( T0 + ${LOOP_DEADLINE:-900} )) 2>&1 | tail -24
  chk ${pipestatus[1]} loop
fi
OV=""
if [ -f "$F/loop/bias_overrides.json" ]; then
  python3 - "$F" <<'PY'
import json, os, sys
F = sys.argv[1]; o = {}
if os.path.exists(F + '/bias_in.json'): o.update(json.load(open(F + '/bias_in.json')))
o.update(json.load(open(F + '/loop/bias_overrides.json'))); json.dump(o, open(F + '/bias_final.json', 'w'), indent=1)
PY
  OV="--bias-overrides $F/bias_final.json"; cp "$F/bias_final.json" "$R/lapse_bias_overrides.json"
elif [ -f "$F/bias_in.json" ]; then OV="--bias-overrides $F/bias_in.json"; fi
python3 tools/perf_ue/sweeps/r07/make_v3.py --knobs "$KN" ${=OV} --in-place || exit 2
cp "$WT/unreal/WebHomage/Scripts/look_presets.json" "$F/look_presets_final.json"
if [[ $STEPS == *build* ]]; then
  tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod; chk $? build
  grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
fi
if [[ $STEPS == *stills* ]]; then
  python3 tools/perf_ue/sweeps/r07/gen_plans_r07.py --out "$F" --set dome
  [ $(rem) -gt 500 ] && { python3 tools/perf_ue/sweeps/run_r06.py --plan "$F/plan_dome.json" --out "$F/stills_dome" --timeout 600; chk $? stills; python3 tools/perf_ue/dome_check.py --dir "$F/stills_dome" --out "$F/stills_dome/DOME" > /dev/null; } || echo "skipping dome stills (budget)"
fi
if [[ $STEPS == *lapse* ]]; then
  [ $(rem) -gt 700 ] && { rm -rf "$R/tod_lapse_S4_frames_kept"; python3 tools/perf_ue/lapse_stitch.py --round "$R" --name tod_lapse_S4 --res 960x540 --deadline $(( T0 + HOLD - 100 )); chk $? lapse; } || echo "skipping lapse (budget)"
fi
echo "hold_b $STEPS done t=$(( $(date +%s) - T0 ))s"
