#!/bin/bash
# one hold: rebuild + probe variant g (0.22 s catch-pose window); if a keep-passing line fails, fall back to variant f; then windows 0,1
T0=$(date +%s)
WT=/Users/midir/sm2-n1/tri; WT="${WT}cks"
S=/Users/midir/sm2-n1/_scratch/tricks
HOLD_T0=$T0 TAG=g PROBE=1 RENDER=0 $WT/tools/tricks/hold_r02.sh
if [ ! -f $S/probe_r02/g/VERDICT ] || grep -wqE "fails .*(G3|G4|V1|V2|K|P|G2)" $S/probe_r02/g/VERDICT || ! grep -q "route OK" $S/probe_r02/g/VERDICT; then
  echo "variant g fails a keep-passing line -> variant f"
  cp $S/r02/WebTravFlips_f.cpp $WT/unreal/WebHomage/Source/WebHomage/Traversal/WebTravFlips.cpp
  $WT/unreal/WebHomage/Scripts/build_editor.sh 2>&1 | tail -1
  mkdir -p $S/probe_r02/g; cp $S/probe_r02/f/VERDICT $S/probe_r02/g/VERDICT; echo "(variant f)" >> $S/probe_r02/g/VERDICT
fi
HOLD_T0=$T0 TAG=g PROBE=0 RENDER=1 RENDER_ARGS="-WHHeroFill=16000,36000" $WT/tools/tricks/hold_r02.sh
