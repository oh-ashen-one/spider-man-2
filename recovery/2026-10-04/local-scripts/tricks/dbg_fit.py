exec(open('/Users/midir/sm2-n1/_scratch/critic-C-r01-work/an.py').read().split('res=[]')[0])
from scipy.spatial.transform import Rotation as Rot
from scipy.optimize import minimize
def F(j):  # chest frame as rotation matrix columns fw,up,side
    return frame(j).T
for c in I:
    e=c['i'][-1]
    if T[e+1]['mode']!='swing': continue
    k1=e+12
    C0=F(J[e]); C1=F(J[k1])
    V=np.array([f(T[e]['vx']),f(T[e]['vy']),0.]); V/=np.linalg.norm(V)
    B0=np.stack([V,np.cross([0,0,1],V),[0,0,1]]).T  # x fwd, y left, z up
    Rn=C1@C0.T
    D=B0.T@Rn@B0
    tot=np.degrees(Rot.from_matrix(D).magnitude())
    def res(x,mode):
        E=Rot.from_euler('yz' if mode==2 else 'y',x if mode==2 else x[:1],degrees=True) if True else None
        E=Rot.from_rotvec([0,np.radians(x[0]),0])*(Rot.from_rotvec([0,0,np.radians(x[1])]) if mode==2 else Rot.identity())
        return np.degrees((E.inv()*Rot.from_matrix(D)).magnitude())
    best1=min((minimize(lambda x:res(x,1),[b,0],method='Nelder-Mead') for b in (-90,-45,0,45,90)),key=lambda r:r.fun)
    best2=min((minimize(lambda x:res(x,2),[b,g],method='Nelder-Mead') for b in (-90,0,90) for g in (-90,0,90)),key=lambda r:r.fun)
    eu=Rot.from_matrix(D).as_euler('ZYZ',degrees=True)
    print(f"{c['p']:16s} {t[e]:6.2f} total {tot:5.1f}  pitch-only best {best1.x[0]:6.1f} resid {best1.fun:5.1f}   pitch+twist {best2.x[0]:6.1f},{best2.x[1]:6.1f} resid {best2.fun:5.1f}  ZYZ {eu.round(0)}")
