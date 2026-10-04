import cv2, numpy as np, sys
sys.path.insert(0,'/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
R='/Users/midir/spiderman-learnings/refs/streets/'; W='/Users/midir/sm2-n1/water/docs/night1/water/round-02/'
def sparkle(path, thr=200, frac=0.02, mode='pack', horizon=None):
    im=cv2.imread(path).astype(np.float32)
    p=ws.pack_crop(im) if mode=='pack' else cv2.resize(im,(3840,2160))
    Y=ws.luma(p); H,Wd=Y.shape
    # horizon: given row fraction
    h0=int(H*horizon)
    wy=Y[h0:]
    col=(wy>=thr).mean(0)
    return round(float((col>=frac).mean()*100),1)
for f,hz in ((W+'river_sun_4k.jpg',None),(R+'waterfront-perch-trailer__eny_0149.jpg',None)):
    for hz in (0.42,0.45,0.5,0.55):
        print(f.split('/')[-1], hz, sparkle(f,horizon=hz), sparkle(f,horizon=hz,mode='full'))
