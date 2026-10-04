#!/bin/bash
# P6 round 03 batch 2: shade-only fill, density, parked-gap proxy, S2 (1080p + 4K), swing camera variants and the ahead-recycling A/B. One capture-slot hold; no new launch after 25 min.
cd /Users/midir/sm2-n1/_scratch/life/r03
T0=$(date +%s)
S1="/Game/Tests/Life/Life_View_S1"; S2="/Game/Tests/Life/Life_View_S2"; SW="/Game/Tests/Life/Life_Swing_Clip"
run() { local el=$(( $(date +%s) - T0 )); if [ $el -gt 1500 ]; then echo "SKIP $1 (elapsed $el s)"; return; fi; echo "== $1 (elapsed $el s)"; ./exp.sh "$@"; }
C1="-WHLifeSample=8:30:1 -WHLifeClearAhead=12 -WHLifeNearAll=10 -WHLifeStats=5"
run g1_s1_d1600_f2500 $S1 1920x1080 12,16,20,24,28 30 - -- $C1 -WHLifePerKm=1600:1100 -WHLifeFill=2500
run g2_s1_d1600_f4500 $S1 1920x1080 12,16,20,24,28 30 - -- $C1 -WHLifePerKm=1600:1100 -WHLifeFill=4500
run g3_s1_d1600_f2500_gap $S1 1920x1080 12,16,20,24,28 30 - -- $C1 -WHLifePerKm=1600:1100 -WHLifeFill=2500 -WHLifeClearParked=254:100:270:150
run g4_s1_sweep $S1 1920x1080 12,16,20,24,28 30 - -- $C1 -WHLifePerKm=1600:1100 -WHLifeFillSteps=0:0,14:1500,18:2500,22:4000,26:6500
run g5_s1_fillall2500 $S1 1920x1080 12,16,20,24,28 30 - -- $C1 -WHLifePerKm=1600:1100 -WHLifeFill=2500 -WHLifeFillAll
run g6_s2_d1600 $S2 1920x1080 12,16,20,24,28 30 - -- $C1 -WHLifePerKm=1600:1100 -WHLifeFill=2500
run g7_s2_4k_d1600 $S2 3840x2160 28 30 - -- $C1 -WHLifePerKm=1600:1100 -WHLifeFill=2500
CS="-WHLifeSample=2.5:12.5:0.5 -WHLifeNearAll=10 -WHLifeStats=5 -WHLifePerKm=1800:1200 -WHLifeFill=2500"
run g8_swing_a $SW 1920x1080 4.5,6.5,8.5,10.5,12.5 13.5 - -- $CS -WHLifeRig=250:232:250:-18:2200:250:0:-170:88:2.5:10 -WHLifeAimAhead=70:0
run g9_swing_b $SW 1920x1080 4.5,6.5,8.5,10.5,12.5 13.5 - -- $CS -WHLifeRig=250:232:250:-18:1600:250:0:-170:82:2.5:10 -WHLifeAimAhead=45:0
run g10_swing_a_noahead $SW 1920x1080 4.5,6.5,8.5,10.5,12.5 13.5 - -- $CS -WHLifeRig=250:232:250:-18:2200:250:0:-170:88:2.5:10 -WHLifeAimAhead=70:0 -WHLifeAheadSpeed=1000000000
echo "batch2 done in $(( $(date +%s) - T0 )) s"
