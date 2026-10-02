#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06 instruments for the sky stills (LOOK-SPEC L24 / L25 / L26), on tod_<pose>_<res>_<variant>.jpg stills (run_r06.py, capture_tour.py --tod).
  L24a  S4: sky band (rows 0-89 of the 1080-high frame, every column) brighter than the far-city band (the far-shore box of spec_regions.json 450,192,1350,236): sky Y - far Y > 0
        (L10 says 15..32 under the sky at golden hour; at the twilight hours the round-06 target is the sign)
  L24b  the still that faces the sun (S4w at dusk, S4e at dawn; S7 also reported at dusk): B-R of the sky band <= -20 at 06:30-07:30 and 19:00-20:30
  L25   S4m at 22:00 (moon-facing perch): the moon disk = connected blob of Y >= 200 around the moon's predicted pixel: equivalent diameter >= 12 px; sky high-pass std
        (Y - gaussian(Y, 6), sky box rows 0-250, moon disk +- 70 px excluded and included) >= 3; S4 itself: rows 0-89 high-pass std
  L26   S1 luma Pearson correlation (480x270 box resize) of the dawn still against the golden still (<= 0.6)
usage: twilight_check.py --dir <stills dir> [--out <json>] [--res 1920x1080] [--golden <S1 golden still>]
Hour of a still = the trailing 'h<number>' of its variant name (e.g. 'h19.5', 'v3_h20')."""
import argparse, glob, json, math, os, re, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FAR_BOX = (450, 192, 1350, 236)     # x0, y0, x1, y1 at 1080p: S4 far_shore of docs/night1/city/spec_regions.json
SKY_ROWS = 90


def load(p, w=1920):
    im = Image.open(p).convert('RGB')
    if im.size[0] != w: im = im.resize((w, int(round(im.size[1] * w / im.size[0]))), Image.BOX if im.size[0] > w else Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)


def Y(im): return 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]


def gblur(a, s):
    try:
        import cv2
        return cv2.GaussianBlur(a, (0, 0), s)
    except Exception:
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(a, s)


def band(im, rows=SKY_ROWS):
    b = im[:rows]
    y = Y(b)
    return {'Y': float(y.mean()), 'BR': float(b[..., 2].mean() - b[..., 0].mean()), 'R': float(b[..., 0].mean()), 'G': float(b[..., 1].mean()), 'B': float(b[..., 2].mean()),
            'p95': float(np.percentile(y, 95))}


def far_band(im):
    x0, y0, x1, y1 = FAR_BOX
    b = im[y0:y1, x0:x1]
    return {'Y': float(Y(b).mean()), 'BR': float(b[..., 2].mean() - b[..., 0].mean())}


def hp_std(y, mask=None, sigma=6.0):
    h = y - gblur(y, sigma)
    return float(h[mask].std()) if mask is not None else float(h.std())


def moon_pixel(pose, hour):
    """predicted pixel of the moon (1920x1080) for a sky pose, from the camera heading / pitch / fov of sky_poses.json and look_tod.py body_dir"""
    sys.path.insert(0, os.path.join(HERE, '..', '..', 'unreal', 'WebHomage', 'Scripts'))
    import look_tod
    doc = look_tod.load_doc(); T = doc['tod']
    el, az = look_tod.body_dir(T['moon'], hour, T['sun']['lat'])
    s = next(x for x in json.load(open(os.path.join(HERE, 'sky_poses.json'))) if x['id'].split('_')[0] == pose)
    dx, dy, dz = (s['target'][i] - s['pos'][i] for i in range(3))
    yaw = math.degrees(math.atan2(dx, -dz)); pitch = math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    f = 960.0 / math.tan(math.radians(s.get('fov', 70) / 2))
    # direction vectors in a camera frame (right, up, forward)
    def vec(e, a): e, a = math.radians(e), math.radians(a); return np.array([math.sin(a) * math.cos(e), math.sin(e), math.cos(a) * math.cos(e)])   # east, up, north
    cy, cp = math.radians(yaw), math.radians(pitch)
    fwd = np.array([math.sin(cy) * math.cos(cp), math.sin(cp), math.cos(cy) * math.cos(cp)])
    right = np.array([math.cos(cy), 0.0, -math.sin(cy)])
    up = np.array([-math.sin(cy) * math.sin(cp), math.cos(cp), -math.cos(cy) * math.sin(cp)])
    d = vec(el, az); z = float(d @ fwd)
    if z <= 0: return None, el, az
    return (960.0 + f * float(d @ right) / z, 540.0 - f * float(d @ up) / z), el, az


def moon_disk(im, pose, hour):
    pos, el, az = moon_pixel(pose, hour)
    if pos is None: return {'in_frame': False, 'elevation': el, 'azimuth': az}
    y = Y(im); H, W = y.shape
    px, py = pos
    if not (0 <= px < W and 0 <= py < H): return {'in_frame': False, 'predicted_px': [px, py], 'elevation': el, 'azimuth': az}
    r = 120
    x0, x1, y0, y1 = int(max(0, px - r)), int(min(W, px + r)), int(max(0, py - r)), int(min(H, py + r))
    sub = y[y0:y1, x0:x1]
    m = (sub >= 200).astype(np.uint8)
    out = {'in_frame': True, 'predicted_px': [round(px, 1), round(py, 1)], 'elevation': round(el, 1), 'azimuth': round(az, 1), 'peak_Y': float(sub.max())}
    try:
        import cv2
        n, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
        best = None
        for i in range(1, n):
            dist = math.hypot(cen[i][0] + x0 - px, cen[i][1] + y0 - py)
            if best is None or st[i, cv2.CC_STAT_AREA] > st[best, cv2.CC_STAT_AREA] * (1.0 if dist < r else 0.0): best = i
        area = float(st[best, cv2.CC_STAT_AREA]) if best else 0.0
        out.update({'blob_area_px': area, 'disk_diameter_px': round(2 * math.sqrt(area / math.pi), 1), 'blob_centre_px': [round(float(cen[best][0] + x0), 1), round(float(cen[best][1] + y0), 1)] if best else None})
    except Exception as e:
        out['error'] = str(e)
    return out


def hour_of(variant):
    m = re.search(r'h(\d+(?:\.\d+)?)$', variant)
    return float(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dir', required=True); ap.add_argument('--out', default=''); ap.add_argument('--res', default='1920x1080'); ap.add_argument('--golden', default='')
    a = ap.parse_args()
    rows = []
    for f in sorted(glob.glob(os.path.join(a.dir, 'tod_*_%s_*.jpg' % a.res))):
        m = re.match(r'tod_(S\d\w*)_%s_(.+)\.jpg' % a.res, os.path.basename(f))
        if not m: continue
        pose, var = m.group(1), m.group(2)
        h = hour_of(var)
        im = load(f)
        r = {'file': os.path.basename(f), 'pose': pose, 'variant': var, 'hour': h, 'sky': band(im)}
        if pose == 'S4':
            r['far'] = far_band(im); r['sky_minus_far_Y'] = r['sky']['Y'] - r['far']['Y']; r['L24a_pass'] = bool(r['sky_minus_far_Y'] > 0)
            r['sky_hp_std_rows0_89'] = hp_std(Y(im)[:SKY_ROWS])
            r['mean_Y'] = float(Y(im).mean())
        if pose in ('S4w', 'S4e', 'S7'):
            r['facing_sun_BR'] = r['sky']['BR']
            if h is not None:
                need = (6.5 <= h <= 7.5) if pose == 'S4e' else (19.0 <= h <= 20.5)
                r['L24b_applies'] = bool(need); r['L24b_pass'] = bool(r['sky']['BR'] <= -20.0) if need else None
            r['mean_Y'] = float(Y(im).mean())
        if pose == 'S4m' and h is not None:
            r['moon'] = moon_disk(im, pose, h)
            y = Y(im)
            box = np.zeros(y.shape, bool); box[:250] = True
            allm = box.copy()
            ex = box.copy()
            mp = r['moon'].get('predicted_px') if r['moon'].get('in_frame') else None
            if mp:
                yy, xx = np.mgrid[:y.shape[0], :y.shape[1]]
                ex &= ((xx - mp[0]) ** 2 + (yy - mp[1]) ** 2) > 70 ** 2
            r['sky_hp_std_box250_incl_moon'] = hp_std(y, allm); r['sky_hp_std_box250_excl_moon'] = hp_std(y, ex)
            r['mean_Y'] = float(y.mean())
            r['L25_pass'] = bool(r['moon'].get('disk_diameter_px', 0) >= 12 and r['moon'].get('peak_Y', 0) >= 200 and r['sky_hp_std_box250_excl_moon'] >= 3.0)
        rows.append(r)
    # L26
    cor = None
    s1 = {r['variant']: os.path.join(a.dir, r['file']) for r in rows if r['pose'] == 'S1'}
    g = a.golden or next((p for v, p in s1.items() if hour_of(v) is not None and abs(hour_of(v) - 18.4) < 0.05), None)
    if g:
        def lum(p): return Y(np.asarray(Image.open(p).convert('RGB').resize((480, 270), Image.BOX), dtype=np.float32))
        gl = lum(g)
        cor = {v: float(np.corrcoef(lum(p).ravel(), gl.ravel())[0, 1]) for v, p in s1.items() if hour_of(v) is not None and (6.0 <= hour_of(v) <= 8.5)}
    lines = ['| still | pose | hour | sky band Y | sky B-R | far Y | sky-far | L24a | L24b | mean Y | moon px | moon peak Y | hp std (excl / incl moon) |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        mo = r.get('moon') or {}
        lines.append('| %s | %s | %s | %.1f | %+.1f | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['variant'], r['pose'], r['hour'], r['sky']['Y'], r['sky']['BR'], ('%.1f' % r['far']['Y']) if 'far' in r else '', ('%+.1f' % r['sky_minus_far_Y']) if 'sky_minus_far_Y' in r else '',
            {True: 'ok', False: 'FAIL'}.get(r.get('L24a_pass'), ''), {True: 'ok', False: 'FAIL', None: ''}.get(r.get('L24b_pass'), ''), ('%.1f' % r['mean_Y']) if 'mean_Y' in r else '',
            ('%.1f' % mo['disk_diameter_px']) if 'disk_diameter_px' in mo else ('out of frame' if mo and not mo.get('in_frame') else ''), ('%.0f' % mo['peak_Y']) if 'peak_Y' in mo else '',
            ('%.2f / %.2f' % (r['sky_hp_std_box250_excl_moon'], r['sky_hp_std_box250_incl_moon'])) if 'sky_hp_std_box250_excl_moon' in r else (('%.2f' % r['sky_hp_std_rows0_89']) if 'sky_hp_std_rows0_89' in r else '')))
    print('\n'.join(lines))
    if cor: print('\nL26 S1 correlation vs golden (%s): ' % os.path.basename(g) + ', '.join('%s %.3f' % (k, v) for k, v in cor.items()))
    if a.out:
        json.dump({'rows': rows, 'L26_S1_corr_vs_golden': cor}, open(a.out + '.json', 'w'), indent=1)
        open(a.out + '.md', 'w').write('# Sky stills (twilight_check.py)\n\n> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.\n\n' + '\n'.join(lines) + '\n' +
                                       (('\nL26 S1 correlation vs golden %s: ' % os.path.basename(g) + ', '.join('%s %.3f' % (k, v) for k, v in cor.items()) + '\n') if cor else ''))


if __name__ == '__main__':
    main()
