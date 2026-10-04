import numpy as np
from tall import S,tallest,floor
xs=np.arange(-250,590,10); ys=np.arange(-545,305,10)
T=np.zeros((len(ys),len(xs))); F=np.zeros_like(T)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        T[j,i]=tallest(x,y); F[j,i]=floor(x,y)
np.savez('scan.npz',xs=xs,ys=ys,T=T,F=F)
# print a char map: '.' street with tallest30<=45, ':' <=60, '-' street <=90, '#' building, ' ' street taller
for j in range(len(ys)):
    row=''
    for i in range(len(xs)):
        if F[j,i]>2: row+='#'
        elif T[j,i]<=45: row+='.'
        elif T[j,i]<=60: row+=':'
        elif T[j,i]<=90: row+='-'
        else: row+=' '
    print('%5d %s'%(ys[j],row))
