# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 Look (round 05): continuous time of day. Pure python (no unreal import): expands the "tod" section of Scripts/look_presets.json into
# the flat key table that the C++ driver AWHLookTimeOfDay (Source/WebHomage/Look/WHLookTimeOfDay.*) interpolates at run time.
#   used by Scripts/build_look.py (step rigs, preset 'tod': the JSON text is baked into the driver actor) and by tools/perf_ue (sweeps:
#   `python3 Scripts/look_tod.py --out <file.txt> [--set h=18.4:sky.Intensity=3 ...]` writes a key file the running game loads with `wh.ToDLoad <file>`).
#
# Table format (also what the driver parses):
#   {"sun": {lat, dec, grid_offset, clock_shift}, "moon": {dec, shift}, "default_hour": h,
#    "keys": [{"h": hour, "p": {param: number | [r, g, b(, a)]}}, ...]  (every key has every param, sorted by h, cyclic over 24 h),
#    "overcast": {param: value}   (wh.Weather blend target, applied with weight weather * daylight)}
# Param names: <target>.<UPROPERTY name> set by reflection on the rig actor's component, or a special name:
#   sun.* / moon.* (DirectionalLight: Intensity lux, Temperature K, LightSourceAngle deg, DiskScale), fill.N|E|S|W (lux) + fillT.N|E|S|W (K): unshadowed horizon fills,
#   sky.Intensity / sky.LightColor (SkyLight), atm.* (SkyAtmosphereComponent), fog.* (ExponentialHeightFogComponent), fog2.* (its SecondFogData),
#   cloudc.* (VolumetricCloudComponent), cloud.<scalar> / cloudv.<vector> (cloud material instance parameters), pp.* (FPostProcessSettings of the unbound volume),
#   mpc.* (MPC_City scalars), lights (night street lights level: intensity scale, hidden below 0.02), stars (star dome gain), weather (0 clear .. 1 overcast)
import json, math, os, copy

HERE = os.path.dirname(os.path.abspath(__file__))

ATM_DEFAULTS = {'atm.RayleighScattering': [0.175287, 0.409607, 1.0, 1.0], 'atm.MieScattering': [1.0, 1.0, 1.0, 1.0], 'atm.SkyLuminanceFactor': [1.0, 1.0, 1.0, 1.0],
                'atm.RayleighScatteringScale': 0.0331, 'atm.MieScatteringScale': 0.003996, 'atm.MieAbsorptionScale': 0.000444, 'atm.MieAnisotropy': 0.8,
                'atm.AerialPespectiveViewDistanceScale': 1.0, 'atm.AerialPerspectiveStartDepth': 0.1, 'atm.HeightFogContribution': 1.0}
FOG_DEFAULTS = {'fog.SkyAtmosphereAmbientContributionColorScale': [1.0, 1.0, 1.0, 1.0]}
PP_DEFAULTS = {'pp.ColorGainShadows': [1.0, 1.0, 1.0, 1.0], 'pp.ColorGainHighlights': [1.0, 1.0, 1.0, 1.0], 'pp.ColorOffset': [0.0, 0.0, 0.0, 0.0],
               'pp.ColorSaturation': [1.0, 1.0, 1.0, 1.0], 'pp.ColorContrast': [1.0, 1.0, 1.0, 1.0], 'pp.LensFlareIntensity': 0.0, 'pp.LumenDiffuseColorBoost': 1.0,
               'pp.AutoExposureLowPercent': 70.0, 'pp.AutoExposureHighPercent': 98.0, 'pp.FilmWhiteClip': 0.04, 'pp.FilmBlackClip': 0.0}
CLOUD_DEFAULTS = {'cloud.Cloud_GlobalCoverage': -0.2, 'cloud.Cloud_GlobalDensity': 0.008, 'cloudv.Cloud_AlbedoColor': [0.98, 0.98, 0.98, 1.0]}
SKIP_POST = {'motion_blur_target_fps', 'lumen_scene_lighting_quality', 'lumen_final_gather_quality', 'lumen_reflection_quality', 'motion_blur_amount', 'motion_blur_max',
             'ambient_occlusion_radius'}   # constant across presets: set once on the volume by build_look.py
