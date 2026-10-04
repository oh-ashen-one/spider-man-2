import sys, json, numpy as np, glob, os
sys.path.insert(0,'/Users/midir/sm2-n1/city/tools/export')
from glbio import read_glb
from proj import POS, f, r, u, fp, W, H
E='/Users/midir/sm2-n1/_scratch/city/export/midtown3x3/'
man=json.load(open(E+'manifest.json'))
S=2  # half-res
w,h=W//S,H//S
zb=np.full((h,w),1e18); idb=np.zeros((h,w),np.int16)
layers={}
def lid(n):
    if n not in layers: layers[n]=len(layers)+1
    return layers[n]
rng=np.random.default_rng(1)
def splat(P, I, name, cen=(0,0,0)):
    # P world-space (n,3) browser coords; I tri indices (m,3)
    tri=P[I]  # m,3,3
    a=tri[:,1]-tri[:,0]; b=tri[:,2]-tri[:,0]
    area=0.5*np.linalg.norm(np.cross(a,b),axis=1)
    cen_t=tri.mean(1); D=np.linalg.norm(cen_t-POS,axis=1)
    foot=D/(fp/S)       # metres per (half-res) pixel
    n=np.ceil(area/(foot**2)*2.0).astype(np.int64); n=np.clip(n,0,4000)
    n[(area>0)&(n<1)]=1
    # only triangles in front of camera
    tot=n.sum()
    if tot==0: return
    ti=np.repeat(np.arange(len(tri)),n)
    r1=rng.random(tot); r2=rng.random(tot); fl=r1+r2>1; r1[fl]=1-r1[fl]; r2[fl]=1-r2[fl]
    pts=tri[ti,0]+a[ti]*r1[:,None]+b[ti]*r2[:,None]
    d=pts-POS; zc=d@f
    ok=zc>1
    d=d[ok]; zc=zc[ok]
    px=(W/2+fp*(d@r)/zc)/S; py=(H/2-fp*(d@u)/zc)/S
    m=(px>=0)&(px<w)&(py>=0)&(py<h)
    px=px[m].astype(int); py=py[m].astype(int); zc=zc[m]
    L=lid(name)
    order=np.argsort(-zc)  # far first, near overwrites
    flat=py[order]*w+px[order]
    # z-buffer via lexsort: pick min z per pixel
    zf=zb.reshape(-1); idf=idb.reshape(-1)
    zz=zc[order]
    # process: for each pixel keep nearest -> since sorted far->near, last write wins in numpy fancy assign
    cur=zf[flat]
    better=zz<cur
    flat=flat[better]; zz=zz[better]
    zf[flat]=zz; idf[flat]=L   # last occurrence wins (nearest)
def tri_from_glb(path,center):
    g=read_glb(path); P=g['attrs']['POSITION']; I=g['index'].reshape(-1,3)
    # glb: tile-local; UE glTF: world = local + center (x,z) ; local y is up
    Pw=P.copy(); Pw[:,0]+=center[0]; Pw[:,2]+=center[2]
    return Pw,I
names=set(sys.argv[1:]) if len(sys.argv)>1 else None
for rec in man['meshes']:
    n=rec['name']
    if rec['kind'] not in ('far','land'): continue
    key=n if not n.startswith('coast_') else 'coast'
    if key.startswith('bridge'): key='bridge'
    if key.startswith('farLand_'): key='farLand'
    try: Pw,I=tri_from_glb(E+rec['file'],rec['center'])
    except Exception as ex: print('skip',rec['file'],ex); continue
    splat(Pw,I,key)
# hinterland boxes (5-sided boxes): sides + top
H_=np.array(json.load(open(E+'hinterland.json'))['items'])
Ps=[];Is=[];o=0
for it in H_:
    x,y,z,sx,sy,sz=it[:6]
    x0,x1=x-sx/2,x+sx/2; z0,z1=z-sz/2,z+sz/2; y0,y1=y,y+sy
    v=np.array([[x0,y0,z0],[x1,y0,z0],[x1,y0,z1],[x0,y0,z1],[x0,y1,z0],[x1,y1,z0],[x1,y1,z1],[x0,y1,z1]])
    tri=[(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7),(4,5,6),(4,6,7)]
    Ps.append(v); Is.append(np.array(tri)+o); o+=8
Ps=np.concatenate(Ps); Is=np.concatenate(Is)
splat(Ps,Is,'hinterland')
# water plane (y=-1.6) as splat of a big grid
np.save('idbuf.npy',idb); json.dump(layers,open('layers.json','w'))
# report layer pixel counts in the far band
inv={v:k for k,v in layers.items()}
reg=idb[150//S:300//S,0:1300//S]
for L in np.unique(reg):
    print(inv.get(L,'none/sky/other'), '%.1f%%'%(100*(reg==L).mean()))
import cv2
pal={0:(255,255,255)}
rs=np.random.default_rng(5)
cols={k:tuple(int(c) for c in rs.integers(40,255,3)) for k in layers.values()}
img=np.full((h,w,3),255,np.uint8)
for k,c in cols.items(): img[idb==k]=c
cv2.imwrite('ids.png',cv2.resize(img,(W,H),interpolation=cv2.INTER_NEAREST))
print({k:cols[v] for k,v in layers.items()})
