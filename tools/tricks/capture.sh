#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Tricks C capture driver: replays docs/night1/tricks/scripts/<seq>.json in the REAL game (-game, offscreen, lit /Game/Maps/Manhattan) through
# the GPU lock and writes per sequence:
#   <round>/<seq>.mp4             1920x1080 60 fps (fixed 1/60 s step, every frame dumped, r.ScreenPercentage 100 = native internal), <= 15 MB
#   <round>/<seq>_telemetry.csv   per-frame traversal telemetry (WebTravCharacter)
#   <round>/<seq>_pose.csv.gz     rendered-bone log of the same run (-WHTrickPose, WebTravFlips.cpp)
# usage: tools/tricks/capture.sh <round dir> <seq> [<seq> ...]     env: QUIT_<seq>=s (default 60.5), EXTRA_ARGS="-WHTrickTempo=0 ..."
set -uo pipefail
ROUND="$(mkdir -p "$1" && cd "$1" && pwd)"; shift
HERE="$(cd "$(dirname "$0")" && pwd)"
WT="$(cd "$HERE/../.." && pwd)"
UE_DIR="$WT/unreal/WebHomage"
SCR="$WT/docs/night1/tricks/scripts"
TMP=/Users/midir/sm2-n1/_scratch/tricks/capture
MAP="${TRICK_MAP:-/Game/Maps/Manhattan}"
GPU=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
PRE=0.8
mkdir -p "$TMP"
for NAME in "$@"; do
  Q=$(eval echo "\${QUIT_${NAME}:-60.5}")
  QUITP=$(python3 -c "print(round($Q + $PRE, 3))")
  D="$TMP/$NAME"
  case "$D" in /Users/midir/sm2-n1/_scratch/tricks/*) rm -rf "$D";; *) echo "bad tmp $D"; exit 1;; esac
  echo "== $NAME quit $Q s  (GPU $(ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1))  $(date +%T)"
  "$GPU" capture --label tricks -- "$UE_DIR/Scripts/run_game.sh" "$D" -map "$MAP" -res 1920x1080 -quit "$QUITP" -name "$NAME" -movie -timeout 3000 \
    -exec "r.ScreenPercentage 100" -- -WHTravScript="$SCR/$NAME.json" -WHTravPreroll=$PRE -WHTravMask -WHTrickPose="$D/${NAME}_pose.csv" ${EXTRA_ARGS:-} | tail -3
  RC=${PIPESTATUS[0]}
  echo "gpu_slot rc $RC  $(date +%T)"
  FR="$D/${NAME}_frames"
  if [ -d "$FR" ] && [ -f "$D/${NAME}_telemetry.csv" ]; then
    NF=$(ls "$FR" | wc -l | tr -d ' '); NT=$(( $(wc -l < "$D/${NAME}_telemetry.csv") - 1 ))
    SKIP=$(( NF - NT ))
    echo "frames $NF, telemetry rows $NT -> trimming the first $SKIP frames"
    # mezzanine (scratch, high quality, for sheets / crops) + the committed <= 15 MB movie
    ffmpeg -loglevel error -y -framerate 60 -start_number $SKIP -i "$FR/MovieFrame%05d.png" -c:v libx264 -pix_fmt yuv420p -crf 16 \
      -movflags +faststart "$D/${NAME}_hq.mp4"
    DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$D/${NAME}_hq.mp4")
    KBPS=$(python3 -c "print(min(12000, int(13.8e6*8/1000/float('$DUR'))))")
    ffmpeg -loglevel error -y -i "$D/${NAME}_hq.mp4" -c:v libx264 -preset slow -b:v ${KBPS}k -maxrate $((KBPS*3/2))k -bufsize $((KBPS*2))k \
      -pix_fmt yuv420p -movflags +faststart "$ROUND/$NAME.mp4"
    cp "$D/${NAME}_telemetry.csv" "$ROUND/"
    [ -f "$D/${NAME}_pose.csv" ] && gzip -c "$D/${NAME}_pose.csv" > "$ROUND/${NAME}_pose.csv.gz"
    echo "movie: $ROUND/$NAME.mp4 $(stat -f %z "$ROUND/$NAME.mp4") bytes, ${DUR}s"
    # the PNG frames are regenerable: drop them once both movies exist
    [ -s "$ROUND/$NAME.mp4" ] && [ -s "$D/${NAME}_hq.mp4" ] && rm -rf "$FR"
  else
    echo "NO FRAMES / TELEMETRY for $NAME (see $D/$NAME.log)"
  fi
done
