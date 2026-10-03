#!/bin/bash
# water r06 final capture hold (copy of r05/final_g.sh) (re-runnable): build once per commit, then the round-05 set in priority order, skipping outputs already
# taken with this build. Every engine run starts only if enough of the 2400 s max hold is left (never reach the lock's SIGKILL).
# Run ONLY under gpu_slot.sh capture.
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; R5=$S/r06g; WT=/Users/midir/sm2-n1/water; R=$WT/docs/night1/water/round-06; UEP=$WT/unreal/WebHomage
CAP=$S/cap; T0=$(date +%s); DEADLINE=${DEADLINE:-2280}
left() { echo $(( DEADLINE - ($(date +%s) - T0) )); }
waitclear() { for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || return 0; sleep 1; done; echo "FINAL: engine still exiting, abort"; exit 8; }
paused() { [ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "FINAL: PAUSED, stop $(date +%T)"; exit 6; }; return 0; }
paused; mkdir -p $R; cd $WT
HEAD=$(git hash-object unreal/WebHomage/Scripts/build_water.py | cut -c1-12); echo "FINAL start $(date +%T) build_water.py $HEAD (commit $(git rev-parse --short HEAD))"
if [ -z "${SKIP_BUILD:-}" ] && [ "$(cat $R5/BUILT 2>/dev/null)" != "$HEAD" ]; then
  SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_PARAMS='{}' SM2_WATER_VARIANTS='{}' \
    python3 unreal/WebHomage/Scripts/build_water.py --steps ue > $R5/build_final.log 2>&1 || { echo "FINAL: build FAILED"; tail -30 $R5/build_final.log; exit 4; }
  echo "$HEAD" > $R5/BUILT; touch $R5/BUILT; echo "built $(date +%T)"
fi
cd $UEP
still() { # map res name need_s
  local map="$1" res="$2" name="$3" need="$4"
  [ "$R/$name.jpg" -nt "$R5/BUILT" ] && { echo "have $name"; return; }
  [ "$(left)" -gt "$need" ] || { echo "skip $name (time $(left) s)"; return; }
  paused; waitclear; rm -rf "$CAP/$name"
  Scripts/run_game.sh "$CAP/$name" -map "$map" -res "$res" -shots 16 -name "$name" -exec "r.ScreenPercentage 100" -timeout 900 >/dev/null 2>&1
  local png; png=$(ls -t "$CAP/$name/${name}"_*.png 2>/dev/null | head -1)
  if [ -n "$png" ]; then sips -s format jpeg -s formatOptions 92 "$png" --out "$R/$name.jpg" >/dev/null && echo "still $name $(date +%T)"
  else echo "NO SCREENSHOT $name"; grep -m3 "Failed to compile Material" "$CAP/$name/$name.log"; fi; }
dolly() { # map-suffix name
  local m="$1" n="$2"
  [ "$R/$n.mp4" -nt "$R5/BUILT" ] && { echo "have $n"; return; }
  [ "$(left)" -gt "${DOLLY_NEED:-1200}" ] || { echo "skip $n (time $(left) s)"; return; }
  paused; waitclear; rm -rf "$CAP/$n"
  Scripts/run_game.sh "$CAP/$n" -map /Game/Water/Maps/Water_View_${m}_Dolly -res 1920x1080 -quit 16.1 -name dolly -movie -timeout 1200 >/dev/null 2>&1
  local N; N=$(ls "$CAP/$n/dolly_frames" 2>/dev/null | wc -l | tr -d ' '); echo "$n frames: $N $(date +%T)"
  ffmpeg -loglevel error -y -framerate 60 -start_number 359 -i "$CAP/$n/dolly_frames/MovieFrame%05d.png" -frames:v 600 \
    -c:v libx264 -pix_fmt yuv420p -crf 20 -preset slow -movflags +faststart "$R/$n.mp4" && ls -la "$R/$n.mp4"
  local crf=20; while [ "$(stat -f %z "$R/$n.mp4")" -gt 15000000 ] && [ $crf -lt 32 ]; do crf=$((crf+3))
    ffmpeg -loglevel error -y -framerate 60 -start_number 359 -i "$CAP/$n/dolly_frames/MovieFrame%05d.png" -frames:v 600 \
      -c:v libx264 -pix_fmt yuv420p -crf $crf -preset slow -movflags +faststart "$R/$n.mp4"; echo "$n re-encoded at CRF $crf: $(stat -f %z "$R/$n.mp4")"; done; }
M=/Game/Water/Maps
# r06 order: the five 4K stills first (the round's numbers), then the dollies, then the 1080p stills
still $M/Water_View_RiverLow 3840x2160 river_low_4k 420
still $M/Water_View_RiverSun 3840x2160 river_sun_4k 420
still $M/Water_View_HarbourHigh 3840x2160 harbour_high_4k 420
still $M/Water_View_HarbourSunHigh 3840x2160 harbour_sun_high_4k 420
still /Game/Maps/Manhattan_View_S4 3840x2160 S4_golden_4k 420
dolly RiverLow river_low_dolly
dolly RiverSun river_sun_dolly
for v in "$M/Water_View_RiverLow|river_low" "$M/Water_View_HarbourHigh|harbour_high" "$M/Water_View_HarbourSunHigh|harbour_sun_high" \
         "/Game/Maps/Manhattan_View_S4|S4_golden" "$M/Water_View_RiverSun|river_sun"; do still "${v%%|*}" 1920x1080 "${v#*|}_1080" 300; done
waitclear
echo "FINAL DONE $(date +%T) ($(( $(date +%s) - T0 )) s)"
