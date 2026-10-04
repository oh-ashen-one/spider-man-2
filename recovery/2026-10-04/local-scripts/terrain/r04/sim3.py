import numpy as np, math
exec(open('sim_detail.py').read().split("for s_m,name in")[0])
def lum_aniso(sx, sy, w1, w2, w3, wa, N=512):
    xs=(np.arange(N)+0.5)*sx; ys=(np.arange(N)+0.5)*sy; X,Y=np.meshgrid(xs,ys)
    fx=lambda tile: sx/tile*det.shape[0]; fy=lambda tile: sy/tile*det.shape[0]
    foot=lambda tile: max(fx(tile),fy(tile))  # isotropic prefilter at the larger footprint (approx)
    d1=sample(det, X/1.15, Y/1.15, foot(1.15))
    x2,y2=rot(X,Y,0.61); d2=sample(det, x2/4.7+0.37, y2/4.7+0.61, foot(4.7))
    x3,y3=rot(X,Y,-0.93); d3=sample(det, x3/16.3+0.71, y3/16.3+0.13, foot(16.3))
    mott=(d1[...,0]-0.5)*w1+(d2[...,0]-0.5)*w2+(d3[...,0]-0.5)*w3+(d1[...,3]-0.5)*wa
    return 100*np.clip(1+mott,0.55,1.55)
sets={'hold2 G':(0.36,0.62,0.26,0.22),'hold3 M':(0.54,0.95,0.26,0.30),'P d3 .45':(0.54,0.95,0.45,0.30),'Q d2 1.2 d3 .5':(0.54,1.2,0.5,0.30),'R d3 .6':(0.54,0.95,0.6,0.30),'S d2 1.1 d3 .7':(0.54,1.1,0.7,0.30)}
for name,w in sets.items():
    row=[]
    for sx,sy in ((0.07,0.14),(0.09,0.18),(0.05,0.10)):
        img=lum_aniso(sx,sy,*w); hp=img-gaussian_filter(img,6.0); row.append(round(float(hp.std()),1))
    print(name,w,'hp6 (aniso .07x.14, .09x.18, .05x.10):',row)
