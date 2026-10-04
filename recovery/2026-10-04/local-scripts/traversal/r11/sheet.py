import sys
from PIL import Image, ImageDraw
name, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); step=float(sys.argv[4]) if len(sys.argv)>4 else 0.1
F='/Users/midir/sm2-n1/_scratch/traversal/capture/%s/%s_frames/MovieFrame%%05d.png'%(name,name)
import os, csv
nf=len(os.listdir(os.path.dirname(F))); nt=sum(1 for _ in open('/Users/midir/sm2-n1/_scratch/traversal/capture/%s/%s_telemetry.csv'%(name,name)))-1
skip=nf-nt
ts=[]; t=t0
while t<=t1+1e-6: ts.append(t); t+=step
W,H=320,180; cols=6; im=Image.new('RGB',(W*cols,H*((len(ts)+cols-1)//cols)))
for k,t in enumerate(ts):
    fi=skip+int(round(t*60))
    try: f=Image.open(F%fi).convert('RGB').resize((W,H))
    except Exception as e: print(e); continue
    ImageDraw.Draw(f).text((4,4),'%.1f'%t,fill='yellow'); im.paste(f,((k%cols)*W,(k//cols)*H))
im.save('/Users/midir/sm2-n1/_scratch/traversal/r11/look/%s_sheet.jpg'%name,quality=85); print('skip',skip)
