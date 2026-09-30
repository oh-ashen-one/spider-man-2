#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# P6 City life capture driver: the running game (offscreen -game via Scripts/run_game.sh), every run wrapped in the GPU lock.
#   <round>/stills/S1_street_{1080p,4k}.jpg, S2_avenue_{1080p,4k}.jpg   city_shots.json S1 / S2 cameras in /Game/Tests/Life/Life_View_S1|S2, shot at game t = 28 s
#   <round>/street_clip_1080p60.mp4                                     20 s street-level walk (Life_Street_Clip), fixed 1/60 s steps (-movie), H.264 <= 15 MB
#   <round>/probe_*.txt                                                 WH_LIFE_* lines (frame counts in the camera frustum, foot-slide watch, sim ms)
#   <round>/perf_*.json / perf_gpu_*.json                               GPU-locked frame times, with and without the life actors (A/B), PERF_TABLE.md
# usage: docs/night1/life/capture_round.sh <round dir> [warm|stills|clip|perf ...]      (heavy frames: _scratch/life/capture)
set -uo pipefail
ROUND="$(mkdir -p "$1" && cd "$1" && pwd)"; shift
HERE="$(cd "$(dirname "$0")" && pwd)"
UE_DIR="$(cd "$HERE/../../../unreal/WebHomage" && pwd)"
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
TMP=/Users/midir/sm2-n1/_scratch/life/capture
SP="${SP:-100}"
WANT=("$@"); [ ${#WANT[@]} -eq 0 ] && WANT=(warm stills clip perf)
has() { [[ " ${WANT[*]} " =~ " $1 " ]]; }
util() { ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1 | grep -o '[0-9]*$'; }
mkdir -p "$TMP" "$ROUND/stills"
echo "{\"sp\": $SP, \"maps\": [\"Life_View_S1\", \"Life_View_S2\", \"Life_Street_Clip\"], \"still_time_s\": 28}" > "$ROUND/capture_settings.json"

if has warm; then
  echo "== warm-up render (shader compile, not kept)  GPU $(util) %"
  rm -rf "$TMP/warm"
  $G capture --label life -- "$UE_DIR/Scripts/run_game.sh" "$TMP/warm" -map /Game/Tests/Life/Life_View_S1 -res 960x540 -quit 12 -name warm -timeout 2400 | tail -1
fi

if has stills; then
  for V in S1 S2; do
    for RES in 1920x1080 3840x2160; do
      TAG=$([ "$RES" = 1920x1080 ] && echo 1080p || echo 4k)
      echo "== $V $RES  GPU $(util) %"
      rm -rf "$TMP/${V}_$TAG"
      $G capture --label life -- "$UE_DIR/Scripts/run_game.sh" "$TMP/${V}_$TAG" -map /Game/Tests/Life/Life_View_$V -res $RES -shots 28 -name $V -timeout 2400 \
        -exec "r.ScreenPercentage $SP" | tail -2
      p=$(ls "$TMP/${V}_$TAG/${V}_00_"*.png 2>/dev/null | head -1)
      NAME=$([ "$V" = S1 ] && echo S1_street || echo S2_avenue)
      [ -n "$p" ] && sips -s format jpeg -s formatOptions 92 "$p" --out "$ROUND/stills/${NAME}_$TAG.jpg" > /dev/null
      grep -E "WH_LIFE" "$TMP/${V}_$TAG/$V.log" | sed 's/^.*LogWHLifeProbe: Display: //' > "$ROUND/probe_${V}_$TAG.txt"
      cp "$UE_DIR/Saved/Logs/life_feet.csv" "$ROUND/feet_${V}_$TAG.csv" 2>/dev/null
    done
  done
fi

if has clip; then
  echo "== street clip 1080p60 movie  GPU $(util) %"
  rm -rf "$TMP/clip"
  $G capture --label life -- "$UE_DIR/Scripts/run_game.sh" "$TMP/clip" -map /Game/Tests/Life/Life_Street_Clip -res 1920x1080 -quit 21 -name clip -movie -timeout 5400 \
    -exec "r.ScreenPercentage $SP" | tail -3
  grep -E "WH_LIFE" "$TMP/clip/clip.log" | sed 's/^.*LogWHLifeProbe: Display: //' > "$ROUND/probe_clip.txt"
  cp "$UE_DIR/Saved/Logs/life_feet.csv" "$ROUND/feet_clip.csv" 2>/dev/null
  if [ -f "$TMP/clip/clip.mp4" ]; then
    cp "$TMP/clip/clip.mp4" "$ROUND/street_clip_1080p60.mp4"
    SZ=$(stat -f %z "$ROUND/street_clip_1080p60.mp4")
    if [ "$SZ" -gt 15000000 ]; then
      D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$ROUND/street_clip_1080p60.mp4"); KBPS=$(python3 -c "print(int(13.5e6*8/1000/float('$D')))")
      ffmpeg -loglevel error -y -framerate 60 -i "$TMP/clip/clip_frames/MovieFrame%05d.png" -c:v libx264 -preset slow -b:v ${KBPS}k -maxrate ${KBPS}k -bufsize $((KBPS*2))k \
        -pix_fmt yuv420p -movflags +faststart "$ROUND/street_clip_1080p60.mp4"
    fi
    ls -la "$ROUND/street_clip_1080p60.mp4"
  fi
fi

if has perf; then
  # exclusive lock (waits for GPU < 15 % for 10 s); off = -WHLifeOff (no traffic, no crowd), on = default, rt_on = instances visible to ray tracing (the expensive setting).
  # Names / labels of the round-01 table: tools/life/perf_table.py. More variants: docs/night1/life/perf_variants.sh
  for RES in 1920x1080 3840x2160; do
    "$HERE/perf_variants.sh" "$ROUND" $RES off:-WHLifeOff on: rt_on:-WHLifeRT
  done
fi
