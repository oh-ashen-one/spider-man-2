#!/bin/bash
# water r05b hold M (4K/1080p stills): build once with the variant set -> Dbg 10 on harbour_high (4K) and river_low -> new-default stills ->
# far-line / river-level / glitter / foam variants at 1080p. Run ONLY under gpu_slot.sh capture. No engine run starts past DEADLINE.
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; RD=$S/r05m; WT=/Users/midir/sm2-n1/water; UEP=$WT/unreal/WebHomage
T0=$(date +%s); DEADLINE=${DEADLINE:-2250}
left() { echo $(( DEADLINE - ($(date +%s) - T0) )); }
waitclear() { for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || return 0; sleep 1; done; echo "HOLD: engine still exiting, abort"; exit 8; }
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "HOLDM: PAUSED exists, abort"; exit 6; }
cd $WT
HASH=$(git hash-object unreal/WebHomage/Scripts/build_water.py | cut -c1-12)
echo "HOLD M start $(date +%T) build_water.py $HASH variants $(git hash-object tools/water/r05/variantsM.json | cut -c1-8)"
if [ -z "${SKIP_BUILD:-}" ]; then
  SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_PARAMS='{}' SM2_WATER_VARIANTS="$(cat tools/water/r05/variantsM.json)" \
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
shot $M/Water_View_RiverLow_P3 D_p3 $P 120 7.5
shot $M/Water_View_RiverLow D_p0 $U 300 16
shot $V/Water_Var_C50_river_low_p3 C50_p3 $P 120 7.5
shot $V/Water_Var_C62_river_low_p3 C62_p3 $P 120 7.5
shot $M/Water_View_RiverLow_P7 D_p7 $P 120 9.5
shot $V/Water_Var_C50_river_low C50_p0 $U 300 16
shot $V/Water_Var_C62_river_low C62_p0 $U 300 16
shot $V/Water_Var_C50_river_low_p7 C50_p7 $P 120 9.5
shot $V/Water_Var_C62_river_low_p7 C62_p7 $P 120 9.5
waitclear
echo "HOLD M DONE $(date +%T) ($(( $(date +%s) - T0 )) s)"
