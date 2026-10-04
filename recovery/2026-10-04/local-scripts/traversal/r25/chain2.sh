#!/bin/bash
# scratch: after hold E -> build 4 (UBT only, no engine) -> holds F, G, H in turn (my own shell, never inside a hold)
R=/Users/midir/sm2-n1/_scratch/traversal/r25
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
H=/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-25/tools/hold4.sh
while [ ! -f $R/hold_E.done ]; do sleep 15; done; sleep 10
while pgrep -f "[s]m2-n1/traversal/unreal/WebHomage/WebHomage.uproject" >/dev/null; do sleep 10; done
/Users/midir/sm2-n1/traversal/unreal/WebHomage/Scripts/build_editor.sh > $R/build4.log 2>&1 || { echo "build 4 FAILED"; exit 1; }
echo "build 4 ok $(date +%T)"
for T in F G H; do
  [ -f $R/STOP_CHAIN2 ] && exit 0
  $G capture --label traversal -- $H $T > $R/hold$T.log 2>&1
  for i in $(seq 1 20); do [ -f $R/hold_$T.done ] && break; sleep 15; done
  echo "hold $T ended $(date +%T)"
done
