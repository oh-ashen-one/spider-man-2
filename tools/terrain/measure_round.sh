#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Terrain SPEC numbers for one round (CPU only): usage tools/terrain/measure_round.sh docs/night1/terrain/round-01
set -uo pipefail
R="$(cd "$1" && pwd)"; REPO="$(cd "$(dirname "$0")/../.." && pwd)"; SCR=/Users/midir/sm2-n1/_scratch/terrain
cd "$REPO"
cp "$SCR/prep/stats.json" "$R/stats.json" 2>/dev/null && echo "E2 stats -> $R/stats.json"
python3 tools/terrain/shore_audit.py "$SCR/manhattan/export/midtown3x3" "$SCR/export" "$R/shore_audit.json" | tail -22 > "$R/shore_audit.txt"; echo "E3 -> $R/shore_audit.json"
python3 tools/terrain/check_hlsl.py > "$R/hlsl_check.txt" 2>&1; grep -c " OK" "$R/hlsl_check.txt" | sed 's/^/HLSL materials OK: /'
S=(); for id in p1_south p2_reservoir p3_lake p4_greatlawn p9_park_panorama p10_lawn_eye; do [ -f "$R/stills/$id.jpg" ] && S+=("$R/stills/$id.jpg"); done
[ ${#S[@]} -gt 0 ] && python3 tools/terrain/crop_stats.py "$R/crop_stats.json" "${S[@]}" | tee "$R/crop_stats.txt"
B=(); for id in p1_south p2_reservoir p10_lawn_eye; do [ -f "$R/stills/base_$id.jpg" ] && B+=("$R/stills/base_$id.jpg"); done
[ ${#B[@]} -gt 0 ] && python3 tools/terrain/crop_stats.py "$R/crop_stats_baseline.json" "${B[@]}" | tee "$R/crop_stats_baseline.txt"
