#!/bin/bash
# water r05b hold E (4K/1080p stills): build once with the variant set -> Dbg 10 on harbour_high (4K) and river_low -> new-default stills ->
# far-line / river-level / glitter / foam variants at 1080p. Run ONLY under gpu_slot.sh capture. No engine run starts past DEADLINE.
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; RD=$S/r05e; WT=/Users/midir/sm2-n1/water; UEP=$WT/unreal/WebHomage
T0=$(date +%s); DEADLINE=${DEADLINE:-2250}
left() { echo $(( DEADLINE - ($(date +%s) - T0) )); }
waitclear() { for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || return 0; sleep 1; done; echo "HOLD: engine still exiting, abort"; exit 8; }
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "HOLDE: PAUSED exists, abort"; exit 6; }
cd $WT
HASH=$(git hash-object unreal/WebHomage/Scripts/build_water.py | cut -c1-12)
echo "HOLD E start $(date +%T) build_water.py $HASH variants $(git hash-object tools/water/r05/variantsE.json | cut -c1-8)"
if [ -z "${SKIP_BUILD:-}" ]; then
  SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_PARAMS='{}' SM2_WATER_VARIANTS="$(cat tools/water/r05/variantsE.json)" \
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
M=/Game/Water/Maps; V=/Game/Water/Variants; P=1920x1080; U=3840x2160
shot $M/Water_View_HarbourHigh base_harbour_high_4k $U 300
shot $V/Water_Var_DBG10_harbour_high DBG10_harbour_high $P 120
if [ -f $OUT/base_harbour_high_4k/base_harbour_high_4k.log ] && grep -q "Failed to compile Material" $OUT/base_harbour_high_4k/base_harbour_high_4k.log; then echo "HOLD: WATER MATERIAL FAILED TO COMPILE"; exit 9; fi
shot $M/Water_View_RiverLow base_river_low $P 120
shot $M/Water_View_RiverSun base_river_sun $P 120
shot $M/Water_View_HarbourSunHigh base_harbour_sun_high $P 120
shot $V/Water_Var_DF0_river_low DF0_river_low $P 120
shot $V/Water_Var_DF0_river_sun DF0_river_sun $P 120
shot $V/Water_Var_DF0_harbour_high DF0_harbour_high $P 120
shot $V/Water_Var_DBG10_river_low DBG10_river_low $P 120
shot $V/Water_Var_MK1_river_low MK1_river_low $P 120
shot $V/Water_Var_MK05_river_low MK05_river_low $P 120
shot $V/Water_Var_MK1_river_sun MK1_river_sun $P 120
shot $V/Water_Var_MK05_river_sun MK05_river_sun $P 120
shot $M/Water_View_HarbourHigh base_harbour_high $P 120
shot $V/Water_Var_DF0_harbour_sun_high DF0_harbour_sun_high $P 120
waitclear
echo "HOLD E DONE $(date +%T) ($(( $(date +%s) - T0 )) s)"
