#!/bin/bash
# 3840x2160 stills of the RUNNING lineup game (real-time run, not -movie; game seconds drift when the machine is below 60 fps).
# usage: tools/ue_char/capture_4k_stills.sh <out_dir>       Fan homage project; not official Marvel/Sony/Insomniac.
set -e
WT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT=${1:-/Users/midir/sm2-n1/_scratch/characters/stills4k}
mkdir -p "$OUT"
"$WT/tools/ue_char/ue_wait.sh"   # owner rule: never a 3rd+ Unreal instance (run_game.sh passes -RenderOffScreen -NoSound)
ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | tee "$OUT/gpu_util_before.txt"   # shared GPU: report next to any frame time
cd "$WT/unreal/WebHomage"
Scripts/run_game.sh "$OUT" -map /Game/Tests/Characters/Char_Lineup -res 3840x2160 -shots 3,8,13,18,21 -perf 3:22 -quit 23 -name lineup4k -timeout 1800 < /dev/null | tail -8
for f in "$OUT"/lineup4k_[0-9][0-9]_t*.png; do
  ffmpeg -loglevel error -y -i "$f" -q:v 2 "${f%.png}.jpg"
done
ls -la "$OUT"/lineup4k_*.jpg
