#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 05: spec numbers for time-of-day stills (tod_<S#>_<res>_<variant>.jpg from tools/perf_ue/sweeps/run_r05.py or capture_tour.py --tod).
Each variant is measured as the preset its hour stands for (--map h18.4=golden,h22=night,h13w1=midday,g*=golden,n*=night): the stills are linked as
<preset>_<S#>_<res>_<variant>.jpg into a scratch folder and run through the unchanged instruments
  look_spec_check.py (L1/L2/L3/L5 means, near-black, clipped, B-R; L10/L11 old far boxes; L13/L14; L17), key_fill_check.py (L21, golden),
  night_city_check.py (L22, night S4), tools/export/s4_far_check.py (CITY-SPEC C11-C15 / C12 / C13 on S4 with the current spec_regions.json, as integration measures it).
Writes <out>.md (+ .json) with a one-line-per-variant summary on top.
usage: tod_tests.py --dir <stills dir> --out <round>/TESTS_tod [--map h18.4=golden,...] [--res 1920x1080]"""
import argparse, fnmatch, glob, json, os, re, shutil, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import key_fill_check as KF   # noqa: E402
import night_city_check as NC   # noqa: E402
import look_spec_check as LS   # noqa: E402
DEFAULT_MAP = 'h18.4=golden,h22=night,h13w1=midday,g*=golden,n*=night'


def far(path):
    r = subprocess.run([sys.executable, os.path.join(WT, 'tools', 'export', 's4_far_check.py'), path, '--json', path + '.far.json'], capture_output=True, text=True, cwd=WT)
    try: return json.load(open(path + '.far.json'))[0]
    except Exception: return {'error': r.stdout[-300:] + r.stderr[-300:]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dir', required=True); ap.add_argument('--out', required=True); ap.add_argument('--map', default=DEFAULT_MAP)
    ap.add_argument('--res', default='1920x1080'); ap.add_argument('--scratch', default='/Users/midir/sm2-n1/_scratch/look/tod_tests')
    a = ap.parse_args()
    rules = [tuple(x.split('=')) for x in a.map.split(',')]
    files = sorted(glob.glob(os.path.join(a.dir, 'tod_S?_%s_*.jpg' % a.res)))
    groups = {}
    for f in files:
        m = re.match(r'tod_(S\d)_%s_(.+)\.jpg' % a.res, os.path.basename(f))
        sid, v = m.group(1), m.group(2)
        pre = next((p for pat, p in rules if fnmatch.fnmatch(v, pat)), None)
        if pre: groups.setdefault(v, (pre, []))[1].append((sid, f))
    shutil.rmtree(a.scratch, ignore_errors=True); os.makedirs(a.scratch)
    pairs = json.load(open(KF.PAIRS)) if os.path.exists(KF.PAIRS) else None
    summary, detail, js = [], [], {}
    for v, (pre, items) in groups.items():
        d = os.path.join(a.scratch, v); os.makedirs(d)
        links = []
        for sid, f in items:
            l = os.path.join(d, '%s_%s_%s.jpg' % (pre, sid, a.res)); os.symlink(f, l); links.append((sid, l))
        rows = [LS.stats(l) for _, l in links]
        for r in rows:
            vv = LS.verdict(r['file'], r); r['spec_line'] = vv[0] if vv else None; r['within'] = vv[1] if vv else None
        ent = {'preset': pre, 'spec': rows}
        line = {'variant': v, 'as': pre, 'n': len(rows),
                'mean': '%.0f..%.0f' % (min(r['mean'] for r in rows), max(r['mean'] for r in rows)),
                'spec_pass': '%d/%d' % (sum(1 for r in rows if r['within'] and all(r['within'].values())), len(rows)),
                'clip_max': '%.2f' % max(r['clipped_pct'] for r in rows), 'BR': '%+.0f..%+.0f' % (min(r['b_minus_r'] for r in rows), max(r['b_minus_r'] for r in rows))}
        if pre == 'golden':
            kf = [KF.stats(l, pairs) for _, l in links]; ent['key_fill'] = kf
            line['p5'] = '%.1f..%.1f' % (min(k['p5'] for k in kf), max(k['p5'] for k in kf))
            line['p95/p5'] = '%.1f..%.1f' % (min(k['ratio'] for k in kf), max(k['ratio'] for k in kf))
            line['sat'] = '%.2f..%.2f' % (min(k['sat'] for k in kf), max(k['sat'] for k in kf))
            pr = [k['pair']['ratio'] for k in kf if k.get('pair')]
            if pr: line['facade pair'] = '/'.join('%.1f' % x for x in pr)
        if pre == 'night':
            s4 = [l for sid, l in links if sid == 'S4']
            if s4: n = NC.stats(s4[0]); ent['night_s4'] = n; line['S4 points %'] = '%.2f' % n['points_pct']; line['S4 median'] = '%.1f' % n['median']; line['S4 mean'] = '%.1f' % n['mean']
            st = [r for r in rows if r['file'].split('_')[1] in ('S1', 'S5', 'S6')]
            if st: line['L13 blobs'] = '/'.join(str(r['lit_blobs_bottom_half']) for r in st)
        s4 = [f for sid, f in items if sid == 'S4']
        if s4 and pre in ('golden', 'midday', 'night'):
            fr = far(s4[0]); ent['s4_far'] = fr
            if 'lines' in fr:
                line['C13 far-sky'] = '%+.1f' % fr['lines']['C13 far-sky Y']['value']; line['C12 dBR'] = '%+.1f' % fr['lines']['C12 dBR']['value']
                line['C14 far-river'] = '%+.1f' % fr['lines']['C14 far-river Y']['value']
        summary.append(line); js[v] = ent
        detail.append('### %s (measured as %s)\n' % (v, pre))
        detail.append('| still | mean Y | Y<10 % | clipped % | B-R | spec (mean / near-black / clipped / B-R) |\n|---|---|---|---|---|---|')
        for r in rows:
            w = r['within']
            detail.append('| %s | %.1f | %.2f | %.2f | %+.1f | %s %s |' % (r['file'], r['mean'], r['near_black_pct'], r['clipped_pct'], r['b_minus_r'], r['spec_line'] or '',
                          ' / '.join('yes' if w[k] else 'NO' for k in ('mean', 'near_black', 'clipped', 'b_minus_r')) if w else '-'))
        if pre == 'golden':
            detail.append('\n| still | p5 Y (<= 12) | p95/p5 (>= 16) | sat (>= .44) | facade pair (>= 3) |\n|---|---|---|---|---|')
            for k in ent['key_fill']:
                detail.append('| %s | %.1f | %.1f | %.3f | %s |' % (k['file'], k['p5'], k['ratio'], k['sat'], ('%.2f' % k['pair']['ratio']) if k.get('pair') else '-'))
        if 's4_far' in ent and 'lines' in ent['s4_far']:
            detail.append('\nS4 far band (s4_far_check.py, current spec_regions.json): ' + ' | '.join('%s %s (%s) %s' % (k, x['value'], x['target'], 'ok' if x['passed'] else 'FAIL') for k, x in ent['s4_far']['lines'].items()))
        detail.append('')
    keys = []
    for l in summary:
        for k in l:
            if k not in keys: keys.append(k)
    S = ['| ' + ' | '.join(keys) + ' |', '|' + '---|' * len(keys)] + ['| ' + ' | '.join(str(l.get(k, '')) for k in keys) + ' |' for l in summary]
    md = ('# Time-of-day stills: spec numbers\n\n> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.\n\nStills: `%s` (1920x1080 output, internal 100 %%). '
          'Targets: golden L1 mean 61..100, clipped <= 1.8 %% (S7: L5 <= 0.7 %%), B-R -55..-20; L21 p5 <= 12, p95/p5 >= 16, sat >= .44, facade pair >= 3; night L3 37..60, L8 B-R +-13, L22 S4 points >= 3 %%, median <= 42; '
          'midday overcast L2 83..97, clipped 0.00 %%; far band C13 far-sky -32..-15 (PLAN: 15-32 under the sky), C12 dBR +-10.\n\n' % os.path.relpath(a.dir, WT)) + '\n'.join(S) + '\n\n' + '\n'.join(detail) + '\n'
    open(a.out + '.md', 'w').write(md); json.dump(js, open(a.out + '.json', 'w'), indent=1, default=float)
    print('\n'.join(S))


if __name__ == '__main__':
    main()
