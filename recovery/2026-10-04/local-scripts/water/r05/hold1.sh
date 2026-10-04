#!/bin/bash
# water r05 hold 1 (1080p only): build with variants -> Dbg 9 import diagnosis (t 16 + 45 s) -> contact-texture candidates -> reflection /
# colour variants. Run ONLY under gpu_slot.sh capture (nested gpu_slot calls pass through). Max hold 2400 s: no engine run starts past DEADLINE.
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; R5=$S/r05; WT=/Users/midir/sm2-n1/water; UEP=$WT/unreal/WebHomage
T0=$(date +%s); DEADLINE=${DEADLINE:-2200}
left() { echo $(( DEADLINE - ($(date +%s) - T0) )); }
waitclear() { for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || return 0; sleep 1; done; echo "HOLD: engine still exiting, abort"; exit 8; }
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "HOLD1: PAUSED exists, abort"; exit 6; }
cd $WT
echo "HOLD r05 1 start $(date +%T)"
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_VARIANTS="$(cat $R5/variants1.json)" \
  python3 unreal/WebHomage/Scripts/build_water.py --steps ue > $R5/build1.log 2>&1 || { echo "HOLD: water build FAILED"; tail -30 $R5/build1.log; exit 4; }
grep -E "TEXINFO|WARN|textures|material" $R5/build1.log | head -20
OUT=$S/iter/r05a; mkdir -p $OUT; cd $UEP
shot() { # map name res [shots]
  [ "$(left)" -gt 150 ] || { echo "skip $2 (time)"; return; }
  [ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED: stop"; exit 6; }
  waitclear; Scripts/run_game.sh "$OUT/$2" -map "$1" -res "$3" -shots "${4:-16}" -name "$2" -exec "r.ScreenPercentage 100" -timeout 400 >/dev/null 2>&1
  local n=0; for png in $(ls "$OUT/$2/$2"_*.png 2>/dev/null); do n=$((n+1)); done
  local png; png=$(ls -t "$OUT/$2/$2"_*.png 2>/dev/null | head -1); [ -n "$png" ] && cp "$png" "$OUT/$2.png" && echo "still $2 ($n png) $(date +%T)" || echo "NO STILL $2"; }
M=/Game/Water/Maps; V=/Game/Water/Variants
shot $V/Water_Var_DBG9_river_low DBG9_river_low 1920x1080 16,45
if grep -q "Failed to compile Material" $OUT/DBG9_river_low/DBG9_river_low.log; then echo "HOLD: WATER MATERIAL FAILED TO COMPILE"; grep -m5 -A6 "Failed to compile" $OUT/DBG9_river_low/DBG9_river_low.log; exit 9; fi
shot $M/Water_View_RiverLow base_river_low 1920x1080
shot $V/Water_Var_C1_river_low C1_river_low 1920x1080
shot $V/Water_Var_C2_river_low C2_river_low 1920x1080
shot $V/Water_Var_DBG7C1_river_low DBG7C1_river_low 1920x1080
shot $V/Water_Var_C1F_river_low C1F_river_low 1920x1080
shot $M/Water_View_HarbourHigh base_harbour_high 1920x1080
shot $V/Water_Var_SC0_harbour_high SC0_harbour_high 1920x1080
shot $V/Water_Var_SC150_harbour_high SC150_harbour_high 1920x1080
shot $V/Water_Var_SC380_harbour_high SC380_harbour_high 1920x1080
shot $V/Water_Var_L2_harbour_high L2_harbour_high 1920x1080
shot $V/Water_Var_HC1_harbour_high HC1_harbour_high 1920x1080
shot $V/Water_Var_HC1F2_harbour_high HC1F2_harbour_high 1920x1080
shot $V/Water_Var_HC2_harbour_high HC2_harbour_high 1920x1080
shot $V/Water_Var_HDBG4_harbour_high HDBG4_harbour_high 1920x1080
shot $M/Water_View_HarbourSunHigh base_harbour_sun_high 1920x1080
shot $V/Water_Var_S6_harbour_sun_high S6_harbour_sun_high 1920x1080
shot $V/Water_Var_S4_harbour_sun_high S4_harbour_sun_high 1920x1080
shot $V/Water_Var_S25_harbour_sun_high S25_harbour_sun_high 1920x1080
waitclear
echo "HOLD r05 1 DONE $(date +%T) ($(( $(date +%s) - T0 )) s)"
