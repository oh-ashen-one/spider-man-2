#!/bin/bash
# numbers for an iteration dir of 1080p stills
D=${1:-/Users/midir/sm2-n1/_scratch/water/iter/i1}; T=/Users/midir/sm2-n1/water/tools/water/water_spec.py
for f in $D/*.png; do n=$(basename $f .png)
  case $n in *s4*|*S4*) python3 $T s4 $f ;; harbour) ;; *) python3 $T near $f ;; esac
done
