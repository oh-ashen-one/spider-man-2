#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Terrain piece (E) capture driver: the REAL game (-game, offscreen), every launch through the GPU lock. Run the WHOLE script under ONE slot hold:
#   /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain -- docs/night1/terrain/capture_round.sh docs/night1/terrain/round-01 [stills|moves|warm ...]
# (the per-run gpu_slot calls inside pass through when nested). Outputs:
#   <round>/stills/<id>.jpg           3840x2160 output, internal 1920x1080 (r.ScreenPercentage auto = 50 % -> TSR 2x upscale), terrain build   (V_<id>)
#   <round>/stills/base_<id>.jpg      same camera, the city alone (VB_<id>): the "previous round" baseline
#   <round>/<name>.mp4                1920x1080 60 fps movie (-movie: fixed 1/60 s step, internal 1920x1080 = r.ScreenPercentage 100), <= 15 MB
#   <round>/<name>_telemetry.csv      per-frame traversal telemetry
# Heavy frames stay in /Users/midir/sm2-n1/_scratch/terrain/capture.
set -uo pipefail
ROUND="$(mkdir -p "$1" && cd "$1" && pwd)"; shift
HERE="$(cd "$(dirname "$0")" && pwd)"
UE_DIR="$(cd "$HERE/../../../unreal/WebHomage" && pwd)"
SCR="$HERE/scripts"
TMP=/Users/midir/sm2-n1/_scratch/terrain/capture
GPU="${GPU_CMD:-/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh}"
HOLD_START="${HOLD_START:-$(date +%s)}"; HOLD_BUDGET="${HOLD_BUDGET:-2100}"   # the lock kills a hold after 40 min: stop launching new runs after 35 min
time_ok() { [ $(( $(date +%s) - HOLD_START )) -lt "$HOLD_BUDGET" ]; }
RUN() { "$GPU" capture --label terrain -- "$UE_DIR/Scripts/run_game.sh" "$@"; }
# GPU etiquette (2026-10-01 20:43: the first terrain warm-up pinned the GPU and WindowServer starved): throttle every run so the GPU idles between frames
export WH_CAPTURE_MAXFPS="${WH_CAPTURE_MAXFPS:-12}"
WANT=("$@"); [ ${#WANT[@]} -eq 0 ] && WANT=(warm stills moves)
want() { [[ " ${WANT[*]} " =~ " $1 " ]]; }
[ -f "$UE_DIR/Content/Terrain/Maps/V_p1_south.umap" ] || { echo "terrain content missing (Content/Terrain/Maps/V_p1_south.umap): build_terrain.py has not produced the maps"; exit 3; }
mkdir -p "$TMP" "$ROUND/stills"
gpu() { ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1; }
IDS=$(python3 -c "import json;print(' '.join(s['id'] for s in json.load(open('$HERE/shots.json'))['shots']))")
BASE_IDS="${BASE_IDS:-p1_south p2_reservoir p10_lawn_eye p6_west_shore}"   # baseline (city alone) stills only for the pair views
if want warm; then
  echo "== warm-up (shader compile, not kept)  $(gpu)"
  rm -rf "$TMP/warm"
  RUN "$TMP/warm" -map /Game/Terrain/Maps/V_p1_south -res 960x540 -quit "${WARM_QUIT:-12}" -name warm -timeout 2300 -- -benchmark -fps=30 | tail -3
fi
still() {  # <prefix> <id>
  local PRE="$1" ID="$2" NAME="$1$2"
  time_ok || { echo "== SKIP still $NAME (hold budget used up)"; return; }
  echo "== still $NAME  $(gpu)"
  rm -rf "$TMP/$NAME"
  RUN "$TMP/$NAME" -map "/Game/Terrain/Maps/$NAME" -res 3840x2160 -shots "${STILL_AT:-2}" -quit "${STILL_QUIT:-3}" -name "$NAME" -timeout 1500 -- -benchmark -fps=30 | tail -2
  for p in "$TMP/$NAME"/${NAME}_*.png; do
    [ -f "$p" ] || continue
    local OUT="$ROUND/stills/$ID.jpg"; [ "$PRE" = VB_ ] && OUT="$ROUND/stills/base_$ID.jpg"
    sips -s format jpeg -s formatOptions 90 "$p" --out "$OUT" >/dev/null && echo "  -> $OUT"
  done
}
if want stills; then
  PRIO="${PRIO_IDS:-p1_south p2_reservoir p10_lawn_eye p6_west_shore}"      # the pair views first (terrain, then baseline), then the rest
  for ID in $PRIO; do still V_ "$ID"; done
  for ID in $BASE_IDS; do still VB_ "$ID"; done
  for ID in $IDS; do [[ " $PRIO " =~ " $ID " ]] || still V_ "$ID"; done
fi
movie() {  # <name> <script.json> <quit seconds>
  local NAME="$1" JSON="$2" Q="$3"
  time_ok || { echo "== SKIP movie $NAME (hold budget used up)"; return; }
  echo "== movie $NAME  $(gpu)"
  rm -rf "$TMP/$NAME"
  RUN "$TMP/$NAME" -map /Game/Terrain/Maps/Manhattan_Terrain -res 1920x1080 -quit "$Q" -name "$NAME" -movie -timeout 2300 -exec "r.ScreenPercentage 100" \
    -- -WHTravScript="$SCR/$JSON" -WHTravCsv="$TMP/$NAME/${NAME}_telemetry.csv" | tail -4
  cp "$TMP/$NAME/${NAME}_telemetry.csv" "$ROUND/" 2>/dev/null
  grep -h "WebTravWorld:\|WH_QUIT" "$TMP/$NAME/$NAME.log" | sed 's/^.*Display: //' | head -5 > "$ROUND/${NAME}_log_excerpt.txt"
  local CRF=23
  while :; do
    ffmpeg -loglevel error -y -framerate 60 -i "$TMP/$NAME/${NAME}_frames/MovieFrame%05d.png" -c:v libx264 -preset slow -pix_fmt yuv420p -crf $CRF -movflags +faststart "$ROUND/$NAME.mp4" || break
    [ "$(stat -f %z "$ROUND/$NAME.mp4")" -le 15000000 ] && break
    CRF=$((CRF + 2)); [ $CRF -gt 35 ] && break
  done
  echo "$NAME.mp4 crf $CRF $(stat -f %z "$ROUND/$NAME.mp4") bytes, $(ls "$TMP/$NAME/${NAME}_frames" | wc -l | tr -d ' ') frames"
  for s in 3 7 11; do f=$(printf "%05d" $((s * 60))); [ -f "$TMP/$NAME/${NAME}_frames/MovieFrame$f.png" ] && \
    ffmpeg -loglevel error -y -i "$TMP/$NAME/${NAME}_frames/MovieFrame$f.png" -q:v 3 "$ROUND/stills/${NAME}_t${s}s_1920x1080.jpg"; done
  rm -rf "$TMP/$NAME/${NAME}_frames"
}
if want moves && [ -f /Users/midir/sm2-n1/_scratch/terrain/turn3_final ]; then
  # turn 3 = round-01 FINAL pass in one hold: rebuild the terrain content with the fixes found in the v1 stills, warm-up, all stills again (v1 kept in stills_v1/), then the movies
  S3=/Users/midir/sm2-n1/_scratch/terrain; M3=$S3/manhattan; WT3="$(cd "$HERE/../../.." && pwd)"
  UE3="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
  STEPS3=$(cat $S3/turn3_rebuild_steps 2>/dev/null || echo "clean,tex,mat,mesh,foliage,trees,map,views")
  echo "== final: rebuild terrain steps=$STEPS3 $(date +%H:%M:%S)"
  cat > $S3/jobs_terrain_final.py <<PY
import os, traceback
import unreal
unreal.SystemLibrary.execute_console_command(None, 'Module Load StaticMeshEditor')
ns = {'__file__': '$WT3/unreal/WebHomage/Scripts/build_terrain.py', '__name__': '__main__', 'JOB_ARGS': {'steps': '$STEPS3'}}
try: exec(compile(open(ns['__file__']).read(), ns['__file__'], 'exec'), ns)
except Exception: traceback.print_exc()
PY
  SM2_TERRAIN_SCRATCH=$S3 "$UE3" "$WT3/unreal/WebHomage/WebHomage.uproject" -run=pythonscript -script=$S3/jobs_terrain_final.py -unattended -nullrhi -nosplash -RenderOffScreen -NoSound -NoCrashReports -abslog=$M3/logs/terrain_final.log
  echo "== final: rebuild done rc=$? $(date +%H:%M:%S)"
  mkdir -p "$ROUND/stills_v1"; cp -p "$ROUND"/stills/*.jpg "$ROUND/stills_v1/" 2>/dev/null
  want_save=("${WANT[@]}"); WANT=(warm stills)
  if want warm; then
    echo "== warm-up (shader compile, not kept)  $(gpu)"; rm -rf "$TMP/warm"
    RUN "$TMP/warm" -map /Game/Terrain/Maps/V_p1_south -res 960x540 -quit "${WARM_QUIT:-12}" -name warm -timeout 2300 -- -benchmark -fps=30 | tail -3
  fi
  PRIO="${PRIO_IDS:-p1_south p2_reservoir p10_lawn_eye p6_west_shore}"
  for ID in $PRIO; do still V_ "$ID"; done
  for ID in $BASE_IDS; do [ -f "$ROUND/stills/base_$ID.jpg" ] || still VB_ "$ID"; done
  for ID in $IDS; do [[ " $PRIO " =~ " $ID " ]] || still V_ "$ID"; done
  WANT=("${want_save[@]}")
fi
if want moves; then
  export WH_CAPTURE_MAXFPS="${MOVIE_MAXFPS:-20}"
  movie t4_lawn_sprint t4_lawn_sprint.json "${MOVE_QUIT:-13.4}"
  movie t5_avenue_to_park t5_avenue_to_park.json "${MOVE_QUIT:-15.4}"
fi
echo "done: $ROUND"
