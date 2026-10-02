#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06, hold 4: keys_v2c.txt (make_v2.py defaults: hold-3 knobs = windows later, twilight factor 30 with the ambient cut to 10 %, dawn mist, moonlit clouds, frozen cloud wind) and plan_d.json
(run_r06.py format, no pins): twilight hours, settled probes around the lapse steps (18.9-19.04, 6.3-6.7), dawn mist hours (S1 + S4 + S4e), golden 18.4 S1..S8, night 22 S1..S8 + S4m, moon variants.
usage: gen_plans_d.py --out <dir>"""
import argparse, copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts')); sys.path.insert(0, HERE)
import look_tod, make_v2   # noqa: E402


def fmt(v): return ' '.join('%.6g' % x for x in (v if isinstance(v, list) else [v]))
def pin(n, v): return 'exec wh.ToDSet %s %s' % (n, fmt(v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--knobs', default=''); ap.add_argument('--final', action='store_true', help='plan without key table overrides (the baked table of the rebuilt rig is measured)')
    a = ap.parse_args()
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    K = copy.deepcopy(make_v2.KNOBS)
    if a.knobs: K.update(json.load(open(a.knobs)))
    doc = make_v2.base_doc(); d2 = make_v2.apply(doc, K); tab = look_tod.expand(d2)
    keys = os.path.join(out, 'keys_v2c.txt'); open(keys, 'w').write(look_tod.to_text(tab)); json.dump(d2, open(os.path.join(out, 'doc_v2c.json'), 'w'), indent=1)

    def G(name, h, shots, cmds=(), **kw):
        g = {'name': name, 'hour': h, 'keys': keys, 'cmds': list(cmds), 'shots': shots}; g.update(kw); return g
    P = []
    allp = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']
    P.append(G('h18.4', 18.4, allp, settle_first=10))
    P.append(G('h22', 22.0, allp + ['S4m'], settle_first=14))
    for h in (6.5, 7.0, 7.5, 19.0, 19.5, 19.8, 20.0, 20.5, 21.0, 21.5):
        P.append(G('h%g' % h, h, ['S4', 'S4e' if h < 12 else 'S4w']))
    for h in (7.0, 7.4, 7.6, 8.0): P.append(G('mist_h%g' % h, h, ['S1', 'S4', 'S4e']))
    for h in (18.9, 18.94, 18.96, 18.98, 19.0, 19.04): P.append(G('step_h%g' % h, h, ['S4'], settle_first=8))
    for h in (6.3, 6.4, 6.5, 6.6, 6.7): P.append(G('dawnstep_h%g' % h, h, ['S4'], settle_first=8))
    for nm, cov, dens, off in (('Mv1', 0.12, 0.02, [0, 0, 0, 0]), ('Mv2', 0.3, 0.03, [0, 0, 0, 0]), ('Mv3', 0.2, 0.025, [30000, 0, 0, 0]), ('Mv4', 0.2, 0.025, [0, 30000, 0, 0])):
        P.append(G('%s_h22' % nm, 22.0, ['S4m'], [pin('cloud.Cloud_GlobalCoverage', cov), pin('cloud.Cloud_GlobalDensity', dens), pin('cloudv.Layout_GlobalTexturePlacement', off)]))
    P.append(G('h13', 13.0, ['S4', 'S8']))
    if a.final:
        for g in P: g.pop('keys', None)
    json.dump({'groups': P}, open(os.path.join(out, 'plan_final.json' if a.final else 'plan_d.json'), 'w'), indent=1)
    print('plan_d', sum(len(x['shots']) for x in P), 'poses', len(P), 'groups ->', out)


if __name__ == '__main__':
    main()
