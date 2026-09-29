from PIL import Image,ImageDraw
from pathlib import Path
import json
root=Path(__file__).resolve().parents[2]
manifest=json.loads((root/'docs/anim/hero/clip-manifest.json').read_text())
for name,meta in manifest.items():
 sheet=Image.new('RGB',(6*320,2*352),(12,16,24));draw=ImageDraw.Draw(sheet)
 for row,view in enumerate(('threequarter','side')):
  for k,u in enumerate((0,.18,.36,.54,.72,.9)):
   p=root/f'docs/anim/hero/poses/{name}-{view}-{k}.png'
   im=Image.open(p).convert('RGB');im.thumbnail((320,320));sheet.paste(im,(k*320,row*352))
   draw.text((k*320+8,row*352+324),f'{view}  {u*meta["duration"]:.2f}s',fill=(220,230,240))
 sheet.save(root/f'docs/anim/hero/{name}-contact.jpg',quality=90)
print('Saved 8 side/three-quarter contact sheets')
