# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 04 (resumed, Opus) golden key / fill sweep on the merged integration build (perf preset perf60_hwl2, P1 canyon shade fill).
New levers against gen_g6: the sun direction (`! sun <elev> <az>`: the v2 sun at 9 deg puts the whole avenue canyon in shadow, so no facade is sunlit and S1 / S5 / S6
cannot show a sunlit / shaded pair) and P1's canyon shade fill (`! mpc MPC_City ShadeFill`, an emissive lift of shaded walls, city default 0.12).
Session A: sun geometry at one reduced-fill look.  Session B: fill / grade / exposure around a middle sun.  Every variant sets every key (sticky state).
usage: gen_g7.py [outdir]   -> v_g7a.json, v_g7b.json"""
import json, os, sys
MPC = '/Game/City/Materials/MPC_City.MPC_City'
def c4(r, g, b, a=1): return '(R=%g,G=%g,B=%g,A=%g)' % (r, g, b, a)
def v4(x, y, z, w=1): return '(X=%g,Y=%g,Z=%g,W=%g)' % (x, y, z, w)
def fcol(r, g, b): return '(B=%d,G=%d,R=%d,A=255)' % (round(255 * b), round(255 * g), round(255 * r))
BASE = dict(elev=9.0, az=238.0, sun=44000, sky=8.0, tint=(0.88, 0.94, 1.0), gi=3.2, glow=1.0, ao=0.35, fog=1.0, off=(0.008, 0.006, 0.004), sat=(1.1, 1.08, 1.05), con=1.08,
            gsh=(0.93, 0.97, 1.08), toe=0.5, bclip=0.0, bias=0.95, lo=70, hi=98, slope=0.92, hg=0.8, sf=0.12, gs=0.11)
FOG = (0.26, 0.2, 0.2)
def V(**k):
    d = dict(BASE); d.update(k)
    return ['sun %g %g' % (d['elev'], d['az']), 'set Sun - Intensity %g' % d['sun'], 'set SkyLight - Intensity %g' % d['sky'], 'set SkyLight - LightColor ' + fcol(*d['tint']),
            'post IndirectLightingIntensity %g' % d['gi'],
            'set CityGlowEast - Intensity %g' % (20 * d['glow']), 'set CityGlowSouth - Intensity %g' % (6 * d['glow']), 'set CityGlowNorth - Intensity %g' % (6 * d['glow']),
            'post AmbientOcclusionIntensity %g' % d['ao'], 'set HeightFog - FogInscatteringLuminance ' + c4(*[x * d['fog'] for x in FOG]),
            'post ColorOffset ' + v4(*d['off'], w=0), 'post ColorSaturation ' + v4(*d['sat']), 'post ColorContrast ' + v4(d['con'], d['con'], d['con']),
            'post ColorGainShadows ' + v4(*d['gsh']), 'post FilmToe %g' % d['toe'], 'post FilmBlackClip %g' % d['bclip'], 'post FilmSlope %g' % d['slope'],
            'post AutoExposureBias %g' % d['bias'], 'post AutoExposureLowPercent %g' % d['lo'], 'post AutoExposureHighPercent %g' % d['hi'],
            'post ColorGainHighlights ' + v4(d['hg'], d['hg'], d['hg']), 'mpc %s ShadeFill %g' % (MPC, d['sf']), 'mpc %s GlassSky %g' % (MPC, d['gs'])]
GRADE = dict(off=(0, 0, 0), sat=(1.35, 1.32, 1.28), con=1.18)
F1 = dict(GRADE, sky=3.0, gi=1.3, glow=0.0, ao=0.7, fog=0.5, sf=0.03, bias=1.2, tint=(0.62, 0.8, 1.0), gsh=(0.86, 0.96, 1.2))
def F(**k): d = dict(F1); d.update(k); return V(**d)
A = {
    'a0_v2': V(),
    'a1_e09': F(elev=9, az=238),
    'a2_e15': F(elev=15, az=238),
    'a3_e22': F(elev=22, az=238),
    'a4_e15w': F(elev=15, az=252),
    'a5_e22w': F(elev=22, az=252),
    'a6_e30w': F(elev=30, az=248),
    'a7_e15s': F(elev=15, az=225),
}
S = dict(elev=20, az=248)
B = {
    'b0_mid': F(**S),
    'b1_sf0': F(sf=0.0, **S),
    'b2_fillup': F(sf=0.06, sky=4.0, gi=1.8, **S),
    'b3_filldn': F(sky=2.0, gi=0.9, bias=1.4, **S),
    'b4_sat': F(sat=(1.5, 1.45, 1.35), con=1.24, **S),
    'b5_meter': F(lo=50, hi=95, bias=1.0, **S),
    'b6_hg65': F(hg=0.65, **S),
    'b7_sun60': F(sun=60000, bias=0.9, **S),
}
if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get('SM2_LOOK_SCRATCH', '/Users/midir/sm2-n1/_scratch/look'), 'eval7')
    os.makedirs(out, exist_ok=True)
    for tag, v in (('a', A), ('b', B)):
        p = os.path.join(out, 'v_g7%s.json' % tag); json.dump({'variants': v}, open(p, 'w'), indent=1); print('wrote', p, len(v))