FILL_DIRS = {'N': 0.0, 'E': 90.0, 'S': 180.0, 'W': 270.0}
FILL_NAME = {'north': 'N', 'east': 'E', 'south': 'S', 'west': 'W'}


def camel(s):
    out = ''.join(w[:1].upper() + w[1:] for w in s.split('_'))
    return {'AerialPerspectiveDistanceScale': 'AerialPespectiveViewDistanceScale'}.get(out, out)


def vec(v):
    return [float(x) for x in v] + ([1.0] if len(v) == 3 else []) if isinstance(v, list) else float(v)


def preset_params(P):
    """one look_presets.json preset -> flat ToD params"""
    o = {}
    s = P['sun']
    o.update({'sun.Intensity': s['lux'], 'sun.Temperature': s['temp'], 'sun.LightSourceAngle': s['angle'], 'sun.DiskScale': s.get('disk', 1.0)})
    m = P.get('moon') or {}
    o.update({'moon.Intensity': m.get('lux', 0.0), 'moon.Temperature': m.get('temp', 5600.0)})
    for d in FILL_DIRS: o['fill.' + d] = 0.0; o['fillT.' + d] = 6500.0
    for f in P.get('fills', []):
        d = FILL_NAME[f['name'].lower()]; o['fill.' + d] = f['lux']; o['fillT.' + d] = f['temp']
    o['sky.Intensity'] = P['sky']['intensity']; o['sky.LightColor'] = P['sky']['tint'] + [1.0]
    o.update(ATM_DEFAULTS)
    for k, v in P['atmosphere'].items():
        if k == 'ground_albedo': continue
        o['atm.' + camel(k)] = v
    o.update(FOG_DEFAULTS)
    for k, v in P['fog'].items():
        if k == 'volumetric_fog': continue
        if k == 'haze':
            for hk, hv in v.items(): o['fog2.' + camel(hk)] = hv
        else: o['fog.' + camel(k)] = v
    c = P['clouds']
    o.update(CLOUD_DEFAULTS)
    o['cloudc.LayerBottomAltitude'] = c['layer_bottom_altitude']; o['cloudc.LayerHeight'] = c['layer_height']
    for k, v in (c.get('mi') or {}).get('scalars', {}).items(): o['cloud.' + k] = v
    for k, v in (c.get('mi') or {}).get('vectors', {}).items(): o['cloudv.' + k] = v
    for k, v in P['mpc'].items(): o['mpc.' + k] = v
    e = P['exposure']
    o.update(PP_DEFAULTS)
    o.update({'pp.AutoExposureMinBrightness': e['min_ev'], 'pp.AutoExposureMaxBrightness': e['max_ev'], 'pp.AutoExposureBias': e['bias']})
    for k, v in P['post'].items():
        if k in SKIP_POST: continue
        o['pp.' + camel(k)] = v
    o['lights'] = 1.0 if P['mpc'].get('NightK', 0.0) > 0.5 else 0.0
    o['stars'] = 1.0 if P['mpc'].get('NightK', 0.0) > 0.5 else 0.0
    o['weather'] = 0.0
    # (round 06) hero rim / fill light scale (1 = the AWHLookHeroLight intensities) and the moon's own light properties (disk size, disk colour scale, cloud luminance scale): driver targets moonc.*
    o['sun.RampLo'] = -2.5; o['sun.RampHi'] = 3.5   # (round 06) sun surface-light ramp limits in degrees of sun elevation (C++ AWHLookTimeOfDay::Apply: diffuse / specular scale = smoothstep(lo, hi, elevation))
    o['cloudv.Layout_GlobalTexturePlacement'] = [0.0, 0.0, 0.0, 0.0]   # (round 06) cloud pattern placement (the moonlit cloud pattern of the night keys is chosen with it)
    o['cloudv.CloudWind'] = [0.0, 0.0, 0.0, 0.0]   # (round 06) the engine cloud material drifts with Time x CloudWind: the cloud field was a function of the session time (the moon was behind a cloud in some captures); frozen
    o['hero'] = 1.0
    o['herofill'] = 1.0   # scale of the traversal character's own hero fill light (P3 'HeroFill', 5000 cd) applied by AWHLookHeroLight
    o['moonc.LightSourceAngle'] = float(m.get('angle', 0.5357))
    o['moonc.AtmosphereSunDiskColorScale'] = [1.0, 1.0, 1.0, 1.0]
    o['moonc.CloudScatteredLuminanceScale'] = [1.0, 1.0, 1.0, 1.0]
    return {k: vec(v) for k, v in o.items()}


