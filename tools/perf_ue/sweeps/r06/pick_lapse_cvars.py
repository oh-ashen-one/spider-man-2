#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06: reads the freeze lapses of hold3_diag.sh ($S/diag3/T*/T*.json) and picks the render settings that remove the 2 h/s lighting lag.
wash(run) = max frame mean Y between game hours 19.8 and 22.0 (a settled night view is ~40; the lagging lapse reads 130-215). Candidates are the runs whose live_cmds carry `exec r.*` console
variables (T5 / T9 pin ToD params and are reported only). Prints a table, writes <dir>/best_cvars.txt = comma separated name=value (the wh.ToDLapseCvars format) of
  - the single best run if its wash is <= --target (default 75), else
  - the union of every run that cut the baseline wash by > 25 % (to be verified by one more freeze run, hold3_diag.sh step T10).
usage: pick_lapse_cvars.py <diag3 dir> [--target 75]"""
import argparse, glob, json, os, re


def cvars_of(cmds):
    out = []
    for c in cmds.split(';'):
        m = re.match(r'\s*exec\s+(r\.\S+)\s+(\S+)\s*$', c)
        if m: out.append((m.group(1), m.group(2)))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('--target', type=float, default=75.0)
    a = ap.parse_args()
    runs = {}
    for f in sorted(glob.glob(os.path.join(a.dir, 'T*', 'T*.json'))):
        d = json.load(open(f)); n = os.path.basename(f)[:-5]
        h = d['hours_per_frame']; y = d['mean_y_per_frame']
        win = [y[i] for i in range(len(y)) if 19.8 <= h[i] <= 22.0 + 1e-6]
        runs[n] = {'wash': max(win) if win else None, 'max_jump': d['checks_L23b']['max_jump'], 'cvars': cvars_of(d.get('live_cmds', '')), 'cmds': d.get('live_cmds', '')}
    base = runs.get('T0_native', {}).get('wash') or max(r['wash'] for r in runs.values() if r['wash'])
    print('%-16s %7s %9s  cvars' % ('run', 'wash', 'max jump'))
    for n, r in runs.items(): print('%-16s %7.1f %9.2f  %s' % (n, r['wash'], r['max_jump'], ' '.join('%s=%s' % c for c in r['cvars'] if c[0] != 'wh.ToDLapseLumen')))
    cand = {n: r for n, r in runs.items() if any(c[0].startswith('r.') for c in r['cvars'])}
    best = min(cand, key=lambda n: cand[n]['wash']) if cand else None
    chosen = []
    if best and cand[best]['wash'] <= a.target: chosen = [c for c in cand[best]['cvars']]; why = 'best single run %s (wash %.1f)' % (best, cand[best]['wash'])
    else:
        good = [n for n, r in cand.items() if r['wash'] < 0.75 * base]
        seen = {}
        for n in good:
            for k, v in cand[n]['cvars']: seen[k] = v
        chosen = list(seen.items()); why = 'union of %s' % good
    spec = ','.join('%s=%s' % c for c in chosen)
    open(os.path.join(a.dir, 'best_cvars.txt'), 'w').write(spec)
    print('baseline wash %.1f; chosen (%s): %s' % (base, why, spec))


if __name__ == '__main__':
    main()
