#!/bin/bash
# water r04: the ONE capture hold. Run ONLY as: gpu_slot.sh capture --label water -- bash hold_r04.sh   (nested gpu_slot calls pass through)
# A) build base + variants -> iteration stills (4K for the harbour views / river_low, 1080 otherwise) -> report
# B) decision gate: waits up to GATE s for $S/decide.json (final params written by the builder after reading the stills), else autopick
# C) final build -> round-04 stills (1080 + 4K, 5 views) + both dollies. Never starts an engine run past DEADLINE s (max hold 2400 s).
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; R4=$S/r04; WT=/Users/midir/sm2-n1/water; R=$WT/docs/night1/water/round-04; UEP=$WT/unreal/WebHomage
T0=$(date +%s); DEADLINE=${DEADLINE:-2300}; GATE=${GATE:-420}
left() { echo $(( DEADLINE - ($(date +%s) - T0) )); }
waitclear() { for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || return 0; sleep 1; done; echo "HOLD: engine still exiting, abort"; exit 8; }
cd $WT
while kill -0 $(cat $R4/hold.pid) 2>/dev/null; do sleep 5; done   # never overlap hold 1 (if the cap is ever 2)
echo "HOLD r04b start $(date +%T)"
rm -f $R4/decide.json $R4/iterA.done
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_VARIANTS="$(cat $R4/variants2.json)" \
  python3 unreal/WebHomage/Scripts/build_water.py --steps ue || { echo "HOLD: water build FAILED"; exit 4; }
OUT=$S/iter/r04b; mkdir -p $OUT; cd $UEP
shot() { # map name res
  [ "$(left)" -gt 1000 ] || { echo "skip $2 (time)"; return; }
  waitclear; Scripts/run_game.sh "$OUT/$2" -map "$1" -res "$3" -shots 16 -name "$2" -exec "r.ScreenPercentage 100" -timeout 600 >/dev/null 2>&1
  local png; png=$(ls -t "$OUT/$2/$2"_*.png 2>/dev/null | head -1); [ -n "$png" ] && cp "$png" "$OUT/$2.png" && echo "still $2 $(date +%T)" || echo "NO STILL $2"; }
M=/Game/Water/Maps; V=/Game/Water/Variants
shot $M/Water_View_RiverLow base_river_low 3840x2160
if grep -q "Failed to compile Material" $OUT/base_river_low/base_river_low.log; then echo "HOLD: WATER MATERIAL FAILED TO COMPILE"; grep -m5 -A3 "Failed to compile" $OUT/base_river_low/base_river_low.log; exit 9; fi
shot $V/Water_Var_DBG4_river_low DBG4_river_low 1920x1080
shot $V/Water_Var_DBG7_river_low DBG7_river_low 1920x1080
shot $V/Water_Var_DBG8_river_low DBG8_river_low 1920x1080
shot $V/Water_Var_F08_river_low F08_river_low 3840x2160
shot $V/Water_Var_F24_river_low F24_river_low 3840x2160
shot $V/Water_Var_B7_river_low B7_river_low 3840x2160
shot $V/Water_Var_B10_river_low B10_river_low 3840x2160
shot $M/Water_View_HarbourHigh base_harbour_high 3840x2160
shot $V/Water_Var_C8_harbour_high C8_harbour_high 3840x2160
shot $V/Water_Var_C15_harbour_high C15_harbour_high 3840x2160
shot $V/Water_Var_C15_harbour_sun_high C15_harbour_sun_high 3840x2160
cd $WT
python3 $R4/report_r04b.py $OUT $R4/variants2.json $R4/auto_params.json > $OUT/report.txt 2>&1; cat $OUT/report.txt
touch $R4/iterA.done
echo "GATE: waiting up to $GATE s for $R4/decide.json ($(date +%T))"
for _ in $(seq 1 $GATE); do [ -f $R4/decide.json ] && break; sleep 1; done
if [ -f $R4/decide.json ]; then FP=$R4/decide.json; echo "decision: builder ($(cat $FP))"; else FP=$R4/auto_params.json; echo "decision: autopick ($(cat $FP))"; fi
cp $FP $R4/final_params.json
[ "$(left)" -gt 900 ] || { echo "HOLD: no time left for the final set"; exit 7; }
waitclear
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_PARAMS="$(cat $R4/final_params.json)" SM2_WATER_VARIANTS='{}' \
  python3 unreal/WebHomage/Scripts/build_water.py --steps ue || { echo "HOLD: final water build FAILED"; exit 4; }
waitclear
SM2_WATER_SCR=$S tools/water/capture_round.sh $R stills water
waitclear
[ "$(left)" -gt 300 ] && SM2_WATER_SCR=$S tools/water/capture_round.sh $R movie water
waitclear
echo "HOLD r04b DONE $(date +%T) ($(( $(date +%s) - T0 )) s)"
