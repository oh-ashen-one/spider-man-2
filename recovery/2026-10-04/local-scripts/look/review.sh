#!/bin/zsh
# usage: review.sh preset:shot ... ; 1080p native stills at t=14 into scratch/review
cd /Users/midir/sm2-n1/look/unreal/WebHomage
for ps in "$@"; do
  P=${ps%%:*}; S=${ps##*:}
  Scripts/run_game.sh /Users/midir/sm2-n1/_scratch/look/review -map /Game/Tests/Look/Look_View_${P}_${S} -res 1920x1080 -shots 14 -name ${P}_${S} -timeout 600 -exec "r.ScreenPercentage 100" | grep -E "WH_SHOT" 
done
