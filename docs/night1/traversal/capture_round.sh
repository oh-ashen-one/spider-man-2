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
# round 06: pre-roll (s) rendered from the start pose before the sequence starts (exposure / Lumen settle), trimmed from the movie
PRE=0.8
mkdir -p "$TMP" "$ROUND/stills"
# name  script                          quit(s)  still times (game s)
SEQS=(
  "a_swing_chain a_swing_chain.json 15.6 1.0,3.4,5.5,7.4"
  "b_release_trick_dive_zip b_release_trick_dive_zip.json 7.0 0.8,2.2,3.6,5.9"
  "c_wallrun_perch c_wallrun_perch.json 10.0 2.0,3.2,4.6,5.45,9.0"
  "d_sprint_jump_first_swing d_sprint_jump_first_swing.json 12.0 2.3,6.5,7.6,9.9"
)
WANT=("$@")
# RULES (owner 2026-09-29): never add a 4th Unreal instance — wait while 3 or more are running
wait_slot() { while [ "$(pgrep -f 'MacOS/UnrealEditor( |$)' | wc -l)" -ge 3 ]; do echo "waiting: 3+ Unreal instances running"; sleep 60; done; }
# round 06: shader / texture warm-up render first (a fresh DDC compiles the hero and city materials on first use, which
# rendered the suit white / unshaded in the first frames of a capture); low-res, not kept
echo "== warm-up render (not kept)"
rm -rf "$TMP/warmup"
wait_slot
"$UE_DIR/Scripts/run_game.sh" "$TMP/warmup" -map "$MAP" -res 960x540 -quit 16 -name warmup -timeout 2400 \
  -- -benchmark -fps=60 -WHTravScript="$SCR/a_swing_chain.json" | tail -1
for entry in "${SEQS[@]}"; do
  read -r NAME JSON QUIT SHOTS <<< "$entry"
  if [ ${#WANT[@]} -gt 0 ] && [[ ! " ${WANT[*]} " =~ " $NAME " ]]; then continue; fi
  echo "== $NAME  (GPU $(ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1))"
  # --- 1080p60 movie + telemetry
  rm -rf "$TMP/$NAME"
  QUITP=$(python3 -c "print(round($QUIT + $PRE, 3))")
  wait_slot
  "$UE_DIR/Scripts/run_game.sh" "$TMP/$NAME" -map "$MAP" -res 1920x1080 -quit "$QUITP" -name "$NAME" -movie -timeout 3000 \
    -exec "r.ScreenPercentage 100" -- -WHTravScript="$SCR/$JSON" -WHTravPreroll=$PRE | tail -3
  FR="$TMP/$NAME/${NAME}_frames"
  if [ -d "$FR" ] && [ -f "$TMP/$NAME/${NAME}_telemetry.csv" ]; then
    NF=$(ls "$FR" | wc -l | tr -d ' '); NT=$(( $(wc -l < "$TMP/$NAME/${NAME}_telemetry.csv") - 1 ))
    SKIP=$(( NF - NT ))   # rendered frames before the sequence's first telemetry row (engine start + pre-roll)
    echo "frames $NF, telemetry rows $NT -> trimming the first $SKIP frames"
    ffmpeg -loglevel error -y -framerate 60 -start_number $SKIP -i "$FR/MovieFrame%05d.png" -c:v libx264 -pix_fmt yuv420p -crf 18 \
      -movflags +faststart "$ROUND/$NAME.mp4"
    DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$ROUND/$NAME.mp4")
    if [ "$(stat -f %z "$ROUND/$NAME.mp4")" -gt 15000000 ]; then # re-encode at a bitrate that fits 14.5 MB
      KBPS=$(python3 -c "print(int(14.5e6*8/1000/float('$DUR')))")
      ffmpeg -loglevel error -y -framerate 60 -start_number $SKIP -i "$FR/MovieFrame%05d.png" -c:v libx264 -preset slow \
        -b:v ${KBPS}k -maxrate ${KBPS}k -bufsize $((KBPS*2))k -pix_fmt yuv420p -movflags +faststart "$ROUND/$NAME.mp4"
    fi
    cp "$TMP/$NAME/${NAME}_telemetry.csv" "$ROUND/"
    echo "movie: $ROUND/$NAME.mp4 $(stat -f %z "$ROUND/$NAME.mp4") bytes, ${DUR}s"
  fi
  # --- 3840x2160 stills (same deterministic replay)
  rm -rf "$TMP/${NAME}_4k"
  # shot times are world seconds: shift by the pre-roll; files are named by sequence time
  SHOTSP=$(python3 -c "print(','.join(str(round(float(t) + $PRE, 3)) for t in '$SHOTS'.split(',')))")
  wait_slot
  "$UE_DIR/Scripts/run_game.sh" "$TMP/${NAME}_4k" -map "$MAP" -res 3840x2160 -shots "$SHOTSP" -name "$NAME" -timeout 1500 \
    -exec "r.ScreenPercentage 100" -- -benchmark -fps=60 -WHTravScript="$SCR/$JSON" -WHTravPreroll=$PRE \
    -WHTravCsv="$TMP/${NAME}_4k/stills_telemetry.csv" | tail -2
  I=0
  for T in ${SHOTS//,/ }; do
    p=$(ls "$TMP/${NAME}_4k/${NAME}_$(printf %02d $I)_"*.png 2>/dev/null | head -1)
    [ -n "$p" ] && sips -s format jpeg -s formatOptions 92 "$p" --out "$ROUND/stills/${NAME}_$(printf %02d $I)_t$(printf %05.1f $T).jpg" > /dev/null
    I=$((I + 1))
  done
done
