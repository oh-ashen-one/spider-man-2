#!/bin/bash
# water r05b hold D (4K/1080p stills): build once with the variant set -> Dbg 10 on harbour_high (4K) and river_low -> new-default stills ->
# far-line / river-level / glitter / foam variants at 1080p. Run ONLY under gpu_slot.sh capture. No engine run starts past DEADLINE.
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; RD=$S/r05d; WT=/Users/midir/sm2-n1/water; UEP=$WT/unreal/WebHomage
T0=$(date +%s); DEADLINE=${DEADLINE:-2250}
left() { echo $(( DEADLINE - ($(date +%s) - T0) )); }
waitclear() { for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || return 0; sleep 1; done; echo "HOLD: engine still exiting, abort"; exit 8; }
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "HOLDD: PAUSED exists, abort"; exit 6; }
cd $WT
HASH=$(git hash-object unreal/WebHomage/Scripts/build_water.py | cut -c1-12)
echo "HOLD D start $(date +%T) build_water.py $HASH variants $(git hash-object tools/water/r05/variantsD.json | cut -c1-8)"
if [ -z "${SKIP_BUILD:-}" ]; then
  SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_PARAMS='{}' SM2_WATER_VARIANTS="$(cat tools/water/r05/variantsD.json)" \
    python3 unreal/WebHomage/Scripts/build_water.py --steps ue > $RD/build.log 2>&1 || { echo "HOLD: water build FAILED"; tail -30 $RD/build.log; exit 4; }
  echo "$HASH" > $RD/BUILT; echo "built $(date +%T) ($(( $(date +%s) - T0 )) s)"
fi
OUT=$RD/stills; mkdir -p $OUT; cd $UEP
shot() { # map name res need_s [shots]
  [ "$(left)" -gt "$4" ] || { echo "skip $2 (time $(left) s)"; return; }
  [ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED: stop"; exit 6; }
  [ -f "$OUT/$2.png" ] && [ "$OUT/$2.png" -nt "$RD/BUILT" ] && { echo "have $2"; return; }
  waitclear; rm -rf "$OUT/$2"; Scripts/run_game.sh "$OUT/$2" -map "$1" -res "$3" -shots "${5:-16}" -name "$2" -exec "r.ScreenPercentage 100" -timeout 600 >/dev/null 2>&1
  local png; png=$(ls -t "$OUT/$2/$2"_*.png 2>/dev/null | head -1)
  if [ -n "$png" ]; then cp "$png" "$OUT/$2.png" && echo "still $2 $(date +%T) (left $(left) s)"
  else echo "NO STILL $2"; grep -m3 "Failed to compile Material" "$OUT/$2/$2.log"; fi; }
M=/Game/Water/Maps; V=/Game/Water/Variants; K=4K; P=1920x1080; U=3840x2160
shot $V/Water_Var_DBG10_harbour_high DBG10_harbour_high $U 300
if [ -f $OUT/DBG10_harbour_high/DBG10_harbour_high.log ] && grep -q "Failed to compile Material" $OUT/DBG10_harbour_high/DBG10_harbour_high.log; then echo "HOLD: WATER MATERIAL FAILED TO COMPILE"; exit 9; fi
shot $V/Water_Var_DBG10_river_low DBG10_river_low $P 120
shot $M/Water_View_HarbourHigh base_harbour_high_4k $U 300
shot $V/Water_Var_FE6_harbour_high FE6_harbour_high $P 120
shot $V/Water_Var_FE18_harbour_high FE18_harbour_high $P 120
shot $M/Water_View_RiverLow base_river_low_4k $U 300
shot $V/Water_Var_CM8_river_low CM8_river_low $P 120
shot $M/Water_View_RiverLow base_river_low $P 120
shot $V/Water_Var_RC0_river_low RC0_river_low $P 120
shot $V/Water_Var_LF40_river_low LF40_river_low $P 120
shot $V/Water_Var_GR15_river_low GR15_river_low $P 120
shot $V/Water_Var_G15L40_river_low G15L40_river_low $P 120
shot $M/Water_View_RiverSun base_river_sun $P 120
shot $V/Water_Var_RC0_river_sun RC0_river_sun $P 120
shot $V/Water_Var_LF40_river_sun LF40_river_sun $P 120
shot $V/Water_Var_GR15_river_sun GR15_river_sun $P 120
shot $V/Water_Var_G15L40_river_sun G15L40_river_sun $P 120
shot $V/Water_Var_GS30_river_sun GS30_river_sun $P 120
shot $V/Water_Var_GS40_river_sun GS40_river_sun $P 120
waitclear
echo "HOLD D DONE $(date +%T) ($(( $(date +%s) - T0 )) s)"
