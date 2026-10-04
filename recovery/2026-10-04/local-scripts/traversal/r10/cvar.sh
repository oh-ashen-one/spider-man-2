#!/bin/bash
# usage: cvar.sh x y jump(0/1) label
cd /Users/midir/sm2-n1/traversal
P=/Users/midir/sm2-n1/_scratch/traversal/probe
python3 - "$1" "$2" "$3" <<'EOF'
import json,sys
x,y,jump=float(sys.argv[1]),float(sys.argv[2]),sys.argv[3]=='1'
j=json.load(open('docs/night1/traversal/scripts/city/c_wallrun_perch.json'))
j['spawn']['pos']=[x,y,0.95]
k=[{"t":0.0,"move":[0,1],"sprint":True}]
if jump: k+= [{"t":0.35,"jump":True},{"t":0.5,"jump":False}]
k+= [{"t":5.1,"move":[0,0],"sprint":False},{"t":5.9,"look":[-150.0,-10.0]},{"t":7.1,"look":[0,0]},{"t":7.3,"zip":True},{"t":7.4,"zip":False}]
j['keys']=k
json.dump(j,open('/Users/midir/sm2-n1/_scratch/traversal/r10/scripts/c_%d_%d.json'%(x,y),'w'),indent=1)
EOF
docs/night1/traversal/probe.sh /Users/midir/sm2-n1/_scratch/traversal/r10/scripts/c_$1_$2.json $P/m13_c_$1_$2 10 >/dev/null 2>&1
echo "--- $*"
python3 -c "
import csv
R=list(csv.DictReader(open('$P/m13_c_$1_$2/probe_telemetry.csv')))
last=None
for r in R:
  k=(r['mode'],r['sub'])
  if k!=last: print(r['t'],k,'%.1f %.1f %.1f'%(float(r['x_m']),float(r['y_m']),float(r['z_m'])),'pitch',r['cam_pitch_deg'],'zt',r['zip_target']); last=k
" | head -24
