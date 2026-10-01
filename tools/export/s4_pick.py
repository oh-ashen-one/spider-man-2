#!/usr/bin/env python3
"""(r10) stage-2 / final choice for the S4 sweep (see _scratch/city/r10/hold2.sh). Reads <out>/<TAG>/score.json (one JSON line each) for the tags
  A (FarGain 4, FarSunK .15, fog .0008), B (FarSunK .10), C (FarGain 2.5), A1 (fog .0011), A2 (fog .0014), A3 (brighter fog colour), Z (the combination, stage 2).
usage: s4_pick.py <out> combine   -> prints shell assignments for the combined stage-2 configuration
       s4_pick.py <out> final     -> prints shell assignments of the best tag overall (FG FK FOG FOGC TAG)"""
import sys, os, json
out, mode = sys.argv[1], sys.argv[2]
BASE = dict(FG='4.0', FK='0.15', FOG='0.0008', FOGC='0.76,0.78,0.80')
CFG = {'A': {}, 'B': dict(FK='0.10'), 'C': dict(FG='2.5'), 'A1': dict(FOG='0.0012'), 'A2': dict(FOG='0.0014'), 'A3': dict(FOGC='0.88,0.89,0.91')}
def score(tag):
    p = os.path.join(out, tag, 'score.json')
    if not os.path.exists(p): return None
    try: return json.loads(open(p).read().strip().splitlines()[-1])['score']
    except Exception: return None
S = {t: score(t) for t in list(CFG) + ['Z']}
def sh(d): return ' '.join('%s=%s' % (k, v if ' ' not in str(v) else '"%s"' % v) for k, v in d.items())
if mode == 'combine':
    c = dict(BASE)
    if S['A'] is not None:
        if S['B'] is not None and S['B'] < S['A']: c['FK'] = CFG['B']['FK']
        if S['C'] is not None and S['C'] < S['A']: c['FG'] = CFG['C']['FG']
        fogs = [(S[t], CFG[t]['FOG']) for t in ('A1', 'A2') if S[t] is not None and S[t] < S['A']]
        if fogs: c['FOG'] = min(fogs)[1]
        if S['A3'] is not None and S['A3'] < S['A']: c['FOGC'] = CFG['A3']['FOGC']
    print(sh(c)); print('scores', S, file=sys.stderr)
else:
    cands = [(v, t) for t, v in S.items() if v is not None]
    best = min(cands)[1] if cands else 'A'
    if best == 'Z':
        z = json.load(open(os.path.join(out, 'Z', 'config.json'))); c = dict(BASE, **z)
    else: c = dict(BASE, **CFG[best])
    c['TAG'] = best; print(sh(c)); print('scores', S, file=sys.stderr)
