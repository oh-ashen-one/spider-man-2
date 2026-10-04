import json,sys,numpy as np
rows=[json.loads(l) for l in open(sys.argv[1]) if l.strip()]
STAND={'hold','approach','attack','aim','fire','stagger','getup','webbed','yanked'}
n5=[];mg=[];occ=[];pit=[];dist=[]
for r in rows:
    if r['rt']<1.5: continue
    hb=r['hero'][3:7]; mg.append(min(hb[0],hb[1],1-hb[2],1-hb[3]))
    k=0;o=0
    for e in r['e']:
        tag,typ,st,x,y,z,x0,y0,x1,y1,d,w,al=e
        if x0<-0.5: continue
        cw=max(0,min(1,x1)-max(0,x0)); ch=max(0,min(1,y1)-max(0,y0)); cx=(x0+x1)/2; cy=(y0+y1)/2
        if al and st in STAND and 0<=cx<=1 and 0<=cy<=1 and ch>=0.05: k+=1
        if d<r['hero'][7]-0.3:
            ox=max(0,min(x1,hb[2])-max(x0,hb[0])); oy=max(0,min(y1,hb[3])-max(y0,hb[1]))
            if ox>0 and oy>0: o=max(o,cw*ch)
    n5.append(k); occ.append(o); pit.append(r['cam'][3])
    c=np.array(r['cam'][:3]); h=np.array(r['hero'][:3]); dist.append(np.linalg.norm((c-h)[:2]))
n5=np.array(n5);mg=np.array(mg);occ=np.array(occ)
print('frames',len(n5),'>=5 enemies',(n5>=5).mean().round(3),'median',np.median(n5),'hist',np.bincount(n5))
print('hero margin>=5%',(mg>=0.05).mean().round(4),'min',mg.min().round(3),'occ>15%',(occ>0.15).sum(),'occmax',occ.max().round(3))
print('pitch pct',np.percentile(pit,[5,50,95]).round(1),'horiz dist pct',np.percentile(dist,[5,50,95]).round(2))
bad=[(round(r['rt'],2),round(min(r['hero'][3],r['hero'][4],1-r['hero'][5],1-r['hero'][6]),3),r['move']) for r in rows if r['rt']>1.5 and min(r['hero'][3],r['hero'][4],1-r['hero'][5],1-r['hero'][6])<0.05]
print('bad margin samples',bad[:15], len(bad))
