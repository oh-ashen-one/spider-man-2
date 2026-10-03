#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 09 hold C (ONE gpu_slot.sh capture hold): headless rebuild of the golden rig + maps only, then the golden S1-S8 tour on /Game/Maps/Manhattan and
# two separate sessions of /Game/Maps/Manhattan_View_S4 (frames at t = 34 / 38 s each), 1920x1080, r.ScreenPercentage 100, then a 13 s fixed-step movie of that view (NOMOVIE=1 skips it).
# usage: gpu_slot.sh capture --label P4 --timeout 7200 -- tools/perf_ue/sweeps/r09/hold_c.sh <out dir>
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"; cd "$WT"; T0=$(date +%s); OUT="$1"; mkdir -p "$OUT"
export SM2_CITY_EXPORT=${SM2_CITY_EXPORT:-/Users/midir/sm2-n1/_scratch/look/manhattan/export/midtown3x3}
tools/perf_ue/rebuild_look.sh rigs,maps golden
grep -q "build_look.*DONE" "${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/build_look_headless.log" || { echo "look rebuild not confirmed"; exit 1; }
echo "build done t=$(( $(date +%s) - T0 ))s"
for k in 1 2; do
  unreal/WebHomage/Scripts/run_game.sh "$OUT/view_s4_$k" -map /Game/Maps/Manhattan_View_S4 -res 1920x1080 -shots 34,38 -quit 40 -name S4_view -timeout 600 -exec "r.ScreenPercentage 100"; echo "view S4 #$k rc=$? t=$(( $(date +%s) - T0 ))s"
done
python3 tools/perf_ue/capture_tour.py --round "$OUT/manhattan" --presets golden --map /Game/Maps/Manhattan --res 1920x1080 --settle 5 --first-settle 14 --timeout 900 --work "$OUT/work_manhattan"; echo "manhattan golden rc=$? t=$(( $(date +%s) - T0 ))s"
if [ -z "$NOMOVIE" ]; then   # S4 clip: the same view, every frame dumped at a fixed 1/60 s step (clouds drift), 13 s of game time; the encode keeps 8-13 s
  unreal/WebHomage/Scripts/run_game.sh "$OUT/movie_s4" -map /Game/Maps/Manhattan_View_S4 -res 1920x1080 -movie -quit 13 -name S4_movie -timeout 1200 -exec "r.ScreenPercentage 100"; echo "movie rc=$? t=$(( $(date +%s) - T0 ))s"
fi
echo "hold_c done t=$(( $(date +%s) - T0 ))s"
