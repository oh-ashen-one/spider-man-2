import numpy as np, math
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
det=np.asarray(Image.open('/Users/midir/sm2-n1/_scratch/terrain/prep/lawn_detail.png')).astype(np.float64)/255
noise=np.asarray(Image.open('/Users/midir/sm2-n1/terrain/public/assets/city/tex/noise.png').convert('RGB')).astype(np.float64)/255
def sample(tex, u, v, foot_tex):
    # box-ish prefilter: gaussian sigma = footprint/2.5 in texels (wrap)
    sig=max(foot_tex/2.5,0.0)
    out=[]
    for ch in range(tex.shape[2]):
        t=gaussian_filter(tex[...,ch], sig, mode='wrap') if sig>0.3 else tex[...,ch]
        out.append(map_coordinates(t, [ (v*tex.shape[0])%tex.shape[0], (u*tex.shape[1])%tex.shape[1] ], order=1, mode='grid-wrap'))
    return np.stack(out,-1)
def rot(x,y,a): c,s=math.cos(a),math.sin(a); return x*c-y*s, x*s+y*c
def lum_mod(s_m, N=640, k=1.0, kstripe=0.15, wear=True):
    xs=(np.arange(N)+0.5)*s_m; X,Y=np.meshgrid(xs,xs)
    out={}
    foot=lambda tile: s_m/tile*det.shape[0]
    d1=sample(det, X/1.15, Y/1.15, foot(1.15))
    x2,y2=rot(X,Y,0.61); d2=sample(det, x2/4.7+0.37, y2/4.7+0.61, foot(4.7))
    x3,y3=rot(X,Y,-0.93); d3=sample(det, x3/16.3+0.71, y3/16.3+0.13, foot(16.3))
    mott=(d1[...,0]-0.5)*0.34+(d2[...,0]-0.5)*0.52+(d3[...,0]-0.5)*0.46+(d1[...,3]-0.5)*0.22
    lum=np.clip(1+k*mott,0.55,1.55)
    wr=np.clip((d3[...,1]*0.55+d2[...,1]*0.45+0.12*(d1[...,1]-0.5)-0.70)/0.14,0,1); wr=wr*wr*(3-2*wr)
    gate=np.clip((d1[...,3]+0.5*(d1[...,1]-0.5)-0.22)/0.28,0,1); gate=gate*gate*(3-2*gate); wr*=gate
    cl=np.clip((d3[...,2]*0.5+d2[...,2]*0.5-0.62)/0.18,0,1); cl=cl*cl*(3-2*cl)*(1-wr)
    sf=((X/4.4)+0.08*0.5)%1.0
    band=np.clip((sf-0.44)/0.06,0,1)*(1-np.clip((sf-0.94)/0.06,0,1))
    stripe=0.92+0.16*band  # luma approx (0.92..1.08 per channel mix)
    stripe=1+kstripe*( (0.92+ (1.08-0.92)*band) -1)
    L=lum*stripe
    L=L*(1-wr*0.8*0.0)  # luma of dirt vs grass handled below
    # luma of dirt patches: dirt (0.2,0.135,0.055)*(0.65+0.7*d1r) -> luma ~0.14*(..) vs grass luma ~0.115 : similar -> small effect; approximate +/-
    dl=(0.2*0.2126+0.135*0.7152+0.055*0.0722)*(0.65+0.7*d1[...,0])
    gl=0.115*lum*stripe*(1+0.0)
    clov=1+cl*0.75*(0.3*0.2126+0.18*0.7152+(-0.1)*0.0722)  # clover brightens ~ +20 %
    base=0.115
    lumi=(gl*clov)*(1-wr*0.8)+dl*(wr*0.8)
    return lumi/base
for s_m,name in ((0.0035,'p10 near 2cm/px?'),(0.02,'p10 mid'),(0.07,'p9-ish'),(0.15,'p4 250m')):
    L=lum_mod(s_m)
    img=140*L
    hp=img-gaussian_filter(img,6.0)
    print('%-18s px %.3f m: luma sd %.1f, hp6 SD %.2f (mean %.0f)' % (name,s_m,img.std(),hp.std(),img.mean()))
print('--- amplitude sweep')
for k,ks in ((0.5,0.12),(0.6,0.15),(0.45,0.0),(0.0,0.15),(0.0,0.0)):
    row=[]
    for s_m in (0.02,0.07,0.15):
        L=lum_mod(s_m,k=k,kstripe=ks); img=140*L; hp=img-gaussian_filter(img,6.0); row.append(round(float(hp.std()),2))
    print('k=%.2f stripe=%.2f -> hp6 SD at 0.02/0.07/0.15 m/px: %s' % (k,ks,row))
print('--- hp3 SD (t5 criterion, sigma 3) with k=0.55 stripe 0.14')
for s_m in (0.03,0.06,0.1,0.2,0.35):
    L=lum_mod(s_m,k=0.55,kstripe=0.14); img=140*L; hp=img-gaussian_filter(img,3.0)
    print('px %.2f m: hp3 SD %.2f' % (s_m, hp.std()))
