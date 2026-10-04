import csv,math,numpy as np
T=list(csv.DictReader(open('/Users/midir/sm2-n1/tricks/docs/night1/tricks/round-01/t60_trick_reel_telemetry.csv')))
f=lambda x:float(x) if x not in ('',None,'None') else float('nan')
H=0.95
prev=None
for i,r in enumerate(T):
    if prev and prev['flip_prog'] and not r['flip_prog'] and r['mode']=='swing':
        P=np.array([f(prev[k]) for k in ('x_m','y_m','z_m')]); V=np.array([f(prev[k]) for k in ('vx','vy','vz')])
        A=np.array([f(r[k]) for k in ('anchor_x','anchor_y','anchor_z')]); V1=np.array([f(r[k]) for k in ('vx','vy','vz')])
        Fl=np.array([V[0],V[1],0]); Fl/=np.linalg.norm(Fl); Rt=np.array([-Fl[1],Fl[0],0])
        Lat=(A-P)@Rt
        fmaxd=P[2]-H-f(prev['height_above_floor_m'])
        hentry=P[2]-H-fmaxd
        best=None
        for drop in (10.2+0.75,17.5+0.75):
            bottomfeet=max(5,hentry-drop); bottomZ=fmaxd+bottomfeet+H
            DZ=max(A[2]-P[2],6.0); cap=34*(1-0.06)
            if P[2]-bottomZ+DZ>cap: DZ=max(6,cap-(P[2]-bottomZ))
            L=np.clip(P[2]+DZ-bottomZ,DZ+3,max(cap,DZ+3)); DH=min(math.sqrt(max(L*L-DZ*DZ,16)),30)
            piv=P+Fl*DH+Rt*(Lat*0.25)+np.array([0,0,DZ])
            RD=(piv-P)/np.linalg.norm(piv-P); tan=V-RD*(V@RD); tan/=np.linalg.norm(tan)
            err=math.degrees(math.acos(np.clip(tan@V1/np.linalg.norm(V1),-1,1)))
            yaw=lambda v:math.degrees(math.atan2(v[1],v[0]))
            print(f"  {r['t']} {prev['flip_prog']:16s} drop {drop:5.2f} pred-vs-actual vel dir err {err:5.1f}  yaw pred {yaw(tan):6.1f} act {yaw(V1):6.1f} pre {yaw(V):6.1f}  hentry {hentry:5.1f}")
    prev=r
