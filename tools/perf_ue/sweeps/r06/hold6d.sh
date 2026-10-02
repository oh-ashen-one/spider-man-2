#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06, hold 8 (C): the FINAL chain after hold 7 (B) (B: max jump 5.75 / p99 3.48 / clipped 1.94 %; the dawn bumps are rig steps: zigzag keys at 07:00 / 07:12 / 07:24, the sun lux x4.5 at 06:15-06:30, the city lights fading while it is dark). C = B + dawn smoothing, later city lights, extra keys, spline least-squares loop (4 iterations), no clips.
# hold 9 (D) = the hold-8 chain continued: knobs_d.json (make_knobs_d.py: the hold-8 loop biases + finer keys at the cliffs), 3 loop iterations with max-delta 3 / gain 1, capture of everything again.
# hold 8 changes: the loop measures only the twilight windows at x16 (lapse_loop_w.py) and the final lapse is stitched from x4 / x16 segments (lapse_stitch.py): the x4 lapse of hold 7 read 54.6 Y at 19:48 against 15.0 for a settled still.
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
F=$S/final6d
STEPS=${1:-loop,build,lapse,stills}
SUB=${SUB:-4}
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
cd "$WT"; mkdir -p "$R/stills" "$F"
FAILS=0
chk() { local rc=$1 name=$2; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"; if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; return 0; }
tmo() { local c=$1; local r=$(( $(rem) - 100 )); [ $r -gt $c ] && r=$c; echo $r; }
KN=$F/knobs_d.json
[ -f "$KN" ] || { echo "no $KN: nothing to do"; exit 2; }
python3 tools/perf_ue/sweeps/r06/make_v2.py --knobs "$KN" --out "$F/doc_pre.json" || exit 2
if [[ $STEPS == *loop* ]]; then
  # each iteration is ~(100 s + 55 s x (SUB-1)... measured: SUB 4 = 280 s at 960x540); 2 iterations + the final lapse must leave time for the build / stills / clips
  python3 tools/perf_ue/lapse_loop_w.py --out "$F/loop" --doc "$F/doc_pre.json" --substeps ${WSUB:-16} --iters ${LOOP_ITERS:-3} --max-delta ${MAXD:-3.0} --gain ${GAIN:-1.0} --keys-hours 5.6,6.1,6.25,6.35,6.4,6.45,6.5,6.55,6.6,6.65,6.7,6.8,6.9,7.0,7.1,7.2,7.3,7.4,7.6,7.8,8.0,8.4,18.8,19.0,19.2,19.35,19.5,19.55,19.6,19.65,19.7,19.75,19.8,19.85,19.9,20.2,20.4,20.6,21.0 --deadline $(( T0 + ${LOOP_DEADLINE:-1000} )) 2>&1 | tail -24
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
  [ $(rem) -gt 700 ] && { rm -rf "$R/tod_lapse_S4_frames_kept"; python3 tools/perf_ue/lapse_stitch.py --round "$R" --name tod_lapse_S4 --res 960x540 --deadline $(( T0 + HOLD - 560 )); chk $? lapse; } || echo "skipping lapse (budget)"
fi
if [[ $STEPS == *stills* ]]; then
  python3 -c "import sys; sys.path.insert(0, 'unreal/WebHomage/Scripts'); import look_tod; open(sys.argv[1], 'w').write(look_tod.to_text(look_tod.expand(look_tod.load_doc())))" "$F/keys_final.txt"
  python3 -c "
import sys, copy; sys.path.insert(0, 'unreal/WebHomage/Scripts'); import look_tod
t = look_tod.expand(look_tod.load_doc())
for k in t['keys']: k['p']['cloudv.Layout_GlobalTexturePlacement'] = [0.0, 0.0, 0.0, 0.0]
open(sys.argv[1], 'w').write(look_tod.to_text(t))" "$F/keys_final_nooffset.txt"
  python3 tools/perf_ue/sweeps/r06/gen_plans_f.py --out "$F" --rt-keys "$F/keys_final.txt" --rt0-keys "$F/keys_final_nooffset.txt"
  [ $(rem) -gt 650 ] && { python3 tools/perf_ue/sweeps/run_r06.py --plan "$F/plan_f.json" --out "$F/stills" --timeout $(tmo 1200); chk $? stills; if [ -f "$F/stills/session.json" ] && ls "$F"/stills/tod_*.jpg >/dev/null 2>&1; then rm -f "$R"/stills/tod_*.jpg "$R"/stills/*.far.json; for X in "$F"/stills/tod_*.jpg; do cp "$X" "$R/stills/"; done; cp "$F/stills/session.json" "$R/stills_session.json"; fi; } || echo "skipping stills (budget)"
fi
if [[ $STEPS == *clips* ]]; then
  [ $(rem) -gt 430 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@22 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(tmo 600); chk $? clip22; } || echo "skipping night clip (budget)"
  [ $(rem) -gt 430 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@18.4 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(tmo 600); chk $? clip18; } || echo "skipping golden clip (budget)"
fi
echo "hold6d $STEPS done t=$(( $(date +%s) - T0 ))s"
