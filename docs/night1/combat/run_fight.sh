#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P5 combat: run the scripted fight in /Game/Tests/Combat/Combat_Street.
#   run_fight.sh logic  <out_dir> <script.json>               -game -nullrhi (no GPU, no window): game logic + telemetry only
#   run_fight.sh movie  <out_dir> <script.json> [WxH]         1080p60 -dumpmovie through Scripts/run_game.sh inside gpu_slot.sh capture
#   run_fight.sh stills <out_dir> <script.json> t1,t2,...     native 4K stills (r.ScreenPercentage 100) inside gpu_slot.sh capture
# Deterministic: -benchmark -fps=60 (fixed 1/60 s step), seeded RNG in the director.
set -uo pipefail
MODE="$1"; OUT="$2"; SCRIPT="$3"; ARG4="${4:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WT="$(cd "$HERE/../../.." && pwd)"
PROJ="$WT/unreal/WebHomage"; UPROJECT="$PROJ/WebHomage.uproject"
UE="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
G=/Users/midir/sm2-n1/_scratch/gpu/bin
MAP=/Game/Tests/Combat/Combat_Street
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"; SCRIPT="$(cd "$(dirname "$SCRIPT")" && pwd)/$(basename "$SCRIPT")"
QUIT=$(python3 -c "import json;print(json.load(open('$SCRIPT')).get('quit',30))")
if pgrep -f "$UPROJECT" >/dev/null; then echo "an Unreal process of this worktree is running"; exit 2; fi
while [ "$(pgrep -f 'MacOS/UnrealEditor( |$)' | wc -l | tr -d ' ')" -ge 3 ]; do echo "3+ Unreal instances, waiting 60 s"; sleep 60; done
case "$MODE" in
  logic)
    "$UE" "$UPROJECT" "$MAP" -game -nullrhi -NoSound -NoCrashReports -benchmark -fps=60 -unattended -WHNoMouseCapture \
      -WHCmbScript="$SCRIPT" -WHCmbOut="$OUT" -WHCmbShotName=fight -abslog="$OUT/fight.log" > "$OUT/stdout.txt" 2>&1 &
    PID=$!; S=$(date +%s)
    while kill -0 $PID 2>/dev/null; do if [ $(( $(date +%s) - S )) -gt 600 ]; then kill -9 $PID; echo timeout; fi; sleep 2; done
    wait $PID; echo "rc $?"
    grep -o 'WH_CMB_SUMMARY.*' "$OUT/fight.log" | head -1 ;;
  movie)
    RES="${ARG4:-1920x1080}"
    $G/gpu_slot.sh capture --label combat -- "$PROJ/Scripts/run_game.sh" "$OUT" -map "$MAP" -res "$RES" -quit 400 -name fight -movie -timeout 2400 \
      -- -WHCmbScript="$SCRIPT" -WHCmbOut="$OUT" -WHCmbShotName=fight
    echo "rc $?" ;;
  stills)
    $G/gpu_slot.sh capture --label combat -- "$PROJ/Scripts/run_game.sh" "$OUT" -map "$MAP" -res 3840x2160 -quit 400 -name still -timeout 2400 \
      -exec "r.ScreenPercentage 100" -- -benchmark -fps=60 -WHCmbScript="$SCRIPT" -WHCmbOut="$OUT" -WHCmbShotName=still -WHCmbShots="$ARG4"
    echo "rc $?" ;;
  *) echo "mode: logic | movie | stills"; exit 1 ;;
esac
pgrep -f "$UPROJECT" >/dev/null && pkill -9 -f "$UPROJECT"
pgrep -f "CrashReportClient.*$WT" >/dev/null && pkill -9 -f "CrashReportClient.*$WT"
exit 0
