import cv2, numpy as np, json, math, sys
S='/Users/midir/sm2-n1/_scratch/water'
cm=json.load(open(S+'/water_contact.json')); box=cm['box']
C=cv2.imread(S+'/water_contact.png', cv2.IMREAD_UNCHANGED).astype(np.float32)*32.0/255.0
H,W=C.shape; print('contact', C.shape, box)
im=cv2.imread('/Users/midir/sm2-n1/water/docs/night1/water/round-05/harbour_high_4k.jpg')
h,w=im.shape[:2]
cam=np.array([0.0,4700.0]); hz=261.6
yaw=-90; pitch=-14; hfov=75
tanH=math.tan(math.radians(hfov/2)); tanV=tanH*h/w
f=np.array([0,-math.cos(math.radians(14)),-math.sin(math.radians(14))])
right=np.array([1.0,0,0]); up=np.array([0,-math.sin(math.radians(14)),math.cos(math.radians(14))])
ys,xs=np.mgrid[0:h,0:w].astype(np.float32)
nx=(xs+0.5)/w*2-1; ny=1-(ys+0.5)/h*2
d=f[None,None,:]+nx[...,None]*tanH*right[None,None,:]+ny[...,None]*tanV*up[None,None,:]
ok=d[...,2]<-1e-4
t=np.where(ok, hz/np.maximum(-d[...,2],1e-4), 0)
X=cam[0]+t*d[...,0]; Y=cam[1]+t*d[...,1]
cu=(X-box[0])/box[2]; cv_=(Y-box[1])/box[3]
inb=ok&(cu>0)&(cu<1)&(cv_>0)&(cv_<1)
px=np.clip((cu*W).astype(int),0,W-1); py=np.clip((cv_*H).astype(int),0,H-1)
D=np.where(inb, C[py,px], 99.0)
np.save(S+'/r05b/D_hh.npy', D.astype(np.float16))
# overlay: contact distance < 3 m red, < 10 m orange
ov=im.copy()
m1=D<2.0; m2=(D>=2.0)&(D<8.0)
ov[m1]=(0,0,255); ov[m2]=(0,160,255)
cv2.imwrite(S+'/r05b/hh_overlay.jpg', cv2.resize(ov,(1920,1080),interpolation=cv2.INTER_AREA))
cv2.imwrite(S+'/r05b/hh_overlay_crop.jpg', ov[700:1300,1100:2700])
# footprint
print('rows with contact<2m:', np.where(m1.any(1))[0][[0,-1]] if m1.any() else None)
