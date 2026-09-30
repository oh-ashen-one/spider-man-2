#!/bin/bash
OUT=/Users/midir/sm2-n1/_scratch/water-sonnet/cap/dolly
rm -rf "$OUT"
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water-sonnet -- /Users/midir/sm2-n1/water-ab-sonnet/unreal/WebHomage/Scripts/run_game.sh "$OUT" -map /Game/Water/Maps/Water_View_Dolly -res 1920x1080 -quit 14.6 -name dolly -movie -timeout 3000 -exec "r.ScreenPercentage 100" > /Users/midir/sm2-n1/_scratch/water-sonnet/logs/cap_dolly.log 2>&1
echo "rc=$?" >> /Users/midir/sm2-n1/_scratch/water-sonnet/logs/cap_dolly.log
