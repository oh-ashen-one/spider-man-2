#!/bin/bash
# Capture the RUNNING lineup game (/Game/Tests/Characters/Char_Lineup) with F1's Scripts/run_game.sh.
# One fixed-step (-movie, 60 fps) 1080p run of the whole 75 s director cycle, then ffmpeg cuts the per-shot-group clips
# (H.264 <= 15 MB) and stills. One launch instead of one per clip (owner rule: few Unreal instances, wait when 3+ run).
# The director starts at shot 0; cumulative shot times: 0 turntable 6 s, 6 hero side 5, 11 hero 3/4 5, 16 suit close-up 4,
# 20 thug 4, 24 brute side 3, 27 citizens wide 5, 32 citizen side 4, 36 citizen 3/4 4, 40 AI suits 5, 45 brute orbit 6,
# 51 thug+brute side tracking 6 (4.2 m), 57 thug 3 m 5, 62 brute 3 m 5, 67 thug face 4, 71 brute face 4 (ends 75).
# usage: tools/ue_char/capture_lineup.sh <out_dir>        Fan homage project; not official Marvel/Sony/Insomniac.
set -e
WT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT=${1:-/Users/midir/sm2-n1/_scratch/characters/mov}
mkdir -p "$OUT"
FR="$OUT/lineup_frames"
if [ ! -d "$FR" ] || [ -z "$(ls "$FR" 2>/dev/null)" ]; then
  "$WT/tools/ue_char/ue_wait.sh"   # owner rule: never a 3rd+ Unreal instance (run_game.sh passes -RenderOffScreen -NoSound)
  cd "$WT/unreal/WebHomage"
  Scripts/run_game.sh "$OUT" -map /Game/Tests/Characters/Char_Lineup -res 1920x1080 -quit 75.5 -name lineup -movie -timeout 5400 -- -WHCharShot=0 < /dev/null | tail -3
fi
cut_clip() {   # name start_s dur_s
  ffmpeg -loglevel error -y -framerate 60 -start_number $(( $2 * 60 )) -i "$FR/MovieFrame%05d.png" -frames:v $(( $3 * 60 )) \
    -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart "$OUT/$1.mp4"
}
cut_still() {  # name time_s
  ffmpeg -loglevel error -y -framerate 60 -start_number $(python3 -c "print(int(round($2 * 60)))") -i "$FR/MovieFrame%05d.png" -frames:v 1 -q:v 2 "$OUT/$1.jpg"
}
cut_clip hero_turntable_walk 0 6
cut_clip hero_run_side_34_hop 6 10
cut_clip hero_suit_fabric_closeup 16 4
cut_clip thug_brute_walk 20 7
cut_clip citizens_walk 27 13
cut_clip ai_suits_walk 40 5
cut_clip brute_orbit 45 6
cut_clip thug_brute_pair_side 51 6
cut_clip thug_side_3m 57 5
cut_clip brute_side_3m 62 5
cut_clip thug_face 67 4
cut_clip brute_face 71 4
cut_still thug_walk_1080 22.5
cut_still brute_walk_1080 25.5
cut_still citizens_wide_1080 29
cut_still ai_suits_1080 42.5
ls -la "$OUT"/*.mp4 "$OUT"/*.jpg
