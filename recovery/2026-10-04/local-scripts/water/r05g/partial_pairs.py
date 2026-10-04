import sys, glob, numpy as np, cv2
sys.path.insert(0,'/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
A = np.array(ws.FOAM_EDGE_REF)
D='/Users/midir/sm2-n1/water/unreal/WebHomage/Saved/Screenshots/MacEditor/'
files=sorted(glob.glob(D+'MovieFrame*.png')); n0=359
sel=[f for f in files if int(f[-9:-4])>=n0 and (int(f[-9:-4])-n0)%15==0]
prev=None; out=[]
for f in sel:
    fr=cv2.imread(f); s=fr.shape[1]/3840.0; y0=int(ws.FOAMCROP[1]*s)
    Yd=ws.luma(fr.astype(np.float32))[y0:fr.shape[0]]
    ex=(np.polyval(A,(np.arange(y0,fr.shape[0])/s)-ws.FOAMCROP[1])+ws.FOAMCROP[0])*s
    Wd,Md=ws._band(Yd,ex,win=int(60*s))
    if prev is not None:
        u=(Md|prev).sum(); out.append((int(f[-9:-4]), round(float((Md^prev).sum()/u),3) if u else 0, int(Md.sum()), round(float((Wd>=12*s).mean()*100),1)))
    prev=Md
for o in out: print(o)
if out: print('pairs',len(out),'min',min(o[1] for o in out),'mean',round(float(np.mean([o[1] for o in out])),3))
