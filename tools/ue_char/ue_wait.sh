#!/bin/bash
# Owner rule 2026-09-29: never exceed the loop's Unreal-process cap. The cap is the orchestrator's adaptive slot count
# (health_monitor.sh writes it to $GPU_DIR/slots from the WindowServer health log); without that file the cap is 3.
# Poll every 60 s until fewer than CAP UnrealEditor processes run. Fan homage project.
# usage: tools/ue_char/ue_wait.sh   (called before every launch of UnrealEditor)
GPU_DIR="${GPU_DIR:-/Users/midir/sm2-n1/_scratch/gpu}"
while true; do
  cap=$(cat "$GPU_DIR/slots" 2>/dev/null | tr -dc '0-9'); [ -z "$cap" ] && cap=3
  n=$(pgrep -fl "MacOS/UnrealEditor( |$)" | wc -l | tr -d ' ')
  [ "$n" -lt "$cap" ] && break
  echo "ue_wait: $n Unreal instances running (cap $cap), waiting 60 s" >&2
  sleep 60
done
