#!/bin/zsh
# headless run of Scripts/build_look.py (editor closed). env: steps=geo,rigs,maps presets=...
cd /Users/midir/sm2-n1/look/unreal/WebHomage
export SM2_CITY_EXPORT=/Users/midir/sm2-n1/_scratch/look/export/midtown3x3
"/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$PWD/WebHomage.uproject" -run=pythonscript -script="$PWD/Scripts/build_look.py" -unattended -nullrhi -NoCrashReports -abslog=/Users/midir/sm2-n1/_scratch/look/build_look_headless.log > /Users/midir/sm2-n1/_scratch/look/build_look_headless.stdout 2>&1
grep -E "build_look|LogPython: (Error|Warning)" /Users/midir/sm2-n1/_scratch/look/build_look_headless.log | cut -c1-260 | tail -30
