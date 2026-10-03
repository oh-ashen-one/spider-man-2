#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Terrain r06 checks (CPU only) on the 4K stills.
  hull   <p10.jpg> [out.json]   r05 critic secondary 1 / r06 target 4: no sky-bordered foliage patch wider than 30 px with hp3 SD < 5.
         hp3 = luma - Gaussian(luma, sigma 3); local SD = std of hp3 in a 15 x 15 window. Sky = luma > 110 and HSV saturation < 0.3 in the upper 32 % of the frame (HULL_YMAX) (the golden sky reads ~(146, 135, 116));
         foliage = not sky, saturation > 0.4 and hue 48-170 deg (sunlit facades read hue 33-36; the dark low-saturation lamp heads are not foliage), same band. Smooth = foliage with local SD < 5. A smooth component counts when it is within 12 px of sky (the 15 px SD window rises at the sky edge itself);
         its width = max horizontal / vertical extent of the component (bounding box). Reported: every counted component >= 10 px, PASS if none is wider than 30 px.
  boxes  <p4.jpg> <out.json> <shot> x,y [x,y ...] --lit x0,y0,x1,y1   r06 target 2: for each tree point, the darkest 15 x 15 LAWN box (local hp3 SD < 6, i.e. not leaf crown) whose centre lies within 60 px of the point on
         the anti-sun side (image direction of the 9 deg / az 238 sun's ground shadow, from the shot camera in docs/night1/terrain/shots.json); ratio = box mean luma / lit lawn luma
         (median of the --lit box). PASS: <= 0.6 for every tree. A preview with the boxes is written next to out.json.
  ratio  <img> <out.json> name:x0,y0,x1,y1:lx0,ly0,lx1,ly1 [...]   plain shadow box / lit box mean-luma ratios (p6 esplanade)."""
import sys, json, math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, uniform_filter, label, binary_dilation

def luma(a): return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(np.float32)

YMAX = float(os.environ.get('HULL_YMAX', '0.32'))   # p10: the crowns stand against the sky above y ~ 690 (below: the dark tree line / lawn, no sky)
def hull(path, out=None):
    im = load(path); Y = luma(im); H, W = Y.shape
    mx = im.max(2); mn = im.min(2); sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    hue = (np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) + 360) % 360
    top = np.zeros_like(Y, bool); top[:int(H * YMAX)] = True
    sky = (Y > 110) & (sat < 0.3) & top
    fol = (~sky) & top & (sat > 0.4) & (hue > 48) & (hue < 170)
    hp = Y - gaussian_filter(Y, 3)
    m1 = uniform_filter(hp, 15); m2 = uniform_filter(hp * hp, 15); sd = np.sqrt(np.maximum(m2 - m1 * m1, 0))
    smooth = fol & (sd < 5)
    near_sky = binary_dilation(sky, iterations=12)
    lab, n = label(smooth)
    res = []
    if n:
        touch = np.unique(lab[near_sky & smooth]); touch = touch[touch > 0]
        for k in touch:
            ys, xs = np.nonzero(lab == k)
            w = int(max(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1))
            if w >= 10: res.append(dict(width_px=w, bbox=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], n_px=int(len(xs)), mean_sd=round(float(sd[ys, xs].mean()), 2), mean_luma=round(float(Y[ys, xs].mean()), 1)))
    res.sort(key=lambda d: -d['width_px'])
    o = dict(image=os.path.basename(path), rule='sky-bordered foliage patch, local hp3 SD < 5, width > 30 px, y < %d' % int(H * YMAX), widest=(res[0]['width_px'] if res else 0), n_over_30=sum(1 for d in res if d['width_px'] > 30), patches=res[:20])
    o['pass'] = o['n_over_30'] == 0
    print(json.dumps({k: v for k, v in o.items() if k != 'patches'}), res[:5])
    if out: json.dump(o, open(out, 'w'), indent=1)
    return o

def cam_dir(shot, px, py, W=3840, H=2160, elev=9.0, az=238.0):
    S = [s for s in json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'night1', 'terrain', 'shots.json')))['shots'] if s['id'] == shot][0]
    C = np.array(S['pos'], float); T = np.array(S['target'], float)
    F = T - C; F /= np.linalg.norm(F); up = np.array([0, 0, 1.0])
    R = np.cross(up, F); R /= np.linalg.norm(R); U = np.cross(F, R)   # UE is left-handed (X east, Y south, Z up): camera right = up x forward
    f = (W / 2) / math.tan(math.radians(S.get('fov', 66) / 2))
    d = F + R * ((px - W / 2) / f) + U * (-(py - H / 2) / f); d /= np.linalg.norm(d)
    G = C + (-C[2] / d[2]) * d
    def proj(P): v = P - C; z = v @ F; return np.array([W / 2 + f * (v @ R) / z, H / 2 - f * (v @ U) / z])
    a = math.radians(az); s = np.array([-math.sin(a), math.cos(a), 0.0])
    v = proj(G + s * 10.0) - proj(G)
    return v / np.linalg.norm(v), float(np.linalg.norm(v)), G

SD_LAWN = float(os.environ.get('SD_LAWN', '6.0'))
def boxes(path, out, shot, pts, lit):
    im = load(path); Y = luma(im)
    x0, y0, x1, y1 = lit; L = float(np.median(Y[y0:y1, x0:x1]))
    m = uniform_filter(Y, 15)
    hp = Y - gaussian_filter(Y, 3); m1 = uniform_filter(hp, 15); sd = np.sqrt(np.maximum(uniform_filter(hp * hp, 15) - m1 * m1, 0))
    res = []
    for (px, py) in pts:
        u, pxm, G = cam_dir(shot, px, py)
        best = None
        for cy in range(py - 60, py + 61):
            for cx in range(px - 60, px + 61):
                dx, dy = cx - px, cy - py
                if dx * dx + dy * dy > 3600 or dx * u[0] + dy * u[1] <= 0: continue
                if sd[cy, cx] >= SD_LAWN: continue   # lawn box only: leaf crowns carry hp3 SD 8-20 at this range, the aerial lawn 2-5
                v = float(m[cy, cx])
                if best is None or v < best[0]: best = (v, cx, cy)
        if best is None: res.append(dict(tree=[px, py], box_centre=None, ratio=9.9, note='no lawn box (hp3 SD < %.1f) in the half disc' % SD_LAWN)); continue
        res.append(dict(tree=[px, py], anti_sun_dir_img=[round(float(u[0]), 3), round(float(u[1]), 3)], px_per_10m_shadow=round(pxm, 1), ground_m=[round(float(G[0]), 1), round(float(G[1]), 1)],
                        box_centre=[best[1], best[2]], box_luma=round(best[0], 1), lit_luma=round(L, 1), ratio=round(best[0] / L, 3)))
    o = dict(image=os.path.basename(path), lit_box=lit, rule='darkest 15 px lawn box (local hp3 SD < %.1f) within 60 px on the anti-sun side <= 0.6 x lit lawn (median of the lit box)' % SD_LAWN, trees=res, pass_all=all(r['ratio'] <= 0.6 for r in res))
    print(json.dumps(o, indent=1)); json.dump(o, open(out, 'w'), indent=1)
    pv = Image.open(path).convert('RGB'); d = ImageDraw.Draw(pv)
    d.rectangle(lit, outline=(0, 160, 255), width=3)
    for r in [r for r in res if r.get('box_centre')]:
        (px, py), (cx, cy) = r['tree'], r['box_centre']
        d.ellipse([px - 60, py - 60, px + 60, py + 60], outline=(255, 255, 0), width=2); d.rectangle([cx - 7, cy - 7, cx + 7, cy + 7], outline=(255, 0, 0), width=2)
    xs = [r['tree'][0] for r in res]; ys = [r['tree'][1] for r in res]
    pv.crop((max(0, min(xs) - 400), max(0, min(ys) - 300), min(pv.width, max(xs) + 400), min(pv.height, max(ys) + 300))).save(out.replace('.json', '_preview.jpg'), quality=90)
    return o

def ratio(path, out, specs):
    Y = luma(load(path)); res = []
    for s in specs:
        nm, a, b = s.split(':'); a = [int(v) for v in a.split(',')]; b = [int(v) for v in b.split(',')]
        sh = float(Y[a[1]:a[3], a[0]:a[2]].mean()); li = float(Y[b[1]:b[3], b[0]:b[2]].mean())
        res.append(dict(name=nm, shadow_box=a, lit_box=b, shadow=round(sh, 1), lit=round(li, 1), ratio=round(sh / li, 3)))
    o = dict(image=os.path.basename(path), boxes=res, pass_all=all(r['ratio'] <= 0.6 for r in res)); print(json.dumps(o, indent=1)); json.dump(o, open(out, 'w'), indent=1)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'hull': hull(a[1], a[2] if len(a) > 2 else None)
    elif a[0] == 'boxes':
        li = a.index('--lit'); lit = [int(v) for v in a[li + 1].split(',')]; rest = a[4:li]
        boxes(a[1], a[2], a[3], [tuple(int(v) for v in p.split(',')) for p in rest], lit)
    elif a[0] == 'ratio': ratio(a[1], a[2], a[3:])
