#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/life
./quick.sh st1 /Game/Tests/Life/Life_Street_Clip 5,8,11,14,17 19 -WHLifeSample=4:18:1 > st1.out 2>&1
./quick.sh sw1 /Game/Tests/Life/Life_Swing_Clip 4,7,10,13 14 -WHLifeSample=3:14:1 > sw1.out 2>&1
./quick.sh sg1 /Game/Tests/Life/Life_Signal_Clip 3,6,9,12 13 -WHLifeSample=1:13:1 -WHLifeSignalPhase=30.5 -WHLifeQueue=1201,1202 > sg1.out 2>&1
echo batch1 done
