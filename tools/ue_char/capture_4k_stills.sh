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
# NATIVE 3840x2160: r.ScreenPercentage 100 (the default auto percentage renders 2160p output at 1920x1080 internal and upscales).
# Still times = director time + ~1.5 s (the director starts about 1.5 s after the automation clock): hero turntable, hero run side,
# hero 3/4, suit close-up, thug 3/4, brute side, thug+brute pair, thug 3 m, brute 3 m, thug face, brute face.
Scripts/run_game.sh "$OUT" -map /Game/Tests/Characters/Char_Lineup -res 3840x2160 -exec "r.ScreenPercentage 100" \
  -shots 4.5,10,14.5,19.5,23.5,27,55.5,61,66,70.5,74.5 -perf 4:76 -quit 76 -name lineup4k -timeout 3600 < /dev/null | tail -14
NAMES=(hero_turntable hero_run_side hero_run_34 suit_closeup thug_walk_34 brute_walk_side thug_brute_pair_side thug_side_3m brute_side_3m thug_face brute_face)
i=0
for f in "$OUT"/lineup4k_[0-9][0-9]_t*.png; do
  ffmpeg -loglevel error -y -i "$f" -q:v 2 "$OUT/${NAMES[$i]}_4k.jpg"
  i=$((i+1))
done
ls -la "$OUT"/*_4k.jpg
