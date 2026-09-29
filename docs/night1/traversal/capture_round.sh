#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Piece P3 capture driver: replays the traversal scripts in the real game (-game, offscreen) and writes, per sequence,
#   <round>/<seq>.mp4            1920x1080 60 fps (run_game.sh -movie: fixed 1/60 s step, every frame dumped), <= 15 MB
#   <round>/<seq>_telemetry.csv  per-frame traversal / camera / input telemetry of that movie run
#   <round>/stills/<seq>_NN_tSSS.jpg  3840x2160 stills (separate deterministic run, JPEG q92 from the PNG)
# usage: docs/night1/traversal/capture_round.sh <round dir> [seq ...]     (heavy frames go to /Users/midir/sm2-n1/_scratch/traversal)
set -uo pipefail
ROUND="$(mkdir -p "$1" && cd "$1" && pwd)"; shift
HERE="$(cd "$(dirname "$0")" && pwd)"
UE_DIR="$(cd "$HERE/../../../unreal/WebHomage" && pwd)"
SCR="$HERE/scripts"
TMP=/Users/midir/sm2-n1/_scratch/traversal/capture
MAP=/Game/Tests/Traversal/Trav_Canyon
mkdir -p "$TMP" "$ROUND/stills"
# name  script                          quit(s)  still times (game s)
SEQS=(
  "a_swing_chain a_swing_chain.json 15.6 1.0,3.4,5.5,7.4"
  "b_release_trick_dive_zip b_release_trick_dive_zip.json 7.0 0.8,2.2,3.6,5.9"
  "c_wallrun_perch c_wallrun_perch.json 10.0 1.5,3.0,4.6,9.0"
  "d_sprint_jump_first_swing d_sprint_jump_first_swing.json 12.0 2.3,6.5,7.6,9.9"
)
WANT=("$@")
for entry in "${SEQS[@]}"; do
  read -r NAME JSON QUIT SHOTS <<< "$entry"
  if [ ${#WANT[@]} -gt 0 ] && [[ ! " ${WANT[*]} " =~ " $NAME " ]]; then continue; fi
  echo "== $NAME  (GPU $(ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1))"
  # --- 1080p60 movie + telemetry
  rm -rf "$TMP/$NAME"
  "$UE_DIR/Scripts/run_game.sh" "$TMP/$NAME" -map "$MAP" -res 1920x1080 -quit "$QUIT" -name "$NAME" -movie -timeout 3000 \
    -exec "r.ScreenPercentage 100" -- -WHTravScript="$SCR/$JSON" | tail -3
  MP4="$TMP/$NAME/$NAME.mp4"
  if [ -f "$MP4" ]; then
    DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MP4")
    SIZE=$(stat -f %z "$MP4")
    if [ "$SIZE" -gt 15000000 ]; then # re-encode from the frames at a bitrate that fits 14.5 MB
      KBPS=$(python3 -c "print(int(14.5e6*8/1000/float('$DUR')))")
      ffmpeg -loglevel error -y -framerate 60 -i "$TMP/$NAME/${NAME}_frames/MovieFrame%05d.png" -c:v libx264 -preset slow \
        -b:v ${KBPS}k -maxrate ${KBPS}k -bufsize $((KBPS*2))k -pix_fmt yuv420p -movflags +faststart "$ROUND/$NAME.mp4"
    else
      cp "$MP4" "$ROUND/$NAME.mp4"
    fi
    cp "$TMP/$NAME/${NAME}_telemetry.csv" "$ROUND/"
    echo "movie: $ROUND/$NAME.mp4 $(stat -f %z "$ROUND/$NAME.mp4") bytes, ${DUR}s"
  fi
  # --- 3840x2160 stills (same deterministic replay)
  rm -rf "$TMP/${NAME}_4k"
  "$UE_DIR/Scripts/run_game.sh" "$TMP/${NAME}_4k" -map "$MAP" -res 3840x2160 -shots "$SHOTS" -name "$NAME" -timeout 1500 \
    -exec "r.ScreenPercentage 100" -- -benchmark -fps=60 -WHTravScript="$SCR/$JSON" -WHTravCsv="$TMP/${NAME}_4k/stills_telemetry.csv" | tail -2
  for p in "$TMP/${NAME}_4k"/*.png; do
    [ -f "$p" ] && sips -s format jpeg -s formatOptions 92 "$p" --out "$ROUND/stills/$(basename "${p%.png}").jpg" > /dev/null
  done
done
