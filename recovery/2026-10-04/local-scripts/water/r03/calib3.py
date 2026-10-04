import cv2, numpy as np, sys
sys.path.insert(0,'/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
W='/Users/midir/sm2-n1/water/docs/night1/water/round-02/'
im=cv2.imread(W+'harbour_high_4k.jpg').astype(np.float32)
c=im[1300:2100,0:2400]; Y=ws.luma(c); bg=cv2.GaussianBlur(Y,(0,0),24)
mx=c.max(2); mn=c.min(2); sat=(mx-mn)/np.maximum(mx,1)
for d in (12,15,18):
  for s in (0.3,0.35,0.45):
    m=((Y-bg>=d)&(sat<=s)).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(m,8)
    mxY=np.zeros(n); np.maximum.at(mxY, lab.ravel(), Y.ravel())
    keep=[(i) for i in range(1,n) if st[i,4]>=20 and mxY[i]<140]
    print(d,s,len(keep), np.median(st[keep,4]) if keep else 0, sat[(Y-bg>=d)].mean())
