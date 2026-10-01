#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Island piece (A) capture driver: the REAL game (-game, offscreen) on /Game/Maps/Manhattan_WP, every run through the GPU lock.
#   <round>/<route>.mp4              1920x1080 60 fps (run_game.sh -movie: fixed 1/60 s step), H.264, <= 15 MB
#   <round>/<route>_telemetry.csv    per-frame traversal telemetry (WebTravScript)
#   <round>/stills/<name>_*.jpg      3840x2160 stills (JPEG q90 from the PNG)
# usage: docs/night1/island/capture_round.sh <round dir> [run ...]      runs: warmup r1 r2 r3 r4 a1 (default all)
# Heavy frames go to the island scratch (/Users/midir/sm2-n1/_scratch/island/capture); nothing heavy stays in the repo.
set -uo pipefail
ROUND="$(mkdir -p "$1" && cd "$1" && pwd)"; shift
HERE="$(cd "$(dirname "$0")" && pwd)"
UE_DIR="$(cd "$HERE/../../../unreal/WebHomage" && pwd)"
SCR="$HERE/scripts"
TMP=/Users/midir/sm2-n1/_scratch/island/capture
MAP="${ISLAND_MAP:-/Game/Maps/Manhattan_WP}"
GPU=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
RUN() { "$GPU" capture --label island -- "$UE_DIR/Scripts/run_game.sh" "$@"; }
WANT=("$@"); [ ${#WANT[@]} -eq 0 ] && WANT=(warmup r1 r2 r3 r4 a1)
want() { [[ " ${WANT[*]} " =~ " $1 " ]]; }
mkdir -p "$TMP" "$ROUND/stills"
gpu() { ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1; }
if want warmup; then
  echo "== warm-up (shader / DDC compile, not kept)  $(gpu)"
  rm -rf "$TMP/warmup"
  RUN "$TMP/warmup" -map "$MAP" -res 960x540 -quit ${WARM_QUIT:-25} -name warmup -timeout 2300 -- -benchmark -fps=60 -WHTravScript="$SCR/r1_north_avenue.json" | tail -3
fi
route() {  # name script
  local NAME="$1" JSON="$2"
  echo "== $NAME  $(gpu)"
  rm -rf "$TMP/$NAME"
  RUN "$TMP/$NAME" -map "$MAP" -res 1920x1080 -quit ${QUIT:-30.4} -name "$NAME" -movie -timeout 2300 \
    -- -WHTravScript="$SCR/$JSON" -WHTravCsv="$TMP/$NAME/${NAME}_telemetry.csv" | tail -4
  cp "$TMP/$NAME/${NAME}_telemetry.csv" "$ROUND/" 2>/dev/null
  grep -h "WebTravWorld:\|LogWorldPartition.*[Ss]treaming\|WH_QUIT" "$TMP/$NAME/$NAME.log" | sed 's/^.*Display: //' | head -5 > "$ROUND/${NAME}_log_excerpt.txt"
  # <= 15 MB: H.264 crf 23, raise crf until it fits
  local CRF=23
  while :; do
    ffmpeg -loglevel error -y -framerate 60 -i "$TMP/$NAME/${NAME}_frames/MovieFrame%05d.png" -c:v libx264 -preset slow -pix_fmt yuv420p -crf $CRF -movflags +faststart "$ROUND/$NAME.mp4" || break
    [ "$(stat -f %z "$ROUND/$NAME.mp4")" -le 15000000 ] && break
    CRF=$((CRF + 2)); [ $CRF -gt 35 ] && break
  done
  echo "$NAME.mp4 crf $CRF $(stat -f %z "$ROUND/$NAME.mp4") bytes, $(ls "$TMP/$NAME/${NAME}_frames" | wc -l | tr -d ' ') frames"
  # contact frames for the critic pack (1080p jpg at 5 / 12 / 20 / 28 s)
  for s in 5 12 20 28; do f=$(printf "%05d" $((s * 60))); [ -f "$TMP/$NAME/${NAME}_frames/MovieFrame$f.png" ] && \
    ffmpeg -loglevel error -y -i "$TMP/$NAME/${NAME}_frames/MovieFrame$f.png" -q:v 3 "$ROUND/stills/${NAME}_t${s}s_1920x1080.jpg"; done
  rm -rf "$TMP/$NAME/${NAME}_frames"
}
want r1 && route r1_north_avenue r1_north_avenue.json
want r2 && route r2_south_avenue r2_south_avenue.json
want r3 && route r3_crosstown_east r3_crosstown_east.json
want r4 && route r4_wallrun_roofs r4_wallrun_roofs.json
if want a1; then
  for A in a1_high_north a1_high_south; do
    echo "== $A (3840x2160 still)  $(gpu)"
    rm -rf "$TMP/$A"
    RUN "$TMP/$A" -map "$MAP" -res 3840x2160 -shots 0.6 -quit 2.0 -name "$A" -timeout 1200 -- -benchmark -fps=60 -WHTravScript="$SCR/$A.json" | tail -2
    for p in "$TMP/$A"/${A}_*.png; do [ -f "$p" ] && sips -s format jpeg -s formatOptions 90 "$p" --out "$ROUND/stills/$(basename "${p%.png}")_3840x2160.jpg" >/dev/null; done
  done
fi
echo "done: $ROUND"
