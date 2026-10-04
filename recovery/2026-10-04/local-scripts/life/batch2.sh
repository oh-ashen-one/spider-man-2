#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/life
./quick.sh s1b /Game/Tests/Life/Life_View_S1 9,12,15,18 19 -WHLifeSample=6:19:1 > s1b.out 2>&1
./quick.sh st2 /Game/Tests/Life/Life_Street_Clip 5,8,11,14,17 19 -WHLifeSample=4:18:1 > st2.out 2>&1
./quick.sh sw2 /Game/Tests/Life/Life_Swing_Clip 4,6,8,10,12 13 -WHLifeSample=3:13:1 > sw2.out 2>&1
./quick.sh sg2 /Game/Tests/Life/Life_Signal_Clip 3,6,9,12 13 -WHLifeSample=1:13:1 -WHLifeSignalPhase=30.5 -WHLifeQueue=1201,1202 > sg2.out 2>&1
echo batch2 done
