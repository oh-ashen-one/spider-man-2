#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Headless rebuild of /Game/Look + /Game/Tests/Look (Scripts/build_look.py) with your editor CLOSED.
# usage: tools/perf_ue/rebuild_look.sh [steps=geo,rigs,maps] [presets=midday,golden,night]
# needs the city content (tools/perf_ue/rebuild_city.sh) and, for the traversal hero, Scripts/build_traversal.py once.
WT="$(cd "$(dirname "$0")/../.." && pwd)"
export SM2_CITY_EXPORT=${SM2_CITY_EXPORT:-/Users/midir/sm2-n1/_scratch/look/export/midtown3x3}
export SM2_LOOK_STEPS=${1:-geo,rigs,maps}; export SM2_LOOK_PRESETS=${2:-midday,golden,night}
LOG=${SM2_LOOK_LOG:-/Users/midir/sm2-n1/_scratch/look/build_look_headless.log}
cd "$WT/unreal/WebHomage"
"/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$PWD/WebHomage.uproject" -run=pythonscript \
  -script="$PWD/Scripts/build_look.py" -unattended -nullrhi -NoCrashReports -abslog="$LOG" > "$LOG.stdout" 2>&1
grep -E "LogPython: \[build_look|LogPython: (Error|Warning)|    [A-Za-z]+\." "$LOG" | sed 's/^.*LogPython: //' | tail -40
