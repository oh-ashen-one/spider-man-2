#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# P6 City life: outfit variants of the 20 crowd citizens. The pack has 20 distinct people; a busy frame shows more than 20, so identical twins would
# appear. Each citizen atlas tile gets two recoloured copies: hue rotated for every saturated pixel that is NOT skin / red-brown (clothes, bags, hats),
# plus a mild global brightness / tint shift. Skin, hair (low saturation) and eyes are left alone. The mesh is shared, only the material differs.
#   python3 tools/life/citizen_variants.py <dir with NAME_basecolor.png> -> NAME_basecolor_v1.png, NAME_basecolor_v2.png
import glob, os, sys
import numpy as np
from PIL import Image

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

d = sys.argv[1]
for f in sorted(glob.glob(os.path.join(d, '*_basecolor.png'))):
    im = np.asarray(Image.open(f).convert('RGB')).astype(np.float32) / 255
    h, s, v = rgb2hsv(im)
    hd = h * 360
    skin = ((hd < 55) | (hd > 335)) & (s > 0.10) & (s < 0.75) & (v > 0.2)          # skin, lips, red / orange / brown cloth stay
    move = ~skin & (s > 0.16)
    for k, (dh, vk, tint) in enumerate([(0.33, 0.96, (1.0, 1.0, 1.0)), (0.66, 1.04, (0.96, 1.0, 1.06))], start=1):
        h2 = np.where(move, (h + dh) % 1.0, h)
        out = hsv2rgb(h2, s, v) * vk * np.array(tint, np.float32)
        Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(f.replace('_basecolor.png', '_basecolor_v%d.png' % k))
print('variants written for', len(glob.glob(os.path.join(d, '*_basecolor.png'))), 'citizens')
