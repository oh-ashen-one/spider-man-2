#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# r06 numbers for one round dir (CPU only): tools/terrain/measure_r06.sh docs/night1/terrain/round-06
#  = measure_r05.sh (E1 lawn crops, p1 crown crops sigma-3 / saturation, E9c silhouette, t4 flat quads, t5 ground) + the r06 targets:
#  (2) p4 trees (3005,1100) (3040,1078) (2900,1060): darkest 15 px box within 60 px on the anti-sun side / lit lawn (r06_checks.py boxes; lit box from <round>/r06_boxes.json "lit")
#  (3) p6 esplanade tree shadows / paving (r06_checks.py ratio; boxes from <round>/r06_boxes.json "p6")
#  (4) p10 sky-bordered foliage patches with hp3 SD < 5 wider than 30 px (r06_checks.py hull)
set -uo pipefail
R="$(cd "$1" && pwd)"; REPO="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$REPO"
S=$R/stills
tools/terrain/measure_r05.sh "$R" > "$R/measure_r05_tools.txt" 2>&1
[ -f "$S/p10_lawn_eye.jpg" ] && python3 tools/terrain/r06_checks.py hull "$S/p10_lawn_eye.jpg" "$R/hull_p10.json" | tee "$R/hull_p10.txt"
if [ -f "$R/r06_boxes.json" ]; then
  LIT=$(python3 -c "import json;print(','.join(map(str,json.load(open('$R/r06_boxes.json'))['lit'])))")
  [ -f "$S/p4_greatlawn.jpg" ] && python3 tools/terrain/r06_checks.py boxes "$S/p4_greatlawn.jpg" "$R/tree_boxes_p4.json" p4_greatlawn 3005,1100 3040,1078 2900,1060 --lit "$LIT" > "$R/tree_boxes_p4.txt"
  P6=$(python3 -c "import json;print(' '.join(json.load(open('$R/r06_boxes.json')).get('p6', [])))")
  [ -n "$P6" ] && [ -f "$S/p6_west_shore.jpg" ] && python3 tools/terrain/r06_checks.py ratio "$S/p6_west_shore.jpg" "$R/p6_shadow_ratio.json" $P6 > "$R/p6_shadow_ratio.txt"
fi
exit 0
