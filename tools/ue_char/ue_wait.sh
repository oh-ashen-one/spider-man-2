#!/bin/bash
# Owner rule 2026-09-29: never add a 3rd+ Unreal instance. Poll every 60 s until fewer than 3 UnrealEditor processes run.
# Fan homage project. usage: tools/ue_char/ue_wait.sh   (sourced/called before every launch of UnrealEditor)
while true; do
  n=$(pgrep -fl "MacOS/UnrealEditor( |$)" | wc -l | tr -d ' ')
  [ "$n" -lt 3 ] && break
  echo "ue_wait: $n Unreal instances running, waiting 60 s" >&2
  sleep 60
done
