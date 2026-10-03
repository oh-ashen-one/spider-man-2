# r06 diag: lawn shadow ratio per caster slot in the top-down D_shadow / D_shadow2 captures (1920x1080, native). Shadow box = darkest 15 px running window along the slot's
# shadow band (12 px tall) 20-260 px left of the row; lit = median of the same span 40-60 px above / below the band.
import sys, json
import numpy as np
from PIL import Image
f, labels = sys.argv[1], sys.argv[2].split(',')
im = np.asarray(Image.open(f).convert('RGB')).astype(float)
L = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
XR = 1100; ys = [920, 810, 700, 590, 485, 380, 270, 160]   # slot rows (k = -4 .. 3), full-frame pixels
out = []
for lab, y in zip(labels, ys):
    x0, x1 = (XR - 340, XR - 100) if 'cube' in lab else (XR - 300, XR - 40)
    prof = L[y - 6:y + 7, x0:x1].mean(0)
    rm = np.convolve(prof, np.ones(15) / 15, 'valid')
    lit = float(np.median(np.r_[L[y - 60:y - 40, x0:x1].ravel(), L[y + 40:y + 60, x0:x1].ravel()]))
    r = dict(slot=lab, y=y, shadow15=round(float(rm.min()), 1), lit=round(lit, 1), ratio=round(float(rm.min()) / lit, 3), x=int(x0 + rm.argmin()))
    out.append(r); print(r)
json.dump(out, open(sys.argv[3], 'w'), indent=1)
