#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07, hold B: second dome sweep (baked table + live pins; every group pins the engine defaults of the sunc.* / moonc.Volumetric params first).
Hold-A findings it builds on: cutoff 0 removes the horizon step (L27b) everywhere; thin clouds + a lit SkyLuminanceFactor give L27a on S4; the sun-facing stills clip because the exposure is
clamped by AutoExposureMaxBrightness (S4w 19:48 mean 80, S4e 07:00 clip 33-51 %), and their far band (150-185 Y) is the Mie / aerial-perspective glow toward the sun on the far city.
  P0 = cutoff 0, sun volumetric 0, fog directional x0.2, thin clouds (.05 / .012), sun cloud luminance x0.4, SkyLuminanceFactor g_mid * [1.6, 1, .8], AutoExposureMaxBrightness 15
  b1 P0 | b2 P0 + aerial-perspective distance x0.3 | b3 b2 + Mie anisotropy .6 | b4 b2 + average metering (10 / 90) | b5 b2 + g_high
  at 19.8 20.0 (S4 S4w), 6.5 7.0 (S4 S4e); 20.5 S4w warm hue variants; golden 18.4 (cutoff 0) all 8 views x 4 exposure / fog variants; night 22 moon volumetric 0 / .2.
usage: gen_sweep_b.py --out <dir>"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402

MID = {19.8: 8.0, 20.0: 16.0, 6.5: 3.5, 7.0: 2.0, 20.5: 40.0}
HIGH = {19.8: 20.0, 20.0: 40.0, 6.5: 8.0, 7.0: 4.0}
HUE = (1.6, 1.0, 0.8)


def pin(p, v):
    v = v if isinstance(v, (list, tuple)) else [v]
    return 'exec wh.ToDSet %s %s' % (p, ' '.join('%.6g' % x for x in v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    t = look_tod.expand(look_tod.load_doc()); G = []
    RESET = [pin('sunc.VolumetricScatteringIntensity', 1), pin('sunc.CloudScatteredLuminanceScale', [1, 1, 1, 1]), pin('moonc.VolumetricScatteringIntensity', 1)]

    def grp(name, h, shots, cmds, **kw):
        g = {'name': name, 'hour': h, 'cmds': RESET + list(cmds), 'shots': shots}; g.update(kw); G.append(g)
    for h in (19.8, 20.0, 6.5, 7.0, 20.5):
        v = look_tod.evaluate(t, h); face = 'S4w' if h > 12 else 'S4e'
        di = v['fog.DirectionalInscatteringLuminance']; apd = v['atm.AerialPespectiveViewDistanceScale']
        F = lambda g, hue=HUE: pin('atm.SkyLuminanceFactor', [g * c for c in hue] + [1])
        P0 = [pin('fog.FogCutoffDistance', 0), pin('sunc.VolumetricScatteringIntensity', 0), pin('fog.DirectionalInscatteringLuminance', [x * 0.2 for x in di[:3]] + [1]),
              pin('cloud.Cloud_GlobalCoverage', 0.05), pin('cloud.Cloud_GlobalDensity', 0.012), pin('sunc.CloudScatteredLuminanceScale', [0.4, 0.4, 0.4, 1]), pin('pp.AutoExposureMaxBrightness', 15)]
        AP = [pin('atm.AerialPespectiveViewDistanceScale', apd * 0.3)]
        if h == 20.5:
            grp('w1_h20.5', h, ['S4w', 'S4'], P0 + [F(40, (4.0, 1.0, 0.4))]); grp('w2_h20.5', h, ['S4w', 'S4'], P0 + AP + [F(40, (4.0, 1.0, 0.4))]); continue
        combos = [('b1', P0 + [F(MID[h])]), ('b2', P0 + AP + [F(MID[h])]), ('b3', P0 + AP + [F(MID[h]), pin('atm.MieAnisotropy', 0.6)]),
                  ('b4', P0 + AP + [F(MID[h]), pin('pp.AutoExposureLowPercent', 10), pin('pp.AutoExposureHighPercent', 90)]), ('b5', P0 + AP + [F(HIGH[h])])]
        for n, c in combos: grp('%s_h%g' % (n, h), h, ['S4', face], c)
    c0 = [pin('fog.FogCutoffDistance', 0)]
    v = look_tod.evaluate(t, 18.4); b0 = v['pp.AutoExposureBias']
    allp = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']
    grp('g1_h18.4', 18.4, allp, c0 + [pin('pp.AutoExposureBias', b0 - 0.35)], settle_first=10)
    grp('g2_h18.4', 18.4, allp, c0 + [pin('pp.AutoExposureBias', b0 - 0.35), pin('pp.AutoExposureHighPercent', 95)])
    grp('g3_h18.4', 18.4, allp, c0 + [pin('pp.AutoExposureBias', b0 - 0.45), pin('pp.AutoExposureHighPercent', 92)])
    grp('g4_h18.4', 18.4, allp, c0 + [pin('fog.FogMaxOpacity', 0.7)])
    grp('n1_h22', 22.0, ['S4m', 'S4'], c0 + [pin('moonc.VolumetricScatteringIntensity', 0)], settle_first=12)
    grp('n2_h22', 22.0, ['S4m', 'S4'], c0 + [pin('moonc.VolumetricScatteringIntensity', 0.2)])
    json.dump({'groups': G}, open(os.path.join(a.out, 'plan_b.json'), 'w'), indent=1)
    print('plan_b', sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
