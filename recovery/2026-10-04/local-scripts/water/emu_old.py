import sys, math, numpy as np, cv2
sys.path.insert(0,'/Users/midir/sm2-n1/water/unreal/WebHomage/Scripts')
import build_water as bw
W=bw.waves(); C=bw.caps()
# top-down 80x80 m around the dolly mid point (UE m), 2 cm px
cx,cy=-768.0,-128.0-10
n=2000; xs=np.linspace(cx-40,cx+40,n); X,Y=np.meshgrid(xs, np.linspace(cy-40,cy+40,n))
t=11.0
sl=np.zeros((n,n,2)); 
for w in W:
    ph=w['k']*(w['dx']*X+w['dy']*Y)-w['w']*t+w['ph']; s,c=np.sin(ph),np.cos(ph)
    sl[...,0]+=w['dx']*w['k']*w['A']*c/np.maximum(1-w['Q']*w['k']*w['A']*s,0.35); sl[...,1]+=w['dy']*w['k']*w['A']*c/np.maximum(1-w['Q']*w['k']*w['A']*s,0.35)
big=sl.copy()
for w in C:
    ph=w['k']*(w['dx']*X+w['dy']*Y)-w['w']*t+w['ph']; c=np.cos(ph)
    sl[...,0]+=w['dx']*w['k']*w['A']*c; sl[...,1]+=w['dy']*w['k']*w['A']*c
for nm,f in (('big',big),('all',sl)):
    v=f[...,0]*0.7+f[...,1]*0.7
    print(nm,'slope sd',f.std(axis=(0,1)))
    im=np.clip(128+v/ (3*v.std())*127,0,255).astype(np.uint8)
    cv2.imwrite('emu_%s.png'%nm, cv2.resize(im,(1000,1000),interpolation=cv2.INTER_AREA))
