#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 08, sweep B on the BAKED round-07 table: bilateral local exposure with a darker pivot (pp.LocalExposureMiddleGreyBias < 0: only the regions darker than the shifted middle grey are lifted,
so the far band and the sky band, both near middle grey, keep their values and L27a its margin), alone and with a stronger sky light (fog scattering compensated).
Sweep A (round-08/diag/sweepA.md): shadow contrast .4 + blur blend .2 took S4e 07:00 from 28.4 to 52.6 (Y<10 53 -> 0.1 %) but lifted the S4 07:00 far band by 19 Y.
  b0 none | m1 LE .35 blend .2 pivot -1 | m2 LE .25 blend .2 pivot -1.5 | m3 LE .35 blend .2 pivot -.5 | m4 LE .4 blend .2 + sky x3 | m5 m2 + sky x3
hours: 6.5 7.0 7.5 (S4e + S4), 19.0 19.5 19.8 (S4w + S4)
usage: gen_sweep_b.py --out <dir> [--hours ...] [--variants ...]  -> <dir>/plan_b.json"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402


def pin(p, v):
    v = v if isinstance(v, (list, tuple)) else [v]
    return 'exec wh.ToDSet %s %s' % (p, ' '.join('%.6g' % x for x in v))


def variants(v):
    sky = lambda k: [pin('sky.Intensity', v['sky.Intensity'] * k), pin('skyc.VolumetricScatteringIntensity', 1.0 / k)]
    le = lambda s, blend, piv: [pin('pp.LocalExposureShadowContrastScale', s), pin('pp.LocalExposureBlurredLuminanceBlend', blend), pin('pp.LocalExposureMiddleGreyBias', piv)]
    # the baked round-07 table has no local-exposure / skyc keys, so a pin would stay on the volume after wh.ToDClear: every variant pins all of them (defaults first)
    D = le(1.0, 0.6, 0.0) + [pin('skyc.VolumetricScatteringIntensity', 1.0)]
    V = {'b0': [], 'm1': le(.35, .2, -1), 'm2': le(.25, .2, -1.5), 'm3': le(.35, .2, -.5), 'm4': le(.4, .2, 0) + sky(3), 'm5': le(.25, .2, -1.5) + sky(3)}
    return {k: D + c for k, c in V.items()}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--hours', default='6.5,7.0,7.5,19.0,19.5,19.8'); ap.add_argument('--variants', default='b0,m1,m2,m3,m4,m5')
    ap.add_argument('--blue', type=int, default=1)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    t = look_tod.expand(look_tod.load_doc()); G = []
    for h in [float(x) for x in a.hours.split(',')]:
        v = look_tod.evaluate(t, h); V = variants(v)
        for n in a.variants.split(','): G.append({'name': '%s_h%g' % (n, h), 'hour': h, 'cmds': V[n], 'shots': ['S4e' if h < 12 else 'S4w', 'S4'], 'settle_first': 8})
    # blue hour 20:30 (sweep A: SkyLuminanceFactor x[.4, .85, 1.6] took S4 sky B-R from -18.7 to -0.2 but S4w with it, -25.2 -> -1.1; a warm Mie lobe did not separate them):
    # the fog's directional inscattering is a lobe around the sun direction (pow(cos, exponent)): ~20 deg from the sun on S4w (cos^12 = .48), ~64 deg on S4 (cos^12 < 1e-4)
    if a.blue:
        v = look_tod.evaluate(t, 20.5); D = variants(v)['b0']; f = v['atm.SkyLuminanceFactor']
        fac = lambda kr, kg, kb: pin('atm.SkyLuminanceFactor', [f[0] * kr, f[1] * kg, f[2] * kb, 1])
        lobe = lambda k, e: [pin('fog.DirectionalInscatteringLuminance', [k, k * 0.42, k * 0.12, 1]), pin('fog.DirectionalInscatteringExponent', e)]
        B = {'b0': [], 'bf1': [fac(.4, .85, 1.6)] + lobe(0.003, 12), 'bf2': [fac(.4, .85, 1.6)] + lobe(0.01, 12), 'bf3': [fac(.4, .85, 1.6)] + lobe(0.03, 12)}
        for n, c in B.items(): G.append({'name': '%s_h20.5' % n, 'hour': 20.5, 'cmds': D + c, 'shots': ['S4', 'S4w'], 'settle_first': 8})
        v = look_tod.evaluate(t, 20.0); D = variants(v)['b0']
        G.append({'name': 'diskfill0_h20', 'hour': 20.0, 'cmds': D + [pin('fill.' + d, 0.0) for d in 'NESW'], 'shots': ['S4w'], 'settle_first': 8})
    json.dump({'groups': G}, open(os.path.join(a.out, 'plan_b.json'), 'w'), indent=1)
    print('plan_b', sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
