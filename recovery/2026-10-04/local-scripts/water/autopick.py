# pick the tuning variant whose river_low near-crop numbers come closest to PLAN section 4 Water (1080p iteration stills; hp x1.7 ~ 4K)
import json, subprocess, sys, os
S='/Users/midir/sm2-n1/_scratch/water'; D=os.path.join(S,'iter',os.environ.get('ITER','i3')); T='/Users/midir/sm2-n1/water/tools/water/water_spec.py'
var=json.load(open(os.path.join(S,'variants.json')))
def near(f): return json.loads(subprocess.run([sys.executable,T,'near',f],capture_output=True,text=True).stdout)
def s4(f): return json.loads(subprocess.run([sys.executable,T,'s4',f],capture_output=True,text=True).stdout)
best=None
for v,pv in var.items():
    f=os.path.join(D,'%s_river_low.png'%v)
    if not os.path.exists(f): continue
    n=near(f); sc=max(0,n['mean_Y']-80)/10+max(0,12-n['highpass_sd']*1.7)/2+max(0,150-n['p99_5'])/10+max(0,1-n['glint_pct_ge140'])
    f4=os.path.join(D,'%s_S4_perch_skyline.png'%v)
    if os.path.exists(f4):
        c=s4(f4)['C14']; sc+=max(0,5-c)/2+max(0,c-35)/2
    print(v, round(sc,2), n, flush=True)
    if best is None or sc<best[0]: best=(sc,v)
pv={k:x for k,x in var[best[1]].items() if not k.startswith('_')}
json.dump(pv, open(os.path.join(S,'final_params.json'),'w')); print('PICK', best[1], pv)
