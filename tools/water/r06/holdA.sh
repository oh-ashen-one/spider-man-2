#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# water r06 hold A (1080p screening stills): build once with variantsA.json, then the base / variant stills in priority order; re-runnable
# (skips stills newer than BUILT; SKIP_BUILD=1 for the next hold). Run ONLY under gpu_slot.sh capture. No engine run starts past DEADLINE.
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; RD=${RD:-$S/r06a}; WT=/Users/midir/sm2-n1/water; UEP=$WT/unreal/WebHomage
VJ=${VJ:-$WT/tools/water/r06/variantsA.json}
T0=$(date +%s); DEADLINE=${DEADLINE:-2250}
left() { echo $(( DEADLINE - ($(date +%s) - T0) )); }
waitclear() { for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || return 0; sleep 1; done; echo "HOLD: engine still exiting, abort"; exit 8; }
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "HOLD: PAUSED exists, abort"; exit 6; }
mkdir -p $RD; cd $WT
HASH=$(git hash-object unreal/WebHomage/Scripts/build_water.py | cut -c1-12)
echo "HOLD start $(date +%T) build_water.py $HASH variants $(git hash-object $VJ | cut -c1-8)"
if [ -z "${SKIP_BUILD:-}" ]; then
  SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_PARAMS='{}' SM2_WATER_VARIANTS="$(cat $VJ)" \
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
M=/Game/Water/Maps; V=/Game/Water/Variants; P=1920x1080
for spec in ${SHOTS:-"$M/Water_View_RiverLow|base_rl" "$M/Water_View_RiverSun|base_rs" "$V/Water_Var_DBG11_river_low|DBG11_rl" "$V/Water_Var_OFF_river_low|OFF_rl" "$V/Water_Var_OFF_river_sun|OFF_rs" "$V/Water_Var_S6_river_low|S6_rl" "$V/Water_Var_S6_river_sun|S6_rs" "$V/Water_Var_CH_river_low|CH_rl" "$V/Water_Var_CH_river_sun|CH_rs" "$V/Water_Var_R2_river_low|R2_rl" "$V/Water_Var_R2_river_sun|R2_rs" "$V/Water_Var_S6G_river_sun|S6G_rs" "$V/Water_Var_F24_river_low|F24_rl" "$V/Water_Var_DBG11_river_sun|DBG11_rs" "$V/Water_Var_S6G_river_low|S6G_rl" "$V/Water_Var_F24_river_sun|F24_rs"}; do
  shot "${spec%%|*}" "${spec#*|}" $P 150
done
waitclear
echo "HOLD DONE $(date +%T) ($(( $(date +%s) - T0 )) s)"
