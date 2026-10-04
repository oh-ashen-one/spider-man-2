#!/bin/zsh
# Stop one of OUR engine runs without wedging the GPU driver.
# usage: stop_ue.sh <regex that only matches your own worktree/scratch path>
# 1) kill the driving scripts first (so nothing relaunches), 2) SIGTERM the engine and wait,
# 3) SIGKILL only as a last resort. A SIGKILL mid-frame left a 4K game stuck in the GPU driver
# on 2026-09-29 23:03 and the machine panicked 5 minutes later.
pat="$1"; [ -n "$pat" ] || { echo "usage: stop_ue.sh <pattern>"; exit 2; }
ue=$(pgrep -f "MacOS/UnrealEditor .*$pat")
drivers=$(pgrep -f "$pat" | grep -vx "$$" | grep -vxF "$ue")
for d in ${=drivers}; do kill -TERM $d 2>/dev/null; done
for p in ${=ue}; do kill -TERM $p 2>/dev/null; done
for i in {1..60}; do
  alive=""; for p in ${=ue}; do kill -0 $p 2>/dev/null && alive="$alive $p"; done
  [ -z "$alive" ] && { echo "stopped cleanly"; exit 0; }
  sleep 1
done
echo "engine did not exit in 60 s, SIGKILL:$alive"; for p in ${=alive}; do kill -9 $p; done
