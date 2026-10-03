#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07 (resume, Sonnet 5.5): single-knob sensitivity sweep of the twilight dome on the BAKED hold-F table (live pins, `wh.ToDClear` before each group).
Poses: S4 + facing pose at 19.5, 20.0 (S4w) and 6.5 (S4e). One pin (or a pair) per group, all values relative to the baked value of the hour.
usage: gen_sweep_c.py --out <dir>  -> <dir>/plan_c.json"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402


def pin(p, v):
    v = v if isinstance(v, (list, tuple)) else [v]
    return 'exec wh.ToDSet %s %s' % (p, ' '.join('%.6g' % x for x in v))


def mul(v, k): return [x * k for x in v[:3]] + [1.0] if isinstance(v, list) else v * k


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--hours', default='19.5,20.0,6.5'); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t = look_tod.expand(look_tod.load_doc()); G = []
    for h in [float(x) for x in a.hours.split(',')]:
        v = look_tod.evaluate(t, h); face = 'S4w' if h > 12 else 'S4e'
        V = lambda k, m: pin(k, mul(v[k], m))
        variants = [
            ('base', []),
            ('fogInsc50', [V('fog.FogInscatteringLuminance', 0.5)]),
            ('fogAmb0', [pin('fog.SkyAtmosphereAmbientContributionColorScale', [0, 0, 0, 1])]),
            ('fogDir0', [pin('fog.DirectionalInscatteringLuminance', [0, 0, 0, 1])]),
            ('apd1.5', [pin('atm.AerialPespectiveViewDistanceScale', 1.5)]),
            ('hfc0.3', [pin('atm.HeightFogContribution', 0.3)]),
            ('dens50', [V('fog.FogDensity', 0.5)]),
            ('maxop60', [pin('fog.FogMaxOpacity', 0.6)]),
            ('sat60', [pin('pp.ColorSaturation', [0.6, 0.6, 0.6, 1])]),
            ('skyX1.8', [V('atm.SkyLuminanceFactor', 1.8)]),
            ('nocloud', [pin('cloud.Cloud_GlobalCoverage', -0.2)]),
            ('cloudlit', [pin('sunc.CloudScatteredLuminanceScale', [0.4, 0.4, 0.4, 1])]),
            ('fog2off', [pin('fog2.FogDensity', 0)]),
            ('volfog30', [V('fog.VolumetricFogExtinctionScale', 0.3)]),
        ]
        for n, c in variants:
            G.append({'name': '%s_h%g' % (n, h), 'hour': h, 'cmds': c, 'shots': ['S4', face], 'settle_first': 8})
    json.dump({'groups': G}, open(os.path.join(a.out, 'plan_c.json'), 'w'), indent=1)
    print('plan_c', sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
