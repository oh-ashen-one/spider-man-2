import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; cols=int(sys.argv[2]); files=sys.argv[3:]
ims=[Image.open(f).convert('RGB') for f in files]
w=960; h=540
ims=[i.resize((w,int(i.height*w/i.width))) for i in ims]
rows=(len(ims)+cols-1)//cols
M=Image.new('RGB',(cols*w,rows*h),(0,0,0))
for k,i in enumerate(ims):
    M.paste(i,((k%cols)*w,(k//cols)*h)); ImageDraw.Draw(M).text(((k%cols)*w+8,(k//cols)*h+8),files[k].split('/')[-1][:60],fill=(255,255,0))
M.save(out,quality=85)