def mix(a, b, t):
    out = {}
    for k in a:
        x, y = a[k], b.get(k, a[k])
        out[k] = [p + (q - p) * t for p, q in zip(x, y)] if isinstance(x, list) else x + (y - x) * t
    return out


def expand(doc, extra_sets=None):
    """look_presets.json document -> driver table (see header)"""
    T = doc['tod']
    PRE = {n: preset_params(p) for n, p in doc['presets'].items()}
    for n, d in T.get('derived', {}).items():   # synthetic bases: {"from": preset, "mix": [preset, t], "set": {...}}
        b = copy.deepcopy(PRE[d['from']])
        if d.get('mix'): b = mix(b, PRE[d['mix'][0]], d['mix'][1])
        for k, v in d.get('set', {}).items(): b[k] = vec(v)
        PRE[n] = b
    keys = []
    for k in T['keys']:
        b = copy.deepcopy(PRE[k['base']])
        if k.get('mix'): b = mix(b, PRE[k['mix'][0]], k['mix'][1])
        for pk, pv in k.get('set', {}).items():
            if pk not in b: raise KeyError('key %s: unknown param %s' % (k['h'], pk))
            b[pk] = vec(pv)
        keys.append({'h': float(k['h']), 'p': b})
    for s in (extra_sets or []):   # 'h=18.4:sky.Intensity=3' (sweep overrides, h=* for every key)
        hs, rest = s.split(':', 1); h = hs.split('=')[1]; pk, pv = rest.split('=', 1)
        v = vec(json.loads(pv))
        for k in keys:
            if h == '*' or abs(k['h'] - float(h)) < 1e-3:
                if pk not in k['p']: raise KeyError(pk)
                k['p'][pk] = v
    keys.sort(key=lambda k: k['h'])
    names = set(keys[0]['p'])
    for k in keys:
        if set(k['p']) != names: raise ValueError('key %s params differ: %s' % (k['h'], sorted(set(k['p']) ^ names)))
    oc = copy.deepcopy(PRE[T['overcast']['base']])
    for pk, pv in T['overcast'].get('set', {}).items(): oc[pk] = vec(pv)
    oc = {k: v for k, v in oc.items() if not k.startswith(('mpc.', 'moon.', 'moonc.', 'fill', 'lights', 'stars', 'weather', 'sun.Temperature', 'hero'))}
    return {'sun': T['sun'], 'moon': T['moon'], 'default_hour': T['default_hour'], 'keys': keys, 'overcast': oc}


