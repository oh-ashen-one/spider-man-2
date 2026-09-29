#!/usr/bin/env python3
"""IP sanitiser for the UNREAL port only (owner rule: we copy nothing).

The browser game's Times Square ad atlas (public/assets/city/tex/ts_ads.webp, 4096x4096) and storefront sign atlas
(ts_signs.webp, 2048x2048) contain cells that show Marvel-universe / real-game brand names. The browser atlas files are
never modified. When prep_textures.py converts the atlases for Unreal it calls sanitize() here, which overwrites every
excluded cell with the pixels of another, original-brand cell of the same orientation (a UV-slot remap, done on the
Unreal-side copy). The table below is the single source of truth; docs/night1/city/IP_EXCLUSIONS.md lists it in prose.

Cell layout (from src/world/timessq.js):
  ts_ads.webp     top half: 64 landscape cells 512x256 (8 x 8, index = row * 8 + col);
                  bottom half: 64 portrait cells 256x512 (16 x 4, index = row * 16 + col, y offset 2048)
  ts_signs.webp   64 signs 512x128 (4 cols x 16 rows, index = row * 4 + col)
"""
from PIL import Image

# (kind, excluded cell, donor cell, why)
ADS = [
    ('L', 0, 55, 'OSCORP - Tomorrow, Engineered (Marvel-universe company)'),
    ('L', 1, 63, 'RE-ELECT OSBORN - Safe Streets, Strong City (Marvel-universe politician)'),
    ('L', 2, 52, 'THE DAILY BUGLE - cafe / newspaper (Marvel-universe newspaper)'),
    ('L', 3, 53, 'ROXXON - Powering New York (Marvel-universe company)'),
    ('L', 22, 45, 'EMPIRE STATE UNIVERSITY - Enroll for Fall (Marvel-universe university)'),
    ('L', 26, 43, 'FROSTED HALOS - Part of a Heavenly Breakfast (brand from the real game)'),
    ('L', 33, 46, 'BOTANICA - Now Playing, Majestic Theatre (show ad from the real game)'),
    ('L', 34, 20, 'FROSTED HALOS - Start Bright (brand from the real game)'),
    ('L', 39, 41, "HELL'S KITCHEN BLUES - New Season Streaming (Marvel-universe / Netflix-Marvel reference)"),
    ('L', 60, 59, "THE DAILY BUGLE - New York's News (Marvel-universe newspaper)"),
    ('L', 27, 4, 'COLTEX SPORT (sneaker brand too close to a real-game brand; round-04 critic)'),
    ('P', 27, 8, 'COLTEX - Own the Court (same brand, portrait cell)'),
    ('P', 38, 15, 'COLEXCO - Run the City (near-copy of the real game\'s COLEXCO brand)'),
    ('L', 35, 47, 'COLEXCO SPORT (red-on-white sneaker ad; it is the "COLEX SPOR..." banner seen in S6; real-game brand)'),
    ('P', 6, 20, 'OSCORP - A Healthier Tomorrow (Marvel-universe company)'),
    ('P', 7, 22, 'DAILY BUGLE - Read All About It (Marvel-universe newspaper)'),
    ('P', 13, 31, 'ROXXON - Fueling Tomorrow (Marvel-universe company)'),
    ('P', 39, 49, 'FROSTED HALOS (brand from the real game)'),
    ('P', 41, 18, 'HYDRA PRO (Marvel-universe organisation name)'),
]
SIGNS = [
    (48, 15, 'HOTEL MIRA (brand from the real game); replaced by HOTEL ASTORIA'),
]

def _box(kind, i):
    if kind == 'L': return ((i % 8) * 512, (i // 8) * 256, (i % 8) * 512 + 512, (i // 8) * 256 + 256)
    if kind == 'P': return ((i % 16) * 256, 2048 + (i // 16) * 512, (i % 16) * 256 + 256, 2048 + (i // 16) * 512 + 512)
    if kind == 'S': return ((i % 4) * 512, (i // 4) * 128, (i % 4) * 512 + 512, (i // 4) * 128 + 128)

def sanitize(basename, im):
    """basename: file name stem (ts_ads / ts_signs / ...). Returns a sanitised copy (or im itself when nothing applies)."""
    stem = basename.split('.')[0].replace('assets_city_tex_', '')
    if stem == 'ts_ads':
        out = im.copy()
        for kind, ex, do, _ in ADS: out.paste(im.crop(_box(kind, do)), _box(kind, ex)[:2])
        return out
    if stem == 'ts_signs':
        out = im.copy()
        for ex, do, _ in SIGNS: out.paste(im.crop(_box('S', do)), _box('S', ex)[:2])
        return out
    return im

if __name__ == '__main__':
    import os, sys
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '../../public/assets/city/tex')
    dst = sys.argv[2] if len(sys.argv) > 2 else '/Users/midir/sm2-n1/_scratch/city/r04/atlas'
    os.makedirs(dst, exist_ok=True)
    for f in ('ts_ads.webp', 'ts_signs.webp'):
        im = Image.open(os.path.join(src, f)).convert('RGB'); s = sanitize(f, im)
        s.thumbnail((2000, 2000)); s.save(os.path.join(dst, f.split('.')[0] + '_clean.jpg'), quality=88); print(f, 'sanitised ->', dst)
