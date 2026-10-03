#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07 (resume, Sonnet 5.5): sweep E on the BAKED hold-F table (live pins), after sweep D (gen_sweep_d.py: k2 = dir x0.4 + sat x0.5 + FilmWhiteClip 0 + red highlights x0.8 clears the red-channel clipping
and puts B-R into -90..-20 on every facing still; the far band toward the sun is still brighter than the sky at 19:30 / 20:00 because the fog directional inscattering is only cut to 40 %).
Variants (relative to the baked value of the hour): POST = FilmWhiteClip 0, red highlights gain x0.8 (G x.95).
  e1 dir x0.1 + sat x0.5 + POST     e2 dir x0.03 + sat x0.5 + POST     e3 dir 0 + sat x0.5 + POST     e4 dir x0.1 + sat x0.65 + POST + fog inscattering x0.6
  e5 dir x0.1 + sat 1 + POST + pp.ColorSaturationHighlights 0.4 (desaturate only the bright parts)
usage: gen_sweep_e.py --out <dir> [--hours ...] [--variants ...]  -> <dir>/plan_e.json"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402


def pin(p, v):
    v = v if isinstance(v, (list, tuple)) else [v]
    return 'exec wh.ToDSet %s %s' % (p, ' '.join('%.6g' % x for x in v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--hours', default='19.5,19.8,20.0,20.5,6.5,7.0'); ap.add_argument('--variants', default='e1,e2,e3,e4,e5'); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t = look_tod.expand(look_tod.load_doc()); G = []
    for h in [float(x) for x in a.hours.split(',')]:
        v = look_tod.evaluate(t, h); face = 'S4w' if h > 12 else 'S4e'
        di = v['fog.DirectionalInscatteringLuminance']; hg = v['pp.ColorGainHighlights']; fi = v['fog.FogInscatteringLuminance']
        D = lambda k: pin('fog.DirectionalInscatteringLuminance', [x * k for x in di[:3]] + [1])
        S = lambda k: pin('pp.ColorSaturation', [k, k, k, 1])
        POST = [pin('pp.FilmWhiteClip', 0), pin('pp.ColorGainHighlights', [hg[0] * 0.8, hg[1] * 0.95, hg[2], 1])]
        V = {'e1': [D(0.1), S(0.5)] + POST, 'e2': [D(0.03), S(0.5)] + POST, 'e3': [D(0.0), S(0.5)] + POST,
             'e4': [D(0.1), S(0.65), pin('fog.FogInscatteringLuminance', [x * 0.6 for x in fi[:3]] + [1])] + POST,
             'e5': [D(0.1), S(1.0), pin('pp.ColorSaturationHighlights', [0.4, 0.4, 0.4, 1])] + POST}
        for n in a.variants.split(','): G.append({'name': '%s_h%g' % (n, h), 'hour': h, 'cmds': V[n], 'shots': ['S4', face], 'settle_first': 8})
    json.dump({'groups': G}, open(os.path.join(a.out, 'plan_e.json'), 'w'), indent=1)
    print('plan_e', sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
