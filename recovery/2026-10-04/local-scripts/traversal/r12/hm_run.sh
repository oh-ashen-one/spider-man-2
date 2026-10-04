#!/bin/bash
UE=/Users/midir/sm2-n1/traversal/unreal/WebHomage
"$UE/Scripts/run_game.sh" /Users/midir/sm2-n1/_scratch/traversal/r12/hm -map /Game/Maps/Manhattan -res 1280x720 -quit 2 -name hm -timeout 900 -- -nullrhi -benchmark -fps=60 \
  -WHTravScript=/Users/midir/sm2-n1/traversal/docs/night1/traversal/scripts/city/f5_canyon_backDouble.json -WHTravHeightmap=/Users/midir/sm2-n1/_scratch/traversal/r12/hm/heightmap.csv | tail -1
