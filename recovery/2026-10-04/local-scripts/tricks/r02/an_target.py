import csv,sys,math
import numpy as np
from scipy.spatial.transform import Rotation as R
sys.path.insert(0,'/Users/midir/sm2-n1/tricks/tools/tricks')
import tricks_check as TC
d=sys.argv[1]
T=list(csv.DictReader(open(d+'/probe_telemetry.csv'))); Pz=list(csv.DictReader(open(d+'/probe_pose.csv')))
f=TC.f
key=lambda r:(round(f(r['x_m']),2),round(f(r['y_m']),2),round(f(r['z_m']),2))
PI={}
for r in Pz: PI.setdefault(key(r),r)
J=[PI.get(key(r)) for r in T]
I=TC.instances(T)
def Q(j,p): return R.from_quat([f(j[p+'_q'+a]) for a in 'xyzw'])
for c in I:
    e=c['rows'][-1][0]
    if T[e+1]['mode']!='swing': continue
    jw=J[e]; W=Q(jw,'catch'); B0=Q(jw,'body'); M0=Q(jw,'mesh')
    out=[]
    for dk in (6,15):
        B=Q(J[e+dk],'body')
        D=W.inv()*B   # actual body relative to predicted (in W frame)
        eu=D.as_euler('ZYX',degrees=True)  # yaw about up(Z), pitch about Y, roll about X
        out.append(f"+{dk/60:.2f}s diff {np.degrees(D.magnitude()):5.1f} (yaw {eu[0]:6.1f} pitch {eu[1]:6.1f} roll {eu[2]:6.1f})")
    # visible root at end vs W
    print(f"{c['prog']:16s} {f(T[e]['t']):6.2f} bank_stale? rho {jw['catch_rho']:>6s} | "+" | ".join(out)+f" | mesh-end vs body+0.25 {np.degrees((M0.inv()*Q(J[e+15],'mesh')).magnitude()):5.1f}")
