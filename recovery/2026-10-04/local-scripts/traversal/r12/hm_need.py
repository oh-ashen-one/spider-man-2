import numpy as np, csv, sys
D=np.genfromtxt('/Users/midir/sm2-n1/_scratch/traversal/r12/hm/heightmap.csv',delimiter=',',names=True)
xs=np.arange(-320,681,5); ys=np.arange(-620,381,5)
Z=np.zeros((len(ys),len(xs))); GR=np.ones_like(Z)
for r in D:
    i=int(round((r['x']+320)/5)); j=int(round((r['y']+620)/5))
    Z[j,i]=r['z']; GR[j,i]=r['ground']
B=np.where(GR>0,0.0,Z)   # building/prop tops (non-ground)
def cell(x,y): return int(round((y+620)/5)), int(round((x+320)/5))
def tall_strip(x,y,dx,dy,D0,D1,R=30):
    best=0.0
    for a in np.arange(D0-R,D1+R+1,5):
        ac=min(max(a,D0),D1)
        for l in np.arange(-R,R+1,5):
            if (a-ac)**2+l*l>R*R: continue
            px,py=x+dx*a-dy*l, y+dy*a+dx*l
            j,i=cell(px,py)
            if 0<=j<len(ys) and 0<=i<len(xs): best=max(best,B[j,i])
    return best
G=24.0
def v0(peak_over, feet_over):
    Dh=max(2,peak_over-feet_over); Vh=7; GH=G*0.55; HH=Vh*Vh/(2*GH)
    return min(max(np.sqrt(max(0,2*G*max(0,Dh-HH))+Vh*Vh),26),60)
def solve(x,y,dx,dy,HS=28,feet=20,street=0):
    peak=38
    for _ in range(2):
        V=v0(peak,feet); ts=max(0,V-9)/G; D0=min(HS,32)*ts; D1=D0+min(HS,32)*2.4
        t=tall_strip(x,y,dx,dy,D0,D1)-street; peak=max(38,t+6)
    return peak,t
if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'map'
    if mode=='map':
        for j in range(0,len(ys),4):
            print('%5d '%ys[j]+''.join(' ' if B[j,i]<1 else ('.' if B[j,i]<20 else (':' if B[j,i]<60 else ('-' if B[j,i]<100 else '#'))) for i in range(0,len(xs),3)))
