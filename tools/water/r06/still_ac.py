#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""r06: the dolly autocorrelation instrument (water_spec.dolly: 84 % pack crop, 1612 px wide, water crop y 480-700 x 0-820, high-pass sigma 24,
80 px shift) applied to single stills, to screen variants without a 16 min dolly.  usage: still_ac.py <frame> [...]"""
import os, sys
import cv2, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import water_spec as w
for f in sys.argv[1:]:
    im = cv2.imread(f).astype(np.float32)
    im = cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA) if im.shape[1] != 1920 else im
    h, wd = im.shape[:2]; cw, ch = int(wd * 0.84), int(h * 0.84)
    p = im[(h - ch) // 2:(h - ch) // 2 + ch, (wd - cw) // 2:(wd - cw) // 2 + cw]
    p = cv2.resize(p, (1612, int(round(p.shape[0] * 1612 / p.shape[1]))), interpolation=cv2.INTER_AREA)
    x0, x1, y0, y1 = w.DOLLY; Y = w.luma(p)[y0:y1, x0:x1]
    print('%-60s ac80 %.3f' % (f[-60:], w._ac(Y - cv2.GaussianBlur(Y, (0, 0), 24), 80)))
