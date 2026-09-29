#!/bin/zsh
# Capture every SHOTLIST view from the RUNNING game (Scripts/run_game.sh: offscreen -game, auto-activated shot camera),
# with frame times at 1920x1080 and 3840x2160. usage: tools/export/capture_round.sh <round_dir> [ids...]
set -u
OUT=$1; shift
cd "$(dirname "$0")/../../unreal/WebHomage"
IDS=("$@"); [ ${#IDS[@]} -eq 0 ] && IDS=($(python3 -c "import json;print(' '.join(s['id'] for s in json.load(open('Scripts/city_shots.json'))))"))
mkdir -p "$OUT/raw"
for id in $IDS; do
  for res in 1920x1080 3840x2160; do
    /Users/midir/sm2-n1/city/tools/export/ue/wait_slot.sh
    GPU=$(ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1 | grep -o '[0-9]*$')
    /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label city -- Scripts/run_game.sh "$OUT/raw" -map /Game/Tests/City/City_View_$id -res $res -shots 28 -perf 18:28 -name ${id}_${res} -timeout 900 > "$OUT/raw/${id}_${res}.run.txt" 2>&1
    echo "{\"id\":\"$id\",\"res\":\"$res\",\"gpu_util_before_pct\":${GPU:-null}}" > "$OUT/raw/${id}_${res}_gpu.json"
    grep WH_PERF "$OUT/raw/${id}_${res}.run.txt" | tail -1
  done
done
