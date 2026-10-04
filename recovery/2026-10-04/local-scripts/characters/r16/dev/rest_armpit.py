import sys, os, numpy as np, cv2
WT='/Users/midir/sm2-n1/characters'
sys.path[:0]=[WT+'/tools/ue_char/suit8', WT+'/tools/ue_char', WT+'/tools/ue_char/suits']
import meshio, softrender as sr, swatch_cpu as SC
m=meshio.load_body()
sid=sys.argv[1]; maps=WT+'/art/night1/characters/hero/suits'
bc=SC.load_tex('%s/%s_basecolor.png'%(maps,sid))
body=sr.Prim(m['P'],m['N'],m['F'],UV=m['UV'],tex=bc,nmap=None,rough=0.7,spec=0.12,name='suit')
for nm,(eye,tgt) in dict(R=((-0.22,1.31,0.55),(-0.17,1.31,0.0)), L=((0.22,1.31,0.55),(0.17,1.31,0.0))).items():
    im=sr.render([body],sr.look_at(eye,tgt),24,900,900,ssaa=1)
    cv2.imwrite('/Users/midir/sm2-n1/_scratch/characters/r16/look/rest_%s_%s.jpg'%(sid,nm),(np.clip(im,0,1)**(1/2.2)*255).astype(np.uint8)[...,::-1])
