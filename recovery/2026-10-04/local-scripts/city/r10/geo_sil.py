import sys, json, numpy as np
sys.path.insert(0,'/Users/midir/sm2-n1/city/tools/export'); sys.path.insert(0,'.')
from glbio import read_glb
from proj import POS, f, r, u, fp, W, H
E='/Users/midir/sm2-n1/_scratch/city/export/midtown3x3/'
man=json.load(open(E+'manifest.json')); fs=json.load(open(E+'farsky.json'))
top_old=np.full(W,1e9); top_new=np.full(W,1e9); rng=np.random.default_rng(2)
def rec(Pw,I,dest):
    tri=Pw[I]; a=tri[:,1]-tri[:,0]; b=tri[:,2]-tri[:,0]
    area=0.5*np.linalg.norm(np.cross(a,b),axis=1); D=np.linalg.norm(tri.mean(1)-POS,axis=1)
    n=np.clip(np.ceil(area/((D/fp)**2)*2),1,2000).astype(int)
    ti=np.repeat(np.arange(len(tri)),n); r1=rng.random(len(ti)); r2=rng.random(len(ti)); fl=r1+r2>1; r1[fl]=1-r1[fl]; r2[fl]=1-r2[fl]
    pts=tri[ti,0]+a[ti]*r1[:,None]+b[ti]*r2[:,None]
    d=pts-POS; zc=d@f; ok=zc>1; d=d[ok]; zc=zc[ok]
    px=(W/2+fp*(d@r)/zc).astype(int); py=H/2-fp*(d@u)/zc
    m=(px>=0)&(px<W)&(py>0)
    for d_ in dest: np.minimum.at(d_, px[m], py[m])
def boxes(items,dest):
    P=[];I=[];o=0
    for x,y,z,sx,sy,sz in [it[:6] for it in items]:
        x0,x1=x-sx/2,x+sx/2; z0,z1=z-sz/2,z+sz/2; y0,y1=y,y+sy
        v=np.array([[x0,y0,z0],[x1,y0,z0],[x1,y0,z1],[x0,y0,z1],[x0,y1,z0],[x1,y1,z0],[x1,y1,z1],[x0,y1,z1]])
        tri=[(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7),(4,5,6),(4,6,7)]
        P.append(v); I.append(np.array(tri)+o); o+=8
    rec(np.concatenate(P),np.concatenate(I),dest)
H_=json.load(open(E+'hinterland.json'))['items']
boxes(H_,[top_old,top_new]); boxes(fs['hinterland'],[top_new])
for rcd in man['meshes']:
    if rcd['name']=='farCityMass':
        g=read_glb(E+rcd['file']); P=g['attrs']['POSITION'].copy(); P[:,0]+=rcd['center'][0]; P[:,2]+=rcd['center'][2]
        rec(P,g['index'].reshape(-1,3),[top_old,top_new])
for fl in fs['files']:
    if fl['mat']=='towers':
        g=read_glb(E+fl['file']); P=g['attrs']['POSITION'].copy(); P[:,0]+=fl['center'][0]; P[:,2]+=fl['center'][2]
        rec(P,g['index'].reshape(-1,3),[top_new])
for n,t in (('old',top_old),('new',top_new)):
    t=t[:1300]; print(n,'geometric top std %.1f mean %.1f p5 %.1f p95 %.1f'%(np.std(t),np.mean(t),np.percentile(t,5),np.percentile(t,95)))
t=top_new[:1300]
print(' '.join('%d'%np.mean(t[i:i+50]) for i in range(0,1300,50)))
print('share of columns with top < 150:', np.mean(t<150), '< 140:', np.mean(t<140), ' >=160:', np.mean(t>=160))
