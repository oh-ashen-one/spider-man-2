#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07 (resume, Sonnet 5.5): sweep D on the BAKED hold-F table (live pins): the three levers found by sweep C (gen_sweep_c.py):
  * fog.DirectionalInscatteringLuminance (the fake sun glow in the fog) is what makes the far band toward the sun brighter than the sky (S4w 19:30 far 136 -> 77 at 0; S4 is insensitive);
  * pp.ColorSaturation x0.6 removes the clipped red channel of the lit cloud streaks (S4 6:30 10.2 % -> 0, S4e 3.7 % -> 0) and brings sky B-R into -90..-20;
  * red highlights gain / FilmWhiteClip 0 (the tonemapper's white clip) for what is left.
All multipliers relative to the baked value of the hour. Hours 19.5 19.8 20.0 20.5 (S4 + S4w), 6.5 7.0 (S4 + S4e).
usage: gen_sweep_d.py --out <dir> [--hours ...] [--variants k0,k1,..]  -> <dir>/plan_d.json"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402


def pin(p, v):
    v = v if isinstance(v, (list, tuple)) else [v]
    return 'exec wh.ToDSet %s %s' % (p, ' '.join('%.6g' % x for x in v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--hours', default='19.5,19.8,20.0,20.5,6.5,7.0'); ap.add_argument('--variants', default='k0,k1,k2,k3,k4'); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t = look_tod.expand(look_tod.load_doc()); G = []
    for h in [float(x) for x in a.hours.split(',')]:
        v = look_tod.evaluate(t, h); face = 'S4w' if h > 12 else 'S4e'
        di = v['fog.DirectionalInscatteringLuminance']; hg = v['pp.ColorGainHighlights']
        D = lambda k: pin('fog.DirectionalInscatteringLuminance', [x * k for x in di[:3]] + [1])
        S = lambda k: pin('pp.ColorSaturation', [k, k, k, 1])
        H = lambda r, g, b: pin('pp.ColorGainHighlights', [hg[0] * r, hg[1] * g, hg[2] * b, 1])
        W0 = pin('pp.FilmWhiteClip', 0)
        V = {'k0': [], 'k1': [D(0.4), S(0.7), W0], 'k2': [D(0.4), S(0.5), W0, H(0.8, 0.95, 1.0)], 'k3': [D(0.2), S(0.5), W0, H(0.8, 0.95, 1.0)], 'k4': [D(0.4), S(0.35), W0, H(0.65, 0.9, 1.0)]}
        for n in a.variants.split(','): G.append({'name': '%s_h%g' % (n, h), 'hour': h, 'cmds': V[n], 'shots': ['S4', face], 'settle_first': 8})
    json.dump({'groups': G}, open(os.path.join(a.out, 'plan_d.json'), 'w'), indent=1)
    print('plan_d', sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
