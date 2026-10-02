#!/usr/bin/env python3
"""Tree-crown detail check (round-01 critic's biggest gap; round-02 PASS test), CPU only.
  1. crown crops: high-pass SD = std of (Y - GaussianBlur(Y, sigma 3)) on hand-picked 150 x 150 crops of pure crown (luma Y 0..255); boxes are pixel boxes on the 3840 x 2160 stills,
     listed in docs/night1/terrain/round-NN/crops.json  {"crowns": {"p1_south.jpg": [[x, y], ...]}, "reference": {"<ref image path>": [[x, y], ...]}}.  PASS: every crop >= 9.
  2. flat-shaded hull faces: foliage-coloured pixels whose local luma variation is almost zero form flat patches (what a smooth-shaded low-poly hull looks like); a patch's width
     is the diameter of its largest inscribed circle (distance transform). PASS: no patch wider than 40 px in p1_south / p10_lawn_eye.
usage: crown_stats.py <stills dir> <crops.json> <out.json> [--flat image.jpg ...] [--preview preview.png]"""
import sys, json, os
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, uniform_filter, distance_transform_edt, label, binary_opening

CROP = 150
def luma(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(np.float32)

def hp_sd(Y, x, y, size=CROP, sigma=3.0):
    # blur the whole image once per call site (cached by the caller); here a local window with margin to avoid edge effects
    m = int(sigma * 4)
    y0, x0 = max(0, y - m), max(0, x - m); y1, x1 = min(Y.shape[0], y + size + m), min(Y.shape[1], x + size + m)
    blur = gaussian_filter(Y[y0:y1, x0:x1], sigma)
    hp = (Y[y0:y1, x0:x1] - blur)[y - y0:y - y0 + size, x - x0:x - x0 + size]
    return float(hp.std())

def crop_stats(path, boxes):
    im = load(path); Y = luma(im); out = []
    for x, y in boxes:
        c = im[y:y + CROP, x:x + CROP]
        r, g, b = c[..., 0].mean(), c[..., 1].mean(), c[..., 2].mean()
        out.append({'box_xywh': [x, y, CROP, CROP], 'hp_sd': round(hp_sd(Y, x, y), 2), 'mean_luma': round(float(Y[y:y + CROP, x:x + CROP].mean()), 1), 'rgb_mean': [round(float(v), 1) for v in (r, g, b)]})
    return out

def flat_faces(path, var_thr=1.4, min_w=40):
    """flat foliage patches: local luma std (7 x 7) <= var_thr on foliage-coloured pixels; opened by 3 px so single smooth pixels do not count"""
    im = load(path); Y = luma(im); r, g, b = im[..., 0], im[..., 1], im[..., 2]
    mx = im.max(axis=2); mn = im.min(axis=2); sat = (mx - mn) / np.maximum(mx, 1.0)
    foliage = (g >= 0.92 * r) & (g > 1.08 * b) & (sat > 0.22) & (Y > 25) & (Y < 235)       # olive / green / yellow-green foliage, not sky / buildings / road
    m1 = uniform_filter(Y, 7); m2 = uniform_filter(Y * Y, 7); lstd = np.sqrt(np.maximum(m2 - m1 * m1, 0))
    flat = foliage & (lstd <= var_thr)
    flat = binary_opening(flat, iterations=3)
    dt = distance_transform_edt(flat)
    lab, n = label(flat)
    wide = []
    if n:
        mxd = np.zeros(n + 1); np.maximum.at(mxd, lab.ravel(), dt.ravel())
        for i in range(1, n + 1):
            w = 2 * mxd[i]
            if w > min_w:
                ys, xs = np.nonzero(lab == i); wide.append({'width_px': round(float(w), 1), 'area_px': int(len(ys)), 'centre_xy': [int(xs.mean()), int(ys.mean())]})
    wide.sort(key=lambda d: -d['width_px'])
    return {'image': os.path.basename(path), 'foliage_pct': round(100 * float(foliage.mean()), 1), 'flat_pct_of_foliage': round(100 * float(flat.sum()) / max(1, float(foliage.sum())), 2),
            'max_flat_width_px': round(float(2 * dt.max()), 1), 'patches_wider_than_%d_px' % min_w: len(wide), 'widest': wide[:6]}

def main():
    args = sys.argv[1:]
    d, cj, out = args[:3]; rest = args[3:]
    flat_imgs, preview, mode = [], None, None
    for a in rest:
        if a == '--flat': mode = 'flat'
        elif a == '--preview': mode = 'preview'
        elif mode == 'preview': preview = a
        else: flat_imgs.append(a)
    C = json.load(open(cj)); res = {'crowns': [], 'reference': [], 'flat': []}
    for f, boxes in C.get('crowns', {}).items():
        p = os.path.join(d, f)
        if not os.path.exists(p): continue
        for c in crop_stats(p, boxes): c['image'] = f; res['crowns'].append(c)
    for p, boxes in C.get('reference', {}).items():
        if not os.path.exists(p): continue
        for c in crop_stats(p, boxes): c['image'] = os.path.basename(p); res['reference'].append(c)
    for p in flat_imgs:
        pp = p if os.path.exists(p) else os.path.join(d, p)
        if os.path.exists(pp): res['flat'].append(flat_faces(pp))
    sds = [c['hp_sd'] for c in res['crowns']]
    p1 = [f for f in res['flat'] if f['image'] in ('p1_south.jpg', 'p10_lawn_eye.jpg')]
    res['summary'] = {'crown_crops': len(sds), 'min_hp_sd': min(sds) if sds else None, 'median_hp_sd': round(float(np.median(sds)), 2) if sds else None, 'max_hp_sd': max(sds) if sds else None,
                      'pass_crown_sd_ge_9': bool(sds) and min(sds) >= 9.0,
                      'reference_hp_sd': [c['hp_sd'] for c in res['reference']],
                      'max_flat_width_px': {f['image']: f['max_flat_width_px'] for f in res['flat']},
                      'pass_no_flat_hull_face_gt_40px': bool(p1) and all(f['max_flat_width_px'] <= 40 for f in p1)}
    json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps(res['summary']))
    for c in res['crowns']: print('%-24s %-14s hp_sd %6.2f  luma %5.1f' % (c['image'], c['box_xywh'][:2], c['hp_sd'], c['mean_luma']))
    for f in res['flat']: print('flat', f['image'], 'max_flat_width', f['max_flat_width_px'], 'patches>40:', f['patches_wider_than_40_px'], 'flat%% of foliage %.2f' % f['flat_pct_of_foliage'])
    if preview and res['crowns']:
        by = {}
        for c in res['crowns']: by.setdefault(c['image'], []).append(c['box_xywh'])
        tiles = []
        for f, boxes in by.items():
            im = Image.open(os.path.join(d, f)).convert('RGB')
            for (x, y, w, h) in boxes: tiles.append(im.crop((x, y, x + w, y + h)).resize((300, 300), Image.LANCZOS))
        cols = 6; rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 300, rows * 300))
        for k, t in enumerate(tiles): sheet.paste(t, ((k % cols) * 300, (k // cols) * 300))
        sheet.save(preview)
if __name__ == '__main__': main()
