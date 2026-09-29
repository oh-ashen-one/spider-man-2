"""Round-04 SPEC checks measured on OUR captures (pixels). Fan homage project; not official Marvel/Sony/Insomniac.
Needs opencv (+ ultralytics for `people`): run with a venv that has them.
  hero_run  CLIP t0 t1          step rate (bob FFT of the head top + bob minima), head-to-hip lean per frame (red/blue suit mask),
                                hero height / frame height                                              (CH2, CH6, CH7)
  takeoff   CLIP t0 t1          run -> jump: frames from the start of the crouch (mask height < 93 % of the running height) to the
                                last grounded frame (mask bottom leaves the ground line)                 (CH10)
  people    CLIP|IMG [step_s]   YOLO11x person boxes per sampled frame: count, count >= 3 % height, heights (CH11, CH12, CH16)
Same colour-mask approach as the round-03 critic's bob.py / hero_meas.py."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); from p2paths import scr as _scr  # noqa: E402
import numpy as np
import cv2


def frames(path, t0=0, t1=1e9):
    cap = cv2.VideoCapture(path); fps = cap.get(5); i = 0
    while True:
        ok, f = cap.read()
        if not ok: break
        t = i / fps; i += 1
        if t0 <= t <= t1: yield t, f, fps


def suit_mask(f):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); h, s, v = cv2.split(hsv)
    red = ((h < 8) | (h > 172)) & (s > 140) & (v > 60); blue = (h > 105) & (h < 130) & (s > 150) & (v > 40)
    m = (red | blue).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)); md = cv2.dilate(m, np.ones((25, 25), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(md)
    if n < 2: return None
    k = 1 + np.argmax(st[1:, 4])
    return (lab == k) & (m > 0)


def hero_run(path, t0, t1):
    rows = []
    for t, f, fps in frames(path, t0, t1):
        m = suit_mask(f)
        if m is None: continue
        ys, xs = np.nonzero(m); top, bot = ys.min(), ys.max(); H = bot - top
        hd = ys < top + 0.10 * H; band = (ys > top + 0.45 * H) & (ys < top + 0.52 * H)
        lean = abs(np.degrees(np.arctan2(xs[hd].mean() - xs[band].mean(), ys[band].mean() - ys[hd].mean())))
        rows.append((t, np.percentile(ys, 0.2), H / f.shape[0], lean))
    R = np.array(rows); fps = 1 / np.median(np.diff(R[:, 0]))
    T = R[:, 1] - np.convolve(R[:, 1], np.ones(31) / 31, 'same'); T = T[15:-15]
    F = np.abs(np.fft.rfft(T * np.hanning(len(T)))); fr = np.fft.rfftfreq(len(T), 1 / fps)
    sel = (fr > 1) & (fr < 6)
    from scipy.signal import find_peaks
    pk, _ = find_peaks(-T, distance=8, prominence=2)
    return dict(clip=path, t0=t0, t1=t1, frames=len(R), bob_fft_hz=round(float(fr[np.argmax(F * sel)]), 3),
                bob_minima_per_s=round(len(pk) / (len(T) / fps), 3), lean_median_deg=round(float(np.median(R[:, 3])), 1),
                lean_p10_deg=round(float(np.percentile(R[:, 3], 10)), 1), lean_min_deg=round(float(R[:, 3].min()), 1),
                hero_height_median=round(float(np.median(R[:, 2])), 3))


def takeoff(path, t0, t1):
    rows = []
    for t, f, fps in frames(path, t0, t1):
        m = suit_mask(f)
        if m is None: rows.append((t, np.nan, np.nan)); continue
        ys, _ = np.nonzero(m); rows.append((t, ys.max() - ys.min(), ys.max()))
    R = np.array(rows); H, B = R[:, 1], R[:, 2]
    run_h = np.nanmedian(H[:30]); ground = np.nanmedian(B[:30])
    lift = next(i for i in range(len(R)) if B[i] < ground - 0.04 * run_h and i > 5)          # feet 4 % of body height above the ground line
    last_ground = lift - 1
    c0 = last_ground
    while c0 > 0 and H[c0 - 1] < 0.93 * run_h: c0 -= 1
    return dict(clip=path, fps=round(1 / np.median(np.diff(R[:, 0])), 2), crouch_start_t=round(float(R[c0, 0]), 3), liftoff_t=round(float(R[lift, 0]), 3),
                anticipation_frames=int(lift - c0), min_height_ratio=round(float(np.nanmin(H[c0:lift + 1]) / run_h), 3) if lift > c0 else None)


def people(path, step=0.5):
    from ultralytics import YOLO
    import os
    m = YOLO(os.environ.get('YOLO_WEIGHTS', _scr('r4', 'spectools', 'yolo11x-seg.pt')))   # same weights as specs/tools
    out = []
    ims = [(0.0, cv2.imread(path))] if path.lower().endswith(('.jpg', '.png')) else None
    if ims is None:
        ims = []; last = -1e9
        for t, f, fps in frames(path):
            if t - last >= step - 1e-6: ims.append((t, f)); last = t
    for t, im in ims:
        r = m.predict(im, classes=[0], conf=0.35, verbose=False, device='mps', imgsz=1920)[0]
        b = r.boxes.xyxy.cpu().numpy(); hts = (b[:, 3] - b[:, 1]) / im.shape[0]
        out.append(dict(t=round(t, 2), people=int(len(hts)), people_h3=int((hts >= 0.03).sum()), heights=[round(float(x), 3) for x in sorted(hts, reverse=True)]))
    P3 = np.array([o['people_h3'] for o in out])
    return dict(clip=path, samples=len(out), people_h3_median=float(np.median(P3)), people_h3_min=int(P3.min()), people_h3_max=int(P3.max()), per_sample=out)


if __name__ == '__main__':
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd == 'hero_run': r = hero_run(a[0], float(a[1]), float(a[2]))
    elif cmd == 'takeoff': r = takeoff(a[0], float(a[1]), float(a[2]))
    else: r = people(a[0], float(a[1]) if len(a) > 1 else 0.5)
    print(json.dumps(r))
