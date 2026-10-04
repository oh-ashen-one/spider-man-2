import json, math, numpy as np, sys
E='/Users/midir/sm2-n1/_scratch/city/export/midtown3x3/'
cars=json.load(open(E+'streetcars.json')); veh=json.load(open(E+'vehicles.json'))
def cam(pos, tgt, fov, W=1920, H=1080):
    p=np.array(pos,float); t=np.array(tgt,float); f=t-p; f/=np.linalg.norm(f)
    up=np.array([0,1,0.]); r=np.cross(f,up); r/=np.linalg.norm(r); u=np.cross(r,f)   # browser (x east,y up,z south): right-handed; right = f x up
    fx=(W/2)/math.tan(math.radians(fov)/2)
    def proj(q):
        d=np.array(q,float)-p; z=d@f
        if z<0.5: return None
        return (W/2+fx*(d@r)/z, H/2-fx*(d@u)/z, z)
    return proj
def boxes(proj):
    out=[]
    for k,items in cars.items():
        m=veh[k]
        for it in items:
            ry=it['ry']; nx,nz=math.cos(ry),-math.sin(ry)  # nose dir
            # model coords: x fwd, z lateral (browser z of the model maps to ... side = (nz, nx)?) : rotate about y by ry: local (x,z) -> world (x cos + z sin, -x sin + z cos)
            pts=[]
            for lx in (m['x0'],m['x1']):
                for lz in (-m['wid']/2,m['wid']/2):
                    for ly in (0,m['hh']):
                        wx=it['x']+lx*math.cos(ry)+lz*math.sin(ry); wz=it['z']-lx*math.sin(ry)+lz*math.cos(ry)
                        q=proj((wx,ly+it['y'],wz))
                        if q: pts.append(q)
            if len(pts)<8: continue
            P=np.array(pts); out.append((k,P[:,0].min(),P[:,1].min(),P[:,0].max(),P[:,1].max(),P[:,2].mean()))
    return out
if __name__=='__main__':
    shots=json.load(open('unreal/WebHomage/Scripts/city_shots.json'))
    for sid in ('S1_avenue_street','S2_avenue_swing','S6_timessq_street'):
        s=[x for x in shots if x['id']==sid][0]
        pr=cam(s['pos'],s['target'],s.get('fov',70))
        B=[b for b in boxes(pr) if b[3]>0 and b[2]<1080 and b[1]<1920 and b[4]>0]
        vis=[b for b in B if (b[3]-b[1])>=18 and (b[4]-b[2])>=14]
        print(sid,'cars projecting into frame',len(B),'with size >=18x14 px:',len(vis))
        for b in sorted(vis,key=lambda b:b[5])[:30]: print('   %-12s x %4d-%4d y %4d-%4d  w %3d h %3d  dist %.0f'%(b[0],b[1],b[3],b[2],b[4],b[3]-b[1],b[4]-b[2],b[5]))
