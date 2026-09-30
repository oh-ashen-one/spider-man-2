#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# Piece F: 1920x1080 60 fps clip of C's 30 s Manhattan swing route with the perf settings, for the blind critic (footage only: a -movie run uses a fixed
# 1/60 s step, so it says nothing about real-time speed). Internal resolution = output = 1920x1080 (r.ScreenPercentage 100), which is the same pixel count as the
# 3840x2160 / TSR 50 % perf runs; r.Nanite.MaxPixelsPerEdge is halved (2) because Nanite measures the edge error against the OUTPUT resolution
# (4 px at 4K output = 2 px at 1080p output), so the geometry density matches the 4K run.
#   gpu_slot.sh capture --label perf -- tools/perf_ue2/route_movie.sh <out_dir> [set:<override stem>]      (default set:perf60)
set -uo pipefail
WT="$(cd "$(dirname "$0")/../.." && pwd)"; OUT="$1"; SET="${2:-set:perf60}"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
TMP=/Users/midir/sm2-n1/_scratch/perf/movie_tmp; case "$TMP" in /Users/midir/sm2-n1/_scratch/perf/*) ;; *) exit 1;; esac
rm -rf "$TMP"; mkdir -p "$TMP"
CV=$(python3 -c "import sys; sys.path.insert(0,'$WT/tools/perf_ue2'); import perf_route as p; d=dict(p.read_set('${SET#set:}')); d['r.Nanite.MaxPixelsPerEdge']='2'; print(','.join('%s=%s'%kv for kv in d.items()))")
EX="r.ScreenPercentage 100,$(echo "$CV" | tr '=' ' ')"
echo "{\"output\": \"1920x1080\", \"internal\": \"1920x1080\", \"screen_percentage\": 100, \"cvars\": \"$CV\", \"set\": \"$SET\"}" > "$OUT/route_30s_settings.json"
"$WT/unreal/WebHomage/Scripts/run_game.sh" "$TMP" -map /Game/Maps/Manhattan -res 1920x1080 -quit 30.8 -name route_30s -movie -timeout 3600 \
  -exec "$EX" -- -WHTravScript="$WT/docs/night1/manhattan/scripts/route_30s.json" -WHTravPreroll=0.8 -dpcvars="$CV" | tail -3
FR="$TMP/route_30s_frames"
if [ -d "$FR" ]; then
  # trim the 0.8 s P3 pre-roll (exposure / Lumen settle), keep <= 15 MB
  ffmpeg -loglevel error -y -framerate 60 -start_number 48 -i "$FR/MovieFrame%05d.png" -c:v libx264 -preset slow -pix_fmt yuv420p -crf 22 -movflags +faststart "$OUT/route_30s.mp4"
  if [ "$(stat -f %z "$OUT/route_30s.mp4")" -gt 15000000 ]; then
    ffmpeg -loglevel error -y -framerate 60 -start_number 48 -i "$FR/MovieFrame%05d.png" -c:v libx264 -preset slow -b:v 3800k -maxrate 3800k -bufsize 7600k -pix_fmt yuv420p -movflags +faststart "$OUT/route_30s.mp4"
  fi
  ls -la "$OUT/route_30s.mp4"; ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$OUT/route_30s.mp4"
else echo "movie FAILED: no frames in $TMP"; fi
