#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Unattended run of the REAL game (standalone -game, offscreen by default) with screenshots,
# frame-time stats and an auto-quit. Never opens a window, never touches the mouse.
#
# usage: Scripts/run_game.sh <out_dir> [options] [-- extra UE args]
#   -map /Game/Maps/Foundation_Test   map to open
#   -res 3840x2160                    output (back-buffer) size
#   -shots 20,30,40                   screenshot times (game seconds)
#   -perf 20:40                       frame-time window (writes <name>_perf.json)
#   -quit 41                          exit time (default: perf end + 1, or last shot + 2)
#   -name f4k                         file prefix
#   -exec "r.ScreenPercentage 100,stat unit"   console commands at start (comma separated)
#   -window                           windowed on the secondary 1080x1920 display instead of offscreen
#   -movie                            dump EVERY frame (-dumpmovie) with fixed 60 fps timestep
#   -timeout 300                      hard kill after N wall seconds
set -uo pipefail
OUT="$1"; shift
MAP=/Game/Maps/Foundation_Test; RES=3840x2160; SHOTS=""; PERF=""; QUIT=""; NAME=shot; EXEC=""; WINDOW=0; MOVIE=0; TIMEOUT=300; EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    -map) MAP="$2"; shift 2;; -res) RES="$2"; shift 2;; -shots) SHOTS="$2"; shift 2;;
    -perf) PERF="$2"; shift 2;; -quit) QUIT="$2"; shift 2;; -name) NAME="$2"; shift 2;;
    -exec) EXEC="$2"; shift 2;; -window) WINDOW=1; shift;; -movie) MOVIE=1; shift;;
    -timeout) TIMEOUT="$2"; shift 2;; --) shift; EXTRA=("$@"); break;;
    *) echo "unknown option $1"; exit 1;;
  esac
done
PROJ_DIR="$(cd "$(dirname "$0")/.." && pwd)"
UPROJECT="$PROJ_DIR/WebHomage.uproject"
UE="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
W="${RES%x*}"; H="${RES#*x}"
ARGS=("$UPROJECT" "$MAP" -game -ResX="$W" -ResY="$H" -ForceRes -NoCrashReports -NoSound -NoVSync
      -WHNoMouseCapture -WHShotDir="$OUT" -WHShotName="$NAME" -abslog="$OUT/$NAME.log")
if [ "$WINDOW" = 1 ]; then ARGS+=(-windowed -WinX=-1080 -WinY=40); else ARGS+=(-RenderOffScreen); fi
[ -n "$SHOTS" ] && ARGS+=(-WHShotAt="$SHOTS")
if [ -n "$PERF" ]; then ARGS+=(-WHPerfFrom="${PERF%:*}" -WHPerfTo="${PERF#*:}" -WHCsv); fi
if [ -z "$QUIT" ]; then
  if [ -n "$PERF" ]; then QUIT=$(python3 -c "print(float('${PERF#*:}')+1)");
  elif [ -n "$SHOTS" ]; then QUIT=$(python3 -c "print(max(map(float,'$SHOTS'.split(',')))+2)"); else QUIT=20; fi
fi
ARGS+=(-WHQuitAt="$QUIT")
EXECS="t.MaxFPS 0"; [ -n "$EXEC" ] && EXECS="$EXECS,$EXEC"
ARGS+=(-ExecCmds="$EXECS")
[ "$MOVIE" = 1 ] && ARGS+=(-benchmark -fps=60 -dumpmovie)
ARGS+=("${EXTRA[@]+"${EXTRA[@]}"}")
echo "run_game: out=$OUT res=$RES quit=$QUIT window=$WINDOW movie=$MOVIE"
"$UE" "${ARGS[@]}" > "$OUT/$NAME.stdout.txt" 2>&1 &
PID=$!
START=$(date +%s)
while kill -0 $PID 2>/dev/null; do
  if [ $(( $(date +%s) - START )) -gt "$TIMEOUT" ]; then echo "timeout: killing $PID"; kill -9 $PID; break; fi
  sleep 2
done
wait $PID 2>/dev/null; RC=$?
grep -E "WH_(PERF|SHOT|QUIT)" "$OUT/$NAME.log" | sed 's/^.*LogWebHomage: Display: //'
[ "$MOVIE" = 1 ] && echo "movie frames: $(ls "$PROJ_DIR"/Saved/Screenshots/Mac/ 2>/dev/null | wc -l) in $PROJ_DIR/Saved/Screenshots/Mac"
exit $RC
