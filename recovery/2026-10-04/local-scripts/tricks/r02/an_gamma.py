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
def Q(j,p): return R.from_quat([f(j[p+'_q'+a]) for a in 'xyzw'])
def fit(D):
    U=D.apply([0,0,1]); beta=math.degrees(math.atan2(U[0],U[2]))
    R2=R.from_rotvec([0,math.radians(beta),0]).inv()*D
    q=R2.as_quat(); gam=math.degrees(2*math.atan2(q[2],q[3])); gam=(gam+180)%360-180
    Sw=R2*R.from_rotvec([0,0,math.radians(gam)]).inv(); qs=Sw.as_quat(); rho=math.degrees(2*math.atan2(qs[0],qs[3]))
    return beta,gam,rho
for c in TC.instances(T):
    e=c['rows'][-1][0]
    if T[e+1]['mode']!='swing': continue
    j=J[e]; s=J[c['rows'][0][0]]
    # body frame at the window start (approx: the last row's body), actual body 0.25 s after the catch
    B0=Q(j,'body'); Ba=Q(J[e+15],'body'); W=Q(j,'catch')
    ba,ga,ra=fit(B0.inv()*Ba); bp,gp,rp=fit(B0.inv()*W)
    print(f"{c['prog']:16s} {f(T[e]['t']):6.2f} hand {j['catch_hand']:>2s} pred beta {bp:6.1f} gam {gp:6.1f} rho {rp:6.1f} | actual(+.25) beta {ba:6.1f} gam {ga:6.1f} rho {ra:6.1f}")
print('--- residual |B0^-1 Bact(+0.1) vs Ry(beta)Rz(k*gamma)| by k')
tot={}
for c in TC.instances(T):
    e=c['rows'][-1][0]
    if T[e+1]['mode']!='swing': continue
    j=J[e]; B0=Q(j,'body'); Ba=Q(J[e+6],'body'); W=Q(j,'catch')
    bp,gp,rp=fit(B0.inv()*W); Da=B0.inv()*Ba
    row=[]
    for k in (0,0.3,0.5,1.0):
        E=R.from_rotvec([0,math.radians(bp),0])*R.from_rotvec([0,0,math.radians(k*gp)])
        a=np.degrees((E.inv()*Da).magnitude()); row.append(a); tot.setdefault(k,[]).append(a)
    print(f"{c['prog']:16s} {f(T[e]['t']):6.2f} "+' '.join(f'k{k}:{a:5.1f}' for k,a in zip((0,0.3,0.5,1),row)))
for k,v in tot.items(): print(k, 'median', round(float(np.median(v)),1), 'mean', round(float(np.mean(v)),1))
