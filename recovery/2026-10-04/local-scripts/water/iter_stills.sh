#!/bin/bash
S=/Users/midir/sm2-n1/_scratch/water; UEP=/Users/midir/sm2-n1/water/unreal/WebHomage
OUT=$S/iter/${ITER:-i3}; mkdir -p $OUT; cd $UEP
shot() { Scripts/run_game.sh "$OUT/$2" -map "$1" -res 1920x1080 -shots 16 -name "$2" -exec "r.ScreenPercentage 100" -timeout 600 >/dev/null 2>&1
  local png; png=$(ls -t "$OUT/$2/$2"_*.png 2>/dev/null | head -1); [ -n "$png" ] && cp "$png" "$OUT/$2.png" && echo "still $2" || echo "NO STILL $2"; }
shot /Game/Water/Maps/Water_View_RiverLow rlow
if grep -q "M_RiverWater.uasset: Failed to compile Material" $OUT/rlow/rlow.log; then echo "WATER MATERIAL FAILED TO COMPILE"; exit 9; fi
for v in C E J; do for k in river_low river_sun S4_perch_skyline; do shot /Game/Water/Variants/Water_Var_${v}_$k ${v}_$k; done; done
shot /Game/Water/Variants/Water_Var_G_river_low G_river_low
shot /Game/Water/Variants/Water_Var_G_river_sun G_river_sun
