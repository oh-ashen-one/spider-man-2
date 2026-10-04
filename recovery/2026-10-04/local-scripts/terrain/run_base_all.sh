#!/bin/bash
# terrain: base city+traversal+look+map in one editor session through the GPU lock (headless -nullrhi commandlet)
S=/Users/midir/sm2-n1/_scratch/terrain; M=$S/manhattan
export SM2_MANHATTAN_SCR=$M SM2_CITY_SCRATCH=$M SM2_CITY_EXPORT=$M/export/midtown3x3 SM2_CITY_TEX=$M/tex
exec $S/bin/ue_locked.sh /Users/midir/sm2-n1/terrain/unreal/WebHomage/WebHomage.uproject -run=pythonscript -script=$S/jobs_base_all.py -unattended -nullrhi -nosplash -RenderOffScreen -NoSound -NoCrashReports -abslog=$M/logs/base_all.log
