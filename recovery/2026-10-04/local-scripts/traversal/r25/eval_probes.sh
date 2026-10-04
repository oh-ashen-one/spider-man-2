#!/bin/bash
# scratch: T7/T3/T1/T2/T4 + attach gaps for each a_* nullrhi probe of hold $1
P=/Users/midir/sm2-n1/_scratch/traversal/r25/probe_$1
TD=/Users/midir/sm2-n1/traversal/docs/night1/traversal
for d in $P/a_*; do
  n=$(basename $d); f=$d/${n}_telemetry.csv; [ -f $f ] || continue
  E=/Users/midir/sm2-n1/_scratch/traversal/r25/eval_$n; mkdir -p $E; cp $f $E/a_swing_chain_telemetry.csv
  echo "=== $n vs r25 capture: $(python3 $TD/round-24/tools/same.py $f $TD/round-25/a_swing_chain_telemetry.csv)"
  python3 $TD/r24_checks.py $E > /dev/null 2>&1; grep -E "T7 4 s|T3|T1|T2|T4 ->|OK|FAIL" $E/R24_CHECK.txt | head -14
  python3 -c "
import csv
r=list(csv.DictReader(open('$f'))); prev=0; on=[]
for x in r:
    w=float(x['web_on'])>0.5
    if w and not prev: on.append(float(x['t']))
    prev=w
print('  attach', on, 'gaps', [round(b-a,2) for a,b in zip(on,on[1:])])"
done
