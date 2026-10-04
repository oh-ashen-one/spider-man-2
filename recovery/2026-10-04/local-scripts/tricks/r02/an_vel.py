import csv,math,numpy as np,sys
T=list(csv.DictReader(open(sys.argv[1])))
f=lambda x:float(x) if x not in ('',None,'None') else float('nan')
H=0.95
prev=None
res={}
for i,r in enumerate(T):
    if prev and prev['flip_prog'] and not r['flip_prog'] and r['mode']=='swing':
        P=np.array([f(prev[k]) for k in ('x_m','y_m','z_m')]); V=np.array([f(prev[k]) for k in ('vx','vy','vz')])
        A=np.array([f(r[k]) for k in ('anchor_x','anchor_y','anchor_z')]); V1=np.array([f(r[k]) for k in ('vx','vy','vz')])
        V2=np.array([f(T[i+6][k]) for k in ('vx','vy','vz')])
        Fl=np.array([V[0],V[1],0]); Fl/=np.linalg.norm(Fl); Rt=np.array([-Fl[1],Fl[0],0])
        Lat=(A-P)@Rt
        fmaxd=P[2]-H-f(prev['height_above_floor_m'])
        hentry=P[2]-H-fmaxd
        line=[]
        for keep in (0.25,0.0,1.0):
          for bf in (8.0,):
            bottomZ=fmaxd+bf+H
            DZ=max(A[2]-P[2],6.0); cap=34*0.94
            if P[2]-bottomZ+DZ>cap: DZ=max(6,cap-(P[2]-bottomZ))
            L=np.clip(P[2]+DZ-bottomZ,DZ+3,max(cap,DZ+3)); DH=min(math.sqrt(max(L*L-DZ*DZ,16)),30)
            piv=A if keep>=1 else P+Fl*DH+Rt*(Lat*keep)+np.array([0,0,DZ])
            RD=(piv-P)/np.linalg.norm(piv-P); tan=V-RD*(V@RD); tan/=np.linalg.norm(tan)
            e1=math.degrees(math.acos(np.clip(tan@V1/np.linalg.norm(V1),-1,1)))
            line.append(f"keep{keep}: {e1:5.1f}")
        e6=math.degrees(math.acos(np.clip(V1@V2/np.linalg.norm(V1)/np.linalg.norm(V2),-1,1)))
        print(f"{r['t']:>8s} {prev['flip_prog']:16s} lat {Lat:6.1f} "+'  '.join(line)+f"   vel turn first 0.1 s of swing {e6:5.1f}")
    prev=r
