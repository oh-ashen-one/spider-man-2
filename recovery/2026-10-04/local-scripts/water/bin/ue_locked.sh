#!/bin/bash
# water piece: every Unreal commandlet goes through the GPU lock (RULES.md)
exec /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water -- "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$@"
