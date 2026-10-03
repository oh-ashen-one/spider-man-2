#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 08: the second half of the final captures as sequential GPU holds from the builder's shell (never nested, one engine at a time):
#   (wait for WAIT_PID) -> hold A: table with the tapered bias file + bake -> holds B/C: stitched lapse, the twilight segments re-rendered, the day / night x4 segments reused when
#   present (the bias keys changed by the taper are 06:45-07:09 and 18:54-19:09: they do not reach the x4 segments) -> holds D/E: swing clips tod@19 / tod@22 -> hold F: hold_extra.sh
# usage: WAIT_PID=<pid> nohup tools/perf_ue/sweeps/r08/final_chain2.sh <knobs.json> <bias.json> <extra dir> &
setopt +o nomatch 2>/dev/null
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-08
GS=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
W=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/lapse_stitch/tod_lapse_S4
cd "$WT"
[ -n "$WAIT_PID" ] && while kill -0 $WAIT_PID 2>/dev/null; do sleep 10; done
cp "$2" "$R/lapse_bias_overrides.json"; cp "$1" "$R/diag/knobs_r08.json"
python3 tools/perf_ue/sweeps/r08/make_v4.py --knobs "$1" --r07-bias "$2" --in-place || exit 2
$GS capture --label look --timeout 3600 -- tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod
grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
echo "bake done $(date)"
case "$W" in /Users/midir/sm2-n1/_scratch/look/*) rm -rf "$W/seg1" "$W/seg3";; *) echo "bad work dir $W"; exit 1;; esac
rm -f "$R/tod_lapse_S4.json" "$R/tod_lapse_S4.mp4" "$R/tod_lapse_S4_sheet.jpg"
REUSE=1 $GS capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_lapse.sh
[ -f "$R/tod_lapse_S4.json" ] || REUSE=1 $GS capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_lapse.sh
for P in tod@19 tod@22; do
  $GS capture --label look --timeout 3600 -- python3 tools/perf_ue/capture_looks.py --round "$R" --presets $P --clips --no-stills --no-warmup --res 1920x1080 --timeout 2200
done
$GS capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_extra.sh "$3"
echo "final_chain2 done $(date)"
