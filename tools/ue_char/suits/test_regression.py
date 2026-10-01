#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Regression guard of the suit generator (round 11): the DEFAULT style must reproduce the round-08 Tessera maps texel for texel.
The three md5 sums are those of the 1024 px base colour / normal / ORM written by the ROUND-08 code (before design.py got a style argument).
  python3 tools/ue_char/suits/test_regression.py        (CPU, ~15 s)  -> exit 1 on a mismatch"""
import sys, os, hashlib, tempfile, subprocess
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
EXPECT = {'suit_basecolor_r8.png': '66e3b691813cc83cd9dc7bd20bdf0c59', 'suit_normal_r8.png': '09f0c6554c3a706529387e78ea4ff2e8', 'suit_orm_r8.png': 'ad1be27f39d2b4d5bb77f124125d5a8f'}
out = tempfile.mkdtemp()
subprocess.run([sys.executable, os.path.join(WT, 'tools', 'ue_char', 'hero_suit_r8.py'), '--n', '1024', '--out', out, '--legacy-r8'], check=True, capture_output=True)
bad = 0
for f, h in EXPECT.items():
    got = hashlib.md5(cv2.imread(os.path.join(out, f)).tobytes()).hexdigest()
    ok = got == h; bad += not ok
    print('%-24s %s %s' % (f, got, 'OK' if ok else 'MISMATCH (expected %s)' % h))
print('REGRESSION', 'PASS' if not bad else 'FAIL')
sys.exit(1 if bad else 0)
