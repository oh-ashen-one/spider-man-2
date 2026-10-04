#!/bin/bash
# water r03: the ONE capture hold. Run ONLY as: gpu_slot.sh capture --label water -- bash hold_r03.sh   (nested gpu_slot calls pass through)
# build (base + variants) -> 1080p iteration stills -> autopick -> final build -> round-03 stills (1080 + 4K) + both dollies.
# Never starts a new engine run after DEADLINE s (gpu_slot max hold is set to 3000 s by the caller).
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; WT=/Users/midir/sm2-n1/water; R=$WT/docs/night1/water/round-03; UEP=$WT/unreal/WebHomage
T0=$(date +%s); DEADLINE=${DEADLINE:-2350}
left() { echo $(( DEADLINE - ($(date +%s) - T0) )); }
waitclear() { for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || return 0; sleep 1; done; echo "HOLD: engine still exiting, abort"; exit 8; }
cd $WT
echo "HOLD r03 start $(date +%T)"
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_VARIANTS="$(cat $S/r03/variants.json)" \
  python3 unreal/WebHomage/Scripts/build_water.py --steps ue || { echo "HOLD: water build FAILED"; exit 4; }
OUT=$S/iter/r03; mkdir -p $OUT; cd $UEP
shot() { waitclear; Scripts/run_game.sh "$OUT/$2" -map "$1" -res 1920x1080 -shots 16 -name "$2" -exec "r.ScreenPercentage 100" -timeout 600 >/dev/null 2>&1
  local png; png=$(ls -t "$OUT/$2/$2"_*.png 2>/dev/null | head -1); [ -n "$png" ] && cp "$png" "$OUT/$2.png" && echo "still $2 $(date +%T)" || echo "NO STILL $2"; }
shot /Game/Water/Maps/Water_View_RiverLow base_river_low
if grep -q "Failed to compile Material" $OUT/base_river_low/base_river_low.log; then echo "HOLD: WATER MATERIAL FAILED TO COMPILE"; grep -m5 -A3 "Failed to compile" $OUT/base_river_low/base_river_low.log; exit 9; fi
shot /Game/Water/Maps/Water_View_RiverSun base_river_sun
shot /Game/Water/Maps/Water_View_HarbourHigh base_harbour_high
for v in V1 V2 V3; do for k in river_low river_sun harbour_high; do
  [ "$(left)" -gt 1500 ] && shot /Game/Water/Variants/Water_Var_${v}_$k ${v}_$k
done; done
cd $WT
python3 $S/r03/autopick_r03.py $OUT $S/r03/variants.json $S/r03/final_params.json || cp $S/r03/base_params.json $S/r03/final_params.json
echo "final params: $(cat $S/r03/final_params.json)"
[ "$(left)" -gt 1100 ] || { echo "HOLD: no time left for the final set"; exit 7; }
waitclear
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_PARAMS="$(cat $S/r03/final_params.json)" SM2_WATER_VARIANTS='{}' \
  python3 unreal/WebHomage/Scripts/build_water.py --steps ue || { echo "HOLD: final water build FAILED"; exit 4; }
waitclear
SM2_WATER_SCR=$S tools/water/capture_round.sh $R stills water
waitclear
[ "$(left)" -gt 120 ] && SM2_WATER_SCR=$S tools/water/capture_round.sh $R movie water
waitclear
echo "HOLD r03 DONE $(date +%T) ($(( $(date +%s) - T0 )) s)"
