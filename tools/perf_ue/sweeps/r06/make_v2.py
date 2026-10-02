#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06: builds the round-06 time-of-day table ("tod" block of Scripts/look_presets.json) from the round-05 one + a knob file, so every change is one reviewable script.
  python3 make_v2.py --knobs knobs_v2.json --out <doc.json>            (writes a full look_presets.json document; use --in-place to rewrite Scripts/look_presets.json)
Structure (independent of any measurement; the numbers are in the knob file / KNOBS below):
  * keys: extra keys through the twilights so every ramp is shaped by >= 3 keys (dusk 18.8 19.5 20.2 21.0 21.4, dawn 5.6 6.5 7.2) built as mixes of their neighbours, then overridden;
  * city lights schedule u(h) (0 = day, 1 = night) drives mpc.EmissiveScale (log), NightK, DnTime, InteriorGain, ShopGain, ShadeFill: the x11 dusk emissive ramp spreads over 18.8-21.0
    (10-90 % in ~1.1 h instead of 36 min), dawn mirrored;
  * moon.Intensity keyed in only after 20:00 (0 until 20.2, 9 lux at 21.4): no moonlit surfaces in the blue hour; moon disk / cloud properties (moonc.*);
  * hero (exposure-relative rim / fill / top) and herofill (the traversal character's 5000 cd fill) by hour;
  * exposure windows widened at the twilights (max EV) so a bright excursion is metered down, not clamped;
  * dawn base `dawn`: cooler, hazier (own palette, not golden mirrored).
"""
import argparse, copy, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
PRESETS = os.path.join(WT, 'unreal', 'WebHomage', 'Scripts', 'look_presets.json')
BASE = os.path.join(HERE, 'look_presets_r05.json')   # the round-05 document: apply() always starts from it, so --in-place is idempotent


def base_doc(): return json.load(open(BASE))

# ----------------------------------------------------------------------------------------------- knobs (defaults = the pre-measurement design)
KNOBS = {
    # city lights schedule u(h): (hour, u) anchors, piecewise linear, cyclic
    'u_dusk': [(18.8, 0.0), (19.2, 0.03), (19.5, 0.08), (19.8, 0.18), (20.2, 0.42), (20.6, 0.70), (21.0, 0.92), (21.4, 1.0)],   # round 06 hold 3: windows later, the far band at 20:00-20:30 stays under the sky
    'u_dawn': [(5.6, 1.0), (6.25, 0.60), (6.8, 0.20), (7.2, 0.05), (7.6, 0.0)],
    'moon': {19.8: 0.0, 20.2: 0.0, 20.6: 2.5, 21.0: 6.0, 21.4: 9.0},
    'hero': {18.4: 0.0, 19.2: 0.2, 19.8: 0.7, 20.6: 1.0, 6.25: 1.0, 6.8: 0.3, 7.6: 0.0},
    'herofill': {18.4: 1.0, 19.2: 0.5, 19.8: 0.1, 20.6: 0.0, 6.25: 0.0, 6.8: 0.3, 7.6: 1.0},
    'night_cloud': {'cloud.Cloud_GlobalCoverage': 0.2, 'cloud.Cloud_GlobalDensity': 0.025},   # moonlit clouds (hold 2 Mb1: sky high-pass std 3.5)
    'moonc': {'moonc.LightSourceAngle': 1.0, 'moonc.CloudScatteredLuminanceScale': [3, 3, 3, 1], 'moonc.AtmosphereSunDiskColorScale': [1, 1, 1, 1]},
    'night_stars': {4.9: 2.0, 5.6: 1.0, 20.2: 0.6, 20.6: 1.4, 21.0: 2.0, 21.4: 2.0},
    # dawn mist at 07:36 (own palette; hold 3 M1: S1 correlation against golden 0.977 -> 0.486 at density 4; cooler inscatter than M1's orange)
    'dawn_mist': {7.0: 0.02, 7.2: 0.1, 7.4: 0.6, 7.6: 3.0, 8.0: 1.2, 8.8: 0.05},
    'dawn_set': {'fog.FogDensity': 3.0, 'fog.FogHeightFalloff': 0.5, 'fog.StartDistance': 0.0, 'fog.FogMaxOpacity': 0.95, 'fog.FogInscatteringLuminance': [0.5, 0.56, 0.68, 1.0],
                 'fog.DirectionalInscatteringLuminance': [0.1, 0.1, 0.1, 1.0], 'sun.Temperature': 6500.0, 'pp.ColorContrast': [1.0, 1.0, 1.0, 1.0]},
    # fog cutoff is a switch (the driver steps it at the middle of the segment): explicit 0 / 700000 on every new key, never a mix. 0 = fog applies to the sky pixels, 7e5 = sky unfogged
    'cutoff': {18.8: 0, 19.5: 0, 20.2: 0, 21.0: 700000, 21.4: 700000, 5.6: 700000, 6.5: 0, 7.2: 0},
    # twilight sky design (round-06 hold-1 sweep A: dimming the ambient (sky light, fills, fog sky ambient) takes the far band 15-25 Y under the sky at 6.5-7.5 and 19.5-21.5; the warm
    # SkyLuminanceFactor gives the sun-facing sky band B-R <= -20 until ~19.5 only: the tint is stronger and later, see tw_warm)
    'tw_w': {'dusk': [(18.8, 0.0), (19.2, 0.6), (19.5, 1.0), (20.6, 1.0), (21.0, 0.5), (21.5, 0.0)], 'dawn': [(5.6, 0.0), (6.0, 0.5), (6.25, 1.0), (7.0, 1.0), (7.3, 0.8), (7.6, 0.5)]},
    'tw_warm': {'dusk': [(18.8, 0.0), (19.2, 0.4), (19.5, 0.8), (19.8, 1.0), (20.6, 1.0), (21.0, 0.5), (21.5, 0.0)], 'dawn': [(5.6, 0.0), (6.0, 0.6), (6.25, 1.0), (6.8, 0.8), (7.3, 0.2), (7.6, 0.0)]},
    'tw_factor': [30.0, 6.0, 1.2],   # hold 3 C2: sky band B-R <= -20 facing the sun until 20:30 with the ambient cut to 10 %
    'tw_sky_scale': 0.1, 'tw_fill_scale': 0.1, 'tw_amb': 0.1,
    # round-06 hold-2 findings: the sky unfogged at EVERY hour (cutoff 7e5 on every key) = no cutoff switch at all (golden S4 117.6 -> 99.9, far band 168 -> 141); hero lights 1.6 x nominal;
    # golden: red highlights down (S7 clipped 3.6 -> 1.6 %), shade fill .2 (Y<10 on S1 / S3 / S6 / S8 under 8 %)
    'cutoff_all': 700000.0,
    'hero_scale': 1.6,
    'golden_set': {'pp.ColorGainHighlights': [0.55, 0.72, 0.72, 1.0], 'mpc.ShadeFill': 0.2},
    'golden_hours': [7.6, 18.4],
    'twilight_overrides': {},      # {hour: {param: value}} applied last (sweep results go here)
    # ---- round 06 hold 5+ knobs (all default OFF = the committed hold-4 table; variants / the final table set them) ----
    # explicit SkyLuminanceFactor schedule per twilight (replaces tw_warm x tw_factor): {'dusk': [(h, [r, g, b]), ...], 'dawn': [...]}; outside the listed hours the factor is 1
    'tw_fac_pts': None,
    # R-highlight compression at the twilights (the red sky clips the R channel): {'dusk': [(h, mult)], 'dawn': [...]} multiplies pp.ColorGainHighlights R (outside the hours 1)
    'tw_hl_r': None,
    # twilight clouds: {'dusk': [(h, coverage, density)], 'dawn': [...]} written on the key hours inside the listed range
    'tw_cloud': None,
    # night highlight roll-off (L15b: no clipped px in the hero box): {'dusk': [(h, mult)], 'dawn': [(h, mult)], 'night': mult} multiplies pp.ColorGainHighlights on the night keys
    'night_hl': None,
    # moonlit cloud pattern: cloudv.Layout_GlobalTexturePlacement on every key (hold-2 Mv4: [0, 30000, 0, 0] = sky high-pass std 3.4 at 22:00 with the disk clear)
    'cloud_offset': None,
}


def u_of(h, anchors):
    pts = sorted(anchors)
    if h <= pts[0][0]: return pts[0][1]
    if h >= pts[-1][0]: return pts[-1][1]
    for (h0, u0), (h1, u1) in zip(pts, pts[1:]):
        if h0 <= h <= h1: return u0 + (u1 - u0) * (h - h0) / (h1 - h0)


def sched(h, pts, outside=None):
    """piecewise-linear interpolation of (hour, number | list) points; `outside` (default: the end values are NOT extended, None) outside the listed hours"""
    pts = sorted(pts, key=lambda p: p[0])
    if h < pts[0][0] or h > pts[-1][0]: return outside
    for (h0, v0), (h1, v1) in zip(pts, pts[1:]):
        if h0 <= h <= h1:
            t = 0.0 if h1 == h0 else (h - h0) / (h1 - h0)
            return [a + (b - a) * t for a, b in zip(v0, v1)] if isinstance(v0, list) else v0 + (v1 - v0) * t
    return outside


def city_u(h, K):
    if 18.0 <= h <= 24.0 or h < 0.5: return u_of(h, K['u_dusk']) if h >= 18.0 else 1.0
    if h < 4.9: return 1.0
    if h <= 7.6: return u_of(h, K['u_dawn'])
    return 0.0


def lerp(a, b, t): return a + (b - a) * t


def apply(doc, K):
    K = copy.deepcopy(K)
    for n in ('moon', 'hero', 'herofill', 'cutoff', 'night_stars', 'dawn_mist'): K[n] = {float(k): v for k, v in K[n].items()}   # json knob files carry string keys
    d = copy.deepcopy(doc); T = d['tod']
    P = d['presets']
    gold, night = P['golden']['mpc'], P['night']['mpc']
    # dawn base: cooler and hazier than golden_am (placeholder values until the dawn sweep is read; see HANDOFF)
    T['derived']['dawn'] = {'from': 'golden_am', 'set': dict(K.get('dawn_set', {}))}
    keys = {k['h']: k for k in T['keys']}
    def key(h, base, mix=None, **s):
        e = {'h': h, 'base': base, 'set': dict(s)}
        if mix: e['mix'] = mix
        keys[h] = e
    nc = K['night_cloud']
    # dusk
    key(18.8, 'golden', ['dusk', 0.5], **{'cloud.Cloud_GlobalCoverage': 0.05, 'cloud.Cloud_GlobalDensity': 0.015})
    key(19.5, 'dusk', ['blue', 0.5], **{'cloud.Cloud_GlobalCoverage': 0.05, 'cloud.Cloud_GlobalDensity': 0.015})
    key(20.2, 'blue', ['night', 0.5], **nc)
    key(21.0, 'night', **nc)
    key(21.4, 'night', **nc)
    # dawn
    key(5.6, 'night', ['blue', 0.3], **nc)
    key(6.5, 'blue', ['dusk_am', 0.5], **{'cloud.Cloud_GlobalCoverage': 0.05, 'cloud.Cloud_GlobalDensity': 0.015})
    key(7.2, 'dusk_am', ['golden_am', 0.5], **{'cloud.Cloud_GlobalCoverage': 0.05, 'cloud.Cloud_GlobalDensity': 0.015})
    keys[7.6]['base'] = 'dawn'
    cl = {'cloud.Cloud_GlobalCoverage': 0.05, 'cloud.Cloud_GlobalDensity': 0.015}
    # dawn mist builds up and burns off in log steps (fog density is exponential in its effect)
    key(7.0, 'dusk_am', ['dawn', 0.6], **cl); key(7.4, 'dusk_am', ['dawn', 0.9], **cl)
    key(8.0, 'dawn', ['day', 0.15], **cl); key(8.8, 'dawn', ['day', 0.6], **cl)
    for hh, dens in K['dawn_mist'].items(): keys[float(hh)].setdefault('set', {})['fog.FogDensity'] = dens
    for hh in (4.9, 20.6): keys[hh].setdefault('set', {}).update(nc)
    for h, k in keys.items():
        u = city_u(h, K)
        s = k.setdefault('set', {})
        s['mpc.EmissiveScale'] = round(gold['EmissiveScale'] * (night['EmissiveScale'] / gold['EmissiveScale']) ** u, 4)
        s['mpc.NightK'] = round(u, 4); s['mpc.DnTime'] = round(night['DnTime'] * u, 2)
        for n in ('InteriorGain', 'ShopGain', 'ShadeFill'): s['mpc.' + n] = round(lerp(gold[n], night[n], u), 4)
        for n, tab in (('moon.Intensity', K['moon']), ('hero', K['hero']), ('herofill', K['herofill'])):
            pts = sorted(tab.items())
            if n == 'moon.Intensity': s[n] = round(u_of(h, pts) if pts[0][0] <= h <= pts[-1][0] else (9.0 if (h >= 21.4 or h < 5.0) else 0.0), 3)
            elif n in ('hero', 'herofill'):
                dusk_pts = sorted((a, b) for a, b in tab.items() if a >= 18.0); dawn_pts = sorted((a, b) for a, b in tab.items() if a < 12.0)
                if h >= 18.0: s[n] = round(u_of(h, dusk_pts), 3)
                elif h <= 7.6: s[n] = round(u_of(h, dawn_pts), 3)
                else: s[n] = 0.0 if n == 'hero' else 1.0
        for pk, pv in K['moonc'].items(): s[pk] = pv
        if h in K['cutoff']: s['fog.FogCutoffDistance'] = K['cutoff'][h]
        for pk, pv in K['twilight_overrides'].get(str(h), {}).items(): s[pk] = pv
    T['keys'] = [keys[h] for h in sorted(keys)]
    # twilight shaping: multipliers of the already-expanded base values (look_tod.expand gives them), written back as explicit `set` values
    import sys as _s; _s.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts')); import look_tod
    t0 = look_tod.expand(d)
    base_by_h = {k['h']: k['p'] for k in t0['keys']}
    def w_of(h, tab): return u_of(h, tab['dusk']) if h >= 12 else u_of(h, tab['dawn'])
    for k in T['keys']:
        h = k['h']; b = base_by_h[h]; sset = k.setdefault('set', {})
        w = w_of(h, K['tw_w']) if (h >= 18.0 or h <= 7.6) else 0.0
        ww = w_of(h, K['tw_warm']) if (h >= 18.0 or h <= 7.6) else 0.0
        if w > 0:
            sset['sky.Intensity'] = round(b['sky.Intensity'] * (1 - (1 - K['tw_sky_scale']) * w), 4)
            for dn in 'NESW': sset['fill.' + dn] = round(b['fill.' + dn] * (1 - (1 - K['tw_fill_scale']) * w), 4)
            sset['fog.SkyAtmosphereAmbientContributionColorScale'] = [round(1 - (1 - K['tw_amb']) * w, 4)] * 3 + [1.0]
        if K.get('tw_fac_pts'):
            ph = 'dusk' if h >= 12 else 'dawn'
            v = sched(h, [(a, b) for a, b in K['tw_fac_pts'][ph]]) if (h >= 18.0 or h <= 7.6) else None
            if v is not None: sset['atm.SkyLuminanceFactor'] = [round(x, 4) for x in v] + [1.0]
            elif h >= 18.0 or h <= 7.6: sset['atm.SkyLuminanceFactor'] = [1.0, 1.0, 1.0, 1.0]
        elif ww > 0: sset['atm.SkyLuminanceFactor'] = [round(1 + (f - 1) * ww, 4) for f in K['tw_factor']] + [1.0]
        if K.get('tw_hl_r') and (h >= 18.0 or h <= 7.6):
            m = sched(h, K['tw_hl_r']['dusk' if h >= 12 else 'dawn'])
            if m is not None:
                g = list(b['pp.ColorGainHighlights']); g[0] = round(g[0] * m, 4); sset['pp.ColorGainHighlights'] = g
        if K.get('tw_cloud') and (h >= 18.0 or h <= 7.6):
            c = sched(h, [(a, [cv, dn]) for a, cv, dn in K['tw_cloud']['dusk' if h >= 12 else 'dawn']])
            if c is not None: sset['cloud.Cloud_GlobalCoverage'] = round(c[0], 4); sset['cloud.Cloud_GlobalDensity'] = round(c[1], 5)
        if K.get('night_hl'):
            nh = K['night_hl']; m = None
            if h >= 18.0: m = sched(h, nh['dusk'], nh['night'] if h > nh['dusk'][-1][0] else None)
            elif h <= 7.6: m = sched(h, nh['dawn'], nh['night'] if h < nh['dawn'][0][0] else None)
            if m is not None:
                g = list((sset.get('pp.ColorGainHighlights') or b['pp.ColorGainHighlights'])); sset['pp.ColorGainHighlights'] = [round(x * m, 4) for x in g[:3]] + [1.0]
        if K.get('cloud_offset') is not None: sset['cloudv.Layout_GlobalTexturePlacement'] = list(K['cloud_offset'])
        for pk, pv in K['twilight_overrides'].get(str(h), {}).items(): sset[pk] = pv
        if K.get('cutoff_all') is not None: sset['fog.FogCutoffDistance'] = K['cutoff_all']
        if h in K['night_stars']: sset['stars'] = K['night_stars'][h]
        if h in K.get('golden_hours', []):
            for pk, pv in K['golden_set'].items(): sset[pk] = pv
        if 'hero' in sset and K.get('hero_scale') is not None: sset['hero'] = round(sset['hero'] * K['hero_scale'], 3)
    return d


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--knobs', default=''); ap.add_argument('--out', default=''); ap.add_argument('--in-place', action='store_true')
    ap.add_argument('--bias-overrides', default='', help='json {hour: pp.AutoExposureBias} (lapse_loop.py output) merged into the knob twilight_overrides')
    a = ap.parse_args()
    K = copy.deepcopy(KNOBS)
    if a.knobs: K.update(json.load(open(a.knobs)))
    if a.bias_overrides:
        ov = {k: dict(v) for k, v in (K.get('twilight_overrides') or {}).items()}
        for hh, b in json.load(open(a.bias_overrides)).items(): ov.setdefault(str(float(hh)), {})['pp.AutoExposureBias'] = float(b)
        K['twilight_overrides'] = ov
    doc = base_doc()
    d = apply(doc, K)
    txt = json.dumps(d, indent=1)
    if a.in_place: open(PRESETS, 'w').write(txt)
    elif a.out: open(a.out, 'w').write(txt)
    sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
    import look_tod
    t = look_tod.expand(d)
    print('keys', [k['h'] for k in t['keys']], 'params', len(t['keys'][0]['p']))


if __name__ == '__main__':
    main()
