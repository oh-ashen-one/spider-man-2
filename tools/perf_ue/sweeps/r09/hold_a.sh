#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 09 hold A (inside ONE gpu_slot.sh capture hold): headless look rebuild (rigs + maps of every preset, the city export of the Manhattan build),
# then the golden S1-S8 tour on the INTEGRATED map /Game/Maps/Manhattan, the S4 frame of /Game/Maps/Manhattan_View_S4 (the map's own shot camera),
# and the fixed midday / night preset tours (round-03 floors). 1920x1080, r.ScreenPercentage 100.
# usage: gpu_slot.sh capture --label P4 --timeout 7200 -- tools/perf_ue/sweeps/r09/hold_a.sh <out dir> [nobuild]
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"; cd "$WT"; T0=$(date +%s); OUT="$1"; mkdir -p "$OUT"
export SM2_CITY_EXPORT=${SM2_CITY_EXPORT:-/Users/midir/sm2-n1/_scratch/look/manhattan/export/midtown3x3}
if [ "$2" != nobuild ]; then
  tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod
  grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
  echo "build done t=$(( $(date +%s) - T0 ))s"
fi
python3 tools/perf_ue/capture_tour.py --round "$OUT/manhattan" --presets golden --map /Game/Maps/Manhattan --res 1920x1080 --settle 5 --first-settle 14 --timeout 900 --work "$OUT/work_manhattan"; echo "manhattan golden rc=$? t=$(( $(date +%s) - T0 ))s"
unreal/WebHomage/Scripts/run_game.sh "$OUT/view_s4" -map /Game/Maps/Manhattan_View_S4 -res 1920x1080 -shots 34,38 -quit 40 -name S4_view -timeout 600 -exec "r.ScreenPercentage 100"; echo "view S4 rc=$? t=$(( $(date +%s) - T0 ))s"
python3 tools/perf_ue/capture_tour.py --round "$OUT/fixed" --presets midday,night --res 1920x1080 --timeout 900 --work "$OUT/work_fixed"; echo "fixed rc=$? t=$(( $(date +%s) - T0 ))s"
echo "hold_a done t=$(( $(date +%s) - T0 ))s"
