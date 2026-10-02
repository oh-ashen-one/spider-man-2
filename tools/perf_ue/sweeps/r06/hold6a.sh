#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06, hold 6 (A): decides (1) the lapse instrument (sub-stepped render: the engine's temporal lighting caches settle between output frames; no render setting is changed) and (2) the twilight / night / golden /
# dawn-mist variants of gen_plans_e.py. ONE gpu_slot hold (max 40 min; remaining-budget guard, no step is started that cannot finish):
#   D0   full-day lapse, S4 perch, 960x540, 04:00 start, nominal 2 h/s, --substeps 4 (rendered at 0.5 h/s, every 4th frame kept), baked table, metering pinned
#   SWP  one stills session (run_r06.py) over plan_e.json: W1 / W3 / W4 twilight variants (S4 + the sun-facing pose at 06:30 07:00 07:30 19:00 19:30 20:00 20:30, S4 21:00), N1 night (S4m S4 S1 S6 S5 S7 at 22:00, S1 + S4 mist at 07:36), G1 / G2 golden 18:24 S1..S8
#   D2   dusk window 18:00-22:00 at --substeps 2 (rendered at 1 h/s)
#   CL   swing_tod_22 clip with the N1 keys (hero box clipped px / mean) when the budget allows
# usage (from the worktree): /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label look --timeout 21600 -- tools/perf_ue/sweeps/r06/hold6a.sh
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
cd "$WT"; mkdir -p "$S/diag6" "$S/sweep_e" "$S/clipsA"
FAILS=0
chk() { local rc=$1 name=$2; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"; if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; }
tmo() { local c=$1; local r=$(( $(rem) - 100 )); [ $r -gt $c ] && r=$c; echo $r; }
python3 tools/perf_ue/sweeps/r06/gen_plans_e.py --out "$S/plans_e" || exit 2
LAP="python3 tools/perf_ue/capture_tod_lapse.py --shot S4 --res 960x540 --no-encode"
[ $(rem) -gt 500 ] && { ${=LAP} --round "$S/diag6/D0_sub4" --name D0_sub4 --from 4.0 --hours 24 --seconds 12 --substeps 4 --save-frames 435:455 --timeout $(tmo 700); chk $? D0; } || echo "skipping D0 (budget)"
[ $(rem) -gt 1000 ] && { python3 tools/perf_ue/sweeps/run_r06.py --plan "$S/plans_e/plan_e.json" --out "$S/sweep_e" --timeout $(tmo 1500); chk $? sweep_e; } || echo "skipping sweep (budget)"
[ $(rem) -gt 250 ] && { ${=LAP} --round "$S/diag6/D2_sub2_dusk" --name D2_sub2_dusk --from 18.0 --hours 4 --seconds 2 --substeps 2 --timeout $(tmo 300); chk $? D2; } || echo "skipping D2 (budget)"
[ $(rem) -gt 420 ] && { python3 tools/perf_ue/capture_looks.py --round "$S/clipsA" --presets tod@22 --clips --no-stills --no-warmup --res 1920x1080 --keys "$S/plans_e/keys_N1.txt" --name-suffix _N1 --timeout $(tmo 600); chk $? clip22_N1; } || echo "skipping clip (budget)"
echo "hold6a done t=$(( $(date +%s) - T0 ))s"
