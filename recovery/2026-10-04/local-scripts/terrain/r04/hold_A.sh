#!/bin/bash
cd /Users/midir/sm2-n1/terrain
STAGE=A /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round4.sh
echo "hold rc=$?"
