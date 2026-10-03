#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# tricks r02: hero-fill A/B (run INSIDE one gpu_slot capture hold). Renders the same short reel window (LT_FROM..LT_TO s, native 1080p)
# once per spec "tag:<extra game args>" so the frames can be compared; -WHHeroFill=<base cd>,<flip cd> is the character's command-line
# fill light (WebTravCharacter: 5000 / 18000 cd by default, scaled down when the hero is front-lit).
cd /Users/midir/sm2-n1/tricks
UP=/Users/midir/sm2-n1/tri; UP="${UP}cks/unreal/WebHomage/WebHomage.uproject"
while pgrep -f "$UP" >/dev/null; do sleep 5; done
A=${LT_FROM:-28.0}; B=${LT_TO:-29.5}
Q=$(python3 -c "print(round($B + 0.1 + 0.8, 3))")
for SPEC in ${LT_SPECS:-"base:" "fill:-WHHeroFill=14000,32000"}; do
  TAG=${SPEC%%:*}; ARG=${SPEC#*:}
  D=/Users/midir/sm2-n1/_scratch/tricks/light/$TAG
  case "$D" in /Users/midir/sm2-n1/_scratch/tricks/*) rm -rf "$D";; *) exit 1;; esac
  mkdir -p "$D"
  echo "== light $TAG ($ARG) $(date +%T)"
  unreal/WebHomage/Scripts/run_game.sh "$D" -map /Game/Maps/Manhattan -res 1920x1080 -quit "$Q" -name lt -movie -timeout 1200 \
    -exec "r.ScreenPercentage 100" -- -WHTravScript=/Users/midir/sm2-n1/tricks/docs/night1/tricks/scripts/t60_trick_reel.json -WHTravPreroll=0.8 -WHTravMask \
    -WHTrickDumpFrom=$A -WHTrickDumpTo=$B -WHTrickWarm=3 $ARG | tail -2
  echo "   $(ls "$D/lt_frames" 2>/dev/null | wc -l | tr -d ' ') frames $(date +%T)"
done
