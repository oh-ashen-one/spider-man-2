import numpy as np
S=np.load('solids.npy')
def strip_tall(x,y,dx,dy,D0=35,D1=100,R=30):
    # boxes within R of segment
    ax,ay=x+dx*D0,y+dy*D0; bx,by=x+dx*D1,y+dy*D1
    # sample segment points every 5 m, distance box-to-point
    best=0
    for t in np.arange(D0,D1+1,5):
        px,py=x+dx*t,y+dy*t
        ddx=np.maximum(0,np.maximum(S[:,0]-px,px-S[:,3])); ddy=np.maximum(0,np.maximum(S[:,2]-py,py-S[:,5]))
        m=(ddx*ddx+ddy*ddy)<=R*R
        if m.any(): best=max(best,S[m,4].max())
    return best
def floor(x,y):
    m=(S[:,0]<=x)&(S[:,3]>=x)&(S[:,2]<=y)&(S[:,5]>=y)
    return S[m,4].max() if m.any() else 0.0
if __name__=='__main__':
    xs=np.arange(-250,590,10); ys=np.arange(-545,305,10)
    for name,(dx,dy) in {'+Y (south)':(0,1),'-Y (north)':(0,-1),'+X (east)':(1,0),'-X (west)':(-1,0)}.items():
        print('==',name)
        for y in ys:
            row=''
            for x in xs:
                if floor(x,y)>2: row+='#'; continue
                n=strip_tall(x,y,dx,dy)+6
                row+= '.' if n<=60 else (':' if n<=80 else ' ')
            print('%5d %s'%(y,row))
