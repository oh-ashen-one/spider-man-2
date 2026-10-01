#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Night skyline numbers (LOOK-SPEC L22, round 04; from the round-03 critic verdict, secondary 1: night S4 window points on >= 3 % of the frame, city median Y <= 42;
the critic measured round 03 at 0.96 % / 58, the reference at 4.38 % / 37).
Per still (resized to 1920 wide, luma Y = .2126 R + .7152 G + .0722 B of the 8-bit sRGB):
  window points   share of pixels with Y >= 120 AND Y - median9x9(Y) >= 35 (small bright points standing out of their surroundings); on the round-03 night S4 this gives 1.10 % (critic 0.96 %)
  city median     median Y of the whole frame (round 03 S4: 51.9 here; its MEAN is 58.1 = the critic's '58', so both median and mean must be <= 42)
usage: night_city_check.py files... [--md out.md]"""
import argparse, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd
def stats(path):
    im = Image.open(path).convert('RGB')
    if im.width != 1920: im = im.resize((1920, int(round(im.height * 1920 / im.width))), Image.BOX if im.width % 1920 == 0 else Image.LANCZOS)
    a = np.asarray(im, dtype=np.float32); Y = .2126 * a[..., 0] + .7152 * a[..., 1] + .0722 * a[..., 2]
    pts = (Y >= 120) & (Y - nd.median_filter(Y, size=9) >= 35)
    return {'file': os.path.basename(path), 'points_pct': float(pts.mean() * 100), 'median': float(np.median(Y)), 'mean': float(Y.mean())}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('files', nargs='+'); ap.add_argument('--md'); a = ap.parse_args()
    L = ['| still | window points % (>= 3, aim 3.5) | median Y (<= 42) | mean Y (<= 42: the critic\'s round-03 "58" is this mean) |', '|---|---|---|---|']
    for f in a.files:
        d = stats(f); L.append('| %s | %.2f %s | %.1f %s | %.1f %s |' % (d['file'], d['points_pct'], 'yes' if d['points_pct'] >= 3 else 'NO', d['median'], 'yes' if d['median'] <= 42 else 'NO', d['mean'], 'yes' if d['mean'] <= 42 else 'NO'))
    out = '\n'.join(L) + '\n'; print(out)
    if a.md: open(a.md, 'w').write(out)
if __name__ == '__main__': main()
