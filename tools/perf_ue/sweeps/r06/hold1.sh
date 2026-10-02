#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06, hold 1 (diagnostic): run as ONE gpu_slot hold (max 40 min):
#   /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label look --timeout 14400 -- tools/perf_ue/sweeps/r06/hold1.sh
# 1 pinned-metering lapse (L23b, 960x540, the current key table)      -> $S/lapse_L0
# 2 ONE game session: twilight sky sweep A, fog cutoff continuity H, dawn / golden D, moon / cloud M   -> $S/sweep (tod_<pose>_<res>_<variant>.jpg)
# 3 diagnostic lapse with the sky fog taken off (HeightFogContribution 0, ambient 0)                    -> $S/lapse_L1
# Stops after two consecutive failed game runs (RULES: never relaunch a crashing engine), and skips step 3 when the hold is past 28 min.
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
T0=$(date +%s)
cd "$WT"
mkdir -p "$S" "$S/plans"
python3 tools/perf_ue/sweeps/r06/gen_plans.py --out "$S/plans" || exit 1
python3 - "$S/plans" <<'PY'
import json, sys, os
d = sys.argv[1]
g = []
for n in ('plan_a', 'plan_h', 'plan_d', 'plan_m'): g += json.load(open(os.path.join(d, n + '.json')))['groups']
json.dump({'groups': g}, open(os.path.join(d, 'plan_all.json'), 'w'), indent=1)
print('plan_all', len(g), 'groups')
PY
FAILS=0
python3 tools/perf_ue/capture_tod_lapse.py --round "$S/lapse_L0" --shot S4 --from 4.0 --hours 24 --seconds 12 --res 960x540 --name lapse_L0 --keys "$S/plans/keys_base.txt" --no-encode --timeout 1500
RC=$?; echo "lapse L0 rc=$RC t=$(( $(date +%s) - T0 ))s"; [ $RC -ne 0 ] && FAILS=$((FAILS+1))
python3 tools/perf_ue/sweeps/run_r06.py --plan "$S/plans/plan_all.json" --out "$S/sweep" --timeout 1900
RC=$?; echo "sweep rc=$RC t=$(( $(date +%s) - T0 ))s"; if [ $RC -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi
[ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }
if [ $(( $(date +%s) - T0 )) -lt 1680 ]; then
  python3 tools/perf_ue/capture_tod_lapse.py --round "$S/lapse_L1" --shot S4 --from 4.0 --hours 24 --seconds 12 --res 960x540 --name lapse_L1 --keys "$S/plans/keys_base.txt" --no-encode --timeout 1000 \
    --cmds 'exec wh.ToDSet atm.HeightFogContribution 0;exec wh.ToDSet fog.SkyAtmosphereAmbientContributionColorScale 0 0 0 1'
  echo "lapse L1 rc=$? t=$(( $(date +%s) - T0 ))s"
else echo "skipping lapse L1 (hold past 28 min)"; fi
echo "hold1 done t=$(( $(date +%s) - T0 ))s"
