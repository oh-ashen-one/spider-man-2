#!/bin/bash
# P6 round 03 batch 1 (one capture-slot hold, launches strictly sequential, stops starting new ones after 25 min so the 40 min max hold is never hit)
cd /Users/midir/sm2-n1/_scratch/life/r03
T0=$(date +%s)
S1="/Game/Tests/Life/Life_View_S1"; S2="/Game/Tests/Life/Life_View_S2"
run() { local el=$(( $(date +%s) - T0 )); if [ $el -gt 1500 ]; then echo "SKIP $1 (elapsed $el s)"; return; fi; echo "== $1 (elapsed $el s)"; ./exp.sh "$@"; }
COMMON="-WHLifeSample=8:30:1 -WHLifeClearAhead=12 -WHLifeNearAll=10 -WHLifeStats=5"
run e1_s1_fill $S1 1920x1080 12,16,20,24,28 30 - -- $COMMON -WHLifeFillSteps=0:0,14:2500,18:6000,22:12000,26:25000
run e2_s1_d2000 $S1 1920x1080 12,16,20,24,28 30 - -- $COMMON -WHLifePerKm=2000:1300 -WHLifeFill=6000
run e3_s1_d2800 $S1 1920x1080 12,16,20,24,28 30 - -- $COMMON -WHLifePerKm=2800:1700 -WHLifeFill=6000
run e4_s2_d2000 $S2 1920x1080 12,16,20,24,28 30 - -- $COMMON -WHLifePerKm=2000:1300 -WHLifeFill=6000
echo "batch1 done in $(( $(date +%s) - T0 )) s"
