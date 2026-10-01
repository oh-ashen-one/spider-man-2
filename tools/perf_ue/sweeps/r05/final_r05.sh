#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 05 final captures, in order (each step takes its own GPU slot hold through gpu_slot.sh; the lock refuses while PAUSED / owner game):
#   1 headless rebuild of the rigs + maps from Scripts/look_presets.json (ToD key table baked into Look_Rig_tod)
#   2 hour tour: every shot at golden 18.4, night 22, overcast 13w1, clear 13, dawn 7.6, blue hour 19.8 (ONE session of Look_Midtown_tod)
#   3 24 h time-lapse from the S4 perch (L23b), 4 swing clips on the ToD map (golden, night)
# usage: tools/perf_ue/sweeps/r05/final_r05.sh [steps=build,tour,lapse,clips]
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-05
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r05
STEPS=${1:-build,tour,lapse,clips}
cd "$WT"
mkdir -p "$R" "$S"
if [[ $STEPS == *build* ]]; then
  tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod; echo "build rc=$?"
  grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
fi
if [[ $STEPS == *tour* ]]; then
  python3 tools/perf_ue/capture_tour.py --round "$R" --tod 18.4,22,13w1,13,7.6,19.8 --res 1920x1080 --timeout 3000 --work "$S/tour" --redo; echo "tour rc=$?"
fi
if [[ $STEPS == *lapse* ]]; then
  python3 tools/perf_ue/capture_tod_lapse.py --round "$R" --shot S4 --from 4.0 --hours 24 --seconds 12; echo "lapse rc=$?"
fi
if [[ $STEPS == *clips* ]]; then
  python3 tools/perf_ue/capture_looks.py --round "$R" --presets tod@18.4,tod@22 --clips --no-stills --no-warmup --res 1920x1080; echo "clips rc=$?"
fi
