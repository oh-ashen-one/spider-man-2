#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07: the time-of-day table of round 07 = make_v2.py (the round-06 table builder) with the round-06 hold-9 knobs (docs/night1/look/round-06/diag/knobs_d_r06.json: C + the dawn exposure biases)
+ the round-07 twilight dome design, applied as explicit values on every key:
  * fog.FogCutoffDistance 0 on EVERY key: the height fog applies to the sky pixels at every hour, so the fog meets the sky continuously (round 06: 7e5 = an unfogged sky over a fogged city = a 90-113 Y step
    at the horizon facing the sun); no cutoff switch anywhere;
  * the sun's surface light decays GEOMETRICALLY (sun.SurfaceGain computed per key): from its natural value at `surface_geo` start to `end_lux` at the end hour, constant ratio per game minute, then 0
    (dusk 18:33 -> 19:30 at ~x3.3 per 6 min, 0 from 19:33; dawn mirrored 06:30 -> 07:27); extra keys every 0.05 h carry the curve;
  * sunc.VolumetricScatteringIntensity (the sun's volumetric-fog light) follows the sun's elevation from 1 (>= vol_elev[1] deg) to 0 (<= vol_elev[0] deg): the sun under the horizon no longer lights the
    volumetric fog unshadowed (the glowing band toward the sun);
  * sunc.CloudScatteredLuminanceScale, the fog's directional inscattering, fog max opacity / density multipliers and the SkyLuminanceFactor by twilight hour (schedules in the knob file).
usage: make_v3.py --knobs knobs_r07.json [--bias-overrides <json>] (--out <doc.json> | --in-place)"""
import argparse, copy, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts')); sys.path.insert(0, os.path.join(HERE, '..', 'r06'))
import look_tod, make_v2   # noqa: E402

PRESETS = os.path.join(WT, 'unreal', 'WebHomage', 'Scripts', 'look_presets.json')
KNOBS_D = os.path.join(WT, 'docs', 'night1', 'look', 'round-06', 'diag', 'knobs_d_r06.json')

R07 = {
    'cutoff_all': 0.0,
    # [start hour, end hour, lux at the end hour]; between them the surface lux falls (dusk) / rises (dawn) geometrically; dusk: 0 after end + 0.05 h; dawn: 0 before start - 0.05 h
    'surface_geo': {'dusk': [18.55, 19.5, 0.5], 'dawn': [6.5, 7.45, 0.5]},
    'surface_step': 0.05,
    'vol_elev': [-2.0, 3.0],
    'sun_cloud': None,     # {'dusk': [(h, scale)], 'dawn': [...]}: sunc.CloudScatteredLuminanceScale (grey) inside the listed hours, 1 outside
    'tw_dir': None,        # {'dusk': [(h, mult)], 'dawn': [...]}: multiplier of fog.DirectionalInscatteringLuminance
    'tw_maxop': None,      # {'dusk': [(h, value)], 'dawn': [...]}: fog.FogMaxOpacity
    'tw_dens': None,       # {'dusk': [(h, mult)], 'dawn': [...]}: multiplier of fog.FogDensity
    'tw_maxev': None,      # {'dusk': [(h, EV100)], 'dawn': [...]}: pp.AutoExposureMaxBrightness (hold A: the sun-facing stills were clamped by it and clipped)
    'tw_minev': None,      # {'dusk': [(h, EV100)], 'dawn': [...]}: pp.AutoExposureMinBrightness (hold B: the twilight exposure sat on its MIN clamp, so the sun-facing views blew out at the S4 bias)
    'bias_curve': None,    # {'dusk': [(h, bias)], 'dawn': [...]}: pp.AutoExposureBias on EVERY key inside the range (no zigzag between main keys and snapshot keys); --bias-overrides apply after it
    'tw_set': None,        # {param: {'dusk': [(h, number | [r, g, b, a])], 'dawn': [...]}}: explicit values of any param inside the listed hours (e.g. cloudv.Cloud_AlbedoColor)
    'moon_vol': None,      # number: moonc.VolumetricScatteringIntensity on every key
    'golden_sky': None,    # {'hours': [..], 'factor': [r, g, b]} SkyLuminanceFactor on golden keys (golden S4 <= 100 with the fog on the sky)
    'v2': {},              # make_v2 knob overrides (tw_fac_pts, tw_cloud, twilight_overrides, ...)
}


def ss(a, b, x):
    x = min(1.0, max(0.0, (x - a) / (b - a))); return x * x * (3 - 2 * x)


def natural_lux(t, h):
    T = t
    el = look_tod.body_dir(T['sun'], h, T['sun']['lat'])[0]
    v = look_tod.evaluate(t, h)
    return v['sun.Intensity'] * ss(v['sun.RampLo'], max(v['sun.RampLo'] + 0.5, v['sun.RampHi']), el), el


def geo_hours(R):
    st = R['surface_step']; hs = set()
    for ph, (h0, h1, _) in R['surface_geo'].items():
        n = int(round((h1 - h0) / st))
        hs |= {round(h0 + i * st, 4) for i in range(n + 1)}
        hs |= {round(h1 + st, 4)} if ph == 'dusk' else {round(h0 - st, 4)}
    return sorted(hs)


def side(h): return 'dusk' if h >= 12 else 'dawn'


BIAS_OV = set()


def apply(K, R):
    K = copy.deepcopy(K); R = copy.deepcopy(R)
    K.update(R.get('v2') or {})
    K['surface_gain'] = None
    K['cutoff_all'] = R['cutoff_all']
    K['extra_keys'] = sorted(set(float(x) for x in (K.get('extra_keys') or [])) | set(geo_hours(R)))
    d = make_v2.apply(make_v2.base_doc(), K)
    t0 = look_tod.expand(d)
    base = {k['h']: k['p'] for k in t0['keys']}
    # geometric surface-light curve per phase
    G = {}
    for ph, (h0, h1, lux_end) in R['surface_geo'].items():
        a_h, b_h = (h0, h1)
        if ph == 'dusk': e0, _ = natural_lux(t0, a_h); r = (lux_end / e0) ** (1.0 / (b_h - a_h))   # lux(h) = e0 * r^(h - h0)
        else: e1, _ = natural_lux(t0, b_h); r = (e1 / lux_end) ** (1.0 / (b_h - a_h))              # lux(h) = lux_end * r^(h - h0)
        G[ph] = (h0, h1, lux_end, r, e0 if ph == 'dusk' else e1)
    rep = []
    for k in d['tod']['keys']:
        h = float(k['h']); s = k.setdefault('set', {}); b = base[h]
        el = look_tod.body_dir(t0['sun'], h, t0['sun']['lat'])[0]
        # surface gain
        ph = side(h); h0, h1, lux_end, r, eref = G[ph]
        nat, _ = natural_lux(t0, h)
        if ph == 'dusk':
            if h < h0 - 1e-6: g = 1.0
            elif h <= h1 + 1e-6: g = min(1.0, eref * r ** (h - h0) / nat) if nat > 0 else 0.0
            else: g = 0.0
        else:
            if h < h0 - 1e-6: g = 0.0
            elif h <= h1 + 1e-6: g = min(1.0, lux_end * r ** (h - h0) / nat) if nat > 0 else 0.0
            else: g = 1.0
        s['sun.SurfaceGain'] = round(g, 6)
        if 17.5 <= h <= 20.0 or 6.0 <= h <= 8.0: rep.append((h, round(nat, 1), round(nat * g, 2), round(g, 5)))
        # sun volumetric scattering by elevation
        lo, hi = R['vol_elev']; s['sunc.VolumetricScatteringIntensity'] = round(ss(lo, hi, el), 4)
        def sch(name):
            tab = R.get(name)
            return make_v2.sched(h, [tuple(p) for p in tab[ph]]) if tab and tab.get(ph) else None
        c = sch('sun_cloud'); s['sunc.CloudScatteredLuminanceScale'] = [round(c, 4)] * 3 + [1.0] if c is not None else [1.0, 1.0, 1.0, 1.0]
        m = sch('tw_dir')
        if m is not None: s['fog.DirectionalInscatteringLuminance'] = [round(x * m, 6) for x in b['fog.DirectionalInscatteringLuminance'][:3]] + [1.0]
        mo = sch('tw_maxop')
        if mo is not None: s['fog.FogMaxOpacity'] = round(mo, 4)
        md = sch('tw_dens')
        if md is not None: s['fog.FogDensity'] = round(b['fog.FogDensity'] * md, 6)
        mn = sch('tw_minev')
        if mn is not None: s['pp.AutoExposureMinBrightness'] = round(mn, 3)
        bc = sch('bias_curve')
        if bc is not None and str(h) not in BIAS_OV: s['pp.AutoExposureBias'] = round(bc, 4)
        for pn, tab in (R.get('tw_set') or {}).items():
            if tab.get(ph):
                vv = make_v2.sched(h, [(p0, p1) for p0, p1 in tab[ph]])
                if vv is not None: s[pn] = [round(x, 5) for x in vv] if isinstance(vv, list) else round(vv, 5)
        mx = sch('tw_maxev')
        if mx is not None: s['pp.AutoExposureMaxBrightness'] = round(mx, 3)
        if R.get('moon_vol') is not None: s['moonc.VolumetricScatteringIntensity'] = float(R['moon_vol'])
        gs = R.get('golden_sky')
        if gs and any(abs(h - x) < 1e-6 for x in gs['hours']): s['atm.SkyLuminanceFactor'] = list(gs['factor'][:3]) + [1.0]
        s['fog.FogCutoffDistance'] = R['cutoff_all']
    return d, rep


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--knobs', default=''); ap.add_argument('--out', default=''); ap.add_argument('--in-place', action='store_true'); ap.add_argument('--bias-overrides', default='')
    ap.add_argument('--report', action='store_true')
    a = ap.parse_args()
    K = copy.deepcopy(make_v2.KNOBS); K.update(json.load(open(KNOBS_D)))
    R = copy.deepcopy(R07)
    if a.knobs: R.update(json.load(open(a.knobs)))
    if a.bias_overrides:
        v2 = R.setdefault('v2', {}); ov = {k: dict(v) for k, v in (v2.get('twilight_overrides') or K.get('twilight_overrides') or {}).items()}
        for hh, bb in json.load(open(a.bias_overrides)).items(): ov.setdefault(str(float(hh)), {})['pp.AutoExposureBias'] = float(bb); BIAS_OV.add(str(float(hh)))
        v2['twilight_overrides'] = ov
    d, rep = apply(K, R)
    txt = json.dumps(d, indent=1)
    if a.in_place: open(PRESETS, 'w').write(txt)
    elif a.out: open(a.out, 'w').write(txt)
    t = look_tod.expand(d)
    print('keys', len(t['keys']), 'params', len(t['keys'][0]['p']))
    if a.report:
        for h, nat, eff, g in rep: print('  %.2f natural %.1f lux -> surface %.2f lux (gain %.5f)' % (h, nat, eff, g))


if __name__ == '__main__':
    main()
