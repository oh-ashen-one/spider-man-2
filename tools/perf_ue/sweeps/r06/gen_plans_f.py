#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06, hold 7 (B): the FINAL stills plan (run_r06.py format) for the rebuilt Look_Midtown_tod (no key override: the baked table is measured): golden 18:24 S1..S8, night 22:00 S1..S8 + S4m,
the L24 hours (S4 + the sun-facing pose at 06:30 07:00 07:30 19:00 19:30 19:48 20:00 20:30, S4 at 21:00 21:30), the dawn mist 07:36 (S1 S4 S4e), clear 13:00 (S4 S8). 40 poses, ~9 min.
usage: gen_plans_f.py --out <dir>"""
import argparse, json, os


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    allp = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']
    P = [{'name': 'h18.4', 'hour': 18.4, 'cmds': [], 'shots': allp, 'settle_first': 10}, {'name': 'h22', 'hour': 22.0, 'cmds': [], 'shots': allp + ['S4m'], 'settle_first': 14}]
    for h in (6.5, 7.0, 7.5): P.append({'name': 'h%g' % h, 'hour': h, 'cmds': [], 'shots': ['S4', 'S4e']})
    for h in (19.0, 19.5, 19.8, 20.0, 20.5): P.append({'name': 'h%g' % h, 'hour': h, 'cmds': [], 'shots': ['S4', 'S4w']})
    for h in (21.0, 21.5): P.append({'name': 'h%g' % h, 'hour': h, 'cmds': [], 'shots': ['S4']})
    P.append({'name': 'mist_h7.6', 'hour': 7.6, 'cmds': [], 'shots': ['S1', 'S4', 'S4e']})
    P.append({'name': 'h13', 'hour': 13.0, 'cmds': [], 'shots': ['S4', 'S8']})
    json.dump({'groups': P}, open(os.path.join(a.out, 'plan_f.json'), 'w'), indent=1)
    print('plan_f', sum(len(g['shots']) for g in P), 'poses', len(P), 'groups ->', a.out)


if __name__ == '__main__':
    main()
