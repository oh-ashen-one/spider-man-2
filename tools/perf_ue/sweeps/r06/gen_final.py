#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06: the plan of the FINAL still session (run_r06.py format, no key table override: the baked table of the rebuilt Look_Rig_tod is what is measured).
Groups (settle 8 s after every hour change, the first pose of a session 12 s):
  golden 18.4   S1..S8                       (L1 / L5 / L6 / L21, S4 <= 100)
  night 22      S1..S8 + S4m                 (L3 / L8 / L13 / L14 / L22, moon disk, sky high-pass; S1 settles 14 s)
  dawn 7.6      S1 S4 S4e                    (S1 correlation against golden, L24)
  twilight      6.5 7.0 7.5 19.0 19.5 19.8 20.0 20.5 21.0 21.5 : S4 + the sun-facing perch (S4e at dawn, S4w at dusk) (+ S7 at dusk hours)
  day           13 S4 S8 ; overcast 13 w1 S4 S8 (critic pack)
usage: gen_final.py --out plan_final.json"""
import argparse, json


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    G = []
    G.append({'name': 'h18.4', 'hour': 18.4, 'shots': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'], 'settle_first': 10, 'settle': 5})
    G.append({'name': 'h22', 'hour': 22, 'shots': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S4m'], 'settle_first': 14, 'settle': 5})
    G.append({'name': 'h7.6', 'hour': 7.6, 'shots': ['S1', 'S4', 'S4e'], 'settle_first': 10, 'settle': 5})
    for h in (6.5, 7.0, 7.5, 19.0, 19.5, 19.8, 20.0, 20.5, 21.0, 21.5):
        shots = ['S4', 'S4e' if h < 12 else 'S4w'] + (['S7'] if 19.0 <= h <= 20.5 else [])
        G.append({'name': 'h%g' % h, 'hour': h, 'shots': shots, 'settle_first': 8, 'settle': 5})
    G.append({'name': 'h13', 'hour': 13, 'shots': ['S4', 'S8'], 'settle_first': 8, 'settle': 5})
    G.append({'name': 'h13w1', 'hour': 13, 'weather': 1, 'shots': ['S4', 'S8'], 'settle_first': 8, 'settle': 5})
    json.dump({'groups': G}, open(a.out, 'w'), indent=1)
    print('final plan', sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
