#!/bin/bash
WT=/Users/midir/sm2-n1/terrain; S=/Users/midir/sm2-n1/_scratch/terrain
UE="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
"$UE" "$WT/unreal/WebHomage/WebHomage.uproject" -run=pythonscript -script="$S/r04/inspect3_job.py" -unattended -nullrhi -nosplash -RenderOffScreen -NoSound -NoCrashReports -abslog="$S/r04/inspect3.log" > /dev/null 2>&1
echo "rc=$?" > "$S/r04/inspect3.rc"
