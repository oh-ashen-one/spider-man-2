#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 08, generic live-pin sweep on the BAKED table (every group pins every round-08 param, so nothing stays on the volume between groups).
variants JSON: {name: {"le": [shadow contrast, blurred-luminance blend, middle-grey bias], "sky": sky-light multiplier (fog scattering 1/k), "ili": pp.IndirectLightingIntensity multiplier,
                       "bias": EV added to pp.AutoExposureBias, "pins": {param: value}}}   (absent = the baked value / local exposure off)
usage: gen_sweep_c.py --out <dir> --name c --variants <json file or inline> --hours 7.0,7.5,19.0 [--shots facing,S4] -> <dir>/plan_<name>.json"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402


def pin(p, v):
    v = v if isinstance(v, (list, tuple)) else [v]
    return 'exec wh.ToDSet %s %s' % (p, ' '.join('%.6g' % x for x in v))


def cmds(v, spec):
    le = spec.get('le', [1.0, 0.6, 0.0]); k = spec.get('sky', 1.0)
    c = [pin('pp.LocalExposureShadowContrastScale', le[0]), pin('pp.LocalExposureBlurredLuminanceBlend', le[1]), pin('pp.LocalExposureMiddleGreyBias', le[2]),
         pin('skyc.VolumetricScatteringIntensity', 1.0 / k)]
    if k != 1.0: c.append(pin('sky.Intensity', v['sky.Intensity'] * k))
    if spec.get('ili'): c.append(pin('pp.IndirectLightingIntensity', v['pp.IndirectLightingIntensity'] * spec['ili']))
    if spec.get('bias'): c.append(pin('pp.AutoExposureBias', v['pp.AutoExposureBias'] + spec['bias']))
    for p, x in (spec.get('pins') or {}).items(): c.append(pin(p, x))
    return c


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--name', default='c'); ap.add_argument('--variants', required=True)
    ap.add_argument('--hours', default='7.0,7.5,19.0'); ap.add_argument('--shots', default='facing,S4')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    V = json.load(open(a.variants)) if os.path.exists(a.variants) else json.loads(a.variants)
    t = look_tod.expand(look_tod.load_doc()); G = []
    for h in [float(x) for x in a.hours.split(',')]:
        v = look_tod.evaluate(t, h)
        shots = [('S4e' if h < 12 else 'S4w') if s == 'facing' else s for s in a.shots.split(',')]
        for n, spec in V.items(): G.append({'name': '%s_h%g' % (n, h), 'hour': h, 'cmds': cmds(v, spec), 'shots': shots, 'settle_first': 8})
    json.dump({'groups': G, 'variants': V}, open(os.path.join(a.out, 'plan_%s.json' % a.name), 'w'), indent=1)
    print('plan_%s' % a.name, sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
