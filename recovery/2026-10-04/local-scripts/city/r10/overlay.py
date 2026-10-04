import sys, json, numpy as np, cv2
sys.path.insert(0,'/Users/midir/sm2-n1/city/tools/export'); sys.path.insert(0,'.')
from glbio import read_glb
from proj import POS, f, r, u, fp, W, H
E='/Users/midir/sm2-n1/_scratch/city/export/midtown3x3/'
fs=json.load(open(E+'farsky.json'))
img=cv2.imread(sys.argv[1] if len(sys.argv)>1 else '/Users/midir/sm2-n1/city/docs/night1/city/round-09/S4_perch_skyline_1920x1080.jpg')
ov=img.copy()
def P2(p):
    d=p-POS; zc=d@f; ok=zc>1
    px=W/2+fp*(d@r)/zc; py=H/2-fp*(d@u)/zc
    return px,py,zc,ok
rng=np.random.default_rng(1)
def splat_tris(Pw,I,col,dens=1.0):
    tri=Pw[I]; a=tri[:,1]-tri[:,0]; b=tri[:,2]-tri[:,0]
    area=0.5*np.linalg.norm(np.cross(a,b),axis=1); D=np.linalg.norm(tri.mean(1)-POS,axis=1)
    n=np.clip(np.ceil(area/((D/fp)**2)*2*dens),1,3000).astype(int)
    ti=np.repeat(np.arange(len(tri)),n); r1=rng.random(len(ti)); r2=rng.random(len(ti)); fl=r1+r2>1; r1[fl]=1-r1[fl]; r2[fl]=1-r2[fl]
    pts=tri[ti,0]+a[ti]*r1[:,None]+b[ti]*r2[:,None]
    px,py,zc,ok=P2(pts); m=ok&(px>=0)&(px<W)&(py>=0)&(py<H)
    ov[py[m].astype(int),px[m].astype(int)]=col
for fl in fs['files']:
    g=read_glb(E+fl['file']); Pw=g['attrs']['POSITION'].copy(); Pw[:,0]+=fl['center'][0]; Pw[:,2]+=fl['center'][2]
    col={'towers':(0,0,255),'bluff':(0,160,0),'shore':(255,0,0)}[fl['mat']]
    splat_tris(Pw,g['index'].reshape(-1,3),col)
# hinterland boxes
for h in fs['hinterland']:
    x,y,z,sx,sy,sz=h[:6]
    corners=[]
    for dx in (-.5,.5):
        for dz in (-.5,.5):
            for dy in (0,1): corners.append([x+dx*sx,y+dy*sy,z+dz*sz])
    c=np.array(corners); px,py,zc,ok=P2(c)
    if ok.all():
        x0,x1=px.min(),px.max(); y0,y1=py.min(),py.max()
        cv2.rectangle(ov,(int(x0),int(y0)),(int(max(x1,x0+1)),int(y1)),(255,0,255),-1)
for c in fs['clumps']:
    p=np.array([[c[0],c[1]+2,c[2]]]); px,py,zc,ok=P2(p)
    if ok[0] and 0<=px[0]<W and 0<=py[0]<H: cv2.circle(ov,(int(px[0]),int(py[0])),1,(0,255,255),-1)
out=cv2.addWeighted(img,0.45,ov,0.55,0)
cv2.imwrite('overlay.png',out[100:420,0:1500])
