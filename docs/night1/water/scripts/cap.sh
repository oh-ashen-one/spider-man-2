#!/bin/bash
# usage: cap.sh <name> <map> <res> [extra run_game args...]   (one capture through the GPU lock, waits for the shots)
NAME="$1"; MAP="$2"; RES="$3"; shift 3
OUT=/Users/midir/sm2-n1/_scratch/water-sonnet/cap/$NAME
rm -rf "$OUT"
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water-sonnet -- /Users/midir/sm2-n1/water-ab-sonnet/unreal/WebHomage/Scripts/run_game.sh "$OUT" -map "$MAP" -res "$RES" -name "$NAME" -timeout 2400 "$@" > /Users/midir/sm2-n1/_scratch/water-sonnet/logs/cap_$NAME.log 2>&1
echo "rc=$? $NAME"; tail -3 /Users/midir/sm2-n1/_scratch/water-sonnet/logs/cap_$NAME.log | cut -c1-200
