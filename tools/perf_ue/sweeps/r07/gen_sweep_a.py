#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07, hold A: twilight dome sweep (run_r06.py plan). The BAKED table (Scripts/look_presets.json as built) + live pins (wh.ToDSet) per group, so no key table is loaded at run time
(round-06 finding 7: a table loaded with wh.ToDLoad at the end of a session rendered the night differently from the baked one).
Every r07 combo pins fog.FogCutoffDistance 0 (the height fog applies to the sky pixels: the fog meets the sky continuously, no cutoff switch).
Combos at 19.5 19.8 20.0 20.5 (S4 + S4w) and 6.5 7.0 (S4 + S4e):
  c0  cutoff 0 only
  c1  c0 + sun volumetric scattering 0 (the sun under the horizon lit the volumetric fog unshadowed: the glowing band toward the sun) + fog directional inscattering x0.2
  c2  c1 + thin twilight clouds (coverage .05, density .012) + sun cloud scattered luminance x0.4 (the black ceiling / clipped streaks)
  c3..c5  c2 + SkyLuminanceFactor = g * [1.6, 1, 0.8] with g = the hour's ladder (low / mid / high)
  c6  c4 + FogMaxOpacity .75     c7  c4 + fog density x0.4     c8  c1 + mid g (clouds as baked)
golden 18.4 (cutoff 0: S4 S3 S7 S1; + SkyLuminanceFactor .75: S4; + height falloff x2: S4), night 22 (cutoff 0: S4m S4 S1 S6), baseline (no pin) 20.0 S4 S4w.
usage: gen_sweep_a.py --out <dir>  -> <dir>/plan_a.json"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import look_tod   # noqa: E402

LADDER = {19.5: (1.5, 3.5, 8.0), 19.8: (3.0, 8.0, 20.0), 20.0: (6.0, 16.0, 40.0), 20.5: (15.0, 40.0, 100.0), 6.5: (1.5, 3.5, 8.0), 7.0: (1.0, 2.0, 4.0)}
HUE = (1.6, 1.0, 0.8)


def pin(p, v):
    v = v if isinstance(v, (list, tuple)) else [v]
    return 'exec wh.ToDSet %s %s' % (p, ' '.join('%.6g' % x for x in v))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t = look_tod.expand(look_tod.load_doc())
    G = []

    # sunc.* are not in the baked table: a pinned value would stay on the light after wh.ToDClear, so every group first pins the engine defaults (a later pin of the same param replaces it)
    RESET = [pin('sunc.VolumetricScatteringIntensity', 1), pin('sunc.CloudScatteredLuminanceScale', [1, 1, 1, 1])]

    def grp(name, h, shots, cmds, **kw):
        g = {'name': name, 'hour': h, 'cmds': RESET + list(cmds), 'shots': shots}; g.update(kw); G.append(g)
    grp('base_h20', 20.0, ['S4', 'S4w'], [], settle_first=10)
    for h in (19.5, 19.8, 20.0, 20.5, 6.5, 7.0):
        v = look_tod.evaluate(t, h)
        face = 'S4w' if h > 12 else 'S4e'
        c0 = [pin('fog.FogCutoffDistance', 0)]
        di = v['fog.DirectionalInscatteringLuminance']
        c1 = c0 + [pin('sunc.VolumetricScatteringIntensity', 0), pin('fog.DirectionalInscatteringLuminance', [x * 0.2 for x in di[:3]] + [1])]
        cs = [1.0, 1.0, 1.0]
        c2 = c1 + [pin('cloud.Cloud_GlobalCoverage', 0.05), pin('cloud.Cloud_GlobalDensity', 0.012), pin('sunc.CloudScatteredLuminanceScale', [x * 0.4 for x in cs[:3]] + [1])]
        F = lambda g: pin('atm.SkyLuminanceFactor', [g * c for c in HUE] + [1])
        lo, mid, hi = LADDER[h]
        combos = [('c0', c0), ('c1', c1), ('c2', c2), ('c3', c2 + [F(lo)]), ('c4', c2 + [F(mid)]), ('c5', c2 + [F(hi)]),
                  ('c6', c2 + [F(mid), pin('fog.FogMaxOpacity', 0.75)]), ('c7', c2 + [F(mid), pin('fog.FogDensity', v['fog.FogDensity'] * 0.4)]), ('c8', c1 + [F(mid)])]
        for n, c in combos: grp('%s_h%g' % (n, h), h, ['S4', face], c)
    c0 = [pin('fog.FogCutoffDistance', 0)]
    v = look_tod.evaluate(t, 18.4)
    grp('c0_h18.4', 18.4, ['S4', 'S3', 'S7', 'S1'], c0, settle_first=10)
    grp('gsky_h18.4', 18.4, ['S4'], c0 + [pin('atm.SkyLuminanceFactor', [0.75, 0.75, 0.75, 1])])
    grp('gfall_h18.4', 18.4, ['S4'], c0 + [pin('fog.FogHeightFalloff', v['fog.FogHeightFalloff'] * 2)])
    grp('c0_h22', 22.0, ['S4m', 'S4', 'S1', 'S6'], c0, settle_first=12)
    json.dump({'groups': G}, open(os.path.join(a.out, 'plan_a.json'), 'w'), indent=1)
    print('plan_a', sum(len(g['shots']) for g in G), 'poses', len(G), 'groups ->', a.out)


if __name__ == '__main__':
    main()
