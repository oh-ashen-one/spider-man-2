#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06, hold 3 plans: keys_v2b.txt (make_v2.py with the hold-2 knobs: sky unfogged at every hour, hero 1.6, golden red highlights / shade fill) and plan_c.json (run_r06.py format):
  twilight probes at 19.8 20.0 20.5 (S4 + S4w) and 6.5 7.5 (S4 + S4e): C1 sun x10 / 2500 K, C2 sky luminance factor [30,6,1.2] with the ambient (sky light, fills, fog sky ambient) cut to 10 %, C3 both,
  dawn mist: denser fog + volumetric shafts at 7.6 (S1 + S4e), golden S1..S8 with fill.E 5 / 10 / 16 (the east fill lights the shaded east-facing facades of S7 / S1), night 22 S1..S8 + S4m, moon variants.
usage: gen_plans_c.py --out <dir>"""
import argparse, copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts')); sys.path.insert(0, HERE)
import look_tod, make_v2   # noqa: E402


def fmt(v): return ' '.join('%.6g' % x for x in (v if isinstance(v, list) else [v]))
def pin(n, v): return 'exec wh.ToDSet %s %s' % (n, fmt(v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--knobs', default='')
    a = ap.parse_args()
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    K = copy.deepcopy(make_v2.KNOBS)
    if a.knobs: K.update(json.load(open(a.knobs)))
    doc = make_v2.base_doc(); d2 = make_v2.apply(doc, K); tab = look_tod.expand(d2)
    keys = os.path.join(out, 'keys_v2b.txt'); open(keys, 'w').write(look_tod.to_text(tab)); json.dump(d2, open(os.path.join(out, 'doc_v2b.json'), 'w'), indent=1)
    E = lambda h: look_tod.evaluate(tab, h)

    def G(name, h, shots, cmds=(), **kw):
        g = {'name': name, 'hour': h, 'keys': keys, 'cmds': list(cmds), 'shots': shots}; g.update(kw); return g
    P = []
    for h, face in ((19.8, 'S4w'), (20.0, 'S4w'), (20.5, 'S4w'), (6.5, 'S4e'), (7.5, 'S4e')):
        b = E(h)
        base = [pin('sky.Intensity', b['sky.Intensity'] * 0.1)] + [pin('fill.' + d, b['fill.' + d] * 0.1) for d in 'NESW'] + [pin('fog.SkyAtmosphereAmbientContributionColorScale', [0.1, 0.1, 0.1, 1.0])]
        sun = [pin('sun.Intensity', min(80000.0, b['sun.Intensity'] * 10.0)), pin('sun.Temperature', 2500)]
        P.append(G('C0_h%g' % h, h, ['S4', face]))
        P.append(G('C1_sun10_h%g' % h, h, ['S4', face], sun))
        P.append(G('C2_fac30_h%g' % h, h, ['S4', face], base + [pin('atm.SkyLuminanceFactor', [30, 6, 1.2, 1.0])]))
        P.append(G('C3_both_h%g' % h, h, ['S4', face], base + [pin('atm.SkyLuminanceFactor', [30, 6, 1.2, 1.0])] + sun))
    mist = [pin('sun.Temperature', 6500), pin('fog.FogHeightFalloff', 0.5), pin('fog.StartDistance', 0), pin('fog.FogInscatteringLuminance', [0.5, 0.56, 0.68, 1.0]), pin('fog.FogMaxOpacity', 0.95),
            pin('pp.ColorContrast', [1.0, 1.0, 1.0, 1.0])]
    P.append(G('M1_mist4_h7.6', 7.6, ['S1', 'S4e'], mist + [pin('fog.FogDensity', 4.0)]))
    P.append(G('M2_mist10_h7.6', 7.6, ['S1', 'S4e'], mist + [pin('fog.FogDensity', 10.0)]))
    P.append(G('M3_shafts_h7.6', 7.6, ['S1', 'S4e'], mist + [pin('fog.FogDensity', 4.0), pin('fog.VolumetricFogExtinctionScale', 4.0), pin('fog.VolumetricFogScatteringDistribution', 0.75), pin('sun.Intensity', 90000)]))
    allp = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']
    P.append(G('G12_base_h18.4', 18.4, allp, [], settle_first=10))
    for nm, v in (('G13_fillE10', 10.0), ('G14_fillE16', 16.0)):
        P.append(G('%s_h18.4' % nm, 18.4, ['S1', 'S3', 'S5', 'S6', 'S7', 'S8'], [pin('fill.E', v)], settle_first=10))
    P.append(G('N0_h22', 22.0, allp + ['S4m'], [], settle_first=14))
    P.append(G('Mc1_h22', 22.0, ['S4m', 'S4'], [pin('moonc.LightSourceAngle', 1.0), pin('moonc.CloudScatteredLuminanceScale', [3, 3, 3, 1]), pin('cloud.Cloud_GlobalCoverage', 0.2), pin('cloud.Cloud_GlobalDensity', 0.025), pin('stars', 2.5)]))
    json.dump({'groups': P}, open(os.path.join(out, 'plan_c.json'), 'w'), indent=1)
    print('plan_c', sum(len(x['shots']) for x in P), 'poses', len(P), 'groups ->', out)


if __name__ == '__main__':
    main()
