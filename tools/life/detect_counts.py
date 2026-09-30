# Homage fan game tooling (not affiliated with Marvel/Sony/Insomniac). P6 city life: the spec instrument.
# Same model / classes / threshold / imgsz as docs/night1/specs/tools/count_people_vehicles.py (YOLO11x-seg, classes person+car/motorcycle/bus/truck,
# conf 0.35, imgsz 1920, MPS), but on our own captures (stills and clips, any path). Clips are sampled every 0.5 s like the spec tool.
#   python detect_counts.py [--json out.json] [--every 0.5] file.jpg|png|mp4 ...
# Needs a venv with ultralytics + opencv (this piece: /Users/midir/sm2-n1/_scratch/life/venv) and the weights (yolo11x-seg.pt).
import sys, os, json, argparse, numpy as np, cv2
from ultralytics import YOLO
ap = argparse.ArgumentParser(); ap.add_argument('files', nargs='+'); ap.add_argument('--json'); ap.add_argument('--every', type=float, default=0.5)
ap.add_argument('--weights', default=os.environ.get('YOLO_WEIGHTS', '/Users/midir/sm2-n1/_scratch/city/yolo/yolo11x-seg.pt')); ap.add_argument('--device', default='mps')
ap.add_argument('--boxes', action='store_true'); ap.add_argument('--annot', help='write annotated frames of stills into this dir')
a = ap.parse_args()
m = YOLO(a.weights)
def det(im):
    r = m.predict(im, classes=[0, 2, 3, 5, 7], conf=0.35, verbose=False, device=a.device, imgsz=1920)[0]
    cls = r.boxes.cls.cpu().numpy(); b = r.boxes.xyxy.cpu().numpy(); hts = (b[:, 3] - b[:, 1]) / im.shape[0]
    ppl = hts[cls == 0]
    d = dict(people=int((cls == 0).sum()), people_h3=int((ppl >= 0.03).sum()), people_h10=int((ppl >= 0.10).sum()), vehicles=int(np.isin(cls, [2, 3, 5, 7]).sum()),
             buses=int((cls == 5).sum()), trucks=int((cls == 7).sum()), ph=[round(float(x), 3) for x in sorted(ppl, reverse=True)[:8]])
    if a.boxes: d['boxes'] = [[int(c), *map(int, bb)] for c, bb in zip(cls, b)]
    return d, r
out = {}
for f in a.files:
    name = os.path.basename(f)
    if f.lower().endswith(('.mp4', '.mov', '.mkv')):
        cap = cv2.VideoCapture(f); fps = cap.get(5); step = max(1, int(round(fps * a.every))); i = 0; rows = []
        while True:
            ok, im = cap.read()
            if not ok: break
            if i % step == 0:
                d, _ = det(im); d['t'] = round(i / fps, 2); rows.append(d)
            i += 1
        P = np.array([r['people'] for r in rows]); P3 = np.array([r['people_h3'] for r in rows]); V = np.array([r['vehicles'] for r in rows])
        s = dict(n=len(rows), people_p10=float(np.percentile(P, 10)), people_med=float(np.median(P)), people_p90=float(np.percentile(P, 90)), people_h3_med=float(np.median(P3)),
                 veh_p10=float(np.percentile(V, 10)), veh_med=float(np.median(V)), veh_p90=float(np.percentile(V, 90)), veh_max=int(V.max()))
        print(f"{name:40s} n{s['n']} people p10 {s['people_p10']:.0f} med {s['people_med']:.0f} p90 {s['people_p90']:.0f} | >=3%H med {s['people_h3_med']:.0f} | vehicles p10 {s['veh_p10']:.0f} med {s['veh_med']:.0f} p90 {s['veh_p90']:.0f} max {s['veh_max']}", flush=True)
        out[name] = dict(summary=s, rows=rows)
    else:
        im = cv2.imread(f)
        d, r = det(im); print(f"{name:40s} people {d['people']} (>=3%H {d['people_h3']}, >=10%H {d['people_h10']}) vehicles {d['vehicles']} (bus {d['buses']} truck {d['trucks']})", flush=True)
        out[name] = d
        if a.annot:
            os.makedirs(a.annot, exist_ok=True); cv2.imwrite(os.path.join(a.annot, os.path.splitext(name)[0] + '_det.jpg'), r.plot(labels=False, line_width=2))
if a.json: json.dump(out, open(a.json, 'w'), indent=1)
