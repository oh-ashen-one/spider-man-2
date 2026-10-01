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
  water_spec.py all <round_dir> [--json out.json]    every known capture in a round dir
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
    elif cmd == 'all':
        R = a[1]; res = {}
        for f in sorted(os.listdir(R)):
            p = os.path.join(R, f)
            if f.endswith(('.jpg', '.png')) and ('river' in f or 'harbour' in f) and not f.startswith('crop'):
                res[f] = near(p)
            if f.endswith(('.jpg', '.png')) and f.startswith('S4'):
                res[f] = s4(p)
            if f.endswith('.mp4'):
                res[f] = dolly(p)
        for k, v in res.items(): print(json.dumps(v))
        if '--json' in a: json.dump(res, open(a[a.index('--json') + 1], 'w'), indent=1)


if __name__ == '__main__':
    main()
