exec(open('/Users/midir/sm2-n1/_scratch/critic-C-r01-work/an.py').read().split('res=[]')[0])
from scipy.spatial.transform import Rotation as Rot
from scipy.optimize import minimize
import sys
def Ch(j): return Rot.from_matrix(frame(j).T)
def mk(up,fw):
    up=up/np.linalg.norm(up); fw=fw-up*np.dot(fw,up); fw/=np.linalg.norm(fw)
    return Rot.from_matrix(np.stack([fw,np.cross(up,fw),up]).T)
def V3(r,a): return np.array([f(r[a+'_x']) if a+'_x' in r else f(r[a[0]+'x']) ,0,0])
mode=sys.argv[1] if len(sys.argv)>1 else 'pt'
dtf=1/60
allok=0
for c in I:
    e=c['i'][-1]
    if e+31>=len(T) or T[e+1]['mode']!='swing': continue
    r=T[e]; vpre=np.array([f(r['vx']),f(r['vy']),f(r['vz'])])
    B=mk(np.array([0,0,1.]),np.array([vpre[0],vpre[1],0]))
    Fr01=Rot.from_rotvec([0,np.radians(f(r['flip_pitch_deg'])-c['ft'][-1]*0 - (360*round(f(r['flip_pitch_deg'])/360))),0])
    # W at catch
    n=T[e+1]; P=np.array([f(n['x_m']),f(n['y_m']),f(n['z_m'])]); A=np.array([f(n['anchor_x']),f(n['anchor_y']),f(n['anchor_z'])])
    def Wk(k):
        n=T[k]; P=np.array([f(n['x_m']),f(n['y_m']),f(n['z_m'])]); A=np.array([f(n['anchor_x']),f(n['anchor_y']),f(n['anchor_z'])])
        U=(A-P)/np.linalg.norm(A-P)+np.array([0,0,.12]); return mk(U,np.array([f(n['vx']),f(n['vy']),f(n['vz'])]))
    D=(B.inv()*Wk(e+1))
    if mode=='none': E=Rot.identity()
    elif mode=='full': E=D
    else:
        def res(x):
            E=Rot.from_rotvec([0,np.radians(x[0]),0])*(Rot.from_rotvec([0,0,np.radians(x[1])]) if mode=='pt' else Rot.identity())
            return np.degrees((E.inv()*D).magnitude())
        b=min((minimize(res,[p,g],method='Nelder-Mead') for p in (-60,0,60) for g in (-60,0,60)),key=lambda q:q.fun)
        E=Rot.from_rotvec([0,np.radians(b.x[0]),0])*(Rot.from_rotvec([0,0,np.radians(b.x[1])]) if mode=='pt' else Rot.identity())
    # simulate: pre-catch ramp of E over 0.3 s (smoothstep) on top of the r01 chest; post-catch Body slerp to W rate 14 and E spring
    chest={}
    Bt=B
    for k in range(e-24,e+31):
        if k<=e:
            u=np.clip(1-(t[e]-t[k])/0.3,0,1); s=u*u*(3-2*u)
            Ek=Rot.from_rotvec(E.as_rotvec()*s)
            chest[k]=B*Ek*B.inv()*Ch(J[k])
        else:
            a=1-np.exp(-14*dtf*(k-e)); 
            # body(t): slerp from B toward W(k) cumulative (approx)
            Bt=Rot.from_rotvec(((Bt.inv()*Wk(k)).as_rotvec())*(1-np.exp(-14*dtf)))  if False else Bt
            sE=np.exp(-dtf*(k-e)/0.07)
            # r01 chest(t)=Body P ; new = Body E^s Fr01^-s Body^-1 chest_r01 ; approximate Body(t) by spring from B to W
            Bk=B*Rot.from_rotvec((B.inv()*Wk(k)).as_rotvec()*a)
            chest[k]=Bk*Rot.from_rotvec(E.as_rotvec()*sE)*Rot.from_rotvec(-Fr01.as_rotvec()*sE)*Bk.inv()*Ch(J[k])
    ws=[]
    for k in range(e-3,e+25):
        ws.append(np.degrees((chest[k].inv()*chest[k+6]).magnitude())/(t[k+6]-t[k]))
    ok=max(ws)<=250; allok+=ok
    print(f"{c['p']:16s} {t[e]:6.2f} D {np.degrees(D.magnitude()):5.1f} resid {np.degrees((E.inv()*D).magnitude()):5.1f} max window {max(ws):5.0f} {'ok' if ok else ''}")
    if len(sys.argv)>2 and abs(t[e]-float(sys.argv[2]))<0.05:
        for i,k in enumerate(range(e-3,e+25)):
            wr=np.degrees((Wk(max(k,e+1)).inv()*Wk(max(k+6,e+1))).magnitude())/0.1
            print(f"   win {t[k]:6.2f} chest {ws[i]:5.0f}  W-rate {wr:5.0f}  r01chest {np.degrees((Ch(J[k]).inv()*Ch(J[k+6])).magnitude())/0.1:5.0f} anim {T[k+1]['anim_node']} {T[k+1]['anim_clip']}")
print('ok',allok)
