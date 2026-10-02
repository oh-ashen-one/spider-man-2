#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06, hold 6 (A) -> hold 7 (B): writes $SM2_LOOK_SCRATCH/r06/final6/knobs_final.json = the winners of the hold-6A variant sweep (gen_plans_e.py) as make_v2.py knobs, plus the sun ramp:
  W5   twilight: W4's R-highlight compression and denser twilight clouds (coverage .25, density .03) up to 19:30 and from 06:15 to 07:24, W4's factor schedule up to 19:30 and the hold-4 late factor (30 / 6 / 1.2 from 19:48:
       the S4w B-R at 20:00 depends on it; the denser clouds at 20:00 turned the sun-facing sky band neutral, so the clouds thin out again by 19:48)
  N2   night: cloud pattern offset (hold-2 Mv4); NO highlight roll-off (measured: it does not remove clipped pixels, it only lowers the means and the sky high-pass)
  D1   dawn mist density 4 at 07:36 (L26)
  G    golden black lift (see --golden)
  R    sun surface-light ramp -4 .. 8 deg (C++ sun.RampLo / sun.RampHi): the sunlit city loses / gains its direct light over 65 game minutes instead of 32
usage: make_final_knobs.py --out <json> [--golden 0.0012] [--ramp -4,8]"""
import argparse, copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_plans_e as E   # noqa: E402
import make_v2            # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--golden', type=float, default=0.0); ap.add_argument('--ramp', default='-4,8')
    ap.add_argument('--late-factor', default='30,6,1.2'); a = ap.parse_args()
    lf = [float(x) for x in a.late_factor.split(',')]
    fac = copy.deepcopy(E.FAC_W3)
    fac['dusk'] = [(h, v) for h, v in fac['dusk'] if h <= 19.5] + [(19.8, [26, 5.5, 1.2]), (20.2, lf), (20.6, lf), (21.0, [15.5, 3.5, 1.1]), (21.4, [3.9, 1.5, 1.02])]
    cloud = {'dusk': [(18.8, 0.25, 0.03), (19.5, 0.25, 0.03), (19.8, 0.1, 0.02)], 'dawn': [(6.25, 0.25, 0.03), (7.4, 0.25, 0.03)]}
    K = {'tw_fac_pts': fac, 'tw_hl_r': E.HL_R, 'tw_cloud': cloud, 'cloud_offset': [0.0, 30000.0, 0.0, 0.0],
         'dawn_mist': {7.0: 0.02, 7.2: 0.1, 7.4: 0.8, 7.6: 4.0, 8.0: 1.6, 8.8: 0.05}, 'sun_ramp': [float(x) for x in a.ramp.split(',')]}
    if a.golden > 0: K['golden_set'] = dict(make_v2.KNOBS['golden_set'], **{'pp.ColorOffset': [a.golden, a.golden, a.golden, 0.0]})
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(K, open(a.out, 'w'), indent=1)
    d = make_v2.apply(make_v2.base_doc(), {**make_v2.KNOBS, **K})   # smoke test: the knobs expand
    sys.path.insert(0, os.path.join(make_v2.WT, 'unreal', 'WebHomage', 'Scripts')); import look_tod
    t = look_tod.expand(d); print('knobs ->', a.out, '| keys', len(t['keys']), 'params', len(t['keys'][0]['p']))


if __name__ == '__main__':
    main()
