#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/life
./quick.sh sw_a /Game/Tests/Life/Life_Street_Clip 5,8,11,14,17 19 -WHLifeSample=4:18:1 -WHLifeRig=241.0:150:241.0:123:180:223:1.6:50:75 -WHLifeClearParked=238.5:100:243.5:155 > sw_a.out 2>&1
./quick.sh sw_b /Game/Tests/Life/Life_Street_Clip 5,8,11,14,17 19 -WHLifeSample=4:18:1 -WHLifeRig=236.0:150:236.0:123:170:243:1.6:50:75 > sw_b.out 2>&1
./quick.sh sw_c /Game/Tests/Life/Life_Street_Clip 5,8,11,14,17 19 -WHLifeSample=4:18:1 -WHLifeRig=239.0:150:239.0:123:180:222:1.6:50:75 -WHLifeClearParked=238.5:100:243.5:155 > sw_c.out 2>&1
echo batch6 done
