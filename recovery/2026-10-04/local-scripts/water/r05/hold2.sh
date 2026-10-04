#!/bin/bash
# water r05 hold 2 (capture): final build (final_params.json over the committed PARAMS) -> round-05 stills (1080 + 4K, 5 views, native 100 %)
# -> both dollies (1080p60 fixed step). Run ONLY under gpu_slot.sh capture. Max hold 2400 s.
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; R5=$S/r05; WT=/Users/midir/sm2-n1/water; R=$WT/docs/night1/water/round-05; UEP=$WT/unreal/WebHomage
T0=$(date +%s)
waitclear() { for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || return 0; sleep 1; done; echo "HOLD: engine still exiting, abort"; exit 8; }
while kill -0 $(cat $R5/hold1.pid) 2>/dev/null; do sleep 5; done   # never overlap hold 1 (if the cap is ever 2)
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "HOLD2: PAUSED exists, abort"; exit 6; }
mkdir -p $R; cd $WT
echo "HOLD r05 2 start $(date +%T)"
# A) 1080p variant pass (SunTilt on harbour_sun_high, FarPx on harbour_high) + base river_low check, then an immediate autopick (no wait)
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_VARIANTS="$(cat $R5/variants2.json)" \
  python3 unreal/WebHomage/Scripts/build_water.py --steps ue > $R5/build2a.log 2>&1 || { echo "HOLD: water build FAILED"; tail -30 $R5/build2a.log; exit 4; }
OUT=$S/iter/r05b; mkdir -p $OUT; cd $UEP
shot() { [ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED: stop"; exit 6; }
  waitclear; Scripts/run_game.sh "$OUT/$2" -map "$1" -res 1920x1080 -shots 16 -name "$2" -exec "r.ScreenPercentage 100" -timeout 400 >/dev/null 2>&1
  local png; png=$(ls -t "$OUT/$2/$2"_*.png 2>/dev/null | head -1); [ -n "$png" ] && cp "$png" "$OUT/$2.png" && echo "still $2 $(date +%T)" || echo "NO STILL $2"; }
M=/Game/Water/Maps; V=/Game/Water/Variants
shot $M/Water_View_HarbourSunHigh base_harbour_sun_high
if grep -q "Failed to compile Material" $OUT/base_harbour_sun_high/base_harbour_sun_high.log; then echo "HOLD: WATER MATERIAL FAILED TO COMPILE"; grep -m5 -A6 "Failed to compile" $OUT/base_harbour_sun_high/base_harbour_sun_high.log; exit 9; fi
for v in T0 T10 T35; do shot $V/Water_Var_${v}_harbour_sun_high ${v}_harbour_sun_high; done
shot $M/Water_View_HarbourHigh base_harbour_high
for v in FP2 FP7; do shot $V/Water_Var_${v}_harbour_high ${v}_harbour_high; done
shot $M/Water_View_RiverLow base_river_low
cd $WT
python3 $R5/autopick.py $OUT $R5/final_params.json > $OUT/report.txt 2>&1; cat $OUT/report.txt
echo "decision: $(cat $R5/final_params.json)"
waitclear
# B) final build + round-05 set
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_PARAMS="$(cat $R5/final_params.json)" SM2_WATER_VARIANTS='{}' \
  python3 unreal/WebHomage/Scripts/build_water.py --steps ue > $R5/build2.log 2>&1 || { echo "HOLD: final water build FAILED"; tail -30 $R5/build2.log; exit 4; }
grep -E "TEXINFO|WARN" $R5/build2.log | head
waitclear
SM2_WATER_SCR=$S tools/water/capture_round.sh $R stills water
waitclear
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "HOLD2: PAUSED after stills, no dollies"; exit 6; }
[ $(( $(date +%s) - T0 )) -lt 2050 ] && SM2_WATER_SCR=$S tools/water/capture_round.sh $R movie water
waitclear
echo "HOLD r05 2 DONE $(date +%T) ($(( $(date +%s) - T0 )) s)"
