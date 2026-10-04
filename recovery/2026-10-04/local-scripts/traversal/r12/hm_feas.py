from hm_need import *
dirs={'+Y':(0,1),'-Y':(0,-1),'+X':(1,0),'-X':(-1,0)}
for name,(dx,dy) in dirs.items():
    print('==',name,'  (. need<=60  : <=76  # building  blank unreachable)')
    for y in range(-600,381,10):
        row=''
        for x in range(-310,681,10):
            j,i=cell(x,y)
            if B[j,i]>12: row+='#'; continue
            p,t=solve(x,y,dx,dy,feet=20)
            row+='.' if p<=60 else (':' if p<=76 else ' ')
        print('%5d %s'%(y,row))
