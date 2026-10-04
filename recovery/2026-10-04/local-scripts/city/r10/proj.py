import numpy as np, math
# browser coords: x east, y up, z south. S4 camera
POS=np.array([182,306,-92.]); TGT=np.array([-120,150,-470.]); FOV=75.0; W,H=1920,1080
f=TGT-POS; f/=np.linalg.norm(f)
up0=np.array([0,1,0.])
r=np.cross(f,up0); r/=np.linalg.norm(r)   # right-handed browser frame: x east, y up, z south -> right = f x up
u=np.cross(r,f)
fp=(W/2)/math.tan(math.radians(FOV/2))
def proj(p):
    d=np.array(p,float)-POS
    zc=d@f
    if zc<=0: return None
    return (W/2 + fp*(d@r)/zc, H/2 - fp*(d@u)/zc, zc)
if __name__=='__main__':
    import sys
    for name,p in [('cliff top z-600',(-1700,58,-600)),('cliff top x-1945 z-1300',(-1945,58,-1300)),('cliff base',(-1945,1.2,-1300)),('cliff top z-2300',(-1905,58,-2300)),('cliff z-3400',(-1885,58,-3400)),('cliff z-5200',(-1880,58,-5200)),
       ('shore z-1000',(-1650,1.2,-1000)), ('shore z-2000',(-1610,1.2,-2000)),('horizon plateau',(-2500,58,-1300)),('nj shore -5000',(-1480,1.2,-5000)),('queens',(1100,1.2,-1000)),('queens far',(1125,1.2,-800))]:
        print(name, proj(p))
