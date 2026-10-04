import sys, numpy as np, glob, os, colorsys
from PIL import Image
def load(p):
    im=Image.open(p).convert('RGB')
    if im.width!=1920: im=im.resize((1920,int(round(im.height*1920/im.width))),Image.BOX if im.width%1920==0 else Image.LANCZOS)
    return np.asarray(im,dtype=np.float32)
def kf(a):
    Y=.2126*a[...,0]+.7152*a[...,1]+.0722*a[...,2]
    mx=a.max(axis=2); mn=a.min(axis=2)
    S=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
    p5=np.percentile(Y,5); p95=np.percentile(Y,95)
    return dict(mean=Y.mean(),p5=p5,p95=p95,ratio=p95/max(p5,1e-3),sat=S.mean(), sat_hsv_all=S.mean())
if __name__=='__main__':
    for f in sys.argv[1:]:
        d=kf(load(f)); print('%-40s mean %.1f p5 %.1f p95 %.1f p95/p5 %.1f sat %.3f'%(os.path.basename(f),d['mean'],d['p5'],d['p95'],d['ratio'],d['sat']))
