#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07, hold C (ONE gpu_slot hold, budget 2250 s): the round's final captures of the BAKED table built by hold B (no rebuild here unless REBUILD=1):
#   STILLS gen_plans_r07.py --set full (44 poses) -> round-07/stills ; CLIPS swing_tod_22 + swing_tod_18h4 (1920x1080) ; LAPSE (only if hold B could not: LAPSE=1)
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-07
F=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r07/holdC
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
tmo() { local c=$1; local r=$(( $(rem) - 100 )); [ $r -gt $c ] && r=$c; echo $r; }
cd "$WT"; mkdir -p "$R/stills" "$F"
FAILS=0
chk() { local rc=$1 name=$2; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"; if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; return 0; }
if [ "${REBUILD:-0}" = 1 ]; then tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod; chk $? build; fi
python3 tools/perf_ue/sweeps/r07/gen_plans_r07.py --out "$F" --set full
python3 tools/perf_ue/sweeps/run_r06.py --plan "$F/plan_full.json" --out "$F/stills" --timeout $(tmo 1300); chk $? stills
if ls "$F"/stills/tod_*.jpg >/dev/null 2>&1; then rm -f "$R"/stills/tod_*.jpg; cp "$F"/stills/tod_*.jpg "$R/stills/"; cp "$F/stills/session.json" "$R/stills_session.json"; fi
[ $(rem) -gt 430 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@22 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(tmo 600); chk $? clip22; } || echo "skipping night clip (budget)"
[ $(rem) -gt 430 ] && { python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@18.4 --clips --no-stills --no-warmup --res 1920x1080 --timeout $(tmo 600); chk $? clip18; } || echo "skipping golden clip (budget)"
if [ "${LAPSE:-0}" = 1 ] && [ $(rem) -gt 700 ]; then python3 tools/perf_ue/lapse_stitch.py --round "$R" --name tod_lapse_S4 --res 960x540 --deadline $(( T0 + HOLD - 100 )); chk $? lapse; fi
echo "hold_c done t=$(( $(date +%s) - T0 ))s"
