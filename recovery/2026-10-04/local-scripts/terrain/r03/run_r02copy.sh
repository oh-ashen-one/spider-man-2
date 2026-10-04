#!/bin/bash
# r03: build the round-02 terrain scripts side by side into /Game/TerrainR2 (scratch content, never committed) for the capture GPU-ms comparison
S=/Users/midir/sm2-n1/_scratch/terrain; WT=/Users/midir/sm2-n1/terrain
UE="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
touch "$S/BUILDING"
SM2_TERRAIN_WT="$WT" SM2_TERRAIN_SCRATCH="$S" "$UE" "$WT/unreal/WebHomage/WebHomage.uproject" -run=pythonscript -script="$S/r03/jobs_r02copy.py" -unattended -nullrhi -nosplash -RenderOffScreen -NoSound -NoCrashReports -abslog="$S/r03/r02copy_build.log"
echo "rc=$?"; rm -f "$S/BUILDING"; grep -a "build_terrain.*\(DONE\|FAILED\)\|Traceback" "$S/r03/r02copy_build.log" | cut -c1-160 | tail -5
