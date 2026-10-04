import numpy as np, json, cv2, math, sys
J=json.load(open('/Users/midir/sm2-n1/_scratch/water/water_contact.json')); x0,z0,w,h=J['box']; im=cv2.imread('/Users/midir/sm2-n1/_scratch/water/water_contact.png',cv2.IMREAD_UNCHANGED).astype(float); H,W=im.shape
def cdm(x,z):
    u=(x-x0)/w*W-0.5; v=(z-z0)/h*H-0.5; i,j=int(np.floor(v)),int(np.floor(u)); fu,fv=u-j,v-i
    return (im[i,j]*(1-fu)*(1-fv)+im[i,j+1]*fu*(1-fv)+im[i+1,j]*(1-fu)*fv+im[i+1,j+1]*fu*fv)*32/255
C=np.array([-768.0,-128.0]); hgt=6.0; yaw=math.radians(-88.282); pit=math.radians(-3)
F=np.array([math.cos(pit)*math.cos(yaw), math.cos(pit)*math.sin(yaw), math.sin(pit)])
R=np.array([-math.sin(yaw), math.cos(yaw), 0.0]); U=np.cross(F,R)
if U[2]<0: U=-U
tx=1.0; ty=tx*2160/3840
def ray(px,py):
    a=(px/3840*2-1)*tx; b=(1-py/2160*2)*ty; d=F+a*R+b*U; t=-hgt/d[2]; return C+t*d[:2], t
for cy in (100,300,500,700,900):
    py=1250+cy; ex=1500+(-0.0536*cy+464.4)
    out=[]
    for dx in (-60,-30,-12,-3):
        p,t=ray(ex+dx,py); out.append('%+d: x%.2f z%.1f cdm%.2f'%(dx,p[0],p[1],cdm(*p)))
    print(cy, out)
