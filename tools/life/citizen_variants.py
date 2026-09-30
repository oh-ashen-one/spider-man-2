#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# P6 City life: outfit variants of the 20 crowd citizens. The pack has 20 distinct people; a busy frame shows more than 20, so identical twins would
# appear. Each citizen atlas tile gets two recoloured copies: hue rotated for every saturated pixel that is NOT skin / red-brown (clothes, bags, hats),
# plus a mild global brightness / tint shift. The mesh is shared, only the material differs.
# Round 02: the HEAD changes too (the critic saw the same bearded head twice): with the head mask of tools/life/citizen_headmask.py (NAME_headmask.json, the UV
# polygons of the top 14 % of the mesh) the dark hair / beard / brow pixels of the head are re-coloured (v1: silver or blond, v2: black or auburn) and every skin pixel
# of the atlas (face, hands, arms) gets a lighter (v1) / darker (v2) tone, so a citizen looks like three different people.
#   python3 tools/life/citizen_variants.py <dir with NAME_basecolor.png [+ NAME_headmask.json]> -> NAME_basecolor_v1.png, NAME_basecolor_v2.png
import glob, json, os, sys
import numpy as np
from PIL import Image, ImageDraw

def rgb2hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1); mn = a.min(-1); d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = m & (mx == r); gc = m & (mx == g) & ~rc; bc = m & ~rc & ~gc
    h[rc] = ((g - b)[rc] / d[rc]) % 6
    h[gc] = (b - r)[gc] / d[gc] + 2
    h[bc] = (r - g)[bc] / d[bc] + 4
    h = h / 6.0
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0.0)
    return h, s, mx

def hsv2rgb(h, s, v):
    i = np.floor(h * 6).astype(int) % 6; f = h * 6 - np.floor(h * 6)
    p = v * (1 - s); q = v * (1 - f * s); t = v * (1 - (1 - f) * s)
    out = np.zeros(h.shape + (3,), np.float32)
    for k, (r, g, b) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        m = i == k
        out[..., 0][m] = r[m]; out[..., 1][m] = g[m]; out[..., 2][m] = b[m]
    return out

def head_mask(f, size):
    j = f.replace('_basecolor.png', '_headmask.json')
    if not os.path.exists(j): return None
    img = Image.new('L', size, 0); dr = ImageDraw.Draw(img)
    for poly in json.load(open(j)): dr.polygon([(u * size[0], v * size[1]) for u, v in poly], fill=255)
    return np.asarray(img) > 0

d = sys.argv[1]
files = sorted(glob.glob(os.path.join(d, '*_basecolor.png')))
for idx, f in enumerate(files):
    im = np.asarray(Image.open(f).convert('RGB')).astype(np.float32) / 255
    h, s, v = rgb2hsv(im)
    hd = h * 360
    skin = ((hd < 55) | (hd > 335)) & (s > 0.10) & (s < 0.75) & (v > 0.2)          # skin, lips, red / orange / brown cloth stay
    move = ~skin & (s > 0.16)
    hm = head_mask(f, (im.shape[1], im.shape[0]))
    # variant k: (clothes hue shift, brightness, tint, skin value x, skin saturation x, hair mode)
    for k, (dh, vk, tint, skv, sks, hair) in enumerate([(0.33, 0.96, (1.0, 1.0, 1.0), 1.17, 0.85, 'light'), (0.66, 1.04, (0.96, 1.0, 1.06), 0.72, 1.10, 'dark')], start=1):
        h2 = np.where(move, (h + dh) % 1.0, h)
        s2, v2 = s.copy(), v.copy()
        s2 = np.where(skin, np.clip(s * sks, 0, 1), s2); v2 = np.where(skin, np.clip(v * skv, 0, 1), v2)
        if hm is not None:
            hair_px = hm & ~skin & (v < 0.55) & (s < 0.5)                              # dark, low-saturation head pixels: hair, beard, brows (not eyes / teeth / hats)
            if hair == 'light':
                if idx % 2 == 0: h2 = np.where(hair_px, 0.115, h2); s2 = np.where(hair_px, 0.42, s2); v2 = np.where(hair_px, np.clip(0.30 + v * 1.25, 0, 0.85), v2)   # blond
                else: h2 = np.where(hair_px, 0.6, h2); s2 = np.where(hair_px, 0.04, s2); v2 = np.where(hair_px, np.clip(0.42 + v * 1.1, 0, 0.88), v2)                   # silver
            else:
                if idx % 2 == 0: v2 = np.where(hair_px, v * 0.45, v2)                                                                                                     # black
                else: h2 = np.where(hair_px, 0.035, h2); s2 = np.where(hair_px, 0.62, s2); v2 = np.where(hair_px, np.clip(0.16 + v * 0.9, 0, 0.6), v2)                    # auburn
        out = hsv2rgb(h2, s2, v2) * vk * np.array(tint, np.float32)
        Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(f.replace('_basecolor.png', '_basecolor_v%d.png' % k))
print('variants written for', len(files), 'citizens (head masks: %d)' % len(glob.glob(os.path.join(d, '*_headmask.json'))))
