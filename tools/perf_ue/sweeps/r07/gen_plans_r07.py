#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07: stills plans (run_r06.py format) for the BAKED Look_Midtown_tod (no key table loaded, no pins).
  --set dome : the L27 hours (S4 + S4w at 19.5 19.8 20.0 20.5, S4 + S4e at 6.5 7.0), S4 / S4m at 22, golden S4 S3 S7 (17 poses, ~4 min)
  --set golden : golden 18.4 S1-S8 (8 poses)
  --set full : golden 18.4 S1-S8, night 22 S1-S8 + S4m, the L24 / L27 hours (S4 + facing at 6.5 7.0 7.5 19.0 19.5 19.8 20.0 20.5; S4 at 21 21.5), dawn mist 7.6 (S1 S4 S4e), clear 13 (S4 S8) - 44 poses
usage: gen_plans_r07.py --out <dir> --set dome|full"""
import argparse, json, os


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--set', default='full'); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    allp = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']
    P = []
    if a.set == 'golden':
        P.append({'name': 'h18.4', 'hour': 18.4, 'cmds': [], 'shots': allp, 'settle_first': 10})
    elif a.set == 'dome':
        for h in (19.0, 19.5, 19.8, 20.0, 20.5): P.append({'name': 'h%g' % h, 'hour': h, 'cmds': [], 'shots': ['S4', 'S4w']})
        for h in (6.5, 7.0): P.append({'name': 'h%g' % h, 'hour': h, 'cmds': [], 'shots': ['S4', 'S4e']})
        P.append({'name': 'h22', 'hour': 22.0, 'cmds': [], 'shots': ['S4', 'S4m'], 'settle_first': 12})
        P.append({'name': 'h18.4', 'hour': 18.4, 'cmds': [], 'shots': allp, 'settle_first': 10})
    else:
        P = [{'name': 'h18.4', 'hour': 18.4, 'cmds': [], 'shots': allp, 'settle_first': 10}, {'name': 'h22', 'hour': 22.0, 'cmds': [], 'shots': allp + ['S4m'], 'settle_first': 14}]
        for h in (6.5, 7.0, 7.5): P.append({'name': 'h%g' % h, 'hour': h, 'cmds': [], 'shots': ['S4', 'S4e']})
        for h in (19.0, 19.5, 19.8, 20.0, 20.5): P.append({'name': 'h%g' % h, 'hour': h, 'cmds': [], 'shots': ['S4', 'S4w']})
        for h in (21.0, 21.5): P.append({'name': 'h%g' % h, 'hour': h, 'cmds': [], 'shots': ['S4']})
        P.append({'name': 'mist_h7.6', 'hour': 7.6, 'cmds': [], 'shots': ['S1', 'S4', 'S4e']})
        P.append({'name': 'h13', 'hour': 13.0, 'cmds': [], 'shots': ['S4', 'S8']})
    json.dump({'groups': P}, open(os.path.join(a.out, 'plan_%s.json' % a.set), 'w'), indent=1)
    print('plan_%s' % a.set, sum(len(g['shots']) for g in P), 'poses', len(P), 'groups ->', a.out)


if __name__ == '__main__':
    main()
