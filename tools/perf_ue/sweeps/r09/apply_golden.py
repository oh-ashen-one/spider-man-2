#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 09: writes one gen_s4.py knob set into presets.golden of unreal/WebHomage/Scripts/look_presets.json (sky / atmosphere / fog keys only; the 'tod' table and
the other presets are untouched). The previous golden values are kept in presets.golden._r09_previous.
usage: apply_golden.py '<json knobs, gen_s4.py names>' [--note text]"""
import json, os, sys, collections
WT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
P = os.path.join(WT, 'unreal/WebHomage/Scripts/look_presets.json')
MAP = {'ray': ('atmosphere', 'rayleigh_scattering_scale'), 'mie': ('atmosphere', 'mie_scattering_scale'), 'mie_abs': ('atmosphere', 'mie_absorption_scale'),
       'aniso': ('atmosphere', 'mie_anisotropy'), 'ap': ('atmosphere', 'aerial_perspective_distance_scale'), 'ap_start': ('atmosphere', 'aerial_perspective_start_depth'),
       'hfc': ('atmosphere', 'height_fog_contribution'), 'skylum': ('atmosphere', 'sky_luminance_factor'), 'miecol': ('atmosphere', 'mie_scattering'),
       'saplum': ('atmosphere', 'sky_and_aerial_perspective_luminance_factor'),
       'dens': ('fog', 'fog_density'), 'fall': ('fog', 'fog_height_falloff'), 'start': ('fog', 'start_distance'), 'maxop': ('fog', 'fog_max_opacity'),
       'fogcol': ('fog', 'fog_inscattering_luminance'), 'dircol': ('fog', 'directional_inscattering_luminance'), 'direxp': ('fog', 'directional_inscattering_exponent'),
       'dirstart': ('fog', 'directional_inscattering_start_distance'), 'cutoff': ('fog', 'fog_cutoff_distance'), 'slint': ('sky', 'intensity'), 'vfext': ('fog', 'volumetric_fog_extinction_scale'), 'vfalb': ('fog', 'volumetric_fog_albedo'), 'vfdist': ('fog', 'volumetric_fog_distance')}
if __name__ == '__main__':
    k = json.loads(sys.argv[1]); note = sys.argv[sys.argv.index('--note') + 1] if '--note' in sys.argv else ''
    raw = open(P).read(); D = json.loads(raw, object_pairs_hook=collections.OrderedDict); g = D['presets']['golden']
    prev = {}
    for name, v in k.items():
        sec, key = MAP[name]
        prev[name] = g[sec].get(key)
        g[sec][key] = (list(v) + [1.0]) if isinstance(v, list) and len(v) == 3 else v
    g['_r09'] = 'round 09 (S4 far band / sky, director brief after city r11): ' + note
    g['_r09_previous'] = prev
    open(P, 'w').write(json.dumps(D, indent=1))
    print('golden <-', k); print('previous', prev)
