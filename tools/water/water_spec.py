#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Water acceptance numbers (docs/night1/director/PLAN-firstpass.md section 4 Water), measured the way the round-01 blind critic did.

Calibration (round-01 pack, docs/night1/water/critic/round-01-AB-CRITIC.md): the critic measured on the A/B pack, i.e. the 4K frame centre-cropped
to 84 % (3226 x 1814). Its 'near-water crop' is x 0-1500, y 1150-1800 of that frame. With high-pass = Y - GaussianBlur(sigma 8 px) this
reproduces its numbers for build O (mean 90.6, rgb 98/91/68, p99.5 117, high-pass sd 4.4) and G (4.2 vs 4.1). 'Glint pixels' = luma >= 140
(on the reference's water crops this gives 1.0-2.4 %, the critic quoted 2.2 %; >= 130 is printed too). Autocorrelation 'at 80 px' = dolly
frames as packed (84 % crop, 1612 px wide), water crop y 480-700, x 0-820, high-pass sigma 24 px, horizontal 80 px shift, mean over frames
at 10 fps (round-01 O 0.233 vs the critic's 0.25; G 0.016 vs 0.08).

usage:
  water_spec.py near <frame.png|jpg> [...]          near-crop numbers per frame (any resolution; resized to 3840x2160 first)
  water_spec.py dolly <clip.mp4>                     autocorrelation at 80 px + per-frame temporal change of the water crop
  water_spec.py s4 <S4 frame>                        CITY-SPEC C14 via tools/export/spec_farfield.py
  water_spec.py harbour <harbour_high frame>         (r03) harbour crop: high-pass sd, glints, pale blobs
  water_spec.py sparkle <river_sun frame>            (r03) sparkle width: % of frame width whose water column has >= 2 % of rows at Y >= 200
  water_spec.py sunhigh <harbour_sun_high frame>     (r04) glints from swing height: glint %, glitter-path column coverage, sparkle size
  water_spec.py foam <crop_river_low_4k_seawall_foam> [river_low_dolly.mp4]   (r04) contact-foam band along the seawall (+ its change at 4 fps)
  water_spec.py all <round_dir> [--json out.json]    every known capture in a round dir (+ PASS / FAIL against the r03 targets)

r03 additions (so builder and critic measure identically; calibrated on round-02 + refs):
  harbour crop   = x 0-2400, y 1300-2100 of the NATIVE 3840x2160 frame (not the 84 % pack crop: y 2100 lies outside the pack frame).
                   Round-02 harbour_high_4k: hp sd 4.33 (critic 4.4), glints 0 %, pale blobs 109 (critic 106).
  pale blob      = 8-connected component of >= 20 px whose pixels are >= 18 Y above the local mean (Gaussian sigma 24 px) with
                   chroma (max - min) / max <= 0.35 and whose brightest pixel is < 140 (dull pale patch = foam decal, not a glint).
  sparkle width  = in the pack frame (84 % centre crop), water rows = rows >= 45 % of the height; a column 'sparkles' when >= 2 % of its
                   water rows have Y >= 200; result = % of columns. Round-02 river_sun_4k 35.5 %, reference waterfront-perch-trailer 67.1 %
                   (critic: 35.5 / 66).
r04 additions:
  harbour crop   = x 0-2400, y 1300-2160 (the r03 critic's crop; r03 used y 1300-2100). Round-03 frame: hp sd 4.27 (critic 4.3).
  sunhigh        = harbour_sun_high_4k (harbour_high position, yaw 148 = toward the golden sun). Water crop x 0-3840, y 700-2160 of the native
                   frame (>= 6 deg below the horizon at pitch -14 / hFOV 75; the horizon is at y ~456, the sun's mirror point at y ~861).
                   glint = Y >= 200 AND high-pass (sigma 8) >= 30. Glitter-path columns = x 1480-2360 (sun azimuth +-10 deg; the sun is at the
                   frame centre column). Column coverage = % of path columns with >= 2 % of the crop rows at Y >= 200 (the r03 sparkle-width rule);
                   also reported with >= 1 glint pixel. Sparkle size = max(bbox w, h) of 8-connected glint components: median / p90 / count.
  foam band      = in crop_river_low_4k_seawall_foam.jpg (river_low_4k[1250:2160, 1500:2700]) the bulkhead edge is found per row (first run of
                   12 px with chroma >= 0.42, the orange timber) and fitted with a robust line; band width per row = pixels with Y >= 180 within
                   60 px water-side of the edge. Round 02 (foam present): mean 13.3 px, 37.4 % of rows >= 12 px, band Y 207; round 03: 0 / 0 %.
                   Dolly: the same line scaled to the 1080p dolly frames, sampled at 4 fps: band pixels per sample and the change between samples
                   (XOR / OR of the band masks).
Luma = Rec.709 on the 8-bit sRGB values."""
import json, os, subprocess, sys
import cv2, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(HERE))
NEAR = (0, 1500, 1150, 1800)          # x0, x1, y0, y1 in the 3226 x 1814 pack frame
DOLLY = (0, 820, 480, 700)            # in the 1612 x 906 pack frame


def luma(bgr):
    b, g, r = bgr[..., 0], bgr[..., 1], bgr[..., 2]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def pack_crop(img, w=3840, h=2160):
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_CUBIC if img.shape[1] < w else cv2.INTER_AREA)
    cw, ch = int(w * 0.84), int(h * 0.84)
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    return img[y0:y0 + ch, x0:x0 + cw]


def near(path):
    im = cv2.imread(path).astype(np.float32)
    src_w = im.shape[1]
    p = pack_crop(im)
    x0, x1, y0, y1 = NEAR
    c = p[y0:y1, x0:x1]; Y = luma(c)
    hp = Y - cv2.GaussianBlur(Y, (0, 0), 8)
    rgb = c.reshape(-1, 3).mean(0)[::-1]
    return dict(file=os.path.basename(path), src_width=src_w, mean_Y=round(float(Y.mean()), 1), rgb=[round(float(v), 1) for v in rgb],
                p1=round(float(np.percentile(Y, 1)), 1), p99_5=round(float(np.percentile(Y, 99.5)), 1), highpass_sd=round(float(hp.std()), 2),
                glint_pct_ge140=round(float((Y >= 140).mean() * 100), 2), glint_pct_ge130=round(float((Y >= 130).mean() * 100), 2),
                note='1080p frames are upscaled to 4K before the crop: high-pass / glint numbers read lower than on a native 4K frame' if src_w < 3840 else '')


HARBOUR = (0, 2400, 1300, 2160)       # x0, x1, y0, y1 in the native 3840 x 2160 frame (r04: the critic's crop, r03 checker used y1 2100)
SUNHIGH = (0, 3840, 700, 2160)        # r04 harbour_sun_high water crop (native 4K)
SUNPATH = (1480, 2360)                # glitter-path columns (sun azimuth +-10 deg at hFOV 75)
FOAMCROP = (1500, 1250)               # x0, y0 of crop_river_low_4k_seawall_foam in the native 4K river_low frame


def _frame4k(path):
    im = cv2.imread(path).astype(np.float32)
    if im.shape[1] != 3840: im = cv2.resize(im, (3840, 2160), interpolation=cv2.INTER_CUBIC if im.shape[1] < 3840 else cv2.INTER_AREA)
    return im


def pale_blobs(c, Y, dY=18.0, chroma=0.35, amin=20, glint=140.0):
    bg = cv2.GaussianBlur(Y, (0, 0), 24)
    mx, mn = c.max(2), c.min(2)
    m = ((Y - bg >= dY) & ((mx - mn) / np.maximum(mx, 1.0) <= chroma)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    peak = np.zeros(n); np.maximum.at(peak, lab.ravel(), Y.ravel())
    return int(sum(1 for i in range(1, n) if st[i, 4] >= amin and peak[i] < glint))


def harbour(path):
    im = _frame4k(path); x0, x1, y0, y1 = HARBOUR
    c = im[y0:y1, x0:x1]; Y = luma(c)
    hp = Y - cv2.GaussianBlur(Y, (0, 0), 8)
    return dict(file=os.path.basename(path), crop='native 4K x0-2400 y1300-2160', mean_Y=round(float(Y.mean()), 1),
                highpass_sd=round(float(hp.std()), 2), glint_pct_ge140=round(float((Y >= 140).mean() * 100), 2), pale_blobs_ge20px=pale_blobs(c, Y),
                p1=round(float(np.percentile(Y, 1)), 1), p99_5=round(float(np.percentile(Y, 99.5)), 1))


def sunhigh(path):
    im = _frame4k(path); x0, x1, y0, y1 = SUNHIGH
    c = im[y0:y1, x0:x1]; Y = luma(c); hp = Y - cv2.GaussianBlur(Y, (0, 0), 8)
    g = ((Y >= 200) & (hp >= 30)).astype(np.uint8)
    a, b = SUNPATH
    colf = (Y[:, a:b] >= 200).mean(0)
    n, lab, st, _ = cv2.connectedComponentsWithStats(g, 8)
    sz = np.array([max(st[i, 2], st[i, 3]) for i in range(1, n)]) if n > 1 else np.zeros(0)
    return dict(file=os.path.basename(path), crop='native 4K x0-3840 y700-2160, path columns x1480-2360', mean_Y=round(float(Y.mean()), 1),
                highpass_sd=round(float(hp.std()), 2), glint_pct=round(float(g.mean() * 100), 3),
                path_cols_pct_ge2pct_rows=round(float((colf >= 0.02).mean() * 100), 1), path_cols_pct_any=round(float((colf > 0).mean() * 100), 1),
                sparkles=int(len(sz)), sparkle_px_median=float(np.median(sz)) if len(sz) else None, sparkle_px_p90=float(np.percentile(sz, 90)) if len(sz) else None,
                p99_5=round(float(np.percentile(Y, 99.5)), 1))


def _wall_edge(im):
    mx, mn = im.max(2), im.min(2); ch = (mx - mn) / np.maximum(mx, 1.0); Y = luma(im)
    H = im.shape[0]; e = np.full(H, -1.0)
    for y in range(H):
        m = ((ch[y] > 0.42) & (Y[y] > 40)).astype(int); cv = np.convolve(m, np.ones(12, int), 'valid'); xs = np.where(cv >= 12)[0]
        if len(xs): e[y] = xs[0]
    ys = np.arange(H); ok = e >= 0
    A = np.polyfit(ys[ok], e[ok], 1); keep = ok & (np.abs(e - np.polyval(A, ys)) < 8); A = np.polyfit(ys[keep], e[keep], 1)
    return A, Y


def _band(Y, edge_x, win=60, thr=180.0):
    W = np.zeros(len(edge_x), int); M = np.zeros(Y.shape, bool)
    for y, ex in enumerate(edge_x):
        x = int(round(ex)); a = max(0, x - win)
        if x - 1 > a:
            m = Y[y, a:x - 1] >= thr; W[y] = int(m.sum()); M[y, a:x - 1] = m
    return W, M


def foam(path, dolly_path=None):
    im = cv2.imread(path).astype(np.float32)
    A, Y = _wall_edge(im); ys = np.arange(Y.shape[0])
    W, M = _band(Y, np.polyval(A, ys))
    out = dict(file=os.path.basename(path), edge_line=[round(float(A[0]), 4), round(float(A[1]), 1)], band_px_mean=round(float(W.mean()), 1),
               band_px_median=float(np.median(W)), rows_ge12px_pct=round(float((W >= 12).mean() * 100), 1),
               band_Y_mean=round(float(Y[M].mean()), 1) if M.any() else None)
    if dolly_path:
        cap = cv2.VideoCapture(dolly_path); fps = cap.get(cv2.CAP_PROP_FPS) or 60; step = max(1, int(round(fps / 4))); n = 0; px = []; ch = []; prev = None; rows = []
        while True:
            ok, fr = cap.read()
            if not ok: break
            n += 1
            if (n - 1) % step: continue
            s = fr.shape[1] / 3840.0                       # dolly frames are 1080p: the 4K crop line scaled
            y0, y1 = int(FOAMCROP[1] * s), fr.shape[0]
            Yd = luma(fr.astype(np.float32))[y0:y1]
            ex = (np.polyval(A, (np.arange(y0, y1) / s) - FOAMCROP[1]) + FOAMCROP[0]) * s
            Wd, Md = _band(Yd, ex, win=int(60 * s))
            px.append(int(Md.sum())); rows.append(float((Wd >= 12 * s).mean() * 100))
            if prev is not None:
                u = (Md | prev).sum(); ch.append(float((Md ^ prev).sum() / u) if u else 0.0)
            prev = Md
        out.update(dolly=os.path.basename(dolly_path), dolly_samples_4fps=len(px), dolly_band_px_mean=round(float(np.mean(px)), 1) if px else None,
                   dolly_samples_with_band_pct=round(float(np.mean([p >= 50 for p in px]) * 100), 1) if px else None,
                   dolly_band_change_xor_over_or=round(float(np.mean(ch)), 3) if ch else None,
                   dolly_band_change_min=round(float(np.min(ch)), 3) if ch else None,
                   dolly_rows_ge6px_pct_min=round(float(np.min(rows)), 1) if rows else None, dolly_rows_ge6px_pct_mean=round(float(np.mean(rows)), 1) if rows else None)
    return out


# ---------------------------------------------------------------------------------------------------- r05 (critic r04 gate + merge-blockers)
HARBOUR_REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'night1', 'water', 'round-04', 'harbour_high_4k.jpg')
ISLAND_X = (1250, 2300)        # harbour_high native 4K: the island's south seawall (the edge found in the foam-free round-04 frame)
UNDER, OPEN = (1400, 1800), (1000, 1250)   # harbour_high: water under the island vs open water ~400 px to its left, rows 960-1100


def island_edge(ref_path):
    """per-column y of the island seawall / water edge in a foam-free harbour_high_4k frame (the camera is static: geometry is identical)"""
    Y = cv2.GaussianBlur(luma(_frame4k(ref_path)), (0, 0), 1.5)
    xs = np.arange(*ISLAND_X); e = np.full(len(xs), np.nan)
    for i, x in enumerate(xs):
        col = Y[700:1150, x]; g = col[:-4] - col[4:]; idx = np.where(g >= 14)[0]
        if len(idx): e[i] = 700 + idx.max() + 2
    m = np.isfinite(e); med = np.copy(e)
    for i in range(len(xs)):
        w = e[max(0, i - 40):i + 41]; w = w[np.isfinite(w)]
        med[i] = np.median(w) if len(w) else np.nan
    ok = m & (np.abs(e - med) <= 6)
    return xs, np.where(ok, e, med)


def harbour_line(path, ref_path):
    """bright contact line along the island seawall: per column, pixels 2..14 px below the reference edge with Y >= the column's water
    median (rows +25..+70) + 25 and Y >= 110; a column has a line when >= 3 such pixels"""
    Y = luma(_frame4k(path)); xs, e = island_edge(ref_path); W = []
    for x, ey in zip(xs, e):
        if not np.isfinite(ey): continue
        ey = int(ey); wref = np.median(Y[ey + 25:ey + 70, x])
        seg = Y[ey + 2:ey + 15, x]; W.append(int(((seg >= wref + 25) & (seg >= 110)).sum()))
    W = np.array(W)
    return dict(file=os.path.basename(path), edge_ref=os.path.basename(ref_path), columns=int(len(W)), line_px_median=float(np.median(W)) if len(W) else None,
                cols_ge3px_pct=round(float((W >= 3).mean() * 100), 1) if len(W) else None)


def under_island(path):
    """reflection merge-blocker: mean Y of the water under the island (x 1400-1800) vs open water ~400 px left (x 1000-1250), rows 960-1100,
    and the spread of 100-px column means over x 1000-2800 (the island's mirrored streaks; r03 43, r04 22)"""
    Y = luma(_frame4k(path))[960:1100]
    u, o = float(Y[:, UNDER[0]:UNDER[1]].mean()), float(Y[:, OPEN[0]:OPEN[1]].mean())
    cm = [float(Y[:, x:x + 100].mean()) for x in range(1000, 2800, 100)]
    return dict(under_Y=round(u, 1), open_Y=round(o, 1), open_minus_under=round(o - u, 1), streak_spread=round(max(cm) - min(cm), 1))


def sun_colour(path):
    """harbour_sun_high colour merge-blocker: p1 and mean R-B of the water crop (x 0-3840, y 700-2160 without the far shore strip x > 3000,
    y < 880), and of its upper band y 700-1100 (the bright brass)"""
    im = _frame4k(path); out = {}
    for nm, (y0, y1) in (('crop', (700, 2160)), ('upper', (700, 1100))):
        c = im[y0:y1].copy(); m = np.ones(c.shape[:2], bool)
        if y0 < 880: m[:880 - y0, 3000:] = False
        Y = luma(c)[m]; rb = (c[..., 2] - c[..., 0])[m]
        out[nm] = dict(p1=round(float(np.percentile(Y, 1)), 1), R_minus_B=round(float(rb.mean()), 1), mean_RGB=[round(float(c[..., k][m].mean())) for k in (2, 1, 0)])
    return out


def sparkle(path, thr=200.0, frac=0.02, horizon=0.45):
    p = pack_crop(cv2.imread(path).astype(np.float32))
    Y = luma(p); h0 = int(Y.shape[0] * horizon)
    col = (Y[h0:] >= thr).mean(0)
    return dict(file=os.path.basename(path), sparkle_width_pct=round(float((col >= frac).mean() * 100), 1))


def _ac(c, dx):
    a = c[:, :-dx]; b = c[:, dx:]; a = a - a.mean(); b = b - b.mean()
    return float((a * b).mean() / np.sqrt((a * a).mean() * (b * b).mean()))


def dolly(path, fps_keep=10):
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS) or 60
    step = max(1, int(round(fps / fps_keep))); n = 0; acs = []; dts = []; prev = None
    x0, x1, y0, y1 = DOLLY
    while True:
        ok, im = cap.read()
        if not ok: break
        n += 1
        if (n - 1) % step: continue
        im = im.astype(np.float32)
        h, w = im.shape[:2]; cw, ch = int(w * 0.84), int(h * 0.84)
        p = im[(h - ch) // 2:(h - ch) // 2 + ch, (w - cw) // 2:(w - cw) // 2 + cw]
        if p.shape[1] > 1612: p = cv2.resize(p, (1612, int(round(p.shape[0] * 1612 / p.shape[1]))), interpolation=cv2.INTER_AREA)
        Y = luma(p)[y0:y1, x0:x1]
        acs.append(_ac(Y - cv2.GaussianBlur(Y, (0, 0), 24), 80))
        if prev is not None: dts.append(float(np.abs(Y - prev).mean()))
        prev = Y
    return dict(file=os.path.basename(path), frames=n, sampled=len(acs), autocorr_80px=round(float(np.mean(acs)), 3),
                autocorr_80px_max=round(float(np.max(acs)), 3), water_dT_per_sample=round(float(np.mean(dts)), 2) if dts else None)


def s4(path):
    js = path + '.farfield.json'
    out = subprocess.run([sys.executable, os.path.join(WT, 'tools', 'export', 'spec_farfield.py'), path, js], capture_output=True, text=True)
    d = json.load(open(js))
    return dict(file=os.path.basename(path), C14=d['spec']['C14 far-shore Y minus river Y (target 5..35)'], far_shore_Y=round(d['regions']['far_shore']['Y'], 1),
                river_Y=round(d['regions']['river']['Y'], 1), farfield_json=os.path.basename(js))


def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return
    cmd = a[0]
    if cmd == 'near':
        for f in a[1:]: print(json.dumps(near(f)))
    elif cmd == 'dolly':
        for f in a[1:]: print(json.dumps(dolly(f)))
    elif cmd == 's4':
        for f in a[1:]: print(json.dumps(s4(f)))
    elif cmd == 'harbour':
        for f in a[1:]: print(json.dumps(harbour(f)))
    elif cmd == 'sparkle':
        for f in a[1:]: print(json.dumps(sparkle(f)))
    elif cmd == 'sunhigh':
        for f in a[1:]: print(json.dumps(sunhigh(f)))
    elif cmd == 'line':
        print(json.dumps(harbour_line(a[1], a[2] if len(a) > 2 else HARBOUR_REF)))
    elif cmd == 'under':
        for f in a[1:]: print(json.dumps(dict(file=os.path.basename(f), **under_island(f))))
    elif cmd == 'suncolour':
        for f in a[1:]: print(json.dumps(dict(file=os.path.basename(f), **sun_colour(f))))
    elif cmd == 'foam':
        print(json.dumps(foam(a[1], a[2] if len(a) > 2 else None)))
    elif cmd == 'all':
        R = a[1]; res = {}
        for f in sorted(os.listdir(R)):
            p = os.path.join(R, f)
            if f.endswith(('.jpg', '.png')) and ('river' in f or 'harbour' in f) and not f.startswith('crop'):
                res[f] = near(p)
                if f == 'river_low_4k.jpg':
                    import farshore
                    res[f]['farshore'] = farshore.score(p)
                if 'harbour_high' in f:
                    res[f]['harbour'] = harbour(p); res[f]['under_island'] = under_island(p)
                    if f == 'harbour_high_4k.jpg' and os.path.exists(HARBOUR_REF): res[f]['contact_line'] = harbour_line(p, HARBOUR_REF)
                if 'harbour_sun_high' in f: res[f]['sunhigh'] = sunhigh(p); res[f]['sun_colour'] = sun_colour(p)
                if 'river_sun' in f: res[f].update(sparkle(p))
            if f.endswith(('.jpg', '.png')) and f.startswith('S4'):
                res[f] = s4(p)
            if f.endswith('.mp4'):
                res[f] = dolly(p)
            if f == 'crop_river_low_4k_seawall_foam.jpg':
                d = os.path.join(R, 'river_low_dolly.mp4')
                res[f] = foam(p, d if os.path.exists(d) else None)
        for k, v in res.items(): print(json.dumps(v))
        res['_checks_r03'] = checks(res)
        res['_checks_r04'] = checks_r04(res)
        print('-- r03 targets'); [print('%-4s %-58s %s' % ('PASS' if c[2] else 'FAIL', c[0], c[1])) for c in res['_checks_r03']]
        print('-- r04 round targets'); [print('%-4s %-58s %s' % ('PASS' if c[2] else 'FAIL', c[0], c[1])) for c in res['_checks_r04']]
        res['_checks_r05'] = checks_r05(res)
        print('-- r05 round targets'); [print('%-4s %-66s %s' % ('PASS' if c[2] else 'FAIL', c[0], c[1])) for c in res['_checks_r05']]
        if '--json' in a: json.dump(res, open(a[a.index('--json') + 1], 'w'), indent=1)


def checks(res):
    """round-03 targets (4K frames only; perf is checked from perf.json separately)"""
    out = []
    def add(name, v, ok): out.append((name, v, bool(ok)))
    r = res.get('river_low_4k.jpg')
    if r:
        add('river_low near hp sd >= 12', r['highpass_sd'], r['highpass_sd'] >= 12); add('river_low near p99.5 >= 150', r['p99_5'], r['p99_5'] >= 150)
        add('river_low near glints >= 1 %', r['glint_pct_ge140'], r['glint_pct_ge140'] >= 1); add('river_low near mean Y <= 80', r['mean_Y'], r['mean_Y'] <= 80)
        add('river_low near p1 <= 25', r['p1'], r['p1'] <= 25)
    r = res.get('river_sun_4k.jpg')
    if r:
        add('river_sun sparkle width >= 50 %', r['sparkle_width_pct'], r['sparkle_width_pct'] >= 50)
        add('river_sun near mean Y <= 90', r['mean_Y'], r['mean_Y'] <= 90); add('river_sun near glints 3..15 %', r['glint_pct_ge140'], 3 <= r['glint_pct_ge140'] <= 15)
    r = res.get('harbour_high_4k.jpg')
    if r:
        h = r['harbour']
        add('harbour crop hp sd >= 10', h['highpass_sd'], h['highpass_sd'] >= 10); add('harbour crop glints >= 2 %', h['glint_pct_ge140'], h['glint_pct_ge140'] >= 2)
        add('harbour crop pale blobs (>= 20 px) == 0', h['pale_blobs_ge20px'], h['pale_blobs_ge20px'] == 0)
    for k in ('river_low_dolly.mp4', 'river_sun_dolly.mp4'):
        if k in res: add('%s autocorr at 80 px <= 0.10' % k, res[k]['autocorr_80px'], res[k]['autocorr_80px'] <= 0.10)
    r = res.get('S4_golden_4k.jpg')
    if r: add('S4 C14 5..35', r['C14'], 5 <= r['C14'] <= 35)
    return out


def checks_r04(res):
    """round-04 targets (docs/night1/water/SHOTLIST.md; perf from perf.json separately). river_low p99.5 / glints and the S4 haze band are
    sky-ceiling items (look piece), not scored here."""
    out = []
    def add(name, v, ok): out.append((name, v, bool(ok)))
    r = res.get('harbour_high_4k.jpg')
    if r:
        h = r['harbour']
        add('harbour_high crop hp sd >= 10', h['highpass_sd'], h['highpass_sd'] >= 10)
        add('harbour_high crop pale blobs (>= 20 px) == 0', h['pale_blobs_ge20px'], h['pale_blobs_ge20px'] == 0)
    r = res.get('harbour_sun_high_4k.jpg')
    if r:
        h = r['sunhigh']
        add('harbour_sun_high glints (Y>=200, hp>=30) >= 0.5 %', h['glint_pct'], h['glint_pct'] >= 0.5)
        add('harbour_sun_high path columns with Y>=200 >= 50 %', h['path_cols_pct_ge2pct_rows'], h['path_cols_pct_ge2pct_rows'] >= 50)
        add('harbour_sun_high sparkle size median <= 6 px', h['sparkle_px_median'], h['sparkle_px_median'] is not None and h['sparkle_px_median'] <= 6)
    r = res.get('crop_river_low_4k_seawall_foam.jpg')
    if r:
        add('seawall foam band mean >= 12 px (Y >= 180)', r['band_px_mean'], r['band_px_mean'] >= 12)
        add('seawall foam rows with >= 12 px band >= 30 %', r['rows_ge12px_pct'], r['rows_ge12px_pct'] >= 30)
        if r.get('dolly_band_change_xor_over_or') is not None:
            add('seawall foam changes between 4 fps dolly samples (xor/or >= 0.3)', r['dolly_band_change_xor_over_or'], r['dolly_band_change_xor_over_or'] >= 0.3)
    r = res.get('river_low_4k.jpg')
    if r:
        add('river_low near hp sd >= 9.9 (hold)', r['highpass_sd'], r['highpass_sd'] >= 9.9); add('river_low near mean Y <= 80 (hold)', r['mean_Y'], r['mean_Y'] <= 80)
    for k in ('river_low_dolly.mp4', 'river_sun_dolly.mp4'):
        if k in res: add('%s autocorr at 80 px <= 0.10 (hold)' % k, res[k]['autocorr_80px'], res[k]['autocorr_80px'] <= 0.10)
    r = res.get('S4_golden_4k.jpg')
    if r: add('S4 C14 5..35 (hold)', r['C14'], 5 <= r['C14'] <= 35)
    return out


def checks_r05(res):
    """round-05 targets (critic r04 'Pass when' + merge-blockers + holds; docs/night1/water/SHOTLIST.md)"""
    out = []
    def add(name, v, ok): out.append((name, v, bool(ok)))
    r = res.get('crop_river_low_4k_seawall_foam.jpg')
    if r:
        add('GATE seawall band >= 12 px (Y >= 180) on >= 60 % of wall rows', r['rows_ge12px_pct'], r['rows_ge12px_pct'] >= 60)
        if r.get('dolly_rows_ge6px_pct_min') is not None:
            # presence per frame = >= 50 band pixels against the still's wall line; the row share is informative only (the dolly camera moves
            # 32 m along the wall, so the static edge line leaves the wall near the pier corner late in the clip)
            add('GATE band present in every 4 fps dolly frame (>= 50 band px; min row share at 1080p reported)', [r['dolly_samples_with_band_pct'], r['dolly_rows_ge6px_pct_min']],
                r['dolly_samples_with_band_pct'] >= 100)
            add('GATE band change between consecutive 4 fps frames xor/or >= 0.2 (every pair: min; mean reported)', [r['dolly_band_change_min'], r['dolly_band_change_xor_over_or']],
                r['dolly_band_change_min'] >= 0.2)
    r = res.get('harbour_high_4k.jpg')
    if r:
        if r.get('contact_line'):
            c = r['contact_line']; add('GATE harbour_high contact line >= 3 px on >= 50 % of island seawall columns', c['cols_ge3px_pct'], (c['cols_ge3px_pct'] or 0) >= 50)
        u = r['under_island']; add('BLOCKER harbour_high water under the island >= 15 Y darker than open water', u['open_minus_under'], u['open_minus_under'] >= 15)
        h = r['harbour']; add('HOLD harbour_high crop hp sd >= 7.5', h['highpass_sd'], h['highpass_sd'] >= 7.5)
    r = res.get('harbour_sun_high_4k.jpg')
    if r:
        c = r['sun_colour']['crop']; add('BLOCKER harbour_sun_high p1 <= 55', c['p1'], c['p1'] <= 55); add('BLOCKER harbour_sun_high R-B <= 70', c['R_minus_B'], c['R_minus_B'] <= 70)
        h = r['sunhigh']
        add('HOLD harbour_sun_high glints >= 0.5 %', h['glint_pct'], h['glint_pct'] >= 0.5)
        add('HOLD harbour_sun_high path columns Y>=200 >= 50 %', h['path_cols_pct_ge2pct_rows'], h['path_cols_pct_ge2pct_rows'] >= 50)
        add('HOLD harbour_sun_high median sparkle <= 6 px', h['sparkle_px_median'], h['sparkle_px_median'] is not None and h['sparkle_px_median'] <= 6)
    r = res.get('river_low_4k.jpg')
    if r:
        add('HOLD river_low near hp sd >= 12', r['highpass_sd'], r['highpass_sd'] >= 12); add('HOLD river_low near mean Y <= 80', r['mean_Y'], r['mean_Y'] <= 80)
    if r and r.get('farshore'):
        # r05b: the far contact line must not paint a white bar over the far quay at river level (r03 4.2 %, r05 first build 13.3 %)
        add('GUARD river_low far-water strip bright (Y >= 170) share <= r03 + 3 pp', r['farshore']['bright_bar_pct'], r['farshore']['bright_bar_pct'] <= 4.16 + 3.0)
    r = res.get('river_low_dolly.mp4')
    if r: add('HOLD river_low_dolly autocorr 80 px <= 0.10', r['autocorr_80px'], r['autocorr_80px'] <= 0.10)
    r = res.get('S4_golden_4k.jpg')
    if r: add('HOLD S4 C14 5..35', r['C14'], 5 <= r['C14'] <= 35)
    r = res.get('river_sun_4k.jpg')
    if r: add('HOLD river_sun sparkle width >= 50 %', r['sparkle_width_pct'], r['sparkle_width_pct'] >= 50)
    return out


if __name__ == '__main__':
    main()
