#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06: writes the key table(s) and the sweep plans of the first diagnostic hold (run_r06.py format) into <out>/ :
  keys_base.txt            the current table of Scripts/look_presets.json (Scripts/look_tod.py expand + to_text); keys_herofill0.txt the same with herofill 0 at every key
  plan_a.json              twilight sky sweep: baseline at 6.5 7 7.5 19 19.5 20 20.5 21 21.5 (S4 + the sun-facing perch S4e / S4w) + sky variants A1..A3 at four hours
  plan_h.json              fog cutoff / atm.HeightFogContribution continuity test at 19.8 and 20.5 (is the sky wash a continuous knob?)
  plan_d.json              dawn 7.6 decorrelation variants (S1 + S4e) and golden 18.4 S4 reduction variants (S4, S3, S1)
  plan_m.json              22:00 moon / cloud / star variants (S4m moon-facing perch + S4)
Variants are absolute `wh.ToDSet` pins computed from the baseline value at that hour (look_tod.evaluate), cleared by every group's `wh.ToDClear`.
usage: gen_plans.py --out <dir> [--doc <alternative look_presets.json>]"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402


def fmt(v): return ' '.join('%.6g' % x for x in (v if isinstance(v, list) else [v]))


def pin(name, v): return 'exec wh.ToDSet %s %s' % (name, fmt(v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--doc', default='')
    a = ap.parse_args()
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    doc = json.load(open(a.doc)) if a.doc else look_tod.load_doc()
    tab = look_tod.expand(doc)
    base = os.path.join(out, 'keys_base.txt'); open(base, 'w').write(look_tod.to_text(tab))
    # hero test table: the traversal character's own 5000 cd hero fill (P3 'HeroFill', ~1500 lux on the hero at every hour) switched off at every key, the exposure-relative hero lights at nominal
    open(os.path.join(out, 'keys_herofill0.txt'), 'w').write(look_tod.to_text(look_tod.expand(doc, ['h=*:herofill=0'])))
    E = lambda h: look_tod.evaluate(tab, h)

    def G(name, h, hour_shots, cmds, keys=base, **kw):
        g = {'name': name, 'hour': h, 'keys': keys, 'cmds': cmds, 'shots': hour_shots}; g.update(kw); return g

    # ---------------- A: twilight sky
    dusk = [19.0, 19.5, 20.0, 20.5, 21.0, 21.5]; dawn = [6.5, 7.0, 7.5]
    A = []
    for h in dawn + dusk:
        face = 'S4e' if h < 12 else 'S4w'
        A.append(G('A0_h%g' % h, h, ['S4', face], []))
    def sky_pins(h, k):
        b = E(h); c = []
        if k == 1: c.append(pin('atm.SkyLuminanceFactor', [2.2, 1.4, 0.9, 1.0]))
        if k >= 2: c.append(pin('atm.SkyLuminanceFactor', [4.0, 1.6, 0.6, 1.0]))
        if k >= 3:
            c.append(pin('sky.Intensity', b['sky.Intensity'] * 0.5))
            for d in 'NESW': c.append(pin('fill.' + d, b['fill.' + d] * 0.3))
            c.append(pin('fog.SkyAtmosphereAmbientContributionColorScale', [0.3, 0.3, 0.3, 1.0]))
        if k >= 4: c.append(pin('sun.Intensity', min(60000.0, b['sun.Intensity'] * 3.0)))
        return c
    for h in (7.0, 19.5, 20.5, 21.5):
        face = 'S4e' if h < 12 else 'S4w'
        for k, nm in ((1, 'A1_sky'), (2, 'A2_warm'), (3, 'A3_dim'), (4, 'A4_sun')):
            A.append(G('%s_h%g' % (nm, h), h, ['S4', face], sky_pins(h, k)))
    json.dump({'groups': A}, open(os.path.join(out, 'plan_a.json'), 'w'), indent=1)

    # ---------------- H: fog cutoff continuity (does atm.HeightFogContribution take the fog off the sky continuously?)
    H = []
    # HeightFogContribution scales the sky-ambient and atmosphere-light terms of the fog colour (HeightFogCommon.ush), it does not take the fog off the sky pixels:
    # the cutoff (0 = fog applies to the sky, > 0 = sky unfogged) is the switch. Is the sky better unfogged at dusk? how big is the step at golden / blue?
    for h in (18.4, 19.2):
        H.append(G('H0_base_h%g' % h, h, ['S4', 'S4w'], []))
        H.append(G('H3_cut_h%g' % h, h, ['S4', 'S4w'], [pin('fog.FogCutoffDistance', 700000)]))
    for h in (19.8, 20.5):
        for nm, c in (('H0_base', []), ('H1_hfc0', [pin('fog.FogCutoffDistance', 0), pin('atm.HeightFogContribution', 0)]),
                      ('H3_cut', [pin('fog.FogCutoffDistance', 700000), pin('atm.HeightFogContribution', 1)]),
                      ('H5_cut_hfc0', [pin('fog.FogCutoffDistance', 700000), pin('atm.HeightFogContribution', 0)]),
                      ('H4_amb0', [pin('fog.FogCutoffDistance', 0), pin('fog.SkyAtmosphereAmbientContributionColorScale', [0, 0, 0, 1])])):
            H.append(G('%s_h%g' % (nm, h), h, ['S4', 'S4w'], c))
    json.dump({'groups': H}, open(os.path.join(out, 'plan_h.json'), 'w'), indent=1)

    # ---------------- D: dawn decorrelation (S1 07:36) and golden S4
    D = []
    b = E(7.6)
    cool = [pin('sun.Temperature', 6500), pin('sun.Intensity', b['sun.Intensity'] * 0.6), pin('sky.LightColor', [0.8, 0.9, 1.0, 1.0]), pin('sky.Intensity', b['sky.Intensity'] * 1.3),
            pin('fill.W', 0), pin('fill.E', 3.0), pin('fillT.E', 6500)]
    mist = cool + [pin('fog.FogDensity', b['fog.FogDensity'] * 5), pin('fog.FogHeightFalloff', 0.2), pin('fog.StartDistance', 1000), pin('fog.FogInscatteringLuminance', [0.35, 0.4, 0.5, 1.0]),
                   pin('fog.FogMaxOpacity', 0.8)]
    dense = cool + [pin('fog.FogDensity', b['fog.FogDensity'] * 12), pin('fog.FogHeightFalloff', 0.2), pin('fog.StartDistance', 500), pin('fog.FogInscatteringLuminance', [0.5, 0.56, 0.68, 1.0]),
                    pin('fog.FogMaxOpacity', 0.92), pin('pp.ColorContrast', [1.0, 1.0, 1.0, 1.0]), pin('pp.AutoExposureBias', b['pp.AutoExposureBias'] + 0.3)]
    for nm, c in (('D0_base', []), ('D1_cool', cool), ('D2_mist', mist), ('D3_dense', dense)):
        D.append(G('%s_h7.6' % nm, 7.6, ['S1', 'S4e'], c))
    D.append(G('G0_base_h18.4', 18.4, ['S4', 'S3', 'S1', 'S7'], []))
    g = E(18.4)
    for nm, c in (('G1_mie.6', [pin('atm.MieScatteringScale', g['atm.MieScatteringScale'] * 0.6)]),
                  ('G2_aerial3.5', [pin('atm.AerialPespectiveViewDistanceScale', 3.5)]),
                  ('G3_bias1.05', [pin('pp.AutoExposureBias', 1.05)]),
                  ('G4_mie.6_aer3.5', [pin('atm.MieScatteringScale', g['atm.MieScatteringScale'] * 0.6), pin('atm.AerialPespectiveViewDistanceScale', 3.5)]),
                  # S7's 3.5 % clipped pixels are the R channel only (x 868..1114, the warm sun column): lower the red of the highlights (S2 B-R -57 gets closer to L6 too)
                  ('G5_hiR.62', [pin('pp.ColorGainHighlights', [0.62, 0.72, 0.72, 1.0])]),
                  ('G6_hiR.55_b.8', [pin('pp.ColorGainHighlights', [0.55, 0.72, 0.72, 1.0]), pin('pp.AutoExposureBias', g['pp.AutoExposureBias'] - 0.1)])):
        D.append(G('%s_h18.4' % nm, 18.4, ['S4', 'S3', 'S1', 'S7'], c))
    json.dump({'groups': D}, open(os.path.join(out, 'plan_d.json'), 'w'), indent=1)

    # ---------------- M: night moon / clouds
    M = []
    m1 = [pin('moonc.LightSourceAngle', 1.2), pin('moonc.CloudScatteredLuminanceScale', [8, 8, 8, 1]), pin('cloud.Cloud_GlobalCoverage', 0.3), pin('cloud.Cloud_GlobalDensity', 0.03)]
    for nm, c in (('M0_base', []), ('M1_big+cloud', m1), ('M2_lux20', m1 + [pin('moon.Intensity', 20)]), ('M3_disk3', m1 + [pin('moonc.AtmosphereSunDiskColorScale', [3, 3, 3, 1])]), ('M4_stars3', m1 + [pin('stars', 3)])):
        M.append(G('%s_h22' % nm, 22.0, ['S4m', 'S4'], c))
    # hero calibration at night: the traversal character's own fill off, the exposure-relative rim / fill / top at 0.5 .. 4 x nominal (pose H1, hero in the middle of the frame)
    for sc in (0.5, 1.0, 2.0, 4.0):
        M.append(G('Hero%g_h22' % sc, 22.0, ['H1'], [pin('herofill', 0), pin('hero', sc)]))
    json.dump({'groups': M}, open(os.path.join(out, 'plan_m.json'), 'w'), indent=1)
    print('wrote', sorted(os.listdir(out)), 'A %d groups, H %d, D %d, M %d' % (len(A), len(H), len(D), len(M)))


if __name__ == '__main__':
    main()
