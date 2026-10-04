#!/bin/bash
# curate_perf.sh <src session dir> <dst dir> : keeps result.json, the WH perf json, the CSV (gzip), TABLE.md, perf_gpu.json
SRC="$1"; DST="$2"; case "$DST" in /Users/midir/sm2-n1/perf/docs/*) ;; *) echo bad dst; exit 1;; esac
mkdir -p "$DST"
cp "$SRC/TABLE.md" "$SRC/perf_gpu.json" "$DST/" 2>/dev/null
for d in "$SRC"/*/; do n=$(basename "$d"); [ -f "$d/result.json" ] || continue
  mkdir -p "$DST/$n"; cp "$d/result.json" "$DST/$n/"; cp "$d/${n}_perf.json" "$DST/$n/" 2>/dev/null
  [ -f "$d/csv.csv" ] && gzip -c "$d/csv.csv" > "$DST/$n/csv.csv.gz"
done
du -sh "$DST"
