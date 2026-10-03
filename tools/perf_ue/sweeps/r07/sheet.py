#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07: labelled contact sheet of stills (top part of the frame by default, where the dome is).
usage: sheet.py <out.jpg> <cols> <thumb width> <rows frac of height shown 0..1> file1 file2 ...   (label = file name without tod_ prefix / extension)"""
import sys
from PIL import Image, ImageDraw
out, cols, tw, frac = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]); files = sys.argv[5:]
th = int(tw * 9 / 16 * frac)
rows = (len(files) + cols - 1) // cols
S = Image.new('RGB', (tw * cols, (th + 14) * rows), (20, 20, 20)); d = ImageDraw.Draw(S)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB'); im = im.resize((tw, int(tw * im.size[1] / im.size[0]))).crop((0, 0, tw, th))
    x, y = (i % cols) * tw, (i // cols) * (th + 14)
    S.paste(im, (x, y + 14)); d.text((x + 3, y + 1), f.split('/')[-1].replace('tod_', '').replace('_1920x1080', '')[:60], fill=(255, 255, 0))
S.save(out, quality=88); print(out, S.size)
