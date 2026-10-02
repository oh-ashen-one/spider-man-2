#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06, hold 9 (D): knobs of the continued loop = hold-8 knobs + the exposure-bias overrides the hold-8 loop found (the starting biases) + finer extra keys at the two brightness cliffs of the twilights
(19:33-19:51 where the cloud deck and the sunlit surfaces go dark within 6 output frames; 06:24-06:42 where the sunrise glow switches on).
usage: make_knobs_d.py --knobs-c <knobs_c.json> --overrides <final6c/loop/bias_overrides.json> --out <knobs_d.json>"""
import argparse, json


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--knobs-c', required=True); ap.add_argument('--overrides', required=True); ap.add_argument('--out', required=True); a = ap.parse_args()
    K = json.load(open(a.knobs_c)); ov = json.load(open(a.overrides))
    t = {k: dict(v) for k, v in (K.get('twilight_overrides') or {}).items()}
    for h, b in ov.items(): t.setdefault(str(float(h)), {})['pp.AutoExposureBias'] = float(b)
    K['twilight_overrides'] = t
    K['extra_keys'] = sorted(set(float(x) for x in (K.get('extra_keys') or [])) | {6.4, 6.6, 6.7, 19.55, 19.6, 19.7, 19.75, 19.85})
    json.dump(K, open(a.out, 'w'), indent=1); print('knobs_d ->', a.out, 'extra keys', K['extra_keys'])


if __name__ == '__main__':
    main()
