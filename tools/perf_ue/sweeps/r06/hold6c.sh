#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06, hold 8 (C): the FINAL chain after hold 7 (B) (B: max jump 5.75 / p99 3.48 / clipped 1.94 %; the dawn bumps are rig steps: zigzag keys at 07:00 / 07:12 / 07:24, the sun lux x4.5 at 06:15-06:30, the city lights fading while it is dark). C = B + dawn smoothing, later city lights, extra keys, spline least-squares loop (4 iterations), no clips.
# (the text below is the hold-7 header) ONE gpu_slot hold (max 40 min; remaining-budget guard: a step is only started when it can finish, no engine is ever left for the 2400 s kill):
#   0  (CPU)  doc_pre.json = make_v2.py with $F/knobs_final.json (the variant winners of hold 6A + the sun ramp params), no bias overrides yet
#   1  LOOP   lapse_loop.py: sub-stepped lapses (S4 perch, 960x540, nominal 2 h/s, rendered at 2/SUB h/s), DP target (|dY| <= 1.3 per frame, golden / night anchors pinned, clip ceiling) -> exposure-bias overrides of the twilight keys
#   2  (CPU)  make_v2.py --bias-overrides -> Scripts/look_presets.json in place (the committed table of the round)
#   3  BUILD  tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod (headless; the baked table = what the loop measured)
#   4  LAPSE  the final lapse of the baked build -> round-06/tod_lapse_S4.{mp4,json,_sheet.jpg}
#   5  STILLS gen_plans_f.py (40 poses) -> round-06/stills
#   6  CLIPS  swing_tod_22 and swing_tod_18h4 (1920x1080, -WHTravMask hero box telemetry)
# usage (from the worktree): gpu_slot.sh capture --label look --timeout 21600 -- tools/perf_ue/sweeps/r06/hold6b.sh [steps]   steps = loop,build,lapse,stills,clips (default all)
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-06
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
F=$S/final6c
STEPS=${1:-loop,build,lapse,stills}
SUB=${SUB:-4}
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
cd "$WT"; mkdir -p "$R/stills" "$F"
FAILS=0
chk() { local rc=$1 name=$2; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"; if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; return 0; }
tmo() { local c=$1; local r=$(( $(rem) - 100 )); [ $r -gt $c ] && r=$c; echo $r; }
KN=$F/knobs_c.json
[ -f "$KN" ] || { echo "no $KN: nothing to do"; exit 2; }
python3 tools/perf_ue/sweeps/r06/make_v2.py --knobs "$KN" --out "$F/doc_pre.json" || exit 2
if [[ $STEPS == *loop* ]]; then
  # each iteration is ~(100 s + 55 s x (SUB-1)... measured: SUB 4 = 280 s at 960x540); 2 iterations + the final lapse must leave time for the build / stills / clips
  python3 tools/perf_ue/lapse_loop.py --out "$F/loop" --doc "$F/doc_pre.json" --substeps $SUB --iters ${LOOP_ITERS:-4} --deadline $(( T0 + ${LOOP_DEADLINE:-1000} )) 2>&1 | tail -20
  chk ${pipestatus[1]} loop
  [ -f "$F/loop/bias_overrides.json" ] && cp "$F/loop/bias_overrides.json" "$R/lapse_bias_overrides.json"
fi
if [ -f "$F/loop/bias_overrides.json" ]; then OV="--bias-overrides $F/loop/bias_overrides.json"; else OV=""; fi
python3 tools/perf_ue/sweeps/r06/make_v2.py --knobs "$KN" ${=OV} --in-place || exit 2
cp "$WT/unreal/WebHomage/Scripts/look_presets.json" "$F/look_presets_final.json"
if [[ $STEPS == *build* ]]; then
  tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod; chk $? build
  grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
fi
if [[ $STEPS == *lapse* ]]; then
  [ $(rem) -gt 400 ] && { python3 tools/perf_ue/capture_tod_lapse.py --round "$R" --shot S4 --res 960x540 --from 4.0 --hours 24 --seconds 12 --substeps $SUB --save-frames 440:452,66:78 --timeout $(tmo 700); chk $? lapse; rm -rf "$F/tod_lapse_S4_frames_kept"; mv "$R/tod_lapse_S4_frames_kept" "$F/" 2>/dev/null; } || echo "skipping lapse (budget)"
fi
if [[ $STEPS == *stills* ]]; then
  python3 tools/perf_ue/sweeps/r06/gen_plans_f.py --out "$F"
  [ $(rem) -gt 650 ] && { python3 tools/perf_ue/sweeps/run_r06.py --plan "$F/plan_f.json" --out "$F/stills" --timeout $(tmo 1200); chk $? stills; if [ -f "$F/stills/session.json" ] && ls "$F"/stills/tod_*.jpg >/dev/null 2>&1; then rm -f "$R"/stills/tod_*.jpg "$R"/stills/*.far.json; for X in "$F"/stills/tod_*.jpg; do cp "$X" "$R/stills/"; done; cp "$F/stills/session.json" "$R/stills_session.json"; fi; } || echo "skipping stills (budget)"
fi
if [[ $STEPS == *clips* ]]; then
  [ $(rem) -gt 430 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@22 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(tmo 600); chk $? clip22; } || echo "skipping night clip (budget)"
  [ $(rem) -gt 430 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@18.4 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(tmo 600); chk $? clip18; } || echo "skipping golden clip (budget)"
fi
echo "hold6c $STEPS done t=$(( $(date +%s) - T0 ))s"
