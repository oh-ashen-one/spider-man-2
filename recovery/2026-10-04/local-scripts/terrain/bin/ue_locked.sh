#!/bin/bash
# terrain piece: every Unreal commandlet goes through the GPU lock (RULES.md)
exec /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain -- "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$@"
