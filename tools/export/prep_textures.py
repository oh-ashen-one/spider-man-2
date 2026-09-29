#!/usr/bin/env python3
"""Prepare the browser city textures for Unreal import: split the vertically stacked array textures into one PNG per
layer (UE builds Texture2DArray assets from them) and convert WebP to PNG.  Output: <out>/<name>.png, <out>/<name>_L<k>.png
usage: prep_textures.py [out_dir]"""
import os, sys
from PIL import Image
SRC = os.path.join(os.path.dirname(__file__), '../../public/assets/city/tex')
OUT = sys.argv[1] if len(sys.argv) > 1 else '/Users/midir/sm2-n1/_scratch/city/tex'
os.makedirs(OUT, exist_ok=True)
ARRAYS = {'walls_col.jpg': 1024, 'walls_nrm.webp': 512, 'walls_hao.jpg': 512, 'roof_col.png': 512, 'roof_nrm.png': 256}
PLAIN = ['interiors.png', 'signs.png', 'noise.png', 'detail_nrm.png', 'asphalt_col.png', 'asphalt_nrm.png', 'asphalt_macro.png',
         'asphalt_decals.webp', 'sidewalk_col.png', 'sidewalk_nrm.png', 'curb_col.webp', 'markings.png', 'leaves.png', 'bark_col.webp',
         'bark_nrm.webp', 'ts_ads.webp', 'city_signart.webp', 'grass_col.png', 'grass_nrm.png', 'roofplants.webp', 'ts_pavers.webp', 'ts_road.webp']
for f, size in ARRAYS.items():
    im = Image.open(os.path.join(SRC, f)).convert('RGBA' if f.endswith('.png') else 'RGB')
    n = round(im.height / im.width)
    base = f.split('.')[0]
    for k in range(n):
        im.crop((0, k * im.width, im.width, (k + 1) * im.width)).resize((size, size), Image.LANCZOS).save(os.path.join(OUT, f'{base}_L{k:02d}.png'))
    print(f, n, 'layers')
for f in PLAIN:
    p = os.path.join(SRC, f)
    if not os.path.exists(p): print('missing', f); continue
    im = Image.open(p); im.save(os.path.join(OUT, f.split('.')[0] + '.png')); print(f, im.size, im.mode)

# textures referenced by exported meshes / prototypes (manifest 'map' URLs), converted to PNG as tex/maps/<path_with_underscores>.png
import json
MAN = sys.argv[2] if len(sys.argv) > 2 else '/Users/midir/sm2-n1/_scratch/city/export/midtown3x3/manifest.json'
PUB = os.path.join(os.path.dirname(__file__), '../../public')
if os.path.exists(MAN):
    m = json.load(open(MAN)); os.makedirs(os.path.join(OUT, 'maps'), exist_ok=True)
    for r in m['meshes'] + m['protos']:
        u = (r.get('mat') or {}).get('map')
        if not u: continue
        rel = u.split('5202/', 1)[-1].split('?')[0]
        dst = os.path.join(OUT, 'maps', rel.replace('/', '_').rsplit('.', 1)[0] + '.png')
        if os.path.exists(dst): continue
        Image.open(os.path.join(PUB, rel)).save(dst); print('map', rel)
