#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 08: the time-of-day table of round 08 = the round-07 table (make_v3.py with docs/night1/look/round-07/diag/knobs_v10.json + round-07/lapse_bias_overrides.json, unchanged)
+ SURFACE-ONLY light for the twilight city, applied on top of every key as piecewise-linear schedules over the hour (identity outside the listed points):
  'mul': {param: [[h, m], ...]}           multiplier of the round-07 value (number, or [mr, mg, mb] for colours), 1 outside the first / last point
  'set': {param: [[h, v], ...]}           explicit value inside the listed hours (the round-07 value outside)
  'extra_keys': [h, ...]                  keys added before the schedules (their round-07 values are interpolated by the make_v3 builder)
  'bias_add': [[h, dEV], ...]             added to pp.AutoExposureBias (lapse smoothing of the new light)
  'r07_update': {knob: value}             a round-07 make_v3 knob replaced (e.g. surface_geo)
The sky / far-band settings that pass L27 (fog, haze, sky luminance factor, tonemapper, cloud luminance) are NOT in the r08 schedules except where a knob file names them.
usage: make_v4.py --knobs knobs_r08.json (--out <doc.json> | --in-place) [--r07-knobs ...] [--r07-bias ...]"""
import argparse, copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts')); sys.path.insert(0, os.path.join(HERE, '..', 'r07')); sys.path.insert(0, os.path.join(HERE, '..', 'r06'))
import look_tod, make_v2, make_v3   # noqa: E402

R7 = os.path.join(WT, 'docs', 'night1', 'look', 'round-07')
PRESETS = os.path.join(WT, 'unreal', 'WebHomage', 'Scripts', 'look_presets.json')


def sched(h, pts):
    """piecewise linear; outside the points: the end value is NOT extended (None)"""
    return make_v2.sched(h, [tuple(p) for p in pts])


def r07_doc(knobs, bias, extra, r07_update=None):
    K = copy.deepcopy(make_v2.KNOBS); K.update(json.load(open(make_v3.KNOBS_D)))
    R = copy.deepcopy(make_v3.R07); R.update(json.load(open(knobs)))
    if r07_update: R.update(copy.deepcopy(r07_update))   # e.g. {"surface_geo": {...}}: a round-07 knob replaced (listed in the round-08 knob file)
    if extra:
        v2 = R.setdefault('v2', {}); v2['extra_keys'] = sorted(set(float(x) for x in (v2.get('extra_keys') or [])) | set(float(x) for x in extra))
    v2 = R.setdefault('v2', {}); ov = {k: dict(v) for k, v in (v2.get('twilight_overrides') or K.get('twilight_overrides') or {}).items()}
    for hh, bb in json.load(open(bias)).items(): ov.setdefault(str(float(hh)), {})['pp.AutoExposureBias'] = float(bb); make_v3.BIAS_OV.add(str(float(hh)))
    v2['twilight_overrides'] = ov
    d, _ = make_v3.apply(K, R)
    return d


def apply(d, S):
    d = copy.deepcopy(d)
    t = look_tod.expand(d)
    exp = {k['h']: k['p'] for k in t['keys']}
    for k in d['tod']['keys']:
        h = float(k['h']); s = k.setdefault('set', {}); b = exp[h]
        for pn, pts in (S.get('mul') or {}).items():
            m = sched(h, pts)
            if m is None: continue
            bv = b[pn]
            if isinstance(bv, list):
                mv = m if isinstance(m, list) else [m] * 3
                s[pn] = [round(bv[i] * mv[i], 6) for i in range(3)] + [bv[3] if len(bv) > 3 else 1.0]
            else: s[pn] = round(bv * (m[0] if isinstance(m, list) else m), 6)
        for pn, pts in (S.get('set') or {}).items():
            v = sched(h, pts)
            if v is None: continue
            s[pn] = [round(x, 6) for x in v] if isinstance(v, list) else round(v, 6)
        ba = sched(h, S['bias_add']) if S.get('bias_add') else None
        if ba: s['pp.AutoExposureBias'] = round(float(s.get('pp.AutoExposureBias', b['pp.AutoExposureBias'])) + ba, 4)
    return d


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--knobs', required=True); ap.add_argument('--out', default=''); ap.add_argument('--in-place', action='store_true')
    ap.add_argument('--r07-knobs', default=os.path.join(R7, 'diag', 'knobs_v10.json')); ap.add_argument('--r07-bias', default=os.path.join(R7, 'lapse_bias_overrides.json'))
    a = ap.parse_args()
    S = json.load(open(a.knobs))
    d = apply(r07_doc(a.r07_knobs, a.r07_bias, S.get('extra_keys'), S.get('r07_update')), S)
    txt = json.dumps(d, indent=1)
    if a.in_place: open(PRESETS, 'w').write(txt)
    elif a.out: open(a.out, 'w').write(txt)
    t = look_tod.expand(d)
    print('keys', len(t['keys']), 'params', len(t['keys'][0]['p']))


if __name__ == '__main__':
    main()
