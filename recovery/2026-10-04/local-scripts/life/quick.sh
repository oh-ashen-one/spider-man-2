#!/bin/bash
# quick still runs through the GPU lock: quick.sh <name> <map> <shots> <quit> [extra UE args...]
NAME="$1"; MAP="$2"; SHOTS="$3"; QUIT="$4"; shift 4
UE_DIR=/Users/midir/sm2-n1/life/unreal/WebHomage
T=/Users/midir/sm2-n1/_scratch/life/capture/$NAME
rm -rf "$T"
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label life -- "$UE_DIR/Scripts/run_game.sh" "$T" -map "$MAP" -res ${RES:-1920x1080} -shots "$SHOTS" -quit "$QUIT" -name "$NAME" -timeout 1500 -exec "r.ScreenPercentage 100" -- "$@" 2>&1 | tail -3
source /Users/midir/sm2-n1/_scratch/life/venv/bin/activate
for p in "$T"/${NAME}_*.png; do sips -s format jpeg -s formatOptions 92 "$p" --out "${p%.png}.jpg" >/dev/null; done
python /Users/midir/sm2-n1/life/tools/life/detect_counts.py --annot "$T" "$T"/${NAME}_*.jpg 2>&1 | grep -v Warning
grep -E "WH_LIFE_(SAMPLE|FRAME|BOX)" "$T/$NAME.log" | sed 's/^.*Display: //' | cut -c1-420 > "$T/probe.txt"
