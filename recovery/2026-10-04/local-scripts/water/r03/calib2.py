import cv2, numpy as np, sys
sys.path.insert(0,'/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
R='/Users/midir/spiderman-learnings/refs/streets/'; W='/Users/midir/sm2-n1/water/docs/night1/water/round-02/'
def harb(path, mode, dthr, sthr, amin=20):
    im=cv2.imread(path).astype(np.float32)
    p=ws.pack_crop(im) if mode=='pack' else cv2.resize(im,(3840,2160))
    c=p[1300:2100,0:2400]; Y=ws.luma(c)
    hp=Y-cv2.GaussianBlur(Y,(0,0),8)
    bg=cv2.GaussianBlur(Y,(0,0),24)
    mx=c.max(2); mn=c.min(2); sat=(mx-mn)/np.maximum(mx,1)
    m=((Y-bg>=dthr)&(sat<=sthr)).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(m,8)
    big=(st[1:,4]>=amin).sum()
    return c.shape, round(float(hp.std()),2), round(float((Y>=140).mean()*100),2), int(big), round(float(Y.mean()),1)
for f in (W+'harbour_high_4k.jpg', '/Users/midir/sm2-n1/water/docs/night1/water/round-01/'+'river_low_4k.jpg', W+'river_low_4k.jpg', R+'waterfront-og__og_0244.jpg'):
  for mode in ('full','pack'):
    for d,s in ((15,0.35),(20,0.3),(25,0.25),(12,0.4)):
        print(f.split('/')[-1], mode, d, s, harb(f,mode,d,s))
