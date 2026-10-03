#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 08: the round's final captures as SEQUENTIAL GPU holds started from the builder's shell (never nested, one engine at a time):
#   (wait for PID $WAIT_PID: the previous hold) -> merge the round-07 lapse biases with the loop's -> hold 1 bake + full stills (+ the fixed midday preset S1-S8) into round-08/stills
#   -> hold 2 stitched lapse (REUSE in hold 3 when the deadline cut it) -> holds 4 / 5 swing clips tod@19 and tod@22
# usage: WAIT_PID=<pid> nohup tools/perf_ue/sweeps/r08/final_chain.sh <knobs.json> <loop dir> <work dir> &
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-08
GS=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
K=$1; L=$2; F=$3
cd "$WT"; mkdir -p "$F" "$R/stills"
[ -n "$WAIT_PID" ] && while kill -0 $WAIT_PID 2>/dev/null; do sleep 10; done
python3 - "$WT/docs/night1/look/round-07/lapse_bias_overrides.json" "$L/loop/bias_overrides.json" "$F/bias_final.json" "${BIAS_PATCH:-}" <<'PY'
import json, os, sys
o = json.load(open(sys.argv[1]))
if os.path.exists(sys.argv[2]): o.update(json.load(open(sys.argv[2])))
if len(sys.argv) > 4 and sys.argv[4] and os.path.exists(sys.argv[4]): o.update(json.load(open(sys.argv[4])))   # hand-set keys after the loop (BIAS_PATCH)
json.dump(o, open(sys.argv[3], 'w'), indent=1); print('bias overrides', len(o))
PY
cp "$F/bias_final.json" "$R/lapse_bias_overrides.json"; cp "$K" "$R/diag/knobs_r08.json"
# hold 1: bake (make_v4 with the merged biases, R07_BIAS) + stills
R07_BIAS="$F/bias_final.json" MIDDAY=${MIDDAY-1} STILLS_TMO=1700 $GS capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_build_stills.sh "$K" "$F/stills" full
if ls "$F"/stills/tod_*.jpg >/dev/null 2>&1; then rm -f "$R"/stills/tod_*.jpg; cp "$F"/stills/tod_*.jpg "$R/stills/"; cp "$F/stills/session.json" "$R/stills_session.json"; fi
if ls "$F"/stills/midday_round/stills/midday_S*_1920x1080.jpg >/dev/null 2>&1; then cp "$F"/stills/midday_round/stills/midday_S*_1920x1080.jpg "$R/stills/"; fi
cp "$WT/unreal/WebHomage/Scripts/look_presets.json" "$F/look_presets_final.json"
# hold 2 (+3): lapse
$GS capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_lapse.sh
[ -f "$R/tod_lapse_S4.json" ] || REUSE=1 $GS capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_lapse.sh
# holds 4 / 5: swing clips
for P in tod@19 tod@22; do
  $GS capture --label look --timeout 3600 -- python3 tools/perf_ue/capture_looks.py --round "$R" --presets $P --clips --no-stills --no-warmup --res 1920x1080 --timeout 2200
done
echo "final_chain done $(date)"
