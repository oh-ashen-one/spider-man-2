#!/bin/bash
# r06 post-processing (CPU only): measurements + blind critic pack
set -uo pipefail
cd /Users/midir/sm2-n1/terrain || exit 1
R=docs/night1/terrain/round-06; C=/Users/midir/sm2-n1/_scratch/critic-E-r06
tools/terrain/measure_r06.sh $R
mkdir -p $C
case "$C" in /Users/midir/sm2-n1/_scratch/critic-E-r06) rm -rf "$C/pack" "$C/norm" "$C/pack.key.json";; *) exit 1;; esac
LAWN_PROGRESS=1 python3 tools/terrain/make_pairs.py $R $C/pairs.json docs/night1/terrain/round-05
python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py $C/pack $C/pairs.json
python3 tools/terrain/pack_small.py $C/pack
python3 - <<'PY'
import os, glob
from PIL import Image
bad = []
for d in sorted(glob.glob('/Users/midir/sm2-n1/_scratch/critic-E-r06/pack/*/')):
    a, b = os.path.join(d, 'A.jpg'), os.path.join(d, 'B.jpg')
    if os.path.exists(a) and os.path.exists(b):
        sa, sb = Image.open(a).size, Image.open(b).size
        print(os.path.basename(d.rstrip('/')), sa, sb, 'OK' if sa == sb else 'SIZE MISMATCH')
        if sa != sb: bad.append(d)
print('mismatches:', len(bad))
PY
