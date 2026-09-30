#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Piece F (round 06): per-config route statistics + mean GPU pass / thread times from perf_route CSVs, and the delta of every config vs a
named control of the same session (no trace server, CSV profiler columns only).
usage: pass_diff.py <session dir> [...] [--control ship] [--life-control life] [--md out.md] [--json out.json] [--top 14]
A config whose name starts with 'l' (life runs) is compared with --life-control, every other one with --control."""
import argparse, glob, json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from windows import load, pct

KEYS = ['FrameTime', 'GPUTime', 'RenderThreadTime', 'GameThreadTime', 'RHIThreadTime']


def stats(path):
    hdr, idx, data = load(path)
    ft = [r[idx['FrameTime']] for r in data if r[idx['FrameTime']] > 0]
    med = pct(ft, 50)
    out = {'frames': len(ft), 'p50': pct(ft, 50), 'p95': pct(ft, 95), 'p99': pct(ft, 99), 'max': max(ft), 'over_18_18': sum(1 for x in ft if x > 18.18),
           'hitches': sum(1 for x in ft if x > 25 and x > 2 * med)}
    m = {k: statistics.mean(r[i] for r in data) for k, i in idx.items() if k.startswith('GPU/') or k in KEYS or k.startswith('Exclusive/GameThread/')}
    return out, m


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dirs', nargs='+'); ap.add_argument('--control', default='ship'); ap.add_argument('--life-control', default='life')
    ap.add_argument('--md'); ap.add_argument('--json'); ap.add_argument('--top', type=int, default=14); a = ap.parse_args()
    runs = {}
    for d in a.dirs:
        for c in sorted(glob.glob(os.path.join(d, '*', 'csv.csv*'))):
            name = os.path.basename(os.path.dirname(c)); rj = os.path.join(os.path.dirname(c), 'result.json')
            s, m = stats(c); r = json.load(open(rj)) if os.path.exists(rj) else {}
            s['ingame_p95'] = (r.get('wh_perf') or {}).get('p95_ms') or (r.get('wh_perf') or {}).get('p95')
            runs[name] = {'stats': s, 'means': m, 'spec': r.get('spec')}
    lines = ['| config | CSV p50 | CSV p95 | in-game p95 | p99 | >18.18 | hitches | GPUTime | GT | RHI | ScreenProbeGather | Unaccounted | ShadowDepths | vs control (largest pass deltas, ms) |', '|' + '---|' * 14]
    for n, r in runs.items():
        s, m = r['stats'], r['means']
        ctl = a.life_control if n.startswith('l') else a.control
        dl = ''
        if ctl in runs and ctl != n:
            cm = runs[ctl]['means']
            ds = sorted(((m.get(k, 0) - cm.get(k, 0), k) for k in set(m) | set(cm) if k.startswith('GPU/')), key=lambda x: -abs(x[0]))[:a.top]
            dl = '%s: FT %+.2f GPU %+.2f; ' % (ctl, m['FrameTime'] - cm['FrameTime'], m['GPUTime'] - cm['GPUTime']) + ', '.join('%s %+.2f' % (k[4:], d) for d, k in ds if abs(d) >= 0.03)
            r['delta_vs'] = ctl; r['deltas'] = {k: round(d, 3) for d, k in ds}
        g = lambda k: m.get(k, float('nan'))
        ig = s['ingame_p95']
        lines.append('| %s | %.2f | %.2f | %s | %.2f | %d | %d | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %s |' % (n, s['p50'], s['p95'], ('%.2f' % ig) if isinstance(ig, (int, float)) else '-', s['p99'], s['over_18_18'], s['hitches'],
                     g('GPUTime'), g('GameThreadTime'), g('RHIThreadTime'), g('GPU/LumenScreenProbeGather'), g('GPU/Unaccounted'), g('GPU/ShadowDepths'), dl))
    txt = '\n'.join(lines); print(txt)
    if a.md: open(a.md, 'w').write(txt + '\n')
    if a.json: json.dump(runs, open(a.json, 'w'), indent=1)


if __name__ == '__main__': main()
