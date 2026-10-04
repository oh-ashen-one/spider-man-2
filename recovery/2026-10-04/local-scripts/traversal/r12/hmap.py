import json,numpy as np,csv,sys
d=json.load(open('/Users/midir/sm2-n1/_scratch/traversal/manhattan/export/midtown3x3/collision.json'))
S=np.array([s['bb'] for s in d['solids']])
print(len(S), S[:,0].min(),S[:,3].max(),S[:,2].min(),S[:,5].max(),S[:,4].max())
np.save('solids.npy',S)
def top(bx,bz,S=S):
    m=(S[:,0]<=bx)&(S[:,3]>=bx)&(S[:,2]<=bz)&(S[:,5]>=bz)
    return S[m,4].max() if m.any() else 0.0
R=list(csv.DictReader(open('/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-11/f1_sky_backDouble_telemetry.csv')))
for mp in [(1,1),(1,-1),(-1,1),(-1,-1)]:
  for sw in (0,1):
    err=[]
    for r in R[::20]:
        x,y,z,h=float(r['x_m']),float(r['y_m']),float(r['z_m']),float(r['height_above_floor_m'])
        a,b=(x*mp[0],y*mp[1]) if not sw else (y*mp[0],x*mp[1])
        fl=top(a,b); err.append(abs((z-h)-fl))
    print(mp,sw,np.median(err),np.mean(err))
