# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Far-shore instruments for river_low (round 05b), native 4K frame.
bright_bar_pct : share of the far-shore strip (x 0-2300, y 880-1200) with luma >= 170. r03 (merged floor) ~0, r05 ~ a flat cream bar from the
                 far contact line at river level (FarPx footprints).
refl_hp        : high-pass (sigma 6) standard deviation of the water strip under the far quay (x 0-1500, y 1130-1230): the far shore's
                 mirrored pilings and trees show up as vertical structure there (r03 reference).
usage: python3 tools/water/farshore.py frame.jpg [...]"""
import sys, json
import numpy as np, cv2


def luma(im): return 0.2126 * im[..., 2] + 0.7152 * im[..., 1] + 0.0722 * im[..., 0]


def score(path):
    im = cv2.imread(path)
    if im.shape[1] != 3840: im = cv2.resize(im, (3840, 2160), interpolation=cv2.INTER_CUBIC)
    Y = luma(im.astype(np.float32))
    bar = float((Y[880:1200, 0:2300] >= 170).mean() * 100)
    s = Y[1130:1230, 0:1500]; hp = s - cv2.GaussianBlur(s, (0, 0), 6)
    return dict(file=path.split('/')[-1], bright_bar_pct=round(bar, 2), refl_hp=round(float(hp.std()), 2))


if __name__ == '__main__':
    for f in sys.argv[1:]: print(json.dumps(score(f)))