def evaluate(t, hour, weather=0.0):
    """Python twin of AWHLookTimeOfDay::Evaluate (cyclic Catmull-Rom clamped to the neighbouring keys; FogCutoffDistance steps at the middle of its segment) for a table
    returned by expand(): {param: number | [r, g, b, a]} at `hour` (used by the sweep generators to compute baseline values and by tests; weather blend not applied)."""
    keys = t['keys']; n = len(keys)
    i = n - 1
    for k in range(n):
        if keys[k]['h'] <= hour: i = k
    def kh(k):
        m = k % n; return keys[m]['h'] + 24.0 * ((k - m) // n)
    def kp(k): return keys[k % n]['p']
    h0, h1, h2, h3 = kh(i - 1), kh(i), kh(i + 1), kh(i + 2)
    hx = hour + 24.0 if hour < h1 else hour
    if h2 <= h1: h2 += 24.0; h3 += 24.0
    seg = max(1e-3, h2 - h1); tt = min(1.0, max(0.0, (hx - h1) / seg)); t2, t3 = tt * tt, tt * tt * tt
    b0, b1, b2, b3 = 2 * t3 - 3 * t2 + 1, t3 - 2 * t2 + tt, -2 * t3 + 3 * t2, t3 - t2
    P0, P1, P2, P3 = kp(i - 1), kp(i), kp(i + 1), kp(i + 2)
    out = {}
    for name, v1 in P1.items():
        is_vec = isinstance(v1, list)
        a1 = v1 if is_vec else [v1]
        a2 = P2.get(name, v1) if is_vec else [P2.get(name, v1)]
        a0 = P0.get(name, v1) if is_vec else [P0.get(name, v1)]
        a3 = P3.get(name, P2.get(name, v1)) if is_vec else [P3.get(name, P2.get(name, v1))]
        if not is_vec: a2 = [a2[0]]; a0 = [a0[0]]; a3 = [a3[0]]
        r = []
        for c in range(len(a1)):
            m1 = (a2[c] - a0[c]) / max(1e-3, h2 - h0) * seg; m2 = (a3[c] - a1[c]) / max(1e-3, h3 - h1) * seg
            v = b0 * a1[c] + b1 * m1 + b2 * a2[c] + b3 * m2
            r.append(min(max(v, min(a1[c], a2[c])), max(a1[c], a2[c])))
        if name == 'fog.FogCutoffDistance': r = [a1[0] if tt < 0.5 else a2[0]]
        out[name] = r if is_vec else r[0]
    return out


def body_dir(model, hour, lat):
    """(elevation deg, grid azimuth deg) of a body on a fixed declination circle; same maths as WHLookTimeOfDay.cpp BodyDir"""
    H = math.radians(15.0 * (hour - 12.0 - model.get('clock_shift', model.get('shift', 0.0))))
    la, d = math.radians(lat), math.radians(model['dec'])
    e = math.asin(math.sin(la) * math.sin(d) + math.cos(la) * math.cos(d) * math.cos(H))
    az = math.atan2(math.sin(H), math.cos(H) * math.sin(la) - math.tan(d) * math.cos(la))
    return math.degrees(e), (math.degrees(az) + 180.0 - model.get('grid_offset', 29.0)) % 360.0


def to_text(t):
    """the driver's line format (AWHLookTimeOfDay::LoadKeys; no JSON dependency in the C++ module):
       sun <lat> <dec> <grid_offset> <clock_shift> | moon <dec> <shift> | default <hour> | key <hour> | p <param> <v...> (under the last key) | oc <param> <v...>"""
    def vals(v): return ' '.join('%.7g' % x for x in (v if isinstance(v, list) else [v]))
    L = ['# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. P4 time-of-day key table (Scripts/look_tod.py).',
         'sun %g %g %g %g' % (t['sun']['lat'], t['sun']['dec'], t['sun']['grid_offset'], t['sun']['clock_shift']),
         'moon %g %g' % (t['moon']['dec'], t['moon']['shift']), 'default %g' % t['default_hour']]
    for k in t['keys']:
        L.append('key %g' % k['h'])
        L += ['p %s %s' % (n, vals(v)) for n, v in sorted(k['p'].items())]
    L += ['oc %s %s' % (n, vals(v)) for n, v in sorted(t['overcast'].items())]
    return '\n'.join(L) + '\n'


def load_doc():
    return json.load(open(os.path.join(HERE, 'look_presets.json')))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--set', nargs='*', default=[])
    ap.add_argument('--table', action='store_true', help='print sun / moon positions per hour')
    a = ap.parse_args()
    t = expand(load_doc(), a.set)
    open(a.out, 'w').write(to_text(t) if not a.out.endswith('.json') else json.dumps(t, separators=(',', ':')))
    print('keys', [k['h'] for k in t['keys']], 'params', len(t['keys'][0]['p']), '->', a.out)
    if a.table:
        lat = t['sun']['lat']
        for h in [x * 0.5 for x in range(48)]:
            print('%5.1f sun %6.1f %6.1f   moon %6.1f %6.1f' % ((h,) + body_dir(t['sun'], h, lat) + body_dir(dict(t['moon'], grid_offset=t['sun']['grid_offset']), h, lat)))
