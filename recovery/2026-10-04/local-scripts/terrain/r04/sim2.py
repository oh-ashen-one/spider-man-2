import numpy as np, math
exec(open('sim_detail.py').read().split("for s_m,name in")[0])
def lum_w(s_m, w1, w2, w3, wa, N=640):
    xs=(np.arange(N)+0.5)*s_m; X,Y=np.meshgrid(xs,xs)
    foot=lambda tile: s_m/tile*det.shape[0]
    d1=sample(det, X/1.15, Y/1.15, foot(1.15))
    x2,y2=rot(X,Y,0.61); d2=sample(det, x2/4.7+0.37, y2/4.7+0.61, foot(4.7))
    x3,y3=rot(X,Y,-0.93); d3=sample(det, x3/16.3+0.71, y3/16.3+0.13, foot(16.3))
    mott=(d1[...,0]-0.5)*w1+(d2[...,0]-0.5)*w2+(d3[...,0]-0.5)*w3+(d1[...,3]-0.5)*wa
    return 140*np.clip(1+mott,0.55,1.55)
for name,(w1,w2,w3,wa) in {'cur k=.55':(0.34*0.55,0.52*0.55,0.46*0.55,0.22*0.55),'rebal A':(0.45,0.85,0.30,0.25),'rebal B':(0.55,1.0,0.30,0.25),'rebal C':(0.40,0.95,0.35,0.2),'rebal D':(0.45,1.1,0.25,0.2)}.items():
    row=[]
    for s_m in (0.07,0.15):
        img=lum_w(s_m,w1,w2,w3,wa); hp=img-gaussian_filter(img,6.0); row.append((round(float(hp.std()),1), round(float(img.std()),1)))
    print(name,'(hp6, lumaSD) at 0.07/0.15 m/px:',row)
print('--- candidates (current k=.55 effective weights: .187 .286 .253 .121)')
for name,(w1,w2,w3,wa) in {'E x1.75 uniform':(0.327,0.50,0.443,0.21),'F d2-heavy':(0.30,0.62,0.30,0.2),'G d2/d1-heavy':(0.36,0.62,0.26,0.22),'H':(0.34,0.55,0.28,0.2)}.items():
    row=[]
    for s_m in (0.07,0.15):
        img=lum_w(s_m,w1,w2,w3,wa); hp=img-gaussian_filter(img,6.0); row.append((round(float(hp.std()),1), round(float(img.std()),1)))
    print(name,(w1,w2,w3,wa),'(hp6, lumaSD):',row)
print('--- hold-3 candidates (G = .36 .62 .26 .22 gives 16.7/16.8 at 0.07/0.15)')
for name,(w1,w2,w3,wa) in {'G':(0.36,0.62,0.26,0.22),'I d1,d2 x1.4':(0.50,0.87,0.26,0.28),'J d2 x1.6':(0.40,1.0,0.26,0.22),'K all x1.35':(0.49,0.84,0.35,0.30),'L d1 x1.8 d2 x1.3':(0.65,0.80,0.26,0.25)}.items():
    row=[]
    for s_m in (0.04,0.07,0.15):
        img=lum_w(s_m,w1,w2,w3,wa); hp=img-gaussian_filter(img,6.0); row.append((round(float(hp.std()),1), round(float(img.std()),1)))
    print(name,(w1,w2,w3,wa),'(hp6, lumaSD) at .04/.07/.15:',row)
print('--- final candidate')
for name,(w1,w2,w3,wa) in {'M':(0.54,0.95,0.26,0.30),'N':(0.52,0.92,0.30,0.28)}.items():
    row=[]
    for s_m in (0.04,0.07,0.15):
        img=lum_w(s_m,w1,w2,w3,wa); hp=img-gaussian_filter(img,6.0); row.append((round(float(hp.std()),1), round(float(img.std()),1)))
    print(name,(w1,w2,w3,wa),row)
