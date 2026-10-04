#!/bin/bash
# P6 round 03 experiment runner: exp.sh <name> <map> <res> <shots|-> <quit> <exec extra|-> -- <game args...>
# Every launch goes through gpu_slot.sh (capture). One engine at a time (this script is sequential).
set -uo pipefail
NAME="$1"; MAP="$2"; RES="$3"; SHOTS="$4"; QUIT="$5"; EXEC="$6"; shift 6; [ "${1:-}" = "--" ] && shift
UE_DIR=/Users/midir/sm2-n1/life/unreal/WebHomage
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
OUT=/Users/midir/sm2-n1/_scratch/life/r03/$NAME
case "$OUT" in /Users/midir/sm2-n1/_scratch/life/r03/*) ;; *) exit 1;; esac
rm -rf "$OUT"
ARGS=(-map "$MAP" -res "$RES" -name "$NAME" -timeout 2400 -quit "$QUIT")
[ "$SHOTS" != "-" ] && ARGS+=(-shots "$SHOTS")
EXECS="r.ScreenPercentage 100"; [ "$EXEC" != "-" ] && EXECS="$EXECS,$EXEC"
ARGS+=(-exec "$EXECS")
[ -x /Users/midir/sm2-n1/_scratch/life/bin/gui_ok.sh ] && ! /Users/midir/sm2-n1/_scratch/life/bin/gui_ok.sh && { echo "GUI session cannot launch apps: no engine started"; exit 75; }
$G capture --label life -- "$UE_DIR/Scripts/run_game.sh" "$OUT" "${ARGS[@]}" -- "$@" | tail -3
for p in "$OUT/${NAME}"_*.png; do [ -f "$p" ] && sips -s format jpeg -s formatOptions 92 "$p" --out "${p%.png}.jpg" > /dev/null; done
grep -E "WH_LIFE|\[crowd\]" "$OUT/$NAME.log" | sed 's/^.*Display: //' > "$OUT/probe.txt"
echo "done $NAME"
