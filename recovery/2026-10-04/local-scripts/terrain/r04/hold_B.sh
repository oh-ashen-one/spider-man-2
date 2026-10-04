#!/bin/bash
cd /Users/midir/sm2-n1/terrain
PROBE_DIR=/Users/midir/sm2-n1/terrain/docs/night1/terrain/round-04/t5_candidates2 STAGE=A /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round4.sh
echo "hold rc=$?"
