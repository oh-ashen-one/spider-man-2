#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06, hold 2 plans. Key tables (written next to the plans) and a still plan (run_r06.py format):
  keys_v2a.txt        make_v2.py defaults (structural: eased city lights, moon after 20:00, hero keys, extra keys; twilight: warm sky factor, dimmed ambient)
  keys_hero14.txt / keys_hero18.txt   keys_base with herofill 0 and hero 1.4 / 1.8 (hero clip calibration)
  plan_b.json         V2a twilight stills (S4 + the sun-facing perch at 6.5 .. 21.5), no-cloud twilight probes, dawn mist variants (S1 + S4e at 7.6), golden combinations (S1..S8 at 18.4),
                      22:00 moon / cloud variants (S4m + S4)
usage: gen_plans_b.py --out <dir>"""
import argparse, json, os, sys

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
    import copy; K = copy.deepcopy(make_v2.KNOBS)
    if a.knobs: K.update(json.load(open(a.knobs)))
    doc = look_tod.load_doc()
    d2 = make_v2.apply(doc, K); tab = look_tod.expand(d2)
    v2a = os.path.join(out, 'keys_v2a.txt'); open(v2a, 'w').write(look_tod.to_text(tab))
    json.dump(d2, open(os.path.join(out, 'doc_v2a.json'), 'w'), indent=1)
    base_tab = look_tod.expand(doc)
    for sc in (1.4, 1.8):
        open(os.path.join(out, 'keys_hero%d.txt' % round(sc * 10)), 'w').write(look_tod.to_text(look_tod.expand(doc, ['h=*:herofill=0', 'h=*:hero=%g' % sc])))
    E = lambda h: look_tod.evaluate(tab, h)

    def G(name, h, shots, cmds=(), **kw):
        g = {'name': name, 'hour': h, 'keys': v2a, 'cmds': list(cmds), 'shots': shots}; g.update(kw); return g
    P = []
    for h in (6.5, 7.0, 7.5, 19.0, 19.5, 19.8, 20.0, 20.5, 21.0, 21.5):
        P.append(G('B0_h%g' % h, h, ['S4', 'S4e' if h < 12 else 'S4w']))
    for h in (20.0, 20.5):   # clouds off: does the warm tint reach the top rows of the sun-facing sky?
        P.append(G('B1_nocloud_h%g' % h, h, ['S4w'], [pin('cloud.Cloud_GlobalCoverage', -0.3)]))
    for h in (6.5, 19.8, 20.0, 20.5):   # a warm Rayleigh colour makes the whole twilight sky (and its ambient) orange, independent of the sun's depression: B-R of the sun-facing band
        P.append(G('B2_ray_h%g' % h, h, ['S4', 'S4e' if h < 12 else 'S4w'], [pin('atm.RayleighScattering', [0.9, 0.45, 0.2, 1.0])]))
    b = E(7.6)
    mist = [pin('sun.Temperature', 6500), pin('fog.FogHeightFalloff', 0.5), pin('fog.StartDistance', 0), pin('fog.FogInscatteringLuminance', [0.5, 0.56, 0.68, 1.0]), pin('fog.FogMaxOpacity', 0.9),
            pin('pp.ColorContrast', [1.0, 1.0, 1.0, 1.0])]
    for nm, dens in (('D4_mist.15', 0.15), ('D5_mist.5', 0.5), ('D6_mist1.5', 1.5)):
        P.append(G('%s_h7.6' % nm, 7.6, ['S1', 'S4e'], mist + [pin('fog.FogDensity', dens)]))
    P.append(G('D0v2_h7.6', 7.6, ['S1', 'S4e']))
    g = E(18.4)
    allp = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']
    P.append(G('G9_h18.4', 18.4, allp, [pin('pp.AutoExposureBias', 1.0), pin('pp.ColorGainHighlights', [0.55, 0.72, 0.72, 1.0]), pin('mpc.ShadeFill', 0.2)], settle_first=10))
    P.append(G('G10_h18.4', 18.4, allp, [pin('pp.AutoExposureBias', 1.0), pin('pp.ColorGainHighlights', [0.55, 0.72, 0.72, 1.0]), pin('mpc.ShadeFill', 0.2),
                                            pin('atm.MieScatteringScale', g['atm.MieScatteringScale'] * 0.6), pin('atm.AerialPespectiveViewDistanceScale', 3.5)], settle_first=10))
    # sky fog switch: hold-1 sweep H showed cutoff 7e5 (sky unfogged) at 18.4 takes S4 from 117.6 to 99.9 (far band 168 -> 141, sky B-R -61 -> -86). If the sky is unfogged at EVERY hour there is no cutoff
    # step at all: golden with the best-guess combination, day, dawn
    P.append(G('G11_cut_h18.4', 18.4, allp, [pin('fog.FogCutoffDistance', 700000), pin('pp.AutoExposureBias', 1.0), pin('pp.ColorGainHighlights', [0.55, 0.72, 0.72, 1.0]), pin('mpc.ShadeFill', 0.2)], settle_first=10))
    P.append(G('Day0_h13', 13.0, ['S4', 'S8', 'S1']))
    P.append(G('Day1_cut_h13', 13.0, ['S4', 'S8', 'S1'], [pin('fog.FogCutoffDistance', 700000)]))
    P.append(G('Dawn1_cut_h7.6', 7.6, ['S4', 'S4e'], [pin('fog.FogCutoffDistance', 700000)]))
    P.append(G('Mb0_h22', 22.0, ['S4m', 'S4']))
    P.append(G('Mb1_h22', 22.0, ['S4m', 'S4'], [pin('moonc.LightSourceAngle', 1.0), pin('moonc.CloudScatteredLuminanceScale', [3, 3, 3, 1]), pin('cloud.Cloud_GlobalCoverage', 0.2), pin('cloud.Cloud_GlobalDensity', 0.025)]))
    P.append(G('Mb2_h22', 22.0, ['S4m', 'S4'], [pin('moonc.LightSourceAngle', 1.0), pin('moonc.CloudScatteredLuminanceScale', [4, 4, 4, 1]), pin('cloud.Cloud_GlobalCoverage', 0.12), pin('cloud.Cloud_GlobalDensity', 0.02), pin('stars', 2.5)]))
    json.dump({'groups': P}, open(os.path.join(out, 'plan_b.json'), 'w'), indent=1)
    print('plan_b', sum(len(x['shots']) for x in P), 'poses', len(P), 'groups; keys written to', out)


if __name__ == '__main__':
    main()
