#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07 (resume, Sonnet 5.5): sweep G on the BAKED hold-T table (table v5). The three misses of its first stills (S4 19:48 clip 2.1 %, S4w 19:30 clip .35 %, S4e 06:30 8-row step 27) are lit cloud streaks.
Physics: the Earth's shadow reaches a 9 km cloud deck at a sun depression of ~3 deg (19:30 / 06:30), so after that no direct sun reaches the clouds; the renderer has no Earth shadow, so
`sunc.CloudScatteredLuminanceScale` is the lever. Variants (live pins relative to the baked value): q1 sun cloud luminance 0 (19:30: x.3) | q2 q1 + SkyLuminanceFactor x1.5 | q3 q1 + SkyLuminanceFactor x2.2
Hours 6.5 (S4, S4e), 19.5 / 19.8 / 20.0 (S4, S4w).
usage: gen_sweep_g.py --out <dir>  -> <dir>/plan_g.json"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402


def pin(p, v):
    v = v if isinstance(v, (list, tuple)) else [v]
    return 'exec wh.ToDSet %s %s' % (p, ' '.join('%.6g' % x for x in v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--hours', default='6.5,19.5,19.8,20.0'); ap.add_argument('--variants', default='q1,q2,q3'); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t = look_tod.expand(look_tod.load_doc()); G = []
    for h in [float(x) for x in a.hours.split(',')]:
        v = look_tod.evaluate(t, h); face = 'S4w' if h > 12 else 'S4e'
        sf = v['atm.SkyLuminanceFactor']; sc = v['sunc.CloudScatteredLuminanceScale'][0]
        S0 = pin('sunc.CloudScatteredLuminanceScale', [sc * (0.3 if abs(h - 19.5) < 0.01 else 0.0)] * 3 + [1])
        F = lambda k: pin('atm.SkyLuminanceFactor', [sf[0] * k, sf[1] * k, sf[2] * k, 1])
        V = {'q1': [S0], 'q2': [S0, F(1.5)], 'q3': [S0, F(2.2)]}
        for n in a.variants.split(','): G.append({'name': '%s_h%g' % (n, h), 'hour': h, 'cmds': V[n], 'shots': ['S4', face], 'settle_first': 8})
    json.dump({'groups': G}, open(os.path.join(a.out, 'plan_g.json'), 'w'), indent=1)
    print('plan_g', sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
