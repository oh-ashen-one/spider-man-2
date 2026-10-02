#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07, hold D (the round's FINAL captures; ONE gpu_slot hold, budget 2250 s, a step only starts when it can finish):
#   0 (CPU)  doc_pre.json = make_v3.py --knobs $F/knobs_r07.json --bias-overrides $F/bias_in.json (the hold-C loop biases, adjusted)
#   1 LOOP   lapse_loop_w.py, wide windows (05:30-09:12 and 17:36-21:24 at x16) on EVERY key in them (LOOP_ITERS, default 1)
#   2 (CPU)  make_v3.py --bias-overrides (bias_in + loop) --in-place -> Scripts/look_presets.json
#   3 BUILD  rebuild_look.sh rigs,maps
#   4 STILLS gen_plans_r07.py --set full (44 poses) -> round-07/stills
#   5 LAPSE  lapse_stitch.py with the wide x16 twilight segments -> round-07/tod_lapse_S4.*
#   6 CLIPS  swing_tod_22 + swing_tod_18h4
setopt +o nomatch 2>/dev/null
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-07
F=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r07/holdD
STEPS=${1:-loop,build,stills,lapse,clips}
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
tmo() { local c=$1; local r=$(( $(rem) - 100 )); [ $r -gt $c ] && r=$c; echo $r; }
cd "$WT"; mkdir -p "$R/stills" "$F"
FAILS=0
chk() { local rc=$1 name=$2; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"; if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; return 0; }
KN=$F/knobs_r07.json; BI=$F/bias_in.json
[ -f "$KN" ] && [ -f "$BI" ] || { echo "no knobs / bias_in: nothing to do"; exit 2; }
python3 tools/perf_ue/sweeps/r07/make_v3.py --knobs "$KN" --bias-overrides "$BI" --out "$F/doc_pre.json" || exit 2
if [[ $STEPS == *loop* ]]; then
  python3 tools/perf_ue/lapse_loop_w.py --out "$F/loop" --doc "$F/doc_pre.json" --windows 5.2:4.0,17.3:4.1 --substeps 16 --iters ${LOOP_ITERS:-1} --max-delta 2.0 --gain 0.9 --keys-hours $(cat "$F/keys_h.txt") --deadline $(( T0 + ${LOOP_DEADLINE:-560} )) 2>&1 | tail -10
  chk ${pipestatus[1]} loop
fi
python3 - "$F" <<'PY'
import json, os, sys
F = sys.argv[1]; o = json.load(open(F + '/bias_in.json'))
if os.path.exists(F + '/loop/bias_overrides.json'): o.update(json.load(open(F + '/loop/bias_overrides.json')))
json.dump(o, open(F + '/bias_final.json', 'w'), indent=1)
PY
cp "$F/bias_final.json" "$R/lapse_bias_overrides.json"
if [[ $STEPS == *loop* ]] || [ ! -f "$F/bias_final.json" ]; then python3 tools/perf_ue/sweeps/r07/make_v3.py --knobs "$KN" --bias-overrides "$F/bias_final.json" --in-place || exit 2; fi
cp "$WT/unreal/WebHomage/Scripts/look_presets.json" "$F/look_presets_final.json"
if [[ $STEPS == *build* ]]; then
  tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod; chk $? build
  grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
fi
if [[ $STEPS == *stills* ]]; then
  python3 tools/perf_ue/sweeps/r07/gen_plans_r07.py --out "$F" --set full
  python3 tools/perf_ue/sweeps/run_r06.py --plan "$F/plan_full.json" --out "$F/stills" --timeout $(tmo ${STILLS_TMO:-800}); chk $? stills
  if ls "$F"/stills/tod_*.jpg >/dev/null 2>&1; then rm -f "$R"/stills/tod_*.jpg; cp "$F"/stills/tod_*.jpg "$R/stills/"; cp "$F/stills/session.json" "$R/stills_session.json"; fi
fi
if [[ $STEPS == *lapse* ]]; then
  [ $(rem) -gt 760 ] && { python3 tools/perf_ue/lapse_stitch.py --round "$R" --name tod_lapse_S4 --res 960x540 --segments "3.7:1.8:4:0.3,5.2:4.0:16:0.3,8.9:8.7:4:0.3,17.3:4.1:16:0.3,21.1:6.9:4:0.3" --deadline $(( T0 + HOLD - 60 )); chk $? lapse; } || echo "skipping lapse (budget)"
fi
if [[ $STEPS == *clips* ]]; then
  [ $(rem) -gt 430 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@22 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(tmo 600); chk $? clip22; } || echo "skipping night clip (budget)"
  [ $(rem) -gt 430 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@18.4 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(tmo 600); chk $? clip18; } || echo "skipping golden clip (budget)"
fi
echo "hold_d $STEPS done t=$(( $(date +%s) - T0 ))s"
