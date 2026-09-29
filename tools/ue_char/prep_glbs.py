#!/usr/bin/env python3
"""Prepare the browser character GLBs for Unreal Interchange (fan homage project; not official Marvel/Sony/Insomniac).
- strips EXT_texture_webp textures (UE rejects them; PNGs are imported separately)
- hero: merges the Lenses primitives into the body mesh (same skin) so UE builds ONE skeletal mesh with 3 slots
Outputs to /Users/midir/sm2-n1/_scratch/characters/ueimport/ (derived, reproducible, not committed)."""
import json, struct, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from strip_glb import main as strip  # noqa

WT = '/Users/midir/sm2-n1/characters'
OUT = '/Users/midir/sm2-n1/_scratch/characters/ueimport'
os.makedirs(OUT, exist_ok=True)

def rw(path, fn):
    b = open(path, 'rb').read(); n = struct.unpack('<I', b[12:16])[0]
    g = json.loads(b[20:20 + n]); rest = b[20 + n:]
    fn(g)
    js = json.dumps(g, separators=(',', ':')).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
    open(path, 'wb').write(b'glTF' + struct.pack('<II', 2, 20 + len(js) + len(rest)) + struct.pack('<I', len(js)) + b'JSON' + js + rest)

def merge_lenses(g):
    body = next(n for n in g['nodes'] if n.get('name') == 'SpiderMan')
    lens = next(n for n in g['nodes'] if n.get('name') == 'Lenses')
    g['meshes'][body['mesh']]['primitives'] += g['meshes'][lens['mesh']]['primitives']
    lens.pop('mesh'); lens.pop('skin')

jobs = [('public/assets/spiderman.glb', 'SK_Hero.glb', merge_lenses),
        ('public/assets/thug.glb', 'SK_Thug.glb', None)]
for s in ('claude', 'codex', 'gemini', 'kimi', 'qwen'):
    jobs.append(('public/assets/skins/%s.glb' % s, 'SK_Suit_%s.glb' % s.capitalize(), None))
for src, dst, fn in jobs:
    d = os.path.join(OUT, dst)
    strip(os.path.join(WT, src), d)
    if fn:
        rw(d, fn)
