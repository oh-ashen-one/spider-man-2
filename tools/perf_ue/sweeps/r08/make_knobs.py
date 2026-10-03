#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 08: writes a make_v4.py knob file (the round-08 schedules) from a few numbers.
  local exposure (bilateral, blurred-luminance blend `blend`, middle-grey bias `pivot` on every key; the shadow contrast is 1 = off outside the twilight windows):
    dawn  [[h, shadow contrast], ...]  (1.0 at both ends)        dusk  [[h, shadow contrast], ...]
  blue hour: SkyLuminanceFactor multiplier `bh_fac` [r, g, b] on the keys inside `bh_win` [h0, h1, h2, h3] (ramp h0 -> h1, hold to h2, ramp out to h3) and the fog's directional
    inscattering lobe `bh_lobe` [luminance R, exponent] held over the same window (the round-07 values outside)
usage: make_knobs.py --out knobs.json [--json '{...overrides...}']"""
import argparse, json

D = {
    'blend': 0.2, 'pivot': -1.0,
    'dawn': [[5.8, 1.0], [6.5, 0.45], [7.0, 0.15], [7.6, 0.2], [8.0, 0.45], [8.6, 1.0]],
    'dusk': [[18.45, 1.0], [18.8, 0.6], [19.0, 0.35], [19.5, 0.55], [19.9, 0.8], [20.4, 1.0]],
    'bh_fac': [0.4, 0.85, 1.6], 'bh_win': [19.95, 20.35, 20.65, 21.05], 'bh_lobe': [0.01, 12.0],
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--json', default='{}'); a = ap.parse_args()
    P = dict(D); P.update(json.loads(a.json))
    S = {'set': {}, 'mul': {}, 'params': P}
    S['set']['pp.LocalExposureBlurredLuminanceBlend'] = [[0.0, P['blend']], [24.0, P['blend']]]
    S['set']['pp.LocalExposureMiddleGreyBias'] = [[0.0, P['pivot']], [24.0, P['pivot']]]
    S['set']['pp.LocalExposureShadowContrastScale'] = P['dawn'] + P['dusk']
    if P.get('bh_fac'):
        h0, h1, h2, h3 = P['bh_win']; f = P['bh_fac']
        S['mul']['atm.SkyLuminanceFactor'] = [[h0, [1, 1, 1]], [h1, f], [h2, f], [h3, [1, 1, 1]]]
    if P.get('bh_lobe'):
        h0, h1, h2, h3 = P['bh_win']; k, e = P['bh_lobe']
        S['set']['fog.DirectionalInscatteringLuminance'] = [[h1, [k, k * 0.42, k * 0.12, 1.0]], [h2, [k, k * 0.42, k * 0.12, 1.0]]]
        S['set']['fog.DirectionalInscatteringExponent'] = [[h1, e], [h2, e]]
    json.dump(S, open(a.out, 'w'), indent=1)
    print('knobs ->', a.out)


if __name__ == '__main__':
    main()
