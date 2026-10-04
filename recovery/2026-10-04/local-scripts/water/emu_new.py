import sys, math, numpy as np, cv2
sys.path.insert(0,'/Users/midir/sm2-n1/water/unreal/WebHomage/Scripts')
import build_water as bw
tex=cv2.imread('water_slope.png',-1)[..., [2,1,0,3]].astype(np.float32)/255.0  # RGBA
N=tex.shape[0]
def samp(ch, u, v):
    x=(u*N)%N; y=(v*N)%N; x0=np.floor(x).astype(int); y0=np.floor(y).astype(int); fx=x-x0; fy=y-y0
    x1=(x0+1)%N; y1=(y0+1)%N; T=tex[...,ch]
    return T[y0,x0]*(1-fx)*(1-fy)+T[y0,x1]*fx*(1-fy)+T[y1,x0]*(1-fx)*fy+T[y1,x1]*fx*fy
def field(X,Y,t, layers=bw.LAYERS):
    sl=np.zeros(X.shape+(2,))
    for i,(sc,aA,aB,amp) in enumerate(layers):
        lc=sc/8.5; kc=2*math.pi/lc; spd=math.sqrt(9.81/kc+7.28e-5*kc)
        for (ang,ch,s2,off,vk) in ((aA,(0,1),sc,(0,0),1.0),(aB,(2,3),sc*0.87,(0.37,0.61*(i+1)),1.07)):
            th=math.radians(bw.WIND_DEG+ang); c,s=math.cos(th),math.sin(th)
            qx=(c*X+s*Y)/s2 - spd*vk*t/s2 + off[0]; qy=(-s*X+c*Y)/s2 + off[1]
            gx=(samp(ch[0],qx,qy)-0.5)*6; gy=(samp(ch[1],qx,qy)-0.5)*6
            sl[...,0]+=(c*gx-s*gy)*amp*0.7071; sl[...,1]+=(s*gx+c*gy)*amp*0.7071
    return sl
if __name__=='__main__':
    n=1600; L=float(sys.argv[1]) if len(sys.argv)>1 else 40
    xs=np.linspace(-L/2,L/2,n); X,Y=np.meshgrid(xs-768,xs-128)
    sl=field(X,Y,11.0)
    print('slope sd', sl.std(axis=(0,1)))
    v=sl[...,0]*0.7+sl[...,1]*0.7
    im=np.clip(128+v/(3*v.std())*127,0,255).astype(np.uint8)
    cv2.imwrite('emu_new.png', cv2.resize(im,(1000,1000),interpolation=cv2.INTER_AREA))
    a=v-v.mean()
    for d in (10,40,80,160):
        print('ac shift %d px (%.2f m): %.3f'%(d, d*L/n, (a[:, :-d]*a[:, d:]).mean()/a.var()))
