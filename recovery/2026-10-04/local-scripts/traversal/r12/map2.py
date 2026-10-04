import numpy as np,csv,glob
S=np.load('solids.npy')
def top(bx,bz):
    m=(S[:,0]<=bx)&(S[:,3]>=bx)&(S[:,2]<=bz)&(S[:,5]>=bz)
    return S[m,4].max() if m.any() else 0.0
for f in glob.glob('/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-1[01]/c_*_telemetry.csv')+glob.glob('/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-11/b_*_telemetry.csv'):
  R=list(csv.DictReader(open(f)))
  for mp in [(1,1),(-1,-1),(1,-1),(-1,1)]:
    err=[]
    for r in R[::10]:
        x,y,z,h=float(r['x_m']),float(r['y_m']),float(r['z_m']),float(r['height_above_floor_m'])
        fl=top(x*mp[0],y*mp[1]); err.append(abs((z-h)-fl))
    print(f[-40:],mp,np.median(err),np.mean(err))
