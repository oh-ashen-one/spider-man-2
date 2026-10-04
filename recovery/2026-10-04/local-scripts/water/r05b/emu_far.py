import numpy as np, cv2, math, sys
sys.path.insert(0,'/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
S='/Users/midir/sm2-n1/_scratch/water'
D=np.load(S+'/r05b/D_hh.npy').astype(np.float32)
h,w=D.shape
# recompute world coords for foot
cam=np.array([0.0,4700.0]); hz=261.6
tanH=math.tan(math.radians(37.5)); tanV=tanH*h/w
f=np.array([0,-math.cos(math.radians(14)),-math.sin(math.radians(14))]); up=np.array([0,-math.sin(math.radians(14)),math.cos(math.radians(14))])
ys,xs=np.mgrid[0:h,0:w].astype(np.float32)
nx=(xs+0.5)/w*2-1; ny=1-(ys+0.5)/h*2
d=f[None,None,:]+nx[...,None]*tanH*np.array([1.0,0,0])[None,None,:]+ny[...,None]*tanV*up[None,None,:]
ok=d[...,2]<-1e-4
t=np.where(ok,hz/np.maximum(-d[...,2],1e-4),0)
X=(cam[0]+t*d[...,0]).astype(np.float32); Y=(cam[1]+t*d[...,1]).astype(np.float32)
dpx=np.stack([np.gradient(X,axis=1),np.gradient(Y,axis=1)],-1); dpy=np.stack([np.gradient(X,axis=0),np.gradient(Y,axis=0)],-1)
foot=np.maximum(np.linalg.norm(np.abs(dpx)+np.abs(dpy),axis=-1),1e-4)
dist=np.sqrt(t**2*(d[...,0]**2+d[...,1]**2+d[...,2]**2))
def smooth(a,b,x):
    z=np.clip((x-a)/(b-a),0,1); return z*z*(3-2*z)
CB=0.8; FarPx=float(sys.argv[1]) if len(sys.argv)>1 else 6.0
lapF=0.55+0.1
ce1=np.maximum(0.5+CB*(0.7+0.6*lapF)+0.4, FarPx*foot*(0.8+0.4*lapF))
cf=1-smooth(0.4*ce1,ce1,D)
wf=np.clip(cf*1.0*(0.75+0.35*lapF),0,1)
wf[~ok]=0
print('dist at row 930, col 1920:', dist[930,1920], 'foot', foot[930,1920])
# columns: how many rows with wf>0.5 per column near the edge
xs_, e = ws.island_edge('/Users/midir/sm2-n1/water/docs/night1/water/round-04/harbour_high_4k.jpg')
cnt=[]
for x,ey in zip(xs_,e):
    if not np.isfinite(ey): continue
    ey=int(ey); seg=wf[ey+2:ey+15,x]; cnt.append(((seg>0.5)).sum())
cnt=np.array(cnt); print('FarPx',FarPx,'cols with >=3 px wf>0.5 in rows +2..+14:', (cnt>=3).mean()*100, 'median', np.median(cnt))
# show column profile at several columns
for x in (1300,1600,1900,2200):
    ey=int(e[x-1250]); print(x,'edge',ey,'D',np.round(D[ey-3:ey+16,x],1).tolist()); print('   wf',np.round(wf[ey-3:ey+16,x],2).tolist())
