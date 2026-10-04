import csv,math,numpy as np
T=list(csv.DictReader(open('/Users/midir/sm2-n1/tricks/docs/night1/tricks/round-01/t60_trick_reel_telemetry.csv')))
f=lambda x:float(x) if x not in ('',None,'None') else float('nan')
I=[];cur=None
for i,r in enumerate(T):
    p=r['flip_prog'];ft=f(r['flip_t']) if r['flip_t'] else -1
    if p and ft>=0:
        if cur and cur['p']==p and ft>=cur['ft'][-1]-1e-6: cur['i'].append(i);cur['ft'].append(ft)
        else: cur=dict(p=p,i=[i],ft=[ft]);I.append(cur)
    else: cur=None
for c in I:
    e=c['i'][-1]; n=T[e+1]
    P=np.array([f(n['x_m']),f(n['y_m']),f(n['z_m'])]); A=np.array([f(n['anchor_x']),f(n['anchor_y']),f(n['anchor_z'])])
    V=np.array([f(T[e]['vx']),f(T[e]['vy']),f(T[e]['vz'])])
    h=V[:2]/np.linalg.norm(V[:2]); fwd=np.array([h[0],h[1],0]); lat=np.array([-h[1],h[0],0])
    AD=(A-P)/np.linalg.norm(A-P); U=AD+np.array([0,0,0.12]); U/=np.linalg.norm(U)
    pf=math.degrees(math.atan2(U@fwd,U[2])); pl=math.degrees(math.atan2(U@lat,U[2]))
    # also at trick end-0.3s: predicted anchor relative to position then
    k=e-18; P0=np.array([f(T[k]['x_m']),f(T[k]['y_m']),f(T[k]['z_m'])])
    print(f"{c['p']:16s} end {f(T[e]['t']):6.2f} ft {c['ft'][-1]:.2f} next {n['mode']}/{n['sub']} rope fwd {pf:5.1f} lat {pl:5.1f} dist {np.linalg.norm(A-P):5.1f} ahead {(A-P)@fwd:5.1f} up {(A-P)[2]:5.1f} vz {V[2]:5.1f} hs {np.linalg.norm(V[:2]):4.1f}")
print('---- lateral residual')
for c in I:
    e=c['i'][-1]; n=T[e+1]
    if n['mode']!='swing': continue
    P=np.array([f(n['x_m']),f(n['y_m']),f(n['z_m'])]); A=np.array([f(n['anchor_x']),f(n['anchor_y']),f(n['anchor_z'])])
    V=np.array([f(T[e]["vx"]),f(T[e]["vy"]),f(T[e]["vz"])]); V1=np.array([f(n["vx"]),f(n["vy"]),f(n["vz"])])
    h=V[:2]/np.linalg.norm(V[:2]); fwd=np.array([h[0],h[1],0]); lat=np.array([-h[1],h[0],0])
    AD=(A-P)/np.linalg.norm(A-P); U=AD+np.array([0,0,0.12]); U/=np.linalg.norm(U)
    print(f"{c['p']:16s} {f(T[e]['t']):6.2f} tilt {math.degrees(math.acos(U[2])):5.1f} sag-pitch {math.degrees(math.atan2(U@fwd,U[2])):5.1f} roll-out {math.degrees(math.asin(U@lat)):5.1f} velturn {math.degrees(math.acos(np.dot(V[:2],V1[:2])/np.linalg.norm(V[:2])/np.linalg.norm(V1[:2]))):5.1f}")
