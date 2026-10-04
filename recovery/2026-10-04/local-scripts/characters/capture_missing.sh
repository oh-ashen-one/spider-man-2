#!/bin/bash
# Capture the RUNNING lineup game (/Game/Tests/Characters/Char_Lineup) with F1's Scripts/run_game.sh:
# 60 fps fixed-step movies per shot group (-WHCharShot=N picks the AWHCharShowDirector start shot), H.264 <= 15 MB.
# usage: tools/ue_char/capture_lineup.sh <out_dir>        Fan homage project; not official Marvel/Sony/Insomniac.
set -e
OUT=${1:-/Users/midir/sm2-n1/_scratch/characters/mov}
cd /Users/midir/sm2-n1/characters/unreal/WebHomage
mkdir -p "$OUT"
while read -r shot dur name; do
  [ -z "$name" ] && continue
  Scripts/run_game.sh "$OUT" -map /Game/Tests/Characters/Char_Lineup -res 1920x1080 -quit "$dur" -name "$name" -movie -timeout 1200 -- -WHCharShot="$shot" < /dev/null | tail -1
  rm -rf "$OUT/${name}_frames"
done <<'LIST'
1 10 hero_run_side_34_hop
4 7 thug_brute_walk
9 5 ai_suits_walk
LIST
ls -la "$OUT"/*.mp4
