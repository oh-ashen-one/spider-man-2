#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06 final captures. ONE gpu_slot hold per call (max 40 min = 2400 s; same remaining-budget guard as hold1.sh):
#   gpu_slot.sh capture --label look --timeout 14400 -- tools/perf_ue/sweeps/r06/final_r06.sh <steps>     steps = build,stills,lapse  |  clips
# build   headless rebuild of the rigs + maps from Scripts/look_presets.json (the committed table is baked into Look_Rig_tod), confirmed in the log
# stills  ONE session of the rebuilt Look_Midtown_tod (no key override) -> $S/final/ (PNG) -> round-06/stills/*.jpg
# lapse   24 h lapse from the S4 perch, 1920x1080, metering pinned (L23b) -> round-06/tod_lapse_S4.{mp4,json,_sheet.jpg}
# clips   swing_tod_18h4 / swing_tod_22 at 1920x1080 (+ -WHTravMask hero box telemetry) -> round-06/
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-06
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
STEPS=${1:-build,stills,lapse}
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
cd "$WT"; mkdir -p "$R/stills" "$S/final"
FAILS=0
chk() { local rc=$1 name=$2; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"; if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; }
if [[ $STEPS == *build* ]]; then
  tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod; chk $? build
  grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
fi
if [[ $STEPS == *stills* ]]; then
  python3 tools/perf_ue/sweeps/r06/gen_final.py --out "$S/plan_final.json"
  [ $(rem) -gt 700 ] && { python3 tools/perf_ue/sweeps/run_r06.py --plan "$S/plan_final.json" --out "$S/final" --timeout $(( $(rem) - 120 > 1500 ? 1500 : $(rem) - 120 )); chk $? stills; cp "$S"/final/tod_*.jpg "$R/stills/" 2>/dev/null; cp "$S/final/session.json" "$R/stills_session.json"; } || echo "skipping stills (budget)"
fi
if [[ $STEPS == *lapse* ]]; then
  [ $(rem) -gt 420 ] && { python3 tools/perf_ue/capture_tod_lapse.py --round "$R" --shot S4 --from 4.0 --hours 24 --seconds 12 --timeout $(( $(rem) - 120 > 1400 ? 1400 : $(rem) - 120 )); chk $? lapse; } || echo "skipping lapse (budget)"
fi
if [[ $STEPS == *clips* ]]; then
  [ $(rem) -gt 500 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@18.4 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(( $(rem) - 120 > 1000 ? 1000 : $(rem) - 120 )); chk $? clip18; } || echo "skipping golden clip (budget)"
  [ $(rem) -gt 500 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@22 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(( $(rem) - 120 > 1000 ? 1000 : $(rem) - 120 )); chk $? clip22; } || echo "skipping night clip (budget)"
fi
echo "final_r06 $STEPS done t=$(( $(date +%s) - T0 ))s"
