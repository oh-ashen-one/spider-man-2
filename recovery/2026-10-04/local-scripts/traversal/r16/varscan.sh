#!/bin/bash
# usage: varscan.sh <script name> <quit> <dx> <dy> ... (pairs)  -> probes each variant (nullrhi) in ONE gpu hold; prints per-flip tier
NAME=$1; Q=$2; shift 2
R=/Users/midir/sm2-n1/_scratch/traversal/r16
while [ $# -ge 2 ]; do
  DX=$1; DY=$2; shift 2
  TAG=v_${NAME}_${DX}_${DY}
  python3 $R/mkvar.py $NAME $DX $DY $TAG > /dev/null
  OUTD=$R/scan/$TAG SC=$R/scripts/$TAG $R/batch_probe.sh $NAME:$Q 2>&1 | grep "choice" | sed -E 's/.*hero \(([^)]*)\) heading (-?[0-9]+):.*/\1 h\2/' | tr '\n' ';' ; echo " <= $TAG"
done
