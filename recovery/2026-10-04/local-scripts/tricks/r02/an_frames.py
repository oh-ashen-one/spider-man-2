import csv,sys,math
sys.path.insert(0,'/Users/midir/sm2-n1/tricks/tools/tricks')
import tricks_check as TC
d=sys.argv[1]; tsel=float(sys.argv[2])
T=list(csv.DictReader(open(d+'/probe_telemetry.csv'))); Pz=list(csv.DictReader(open(d+'/probe_pose.csv')))
f=TC.f
key=lambda r:(round(f(r['x_m']),2),round(f(r['y_m']),2),round(f(r['z_m']),2))
PI={}
for r in Pz: PI.setdefault(key(r),r)
J=[PI.get(key(r)) for r in T]
I=TC.instances(T)
c=[c for c in I if abs(f(T[c['rows'][-1][0]]['t'])-tsel)<0.05][0]
e=c['rows'][-1][0]
def q(j,p): return [f(j[p+'_q'+a]) for a in 'xyzw'] if p+'_qx' in j else None
def qang(a,b):
    d=abs(sum(x*y for x,y in zip(a,b))); return 2*math.degrees(math.acos(min(1,d)))
for k in range(e-24,e+20):
    j,j1=J[k],J[k+1]; r=T[k]
    pf=TC.rot_deg(TC.chest_frame(j),TC.chest_frame(j1))*60
    s=f"{f(r['t']):6.3f} {r['mode']:5s} {r['flip_shape']:10s}/{r['flip_shape_legs']:10s} fp {r['flip_pitch_deg']:>7s} rate {r['flip_rate_dps']:>6s} cw {j['catch_w']} chest/fr {pf:5.0f}"
    if q(j,'mesh'): s+=f" mesh/fr {qang(q(j,'mesh'),q(j1,'mesh'))*60:5.0f} body/fr {qang(q(j,'body'),q(j1,'body'))*60:5.0f}"
    s+=f" anim {r['anim_node']}"
    print(s)
