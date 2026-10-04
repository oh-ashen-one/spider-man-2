import numpy as np,sys
S=np.load('solids.npy')
# roof top per solid; tallest roof within R of point (UE X=bx, Y=bz)
def tallest(x,y,R=30):
    dx=np.maximum(0,np.maximum(S[:,0]-x,x-S[:,3])); dy=np.maximum(0,np.maximum(S[:,2]-y,y-S[:,5]))
    m=(dx*dx+dy*dy)<=R*R
    return S[m,4].max() if m.any() else 0.0
def floor(x,y):
    m=(S[:,0]<=x)&(S[:,3]>=x)&(S[:,2]<=y)&(S[:,5]>=y)
    return S[m,4].max() if m.any() else 0.0
if __name__=='__main__':
    X=float(sys.argv[1])
    for y in range(int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])):
        print(X,y,'floor %.1f tallest30 %.1f  tallest20 %.1f'%(floor(X,y),tallest(X,y),tallest(X,y,20)))
