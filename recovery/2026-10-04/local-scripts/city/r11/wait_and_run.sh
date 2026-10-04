#!/bin/zsh
# wait for the health monitor's PAUSED to lift (never render around it), then ONE hold for plan11 (S6 + S7 native 4K)
G=/Users/midir/sm2-n1/_scratch/gpu
while [ -e $G/PAUSED ]; do sleep 20; done
sleep 30
[ -e $G/PAUSED ] && exit 3
cd /Users/midir/sm2-n1/city
exec $G/bin/gpu_slot.sh capture --label city -- zsh tools/export/r11_plan.sh /Users/midir/sm2-n1/_scratch/city/r11/h11 /Users/midir/sm2-n1/_scratch/city/r11/plan11.txt
