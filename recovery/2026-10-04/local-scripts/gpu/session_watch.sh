#!/bin/zsh
# Emits one line when the desktop session can render again, then lifts the orchestrator PAUSE.
T=/private/tmp/claude-501/-Users-midir/16227b43-7e09-4f35-8b47-d0626c6efd77/scratchpad/ws_probe.png
while true; do
  if perl -e 'alarm 10; exec @ARGV' /usr/sbin/screencapture -x "$T" 2>/dev/null && [ -s "$T" ]; then
    rm -f "$T" /Users/midir/sm2-n1/_scratch/gpu/PAUSED
    echo "$(date +%H:%M:%S) desktop session is back — PAUSED lifted, rendering resumes at cap 2"
    exit 0
  fi
  sleep 30
done
