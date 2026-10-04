import sys, numpy as np, cv2
WT='/Users/midir/sm2-n1/characters'
sys.path[:0]=[WT+'/tools/ue_char/suit8']
import meshio
n=2048
m=meshio.load_body(); tri,w0,w1,inside=meshio.raster_tri(m['UV'],m['F'],n)
Pm=np.zeros((n,n,3),np.float32)
for r0 in range(0,n,256):
    sl=slice(r0,min(r0+256,n)); Pm[sl]=meshio.gather(tri,w0,w1,m['F'],m['P'],sl)
cov=tri>=0
x,y,z=Pm[...,0],Pm[...,1],Pm[...,2]
sel=cov&(np.abs(y-1.31)<0.0015)&(z>-0.06)&(np.abs(x)>0.12)&(np.abs(x)<0.23)
ys,xs=np.where(sel)
print('texels',len(ys))
for side in (1,-1):
    s=sel&(np.sign(x)==side)
    yy,xx=np.where(s)
    print('side',side,'uv rows %d-%d cols %d-%d'%(yy.min(),yy.max(),xx.min(),xx.max()))
    # check island: label connected components in uv of the band
    from scipy import ndimage as ndi
    lab,k=ndi.label(ndi.binary_dilation(s,iterations=2))
    for i in range(1,k+1):
        mm=(lab==i)&s
        if mm.sum()<5: continue
        print('  comp',i,'texels',mm.sum(),'x range %.3f..%.3f z %.3f..%.3f'%(x[mm].min(),x[mm].max(),z[mm].min(),z[mm].max()),'uv',np.where(mm)[1].mean().round(),np.where(mm)[0].mean().round())
bc=cv2.imread(WT+'/art/night1/characters/hero/suits/verdant_basecolor.png')
print(bc.shape)
