#!/bin/bash
# waits for hold D (chainD) to finish cleanly, then queues the movie holds E (lineupx0 pawn orbit) and F (hero chase fight crowd) one after the other from this shell (one engine of mine at a time)
P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters; export P2_SCRATCH UE_WAIT_SKIP=1
D=$P2_SCRATCH/r17/chainD; E=$P2_SCRATCH/r17/chainE; F=$P2_SCRATCH/r17/chainF
cd /Users/midir/sm2-n1/characters
for i in $(seq 1 720); do grep -q "chain done" $D/run/chain.log 2>/dev/null && break; sleep 5; done
if ! grep -q "chain done" $D/run/chain.log 2>/dev/null; then echo "hold D did not finish: not launching E"; exit 1; fi
if ! grep -q "crashes 0" $D/run/chain.log; then echo "hold D had crashes: not launching E"; exit 2; fi
while pgrep -f "hold_r17d_run.sh" > /dev/null; do sleep 3; done
sleep 20
while pgrep -f "sm2-n1/characters/unreal/WebHomage/WebHomage.uproject" > /dev/null; do sleep 5; done
echo "$(date +%T) launching E"
CHAIN_SNAPSHOT=.chain_r17e_run.sh STEPS="lineupx0 pawn orbit" /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label characters --timeout 28800 -- bash tools/ue_char/suits/.hold_r17e_run.sh $E > $E/gpu_wrapper.log 2>&1
if ! grep -q "chain done" $E/run/chain.log 2>/dev/null || ! grep -q "crashes 0" $E/run/chain.log; then echo "hold E not clean: not launching F"; exit 3; fi
while pgrep -f "sm2-n1/characters/unreal/WebHomage/WebHomage.uproject" > /dev/null; do sleep 5; done
sleep 20
echo "$(date +%T) launching F"
CHAIN_SNAPSHOT=.chain_r17f_run.sh STEPS="hero chase fight crowd" /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label characters --timeout 28800 -- bash tools/ue_char/suits/.hold_r17f_run.sh $F > $F/gpu_wrapper.log 2>&1
echo "$(date +%T) F done"
