#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06, hold 6 (A) -> hold 7 (B): writes $SM2_LOOK_SCRATCH/r06/final6/knobs_final.json = the winners of the hold-6A variant sweep (gen_plans_e.py) as make_v2.py knobs, plus the sun ramp:
  W5   twilight: W4's R-highlight compression and denser twilight clouds (coverage .25, density .03) up to 19:30 and from 06:15 to 07:24, W4's factor schedule up to 19:30 and the hold-4 late factor (30 / 6 / 1.2 from 19:48:
       the S4w B-R at 20:00 depends on it; the denser clouds at 20:00 turned the sun-facing sky band neutral, so the clouds thin out again by 19:48)
  N2   night: cloud pattern offset (hold-2 Mv4); NO highlight roll-off (measured: it does not remove clipped pixels, it only lowers the means and the sky high-pass)
  D1   dawn mist density 4 at 07:36 (L26)
  G    golden black lift (see --golden)
  F    late-twilight fog x0.5 at 19:48-20:12 (L24a at 20:00: haze 18 Y over a 10.7 Y sky) and sun lux 5000 / 3500 at 20:12 / 20:36 (warm cloud light for L24b at 20:30)
  R    sun surface-light ramp -4 .. 8 deg (C++ sun.RampLo / sun.RampHi): the sunlit city loses / gains its direct light over 65 game minutes instead of 32
usage: make_final_knobs.py --out <json> [--golden 0.0012] [--ramp -4,8]"""
import argparse, copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_plans_e as E   # noqa: E402
import make_v2            # noqa: E402


SMOOTH_DAWN = ['sun.Temperature', 'fill.W', 'sky.Intensity', 'fog.FogHeightFalloff', 'fog.StartDistance', 'fog.FogInscatteringLuminance', 'fog.DirectionalInscatteringLuminance', 'pp.ColorContrast',
               'pp.AutoExposureMinBrightness', 'pp.AutoExposureMaxBrightness', 'pp.AutoExposureBias']


def dawn_smoothing(K):
    """round 06 hold 7 (C): the dawn keys 07:00 / 07:12 / 07:24 are mixes of different bases (dusk_am x dawn 0.6 / x golden_am 0.5 / x dawn 0.9) and zigzag in fog colour, height falloff, start distance, sun temperature,
    sky light, contrast and the exposure window (the lapse's 06:53-07:00 and 07:15-07:25 bumps of +3.5 Y per frame): each of these parameters is put on the straight line between the 06:48 and 07:36 keys. The sun
    lux ramp 05:00-06:48 is made geometric (it went x4.5 between 06:15 and 06:30, the sunrise-glow bump of the lapse: +5 Y per frame at 06:25-06:35)."""
    sys.path.insert(0, os.path.join(make_v2.WT, 'unreal', 'WebHomage', 'Scripts')); import look_tod
    t = look_tod.expand(make_v2.apply(make_v2.base_doc(), {**make_v2.KNOBS, **K}))
    kp = {k['h']: k['p'] for k in t['keys']}
    ov = {}
    for h in (7.0, 7.2, 7.4):
        f = (h - 6.8) / 0.8; o = {}
        for pn in SMOOTH_DAWN:
            a, b = kp[6.8][pn], kp[7.6][pn]
            o[pn] = [round(x + (y - x) * f, 5) for x, y in zip(a, b)] if isinstance(a, list) else round(a + (b - a) * f, 5)
        ov[str(h)] = o
    ov['6.5'] = {'sun.Intensity': round(kp[6.25]['sun.Intensity'] * (kp[6.8]['sun.Intensity'] / kp[6.25]['sun.Intensity']) ** ((6.5 - 6.25) / 0.55), 1)}
    return ov


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--golden', type=float, default=0.0); ap.add_argument('--ramp', default='-4,8')
    ap.add_argument('--late-factor', default='30,6,1.2'); ap.add_argument('--dawn-smooth', action='store_true', help='hold 7 (C): smooth the zigzag dawn keys, shift the city lights later, add extra keys for the loop'); a = ap.parse_args()
    lf = [float(x) for x in a.late_factor.split(',')]
    fac = copy.deepcopy(E.FAC_W3)
    fac['dusk'] = [(h, v) for h, v in fac['dusk'] if h <= 19.5] + [(19.8, [26, 5.5, 1.2]), (20.2, lf), (20.6, lf), (21.0, [15.5, 3.5, 1.1]), (21.4, [3.9, 1.5, 1.02])]
    cloud = {'dusk': [(18.8, 0.25, 0.03), (19.5, 0.25, 0.03), (19.8, 0.1, 0.02)], 'dawn': [(6.25, 0.25, 0.03), (7.4, 0.25, 0.03)]}
    K = {'tw_fac_pts': fac, 'tw_hl_r': E.HL_R, 'tw_cloud': cloud, 'cloud_offset': [0.0, 30000.0, 0.0, 0.0],
         'dawn_mist': {7.0: 0.02, 7.2: 0.1, 7.4: 0.8, 7.6: 4.0, 8.0: 1.6, 8.8: 0.05}, 'sun_ramp': [float(x) for x in a.ramp.split(',')],
         'tw_fog_scale': [(19.5, 1.0), (19.8, 0.5), (20.2, 0.5), (20.6, 0.7), (21.0, 1.0)], 'tw_sun_lux': {20.2: 5000.0, 20.6: 3500.0}}
    if a.dawn_smooth:
        K['twilight_overrides'] = dawn_smoothing(K)
        K['u_dawn'] = [(5.6, 1.0), (6.25, 0.8), (6.8, 0.4), (7.2, 0.12), (7.6, 0.0)]
        K['lights_dawn'] = {6.25: 1.0, 6.5: 0.85, 6.8: 0.5, 7.0: 0.3, 7.2: 0.2, 7.4: 0.08, 7.6: 0.0}
        K['extra_keys'] = [6.1, 6.35, 6.45, 6.55, 6.65, 6.9, 7.1, 7.3, 7.8, 8.4, 19.0, 19.35, 19.65, 19.9, 20.4]
        # hold 7 (B) measured: L26 0.602 (mist 4.0), a -4 Y / frame dip at 19:51-19:57 (fog inscatter x0.5 on top of the factor ramp): mist 4.5, the fog dimming spread over 19:30-20:12
        K['dawn_mist'] = {7.0: 0.02, 7.2: 0.1, 7.4: 0.8, 7.6: 4.5, 8.0: 1.7, 8.8: 0.05}
        K['tw_fog_scale'] = [(19.5, 1.0), (19.8, 0.8), (20.2, 0.55), (20.6, 0.75), (21.0, 1.0)]
    if a.golden > 0: K['golden_set'] = dict(make_v2.KNOBS['golden_set'], **{'pp.ColorOffset': [a.golden, a.golden, a.golden, 0.0]})
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(K, open(a.out, 'w'), indent=1)
    d = make_v2.apply(make_v2.base_doc(), {**make_v2.KNOBS, **K})   # smoke test: the knobs expand
    sys.path.insert(0, os.path.join(make_v2.WT, 'unreal', 'WebHomage', 'Scripts')); import look_tod
    t = look_tod.expand(d); print('knobs ->', a.out, '| keys', len(t['keys']), 'params', len(t['keys'][0]['p']))


if __name__ == '__main__':
    main()
