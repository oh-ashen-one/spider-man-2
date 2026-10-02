#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06, hold 6 (A): key tables for the twilight palette / night / golden / dawn-mist variants and the sweep plan (run_r06.py format).
Every variant is the committed table (make_v2.py default knobs = the hold-4 table) + a few knobs of make_v2.py:
  W1  low amber twilight factor (sun-facing sky B-R <= -20 with a milder red) + R-highlight compression, late (20:00-20:36) factor 30 as before
  W3  mid factor (about 60 % of the hold-4 values at 19:12-19:48 and 06:15-07:12) + R-highlight compression
  W4  W3 + a doubled late factor (20:12-20:36 x60, so the S4 sky band at 20:00 rises over the far band) + twilight clouds (coverage .25, density .03)
  N1  night: moonlit cloud pattern (Layout_GlobalTexturePlacement [0, 30000, 0, 0], hold-2 Mv4) + highlight roll-off .8 on the night keys (L15b) + dawn mist 4.0 at 07:36 (L26)
  G1 / G2  golden black lift (pp.ColorOffset .0012 / .0022 on the golden keys 07:36 and 18:24; Y<10 <= 8 % with p5 <= 12)
usage: gen_plans_e.py --out <dir>   -> <dir>/keys_<variant>.txt, <dir>/doc_<variant>.json, <dir>/plan_e.json"""
import argparse, copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts')); sys.path.insert(0, HERE)
import look_tod, make_v2   # noqa: E402

HL_R = {'dusk': [(18.8, 1.0), (19.2, 0.85), (19.5, 0.8), (19.8, 0.85), (20.2, 1.0)], 'dawn': [(6.0, 1.0), (6.25, 0.85), (6.5, 0.8), (7.0, 0.85), (7.4, 1.0)]}
FAC_W1 = {'dusk': [(18.8, [1, 1, 1]), (19.2, [2.5, 1.4, 1.0]), (19.5, [4, 1.7, 1.0]), (19.8, [6, 2.2, 1.05]), (20.2, [24, 5, 1.2]), (20.6, [30, 6, 1.2]), (21.0, [12, 3, 1.1]), (21.4, [3, 1.4, 1.02])],
          'dawn': [(5.6, [1, 1, 1]), (6.25, [6, 2.2, 1.1]), (6.5, [6, 2.2, 1.1]), (6.8, [5, 2, 1.08]), (7.0, [4, 1.8, 1.06]), (7.2, [3, 1.5, 1.04]), (7.4, [2, 1.25, 1.02]), (7.6, [1, 1, 1])]}
FAC_W3 = {'dusk': [(18.8, [1, 1, 1]), (19.2, [5, 2, 1.04]), (19.5, [9, 3, 1.1]), (19.8, [14, 4, 1.15]), (20.2, [30, 6, 1.2]), (20.6, [30, 6, 1.2]), (21.0, [15.5, 3.5, 1.1]), (21.4, [3.9, 1.5, 1.02])],
          'dawn': [(5.6, [1, 1, 1]), (6.25, [12, 3.5, 1.1]), (6.5, [11, 3.2, 1.1]), (6.8, [9.5, 3, 1.1]), (7.0, [8, 2.7, 1.08]), (7.2, [5.5, 2.1, 1.05]), (7.4, [3, 1.5, 1.03]), (7.6, [1, 1, 1])]}
FAC_W4 = copy.deepcopy(FAC_W3)
FAC_W4['dusk'] = [(h, v) for h, v in FAC_W4['dusk'] if h < 20.2] + [(20.2, [60, 12, 2.4]), (20.6, [60, 12, 2.4]), (21.0, [24, 5, 1.3]), (21.4, [3.9, 1.5, 1.02])]
CLOUD_W4 = {'dusk': [(18.8, 0.25, 0.03), (20.2, 0.25, 0.03)], 'dawn': [(6.25, 0.25, 0.03), (7.4, 0.25, 0.03)]}
NIGHT_HL = {'dusk': [(20.2, 1.0), (21.0, 0.8)], 'dawn': [(5.6, 0.8), (6.25, 1.0)], 'night': 0.8}
GOLD = dict(make_v2.KNOBS['golden_set'])

VARIANTS = {
    'W1': {'tw_fac_pts': FAC_W1, 'tw_hl_r': HL_R},
    'W3': {'tw_fac_pts': FAC_W3, 'tw_hl_r': HL_R},
    'W4': {'tw_fac_pts': FAC_W4, 'tw_hl_r': HL_R, 'tw_cloud': CLOUD_W4},
    'N1': {'cloud_offset': [0.0, 30000.0, 0.0, 0.0], 'night_hl': NIGHT_HL, 'dawn_mist': {7.0: 0.02, 7.2: 0.1, 7.4: 0.8, 7.6: 4.0, 8.0: 1.6, 8.8: 0.05}},
    'G1': {'golden_set': dict(GOLD, **{'pp.ColorOffset': [0.0012, 0.0012, 0.0012, 0.0]})},
    'G2': {'golden_set': dict(GOLD, **{'pp.ColorOffset': [0.0022, 0.0022, 0.0022, 0.0]})},
}


def build(name, out):
    K = copy.deepcopy(make_v2.KNOBS); K.update(copy.deepcopy(VARIANTS.get(name, {})))
    d = make_v2.apply(make_v2.base_doc(), K); t = look_tod.expand(d)
    kf = os.path.join(out, 'keys_%s.txt' % name); open(kf, 'w').write(look_tod.to_text(t)); json.dump(d, open(os.path.join(out, 'doc_%s.json' % name), 'w'), indent=1)
    return kf, t


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    keys = {n: build(n, out)[0] for n in VARIANTS}
    P = []

    def G(name, h, shots, kf, **kw):
        g = {'name': name, 'hour': h, 'keys': kf, 'cmds': [], 'shots': shots}; g.update(kw); return g
    for w in ('W1', 'W3', 'W4'):
        for h in (6.5, 7.0, 7.5): P.append(G('%s_h%g' % (w, h), h, ['S4', 'S4e'], keys[w]))
        for h in (19.0, 19.5, 20.0, 20.5): P.append(G('%s_h%g' % (w, h), h, ['S4', 'S4w'], keys[w]))
        P.append(G('%s_h21' % w, 21.0, ['S4'], keys[w]))
    P.append(G('N1_h22', 22.0, ['S4m', 'S4', 'S1', 'S6', 'S5', 'S7'], keys['N1'], settle_first=12))
    P.append(G('N1_mist_h7.6', 7.6, ['S1', 'S4'], keys['N1']))
    for g in ('G1', 'G2'): P.append(G('%s_h18.4' % g, 18.4, ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'], keys[g], settle_first=10))
    json.dump({'groups': P}, open(os.path.join(out, 'plan_e.json'), 'w'), indent=1)
    print('plan_e', sum(len(x['shots']) for x in P), 'poses', len(P), 'groups ->', out)
    # review numbers: the factor schedule at the key hours of every variant
    for n in ('W1', 'W3', 'W4'):
        _, t = build(n, out)
        print(n, ' '.join('%g:%s' % (k['h'], '/'.join('%.3g' % x for x in k['p']['atm.SkyLuminanceFactor'][:3])) for k in t['keys'] if k['h'] >= 18.8 or k['h'] <= 7.6))


if __name__ == '__main__':
    main()
