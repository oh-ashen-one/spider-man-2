import cv2, numpy as np, json, math, sys
S='/Users/midir/sm2-n1/_scratch/water'
cm=json.load(open(S+'/water_contact.json')); box=cm['box']
C=cv2.imread(S+'/water_contact.png', cv2.IMREAD_UNCHANGED).astype(np.float32)*32.0/255.0
H,W=C.shape
im=cv2.imread('/Users/midir/sm2-n1/water/docs/night1/water/round-05/river_low_4k.jpg'); h,w=im.shape[:2]
cam=np.array([-768.0,-128.0]); hz=6.0; yaw=math.radians(-88.282); pitch=math.radians(-3.0); hfov=90
tanH=math.tan(math.radians(hfov/2)); tanV=tanH*h/w
fh=np.array([math.cos(yaw),math.sin(yaw)])
f=np.array([fh[0]*math.cos(pitch),fh[1]*math.cos(pitch),math.sin(pitch)])
r=np.array([-math.sin(yaw),math.cos(yaw),0.0])
up=np.cross(r,f); 
if up[2]<0: up=-up
# UE: left-handed; right = (-sin yaw, cos yaw)? check: yaw=-90 -> (1,0) ok
ys,xs=np.mgrid[0:h,0:w].astype(np.float32)
nx=(xs+0.5)/w*2-1; ny=1-(ys+0.5)/h*2
d=f[None,None,:]+nx[...,None]*tanH*r[None,None,:]+ny[...,None]*tanV*up[None,None,:]
ok=d[...,2]<-1e-4
t=np.where(ok,hz/np.maximum(-d[...,2],1e-4),0)
X=cam[0]+t*d[...,0]; Y=cam[1]+t*d[...,1]
cu=(X-box[0])/box[2]; cv_=(Y-box[1])/box[3]
inb=ok&(cu>0)&(cu<1)&(cv_>0)&(cv_<1)
px=np.clip((cu*W).astype(int),0,W-1); py=np.clip((cv_*H).astype(int),0,H-1)
D=np.where(inb,C[py,px],99.0)
ov=im.copy(); ov[D<1.0]=(0,0,255); ov[(D>=1.0)&(D<4.0)]=(0,160,255)
cv2.imwrite(S+'/r05b/rl_overlay.jpg', cv2.resize(ov,(1920,1080),interpolation=cv2.INTER_AREA))
# widths: at row 1500 columns where D<1, <4
for y in (1300,1500,1800,2000):
    row=D[y]; print(y,'D<1 cols',np.where(row<1)[0][[0,-1]] if (row<1).any() else None,'D<4',np.where(row<4)[0][[0,-1]] if (row<4).any() else None)
