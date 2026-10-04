#!/bin/bash
# round 10 resume: d 4K stills only (the committed d stills predate the final build). Same commands as capture_round.sh.
set -uo pipefail
ROOT=/Users/midir/sm2-n1/traversal
UE_DIR=$ROOT/unreal/WebHomage
ROUND=$ROOT/docs/night1/traversal/round-10
SCR=$ROOT/docs/night1/traversal/scripts/city
TMP=/Users/midir/sm2-n1/_scratch/traversal/capture
GPU=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
NAME=d_sprint_jump_first_swing; JSON=d_sprint_jump_first_swing.json; SHOTS=2.3,5.6,7.6,11.8; PRE=0.8
while [ "$(pgrep -x UnrealEditor | wc -l)" -ge 3 ]; do sleep 5; done
rm -rf "$TMP/${NAME}_4k"
SHOTSP=$(python3 -c "print(','.join(str(round(float(t) + $PRE, 3)) for t in '$SHOTS'.split(',')))")
echo "GPU util: $(ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1)"
"$GPU" capture --label traversal -- "$UE_DIR/Scripts/run_game.sh" "$TMP/${NAME}_4k" -map /Game/Maps/Manhattan -res 3840x2160 -shots "$SHOTSP" -name "$NAME" -timeout 2400 \
  -exec "r.ScreenPercentage 100" -- -benchmark -fps=60 -WHTravScript="$SCR/$JSON" -WHTravPreroll=$PRE -WHTravCsv="$TMP/${NAME}_4k/stills_telemetry.csv" | tail -3
I=0
for T in ${SHOTS//,/ }; do
  p=$(ls "$TMP/${NAME}_4k/${NAME}_$(printf %02d $I)_"*.png 2>/dev/null | head -1)
  [ -n "$p" ] && sips -s format jpeg -s formatOptions 92 "$p" --out "$ROUND/stills/${NAME}_$(printf %02d $I)_t$(printf %05.1f $T).jpg" > /dev/null && echo "still $I ok"
  I=$((I + 1))
done
echo DONE
