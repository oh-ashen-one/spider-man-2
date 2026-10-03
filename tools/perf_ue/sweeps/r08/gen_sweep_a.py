#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 08, sweep A on the BAKED round-07 table (v10): surface-only light for the twilight city (round-07 critic "Biggest gap": S4e 07:00 / 07:30 and S4w 19:00 frame
mean 59..118 with Y<10 <= 8.8 %), plus blue-hour sky colour at 20:30 and a diagnosis of the sub-horizon disk on S4w 19:48-20:30.
Live pins, relative to the baked value at the hour (look_tod.evaluate of the committed look_presets.json):
  city (hours 7.0: S4e + S4 | 7.5: S4e | 19.0: S4w + S4)
    b0    none
    sk3   sky.Intensity x3, skyc.VolumetricScatteringIntensity 1/3 (the volumetric fog keeps the sky light it had)
    sk6   sky.Intensity x6, skyc.VolumetricScatteringIntensity 1/6
    fl8   anti-solar horizon fill x8 (fill.W at dawn, fill.E at dusk; unshadowed, non-atmosphere, no volumetric scattering), fill.N / fill.S x4
    le5   pp.LocalExposureShadowContrastScale 0.5 (bilateral local exposure: only regions darker than the exposure's middle grey are lifted)
    le4b  pp.LocalExposureShadowContrastScale 0.4 + pp.LocalExposureBlurredLuminanceBlend 0.2 (less halo at the skyline)
    c1    sk3 + fills x4 + local exposure 0.6
    c2    sk3 + fl8 + local exposure 0.5
  blue hour (20.5: S4 + S4w)
    b0 | bh1 SkyLuminanceFactor x[.4, .85, 1.6] | bh2 bh1 + Mie scale x3 with warm Mie colour [1, .6, .3] | bh3 factor x[.25, .8, 2.0] + Mie x4 warm
  disk (20.0: S4w; the last groups of the session, render cvars persist)
    b0 | dsun sun.DiskScale 0 | dsky sky.Intensity .001 | dlumr r.Lumen.Reflections.Allow 0
usage: gen_sweep_a.py --out <dir>  -> <dir>/plan_a.json"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402


def pin(p, v):
    v = v if isinstance(v, (list, tuple)) else [v]
    return 'exec wh.ToDSet %s %s' % (p, ' '.join('%.6g' % x for x in v))


def city_variants(v, h):
    anti = 'fill.W' if h < 12 else 'fill.E'
    sky = lambda k: [pin('sky.Intensity', v['sky.Intensity'] * k), pin('skyc.VolumetricScatteringIntensity', 1.0 / k)]
    fills = lambda ka, kns: [pin(anti, max(v[anti], 0.5) * ka), pin('fill.N', max(v['fill.N'], 0.1) * kns), pin('fill.S', max(v['fill.S'], 0.1) * kns)]
    le = lambda s, blend=None: [pin('pp.LocalExposureShadowContrastScale', s)] + ([pin('pp.LocalExposureBlurredLuminanceBlend', blend)] if blend is not None else [])
    return {'b0': [], 'sk3': sky(3), 'sk6': sky(6), 'fl8': fills(8, 4), 'le5': le(0.5), 'le4b': le(0.4, 0.2),
            'c1': sky(3) + fills(4, 2) + le(0.6), 'c2': sky(3) + fills(8, 4) + le(0.5)}


def bh_variants(v):
    f = v['atm.SkyLuminanceFactor']; mie = v['atm.MieScatteringScale']
    fac = lambda kr, kg, kb: pin('atm.SkyLuminanceFactor', [f[0] * kr, f[1] * kg, f[2] * kb, 1])
    warm = lambda k: [pin('atm.MieScatteringScale', mie * k), pin('atm.MieScattering', [1.0, 0.6, 0.3, 1])]
    return {'b0': [], 'bh1': [fac(.4, .85, 1.6)], 'bh2': [fac(.4, .85, 1.6)] + warm(3), 'bh3': [fac(.25, .8, 2.0)] + warm(4)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t = look_tod.expand(look_tod.load_doc()); G = []
    for h, shots in ((7.0, ['S4e', 'S4']), (7.5, ['S4e']), (19.0, ['S4w', 'S4'])):
        v = look_tod.evaluate(t, h)
        for n, c in city_variants(v, h).items(): G.append({'name': '%s_h%g' % (n, h), 'hour': h, 'cmds': c, 'shots': shots, 'settle_first': 8})
    v = look_tod.evaluate(t, 20.5)
    for n, c in bh_variants(v).items(): G.append({'name': '%s_h20.5' % n, 'hour': 20.5, 'cmds': c, 'shots': ['S4', 'S4w'], 'settle_first': 8})
    for n, c in (('b0', []), ('dsun', [pin('sun.DiskScale', 0.0)]), ('dsky', [pin('sky.Intensity', 0.001)]), ('dlumr', ['exec r.Lumen.Reflections.Allow 0'])):
        G.append({'name': 'disk%s_h20' % n, 'hour': 20.0, 'cmds': c, 'shots': ['S4w'], 'settle_first': 8})
    json.dump({'groups': G}, open(os.path.join(a.out, 'plan_a.json'), 'w'), indent=1)
    print('plan_a', sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
