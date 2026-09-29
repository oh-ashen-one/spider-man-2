#!/bin/bash
# Headless rebuild of /Game/Characters + /Game/Tests/Characters (P2 editor must be closed). Fan homage project.
#   tools/ue_char/build_characters_headless.sh ['{"steps":"mesh,citizens,abp,map"}']
cd "$(dirname "$0")/../.."
WT=$(pwd)
# idempotent: our folders are wiped on disk first (editor closed), then rebuilt from committed sources
case "$1" in ""|*clean*) rm -rf "$WT/unreal/WebHomage/Content/Characters" "$WT/unreal/WebHomage/Content/Tests/Characters";; esac
A="$1"; [ -z "$A" ] && A="{}"; export CHAR_BUILD_ARGS="$A"
"/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$WT/unreal/WebHomage/WebHomage.uproject" \
  -run=pythonscript -script="$WT/unreal/WebHomage/Scripts/build_characters.py" -unattended -nullrhi -nosplash \
  -abslog="$WT/unreal/WebHomage/Saved/Logs/characters_build.log" 2>&1 | grep -E "build_characters\]|Error|Traceback" | grep -v LogInit | tail -40
