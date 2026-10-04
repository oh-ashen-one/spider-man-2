#!/bin/bash
cd /Users/midir/sm2-n1/_scratch/traversal/r20
./probeE.sh > probeE_run.log 2>&1
python3 - <<'P' >> probeE_run.log 2>&1
import csv
rows=list(csv.DictReader(open('probe/f4_chain_flips/f4_chain_flips_telemetry.csv')))
ys=[float(r['y_m']) for r in rows]; print('F4 y range', min(ys), max(ys))
P
./capA.sh > capA.log 2>&1
