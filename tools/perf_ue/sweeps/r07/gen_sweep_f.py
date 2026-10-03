#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07 (resume, Sonnet 5.5): sweep F on the BAKED hold-M table (table v4: dir inscattering cut, saturation x.6, red highlights x.8, FilmWhiteClip 0, fog inscattering x.55):
39 of the 42 L27 lines pass on the first build; the three left are rows 0-150 clipping from near-white pink cloud streaks (S4 19:48 4.4 %, S4 20:00 0.9 %, S4w 19:30 0.6 %).
Variants (live pins relative to the baked value of the hour): n1 sun cloud luminance x0.4 | n2 cloud albedo 0.6 | n3 red/green highlights gain x0.85 / x0.95 | n4 n1 + n3 | n5 n1 + albedo 0.75
usage: gen_sweep_f.py --out <dir> [--hours 19.5,19.8,20.0] [--variants n0,..]  -> <dir>/plan_f.json"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402


def pin(p, v):
    v = v if isinstance(v, (list, tuple)) else [v]
    return 'exec wh.ToDSet %s %s' % (p, ' '.join('%.6g' % x for x in v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--hours', default='19.5,19.8,20.0'); ap.add_argument('--plan-name', default='plan_f'); ap.add_argument('--variants', default='n0,n1,n2,n3,n4,n5'); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t = look_tod.expand(look_tod.load_doc()); G = []
    for h in [float(x) for x in a.hours.split(',')]:
        v = look_tod.evaluate(t, h); face = 'S4w' if h > 12 else 'S4e'
        sc = v['sunc.CloudScatteredLuminanceScale']; hg = v['pp.ColorGainHighlights']
        S = lambda k: pin('sunc.CloudScatteredLuminanceScale', [sc[0] * k] * 3 + [1])
        A = lambda x: pin('cloudv.Cloud_AlbedoColor', [x, x, x, 1])
        H = pin('pp.ColorGainHighlights', [hg[0] * 0.85, hg[1] * 0.95, hg[2], 1])
        V = {'n0': [], 'n1': [S(0.4)], 'n2': [A(0.6)], 'n3': [H], 'n4': [S(0.4), H], 'n5': [S(0.4), A(0.75)],
             'n6': [S(0.0)], 'n7': [S(0.1)], 'n8': [A(0.3)], 'n9': [S(0.0), A(0.5)], 'n10': [pin('pp.FilmShoulder', 0.6)], 'n11': [pin('pp.AutoExposureMaxBrightness', 1.0), S(0.0)],
             'p1': [pin('pp.FilmShoulder', 0.0)], 'p2': [pin('pp.FilmShoulder', 0.1)], 'p3': [pin('pp.FilmShoulder', 0.1), pin('pp.FilmSlope', 0.8)], 'p4': [pin('pp.FilmShoulder', 0.1), S(0.5)],
             'p5': [pin('pp.FilmShoulder', 0.1), A(0.6)], 'p6': [pin('pp.FilmShoulder', 0.1), pin('pp.ColorContrast', [1.0, 1.0, 1.0, 1])], 'p7': [pin('pp.ColorContrast', [1.0, 1.0, 1.0, 1])]}
        for n in a.variants.split(','): G.append({'name': '%s_h%g' % (n, h), 'hour': h, 'cmds': V[n], 'shots': ['S4', face], 'settle_first': 8})
    json.dump({'groups': G}, open(os.path.join(a.out, a.plan_name + '.json'), 'w'), indent=1)
    print('plan_f', sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
