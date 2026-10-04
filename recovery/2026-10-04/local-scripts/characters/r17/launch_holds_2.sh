#!/bin/bash
# waits for hold E to finish cleanly, then runs holds F (crowd chase), G (hero), then rebuilds the editor module and runs hold H (lineupx0 dose-response)
# one after the other from this shell, one engine of mine at a time (RULES.md); stops at the first unclean hold
P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters; export P2_SCRATCH UE_WAIT_SKIP=1
R=$P2_SCRATCH/r17; cd /Users/midir/sm2-n1/characters
waitgone() { while pgrep -f "sm2-n1/characters/unreal/WebHomage/WebHomage.uproject" > /dev/null; do sleep 5; done; sleep 15; }
clean() { grep -q "chain done" $1/run/chain.log 2>/dev/null && grep -q "crashes 0" $1/run/chain.log; }
for i in $(seq 1 720); do grep -q "chain done" $R/chainE/run/chain.log 2>/dev/null && break; sleep 5; done
clean $R/chainE || { echo "hold E not clean: stop"; exit 1; }
while pgrep -f "hold_r17e_run.sh" > /dev/null; do sleep 3; done; waitgone
echo "$(date +%T) launching F (crowd chase)"
CHAIN_SNAPSHOT=.chain_r17f_run.sh STEPS="crowd chase" /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label characters --timeout 28800 -- bash tools/ue_char/suits/.hold_r17f_run.sh $R/chainF > $R/chainF/gpu_wrapper.log 2>&1
clean $R/chainF || { echo "hold F not clean: stop"; exit 2; }
waitgone
echo "$(date +%T) launching G (hero)"
CHAIN_SNAPSHOT=.chain_r17g_run.sh STEPS="hero" /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label characters --timeout 28800 -- bash tools/ue_char/suits/.hold_r17g_run.sh $R/chainG > $R/chainG/gpu_wrapper.log 2>&1
clean $R/chainG || { echo "hold G not clean: stop"; exit 3; }
waitgone
echo "$(date +%T) building the editor module for -WHShotFrames"
unreal/WebHomage/Scripts/build_editor.sh > $R/build_editor4.log 2>&1 || { echo "build failed"; exit 4; }
echo "$(date +%T) launching H (lineupx0)"
CHAIN_SNAPSHOT=.chain_r17h_run.sh STEPS="lineupx0" /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label characters --timeout 28800 -- bash tools/ue_char/suits/.hold_r17h_run.sh $R/chainH > $R/chainH/gpu_wrapper.log 2>&1
echo "$(date +%T) H done"
