#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06, hold 1 (diagnostic): run as ONE gpu_slot hold (max 40 min = 2400 s):
#   /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label look --timeout 14400 -- tools/perf_ue/sweeps/r06/hold1.sh
# 1 pinned-metering lapse (L23b, 960x540, the current key table)      -> $S/lapse_L0
# 2 ONE game session: twilight sky sweep A, fog cutoff continuity H, dawn / golden D, moon / cloud / hero M   -> $S/sweep (tod_<pose>_<res>_<variant>.jpg)
# 3 hero clip at 22:00 (960x540, hero lights exposure-independent at nominal scale, P3's own 5000 cd hero fill scaled to 0: keys_herofill0.txt)   -> $S/clips
# 4 diagnostic lapse with the sky fog taken off (HeightFogContribution 0, ambient 0)                    -> $S/lapse_L1
# 5 lapse with the structural round-06 table (make_v2.py defaults)                                        -> $S/lapse_L2
# Budget: gpu_slot SIGTERMs the whole group at 2400 s and SIGKILLs a rendering engine 10 s later (the 2026-09-29 panic pattern), so every step gets a --timeout of the REMAINING
# budget minus 120 s (run_game.sh stops its game with SIGTERM + 60 s wait) and is skipped when under 330 s remain. Stops after two consecutive failed game runs.
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
T0=$(date +%s)
cd "$WT"
mkdir -p "$S" "$S/plans"
HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
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
step() { # step <name> <min seconds needed> <cap> -- cmd... (the command gets TMO as its last arg through $TMO)
  local name=$1 need=$2 cap=$3; shift 3
  local r=$(rem)
  if [ $r -lt $need ]; then echo "skipping $name ($r s left, needs $need)"; return 9; fi
  TMO=$(( r - 120 )); [ $TMO -gt $cap ] && TMO=$cap
  echo "== $name (timeout $TMO s, $r s left)"
  "$@"; local rc=$?
  echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"
  if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi
  [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }
  return $rc
}
step "lapse L0" 330 1500 python3 tools/perf_ue/capture_tod_lapse.py --round "$S/lapse_L0" --shot S4 --from 4.0 --hours 24 --seconds 12 --res 960x540 --name lapse_L0 --keys "$S/plans/keys_base.txt" --no-encode --timeout $(( $(rem) - 120 > 1500 ? 1500 : $(rem) - 120 ))
step "sweep" 900 1900 python3 tools/perf_ue/sweeps/run_r06.py --plan "$S/plans/plan_all.json" --out "$S/sweep" --timeout $(( $(rem) - 120 > 1900 ? 1900 : $(rem) - 120 ))
step "hero clip" 420 1500 python3 tools/perf_ue/capture_looks.py --round "$S/clips" --presets tod@22 --clips --no-stills --no-warmup --clip-res 960x540 --name-suffix _h1 --keys "$S/plans/keys_herofill0.txt" --timeout $(( $(rem) - 120 > 1500 ? 1500 : $(rem) - 120 ))
step "lapse L1" 330 1000 python3 tools/perf_ue/capture_tod_lapse.py --round "$S/lapse_L1" --shot S4 --from 4.0 --hours 24 --seconds 12 --res 960x540 --name lapse_L1 --keys "$S/plans/keys_base.txt" --no-encode --timeout $(( $(rem) - 120 > 1000 ? 1000 : $(rem) - 120 )) \
  --cmds 'exec wh.ToDSet atm.HeightFogContribution 0;exec wh.ToDSet fog.SkyAtmosphereAmbientContributionColorScale 0 0 0 1'
[ -f "$S/plans/keys_v2struct.txt" ] && step "lapse L2 (v2 structure)" 330 1000 python3 tools/perf_ue/capture_tod_lapse.py --round "$S/lapse_L2" --shot S4 --from 4.0 --hours 24 --seconds 12 --res 960x540 --name lapse_L2 --keys "$S/plans/keys_v2struct.txt" --no-encode --timeout $(( $(rem) - 120 > 1000 ? 1000 : $(rem) - 120 ))
echo "hold1 done t=$(( $(date +%s) - T0 ))s"
