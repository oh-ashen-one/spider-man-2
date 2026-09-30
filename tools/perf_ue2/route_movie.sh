#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# Piece F: 1920x1080 60 fps clip of C's 30 s Manhattan swing route with the perf settings, for the blind critic (footage only: a -movie run uses a fixed
# 1/60 s step, so it says nothing about real-time speed). Internal resolution = output = 1920x1080 (r.ScreenPercentage 100), which is the same pixel count as the
# 3840x2160 / TSR 50 % perf runs; r.Nanite.MaxPixelsPerEdge is halved because Nanite measures the edge error against the OUTPUT resolution
# (4 px at 4K output = 2 px at 1080p output), so the geometry density matches the 4K run.
#   gpu_slot.sh capture --label perf -- tools/perf_ue2/route_movie.sh <out_dir> ["<spec>"]
# <spec> = perf_route.py config syntax  name@SP[+set:<stem>][+cvar=value][+flag:-Flag][+variant:Cl4RT]  (SP is ignored: the clip is always SP 100); a bare
# "set:<stem>" is accepted (default set:perf60). Route = route_30s.json (the 30 s route without the 15 s warm-up), 0.8 s pre-roll trimmed.
set -uo pipefail
WT="$(cd "$(dirname "$0")/../.." && pwd)"; OUT="$1"; SPEC="${2:-set:perf60}"
[[ "$SPEC" == set:* ]] && SPEC="movie@100+$SPEC"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
TMP=/Users/midir/sm2-n1/_scratch/perf/movie_tmp; case "$TMP" in /Users/midir/sm2-n1/_scratch/perf/*) ;; *) exit 1;; esac
rm -rf "$TMP"; mkdir -p "$TMP"
eval "$(python3 - "$SPEC" "$WT" <<'PY'
import sys, shlex; sys.path.insert(0, sys.argv[2] + '/tools/perf_ue2'); import perf_route as p
name, sp, cv = p.parse_cfg(sys.argv[1])
flags = [k[5:] for k, v in cv if k.startswith('flag:')]; var = [k[8:] for k, v in cv if k.startswith('variant:')]
d = dict((k, v) for k, v in cv if not k.startswith(('flag:', 'map:', 'variant:', 'view:')))
d['r.Nanite.MaxPixelsPerEdge'] = '%g' % (float(d.get('r.Nanite.MaxPixelsPerEdge', '1')) / 2.0)
cvs = ','.join('%s=%s' % kv for kv in d.items())
print('CV=%s; MAP=%s; FLAGS=(%s); VAR=%s' % (shlex.quote(cvs), shlex.quote('/Game/PerfF/%s/Manhattan' % var[-1] if var else '/Game/Maps/Manhattan'), ' '.join(shlex.quote(f) for f in flags), shlex.quote(var[-1] if var else '')))
PY
)"
EX="r.ScreenPercentage 100,$(echo "$CV" | tr '=' ' ')"
echo "{\"output\": \"1920x1080\", \"internal\": \"1920x1080\", \"screen_percentage\": 100, \"cvars\": \"$CV\", \"spec\": \"$SPEC\", \"map\": \"$MAP\"}" > "$OUT/route_30s_settings.json"
"$WT/unreal/WebHomage/Scripts/run_game.sh" "$TMP" -map "$MAP" -res 1920x1080 -quit 30.8 -name route_30s -movie -timeout 3600 \
  -exec "$EX" -- -WHTravScript="$WT/docs/night1/manhattan/scripts/route_30s.json" -WHTravPreroll=0.8 -dpcvars="$CV" "${FLAGS[@]+"${FLAGS[@]}"}" | tail -3
FR="$TMP/route_30s_frames"
if [ -d "$FR" ]; then
  # trim the 0.8 s P3 pre-roll (exposure / Lumen settle), keep <= 15 MB
  ffmpeg -loglevel error -y -framerate 60 -start_number 48 -i "$FR/MovieFrame%05d.png" -c:v libx264 -preset slow -pix_fmt yuv420p -crf 22 -movflags +faststart "$OUT/route_30s.mp4"
  if [ "$(stat -f %z "$OUT/route_30s.mp4")" -gt 15000000 ]; then
    ffmpeg -loglevel error -y -framerate 60 -start_number 48 -i "$FR/MovieFrame%05d.png" -c:v libx264 -preset slow -b:v 3800k -maxrate 3800k -bufsize 7600k -pix_fmt yuv420p -movflags +faststart "$OUT/route_30s.mp4"
  fi
  ls -la "$OUT/route_30s.mp4"; ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$OUT/route_30s.mp4"
else echo "movie FAILED: no frames in $TMP"; fi
