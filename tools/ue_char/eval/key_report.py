# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""CH18 in the real engine, round 06: enclosed background pixels of a chroma-key capture, component by component, with 3x crops.

  python3 key_report.py KEY_IMAGE [KEY_IMAGE ...] --out DIR [--min-px 6] [--thin 7] [--crops 12]

Same green-key definition as key_holes.py (Char_CrowdKey: street / facades unlit pure green).  For every image:
  person mask  = non-key pixels (components >= 3000 px, 3x3 closing)
  hole         = key pixel enclosed by the person mask (holes of the filled mask)
  each hole COMPONENT is reported with bbox, area, width (2 x the largest inscribed radius), and `edge_dist` = distance in px from the component to
  the outer background (key pixels connected to the image border).  edge_dist <= 3 px = a silhouette sliver (the enclosing wall is one or two pixels
  thick: the gap between two limbs seen edge-on, the rim of a cuff), everything else is an interior hole.
Writes DIR/<image>_report.json, DIR/<image>_holes.png (overlay: red = interior hole, orange = silhouette sliver) and 3x native crops of the largest
interior holes (DIR/<image>_crop_NN.png, left = native pixels, right = same with the overlay).  Prints one JSON line per image."""
import sys, os, json
import numpy as np
import cv2
from scipy import ndimage

a = sys.argv[1:]
opt = {'--out': None, '--min-px': '6', '--thin': '7', '--crops': '12'}
for k in list(opt):
    if k in a:
        i = a.index(k); opt[k] = a[i + 1]; a = a[:i] + a[i + 2:]
files = a
out = opt['--out']; os.makedirs(out, exist_ok=True)
MINPX = int(opt['--min-px']); THIN = int(opt['--thin']); NCROP = int(opt['--crops'])

for f in files:
    im = cv2.imread(f); H, W = im.shape[:2]
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)
    b, g, r = [im[..., k].astype(int) for k in range(3)]
    key = (hsv[..., 0] > 45) & (hsv[..., 0] < 85) & (hsv[..., 1] > 140) & (g > 90) & (g - np.maximum(r, b) > 60)
    person = ~key
    lab, n = ndimage.label(person); sz = np.bincount(lab.ravel())
    person = (sz[lab] >= 3000) & (lab > 0)
    person = ndimage.binary_closing(person, structure=np.ones((3, 3), bool))
    filled = ndimage.binary_fill_holes(person)
    holes = filled & ~person
    lh, nh = ndimage.label(holes)
    outer = ~filled                                       # background reachable from the border (person holes are inside `filled`)
    dist_outer = ndimage.distance_transform_edt(~outer)   # px to the outer background
    dist_in = ndimage.distance_transform_edt(holes)       # inscribed radius inside each hole
    comps = []
    objs = ndimage.find_objects(lh)
    for i, sl in enumerate(objs, 1):
        m = lh[sl] == i
        px = int(m.sum())
        if px < MINPX: continue
        width = float(2 * dist_in[sl][m].max())
        ed = float(dist_outer[sl][m].min())
        ys, xs = sl[0], sl[1]
        comps.append(dict(id=i, bbox=[int(xs.start), int(ys.start), int(xs.stop - xs.start), int(ys.stop - ys.start)], px=px, width_px=round(width, 1),
                          edge_dist_px=round(ed, 1), kind='sliver' if ed <= 3.0 else 'interior', thin=bool(width <= THIN)))
    inter = [c for c in comps if c['kind'] == 'interior']
    res = dict(image=os.path.basename(f), person_px=int(person.sum()), hole_components=len(comps), hole_px=int(sum(c['px'] for c in comps)),
               interior_components=len(inter), interior_px=int(sum(c['px'] for c in inter)),
               interior_thin_components=int(sum(c['thin'] for c in inter)), interior_thin_px=int(sum(c['px'] for c in inter if c['thin'])),
               sliver_components=len(comps) - len(inter), sliver_px=int(sum(c['px'] for c in comps if c['kind'] == 'sliver')), components=sorted(comps, key=lambda c: -c['px'])[:60])
    base = os.path.splitext(os.path.basename(f))[0]
    json.dump(res, open(os.path.join(out, base + '_report.json'), 'w'), indent=1)
    vis = im.copy()
    for c in comps:
        m = lh == c['id']
        vis[m] = (0, 0, 255) if c['kind'] == 'interior' else (0, 140, 255)
    cv2.imwrite(os.path.join(out, base + '_holes.png'), vis)
    for k, c in enumerate(sorted(inter, key=lambda c: -c['px'])[:NCROP]):
        x, y, w, h = c['bbox']; cx, cy = x + w // 2, y + h // 2
        x0 = min(max(0, cx - 60), W - 120); y0 = min(max(0, cy - 60), H - 120)
        raw = im[y0:y0 + 120, x0:x0 + 120]; ov = vis[y0:y0 + 120, x0:x0 + 120]
        both = np.hstack([cv2.resize(raw, (360, 360), interpolation=cv2.INTER_NEAREST), cv2.resize(ov, (360, 360), interpolation=cv2.INTER_NEAREST)])
        cv2.putText(both, 'x%d y%d %dpx' % (cx, cy, c['px']), (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.imwrite(os.path.join(out, '%s_crop_%02d.png' % (base, k)), both)
    print(json.dumps({k: v for k, v in res.items() if k != 'components'}))
