#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/life
./quick.sh s1c /Game/Tests/Life/Life_View_S1 9,12,15,18,21 22 -WHLifeSample=6:22:1 > s1c.out 2>&1
./quick.sh st3 /Game/Tests/Life/Life_Street_Clip 5,8,11,14,17 19 -WHLifeSample=4:18:1 > st3.out 2>&1
echo batch3 done
