#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06, hold 2 (run through hold2.sh / NEXT_HOLD, one gpu_slot hold, strict remaining budget as in hold1.sh):
#  1 WHY is the 2 h/s lapse at 20-22 h 80-170 Y brighter than the settled stills? (hold 1: L0 211 at 20.5 vs settled 43; HFC 0 + fog ambient 0 changed nothing)
#    freeze lapses: the clock runs 19 -> 22 h at 2 h/s and then STOPS; the frames after the stop show the relaxation time of the lighting. Variants switch one subsystem off at a time.
#  2 V2a lapse (structural + twilight table of make_v2.py), 3 V2a twilight stills / dawn mist / golden / moon sweep (plan_b), 4 hero clips at hero 1.4 / 1.8.
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
rem() { echo $(( HOLD - ($(date +%s) - T0) )); }
cd "$WT"; mkdir -p "$S/plans_b"
python3 tools/perf_ue/sweeps/r06/gen_plans_b.py --out "$S/plans_b" || exit 1
FAILS=0
step() { local name=$1 need=$2; shift 2; local r=$(rem); if [ $r -lt $need ]; then echo "skipping $name ($r s left, needs $need)"; return 9; fi
  echo "== $name ($r s left)"; "$@"; local rc=$?; echo "$name rc=$rc t=$(( $(date +%s) - T0 ))s"
  if [ $rc -ne 0 ]; then FAILS=$((FAILS+1)); else FAILS=0; fi; [ $FAILS -ge 2 ] && { echo "two failed game runs: stopping"; exit 3; }; return $rc; }
tmo() { local c=$1; local r=$(( $(rem) - 120 )); [ $r -gt $c ] && r=$c; echo $r; }
KB="$S/plans/keys_base.txt"; [ -f "$KB" ] || KB="$S/plans_b/keys_v2a.txt"
LAP="python3 tools/perf_ue/capture_tod_lapse.py --shot S4 --res 960x540 --no-encode"
F() { local n=$1 keys=$2 cmds=$3; step "freeze $n" 200 ${=LAP} --round "$S/diag/$n" --name $n --from 19.0 --hours 3 --seconds 1.5 --freeze 2.5 --keys "$keys" --cmds "$cmds" --timeout $(tmo 300); }
# Lumen refreshes its surface-cache lighting over 32 / 64 frames (r.LumenScene.DirectLighting / Radiosity.UpdateFactor): at 2 h/s 0.5-1 game hour of stale bounce light. The driver now speeds the refresh up while
# the clock runs > 0.3 h/s (wh.ToDLapseLumen 1, default); F0 / F2 / F3 / F4 switch that off (wh.ToDLapseLumen 0) to measure the engine-default lag.
F F0_native "$KB" "exec wh.ToDLapseLumen 0"
F F1_fastlumen "$KB" ""
F F2_forceupdate "$KB" "exec wh.ToDLapseLumen 0;exec r.LumenScene.Lighting.ForceLightingUpdate 1"
F F4_nolumen "$KB" "exec wh.ToDLapseLumen 0;exec r.Lumen.DiffuseIndirect.Allow 0"
step "slow lapse" 200 ${=LAP} --round "$S/diag/F5_slow" --name F5_slow --from 19.0 --hours 3 --seconds 6 --keys "$KB" --timeout $(tmo 300)
step "lapse L0 + fast Lumen refresh" 250 ${=LAP} --round "$S/lapse_L0f" --name lapse_L0f --from 4.0 --hours 24 --seconds 12 --keys "$KB" --timeout $(tmo 600)
step "lapse V2a" 250 ${=LAP} --round "$S/lapse_V2a" --name lapse_V2a --from 4.0 --hours 24 --seconds 12 --keys "$S/plans_b/keys_v2a.txt" --timeout $(tmo 600)
for H in 14 18; do
  step "hero clip $H" 330 python3 tools/perf_ue/capture_looks.py --round "$S/clips_b" --presets tod@22 --clips --no-stills --no-warmup --clip-res 960x540 --name-suffix _hero$H --keys "$S/plans_b/keys_hero$H.txt" --timeout $(tmo 600)
done
step "stills plan_b" 600 python3 tools/perf_ue/sweeps/run_r06.py --plan "$S/plans_b/plan_b.json" --out "$S/sweep_b" --timeout $(tmo 1500)
echo "hold2_diag done t=$(( $(date +%s) - T0 ))s"
