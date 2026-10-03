#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 09: the S4 test lines of the round (city tools/export/s4_far_check.py on 1080p frames) for a folder of tour PNG / JPG frames, one line per frame.
usage: quick_s4.py <dir or files...> [--json out.json]"""
import sys, os, glob, json
import numpy as np, cv2
WT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'tools', 'export'))
import s4_far_check as S, city_spec_check as C
def rows(paths):
    cfg = json.load(open(C.REGFILE)); out = []
    for p in paths:
        r = S.analyse(p, cfg)
        if r is None: continue
        im = cv2.imread(p); im = im if im.shape[1] == 1920 else cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA)
        Y = C.luma(im); L = r['lines']
        d = dict(file=os.path.basename(p), sky=r['sky_Y'], far=r['far_Y'], far_m_sky=r['far_Y'] - r['sky_Y'], crit_m_sky=r['C13_critic_box'], T2=r['box_pct204'],
                 T4b=r['T4']['flat_of_bright_pct'], T4a=r['T4']['flat_of_all_pct'], nbright=r['T4']['bright'], T1=min(r['T1_std'].values()), T1A=r['T1_std']['first_Y_lt_215'], T1B=r['T1_std']['first_absdY_gt_4'], T1C=r['T1_std']['first_Y_lt_sky_minus_12'], C11=L['C11 lap/sky']['value'],
                 C11f=L['C11 flat8 %']['value'], C12=L['C12 dBR']['value'], C14=L['C14 far-river Y']['value'], C15=L['C15 rms far/near']['value'], mean=float(Y.mean()),
                 sky_rows_110_150=float(Y[110:150, 540:900].mean()))
        d['pass'] = dict(sky=d['sky'] <= 205, far=-32 <= d['far_m_sky'] <= -25, crit=-32 <= d['crit_m_sky'] <= -25, T2=d['T2'] <= 10, T4=d['T4b'] <= 10 and d['T4a'] <= 10,
                         C12=abs(d['C12']) <= 10, T1=d['T1'] >= 12, T1BC=min(d['T1B'], d['T1C']) >= 12, C11=L['C11 lap/sky']['passed'] and L['C11 flat8 %']['passed'], C14=L['C14 far-river Y']['passed'], C15=L['C15 rms far/near']['passed'])
        out.append(d)
    return out
if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]; jo = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    if jo: a = [x for x in a if x != jo]
    ps = []
    for x in a: ps += sorted(glob.glob(os.path.join(x, '*S4*.png')) + glob.glob(os.path.join(x, '*S4*.jpg'))) if os.path.isdir(x) else [x]
    R = rows(ps)
    print('%-34s %6s %6s %6s %6s %5s %5s %3s %5s %5s %5s %6s %5s %5s %5s  fails' % ('frame', 'sky', 'far', 'f-s', 'c-s', 'T2', 'T4b', 'nb', 'T1B', 'T1C', 'C12', 'C11', 'C14', 'C15', 'mean'))
    for d in R:
        print('%-34s %6.1f %6.1f %6.1f %6.1f %5.1f %5.1f %3d %5.1f %5.1f %5.1f %6.1f %5.1f %5.2f %5.1f  %s' % (d['file'][:34], d['sky'], d['far'], d['far_m_sky'], d['crit_m_sky'], d['T2'], d['T4b'], d['nbright'], d['T1B'], d['T1C'], d['C12'], d['C11'], d['C14'], d['C15'], d['mean'],
              ','.join(k for k, v in d['pass'].items() if not v) or 'ALL PASS'))
    if jo: json.dump(R, open(jo, 'w'), indent=1)
