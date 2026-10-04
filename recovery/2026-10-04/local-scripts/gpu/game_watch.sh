#!/bin/zsh
# owner game guard: when a CrossOver game (GTA5.exe etc.) starts, stop loop renders gracefully + PAUSE; lift 60 s after it exits
G=/Users/midir/sm2-n1/_scratch/gpu
GAME='GTA5\.exe|PlayGTAV\.exe|RDR2\.exe'
while true; do
  if pgrep -f "$GAME" >/dev/null; then
    echo "owner game running $(date +%H:%M) - renders paused by game_watch.sh" > $G/PAUSED
    for wt in $(ps -axo command | grep -E "MacOS/UnrealEditor( |$)" | grep -- "-game" | grep -oE "/Users/midir/sm2-n1/[a-z]+" | sort -u); do
      $G/bin/stop_ue.sh "$wt" >/dev/null 2>&1
    done
    while pgrep -f "$GAME" >/dev/null; do sleep 15; done
    sleep 60
    { ! pgrep -f "$GAME" >/dev/null; } && [ -f $G/PAUSED ] && grep -q game_watch $G/PAUSED && mv $G/PAUSED $G/PAUSED.lifted-game-$(date +%H%M)
  fi
  sleep 10
done
