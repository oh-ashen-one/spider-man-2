#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/life
./quick.sh stv1 /Game/Tests/Life/Life_Street_Clip 5,8,11,14,17 19 -WHLifeSample=4:18:1 -WHLifeRig=240.6:224:240.6:197:180:208:1.5:124:72 -WHLifeClearParked=238.5:188:243.5:232 > stv1.out 2>&1
./quick.sh stv2 /Game/Tests/Life/Life_Street_Clip 5,8,11,14,17 19 -WHLifeSample=4:18:1 -WHLifeRig=240.6:224:240.6:197:250:208:0.5:124:72 -WHLifeClearParked=238.5:188:243.5:232 > stv2.out 2>&1
./quick.sh stv3 /Game/Tests/Life/Life_Street_Clip 5,8,11,14,17 19 -WHLifeSample=4:18:1 -WHLifeRig=235.0:224:235.0:197:170:285:1.6:130:72 > stv3.out 2>&1
echo batch5 done
