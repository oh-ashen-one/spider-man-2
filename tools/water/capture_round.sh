#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# River-water A/B captures (docs/night1/water/views.json), every Unreal run wrapped in the GPU lock (docs/night1/gpu/PROTOCOL.md).
# usage: tools/water/capture_round.sh <round-dir> [warm|stills|movie|perf|all] [label]
#   warm    1080p run of the river view (shader / DDC warm-up, not kept)
#   stills  S4_golden_4k/1080 (/Game/Maps/Manhattan_View_S4) + river_low_4k/1080 (/Game/Water/Maps/Water_View_RiverLow), + midday extras;
#           native internal resolution (r.ScreenPercentage 100), shot at t = 16 s (exposure / Lumen settled)
#   movie   river_low_dolly.mp4: 1080p60 -benchmark -fps=60 -dumpmovie of Water_View_RiverLow_Dolly, t = 6..16 s kept (10 s)
#   perf    EXCLUSIVE gpu_slot perf: tools/perf_ue/run_perf.py, 3840x2160 TSR 67 %, water vs P1 flat-water baseline, river_low + S4
set -uo pipefail
R="$1"; WHAT="${2:-all}"; LABEL="${3:-water}"
WT="$(cd "$(dirname "$0")/../.." && pwd)"
UEP="$WT/unreal/WebHomage"
G=/Users/midir/sm2-n1/_scratch/gpu/bin
SCR="${SM2_WATER_SCR:-/Users/midir/sm2-n1/_scratch/water}/cap"
mkdir -p "$R" "$SCR"; R="$(cd "$R" && pwd)"
cd "$UEP"
shot() { # map res name [exec]
  local map="$1" res="$2" name="$3" ex="${4:-r.ScreenPercentage 100}"
  "$G/gpu_slot.sh" capture --label "$LABEL" -- Scripts/run_game.sh "$SCR/$name" -map "$map" -res "$res" -shots 16 -name "$name" -exec "$ex" -timeout 1500
  local png; png=$(ls -t "$SCR/$name/${name}"_*.png 2>/dev/null | head -1)
  if [ -n "$png" ]; then sips -s format jpeg -s formatOptions 92 "$png" --out "$R/$name.jpg" >/dev/null && echo "still: $R/$name.jpg ($png)"; else echo "NO SCREENSHOT for $name (log $SCR/$name/$name.log)"; fi
}
if [ "$WHAT" = warm ] || [ "$WHAT" = all ]; then
  "$G/gpu_slot.sh" capture --label "$LABEL" -- Scripts/run_game.sh "$SCR/warm" -map /Game/Water/Maps/Water_View_RiverLow -res 1920x1080 -shots 30 -name warm -timeout 2400
fi
if [ "$WHAT" = stills ] || [ "$WHAT" = all ]; then
  shot /Game/Maps/Manhattan_View_S4 3840x2160 S4_golden_4k
  shot /Game/Maps/Manhattan_View_S4 1920x1080 S4_golden_1080
  shot /Game/Water/Maps/Water_View_RiverLow 3840x2160 river_low_4k
  shot /Game/Water/Maps/Water_View_RiverLow 1920x1080 river_low_1080
  shot /Game/Water/Maps/Water_View_RiverLow_Midday 1920x1080 extra_river_low_midday_1080
  shot /Game/Water/Maps/Water_View_S4_Midday 1920x1080 extra_S4_midday_1080
fi
if [ "$WHAT" = movie ] || [ "$WHAT" = all ]; then
  rm -rf "$SCR/dolly"
  "$G/gpu_slot.sh" capture --label "$LABEL" -- Scripts/run_game.sh "$SCR/dolly" -map /Game/Water/Maps/Water_View_RiverLow_Dolly -res 1920x1080 -quit 16.1 -name dolly -movie -timeout 2400
  N=$(ls "$SCR/dolly/dolly_frames" 2>/dev/null | wc -l | tr -d ' ')
  echo "dolly frames: $N"
  # MovieFrame00000 is the first rendered frame (game time 1/60 s): frame n shows t = (n + 1) / 60 s; keep t = 6..16 s -> frames 359..958
  ffmpeg -loglevel error -y -framerate 60 -start_number 359 -i "$SCR/dolly/dolly_frames/MovieFrame%05d.png" -frames:v 600 \
    -c:v libx264 -pix_fmt yuv420p -crf 20 -preset slow -movflags +faststart "$R/river_low_dolly.mp4" && ls -la "$R/river_low_dolly.mp4"
fi
if [ "$WHAT" = perf ] || [ "$WHAT" = all ]; then
  "$G/gpu_slot.sh" perf --label "$LABEL" --json "$R/perf_gpu.json" -- bash -c "
    for m in Water_View_RiverLow Water_Perf_RiverLow_Base Water_Perf_S4 Water_Perf_S4_Base; do
      python3 '$WT/tools/perf_ue/run_perf.py' --out '$SCR/perf/'\$m --map /Game/Water/Maps/\$m --script none --configs tsr67 --res 3840x2160 --window 16:36 --timeout 400 --name \$m || echo \"perf \$m failed\"
    done"
  "$G/gpu_slot.sh" summary "$R/perf_gpu.json"
fi
