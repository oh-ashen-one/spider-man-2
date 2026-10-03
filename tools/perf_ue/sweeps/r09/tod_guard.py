#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 09: the time-of-day table derives most of its keys from presets.golden (base 'golden' and the derived bases golden_am / dusk / dusk_am / dawn).
The round-09 golden change is for the FIXED golden preset only, so this adds tod.derived.golden_r08 = golden with the round-08 values of the changed params
(presets.golden._r09_previous, translated to ToD param names) and points every 'golden' reference of the tod section to it.
Check: --check compares look_tod.expand() of the committed round-08 document (git show <rev>:...) with the current one (must be equal, up to the new
atm.SkyAndAerialPerspectiveLuminanceFactor param = engine default 1 on every key).
usage: tod_guard.py apply | tod_guard.py --check <git rev of the round-08 presets>"""
import json, os, sys, subprocess, collections
WT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
P = os.path.join(WT, 'unreal/WebHomage/Scripts/look_presets.json')
sys.path.insert(0, os.path.join(WT, 'unreal/WebHomage/Scripts'))
import look_tod
TOD_NAME = {'ap': 'atm.AerialPespectiveViewDistanceScale', 'hfc': 'atm.HeightFogContribution', 'skylum': 'atm.SkyLuminanceFactor',
            'saplum': 'atm.SkyAndAerialPerspectiveLuminanceFactor', 'slint': 'sky.Intensity', 'vfext': 'fog.VolumetricFogExtinctionScale'}
if __name__ == '__main__':
    if sys.argv[1] == 'apply':
        D = json.loads(open(P).read(), object_pairs_hook=collections.OrderedDict); T = D['tod']; prev = D['presets']['golden']['_r09_previous']
        st = {}
        for k, v in prev.items():
            if v is None: v = [1.0, 1.0, 1.0, 1.0]   # param not set in round 08 = engine default
            st[TOD_NAME[k]] = v
        der = collections.OrderedDict([('golden_r08', {'from': 'golden', 'set': st, '_r09': 'round-08 golden for the time of day (the round-09 golden change is for the fixed golden preset only)'})])
        for n, d in T['derived'].items():
            if d.get('from') == 'golden': d['from'] = 'golden_r08'
            if d.get('mix') and d['mix'][0] == 'golden': d['mix'][0] = 'golden_r08'
            der[n] = d
        T['derived'] = der
        n = 0
        for k in T['keys']:
            if k['base'] == 'golden': k['base'] = 'golden_r08'; n += 1
            if k.get('mix') and k['mix'][0] == 'golden': k['mix'][0] = 'golden_r08'; n += 1
        if T['overcast']['base'] == 'golden': T['overcast']['base'] = 'golden_r08'
        open(P, 'w').write(json.dumps(D, indent=1)); print('golden_r08 set', st, 'keys repointed', n)
    else:
        rev = sys.argv[2]
        old = json.loads(subprocess.run(['git', '-C', WT, 'show', rev + ':unreal/WebHomage/Scripts/look_presets.json'], capture_output=True, text=True).stdout)
        a = look_tod.expand(old); b = look_tod.expand(json.load(open(P)))
        bad = 0
        for ka, kb in zip(a['keys'], b['keys']):
            pa, pb = dict(ka['p']), dict(kb['p'])
            extra = pb.pop('atm.SkyAndAerialPerspectiveLuminanceFactor', None); pa.pop('atm.SkyAndAerialPerspectiveLuminanceFactor', None)   # (the current look_tod adds it to the old document too)
            if extra != [1.0, 1.0, 1.0, 1.0] or ka['h'] != kb['h'] or pa != pb: bad += 1; print('DIFF at', ka['h'], sorted(k for k in set(pa) | set(pb) if pa.get(k) != pb.get(k))[:8])
        oa, ob = dict(a['overcast']), dict(b['overcast']); ob.pop('atm.SkyAndAerialPerspectiveLuminanceFactor', None); oa.pop('atm.SkyAndAerialPerspectiveLuminanceFactor', None)
        print('keys', len(a['keys']), len(b['keys']), 'differing', bad, 'overcast equal', oa == ob, 'sun/moon equal', a['sun'] == b['sun'] and a['moon'] == b['moon'])
        sys.exit(1 if bad or oa != ob else 0)
