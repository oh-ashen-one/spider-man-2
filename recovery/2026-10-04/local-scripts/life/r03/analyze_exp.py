#!/usr/bin/env python3
# usage: analyze_exp.py <exp dir> ...   YOLO (CPU) on the jpg stills + probe L/R hand counts
import sys, os, re, glob, subprocess, json
PY = '/Users/midir/sm2-n1/_scratch/life/venv/bin/python'
DET = '/Users/midir/sm2-n1/life/tools/life/detect_counts.py'
for d in sys.argv[1:]:
    print('=====', os.path.basename(d.rstrip('/')))
    imgs = sorted(glob.glob(os.path.join(d, '*_t0*.jpg')) + glob.glob(os.path.join(d, '*_t1*.jpg')))
    if imgs:
        out = subprocess.run([PY, DET, '--device', 'cpu', '--json', os.path.join(d, 'det.json')] + imgs, capture_output=True, text=True).stdout
        print(out.strip())
        out = subprocess.run([PY, DET, '--device', 'cpu', '--crop', '0.84', '--json', os.path.join(d, 'det_crop84.json')] + imgs, capture_output=True, text=True).stdout
        print('  -- critic 84 % centre crop:'); print(out.strip())
    pr = os.path.join(d, 'probe.txt')
    if os.path.exists(pr):
        for l in open(pr):
            m = re.search(r'WH_LIFE_FRAME t=([\d.]+).*people >=20px unoccluded: (\d+) \(left of view axis (\d+), right (\d+); within 80 m (\d+): left (\d+) right (\d+)\)', l)
            if m: print('  FRAME t=%s hand>=20px %s (L %s R %s) within80m %s (L %s R %s)' % m.groups())
        rows = []
        for l in open(pr):
            m = re.search(r'WH_LIFE_SAMPLE t=([\d.]+) .*people >=20px: (\d+) \(left (\d+) right (\d+); within 80 m (\d+): left (\d+) right (\d+)\)', l)
            if m: rows.append(tuple(float(x) for x in m.groups()))
        if rows:
            import statistics as st
            near = [r[4] for r in rows]; tot = [r[1] for r in rows]; nl = [r[5] for r in rows]; nr = [r[6] for r in rows]
            print('  SAMPLES n=%d  >=20px unoccluded total med %.0f min %.0f | within 80 m med %.0f min %.0f (left med %.0f right med %.0f)' % (len(rows), st.median(tot), min(tot), st.median(near), min(near), st.median(nl), st.median(nr)))
        for l in open(pr):
            if '[crowd]' in l and ('populated' in l or 'walkers' in l): print('  ', l.strip()[:200]); break
