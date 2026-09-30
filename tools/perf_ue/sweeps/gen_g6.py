# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 04 golden key / fill sweep: rebuild the golden-hour key/fill contrast (critic round 03, "biggest gap").
Every variant sets EVERY property any variant changes (live-sweep state is sticky, see README).  usage: gen_g6.py [out.json]   (default <scratch>/eval/v_g6.json)
Levers (all live, WHLookTour.h):
  sun     Sun Intensity (lux)                        key
  sky     SkyLight Intensity + LightColor            fill from the sky (real-time capture)
  gi      post IndirectLightingIntensity             fill from bounce (Lumen)
  glow    CityGlow* fill directionals (20 / 6 / 6 lux in v2), 0 = off
  ao      post AmbientOcclusionIntensity
  fog     FogInscatteringLuminance scale             the height fog is a flat additive veil in the shadows
  grade   ColorOffset (black lift), ColorSaturation, ColorContrast, ColorGainShadows, FilmToe / FilmBlackClip
  bias    AutoExposureBias, metering window          keeps the frame mean in 61..100
Targets (1080p, per still): p5 Y <= 12, p95/p5 >= 16, mean HSV saturation >= 0.44, mean 61..100, clipped <= 1.8 %."""
import json, os, sys
OUT = os.path.join(os.environ.get('SM2_LOOK_SCRATCH', '/Users/midir/sm2-n1/_scratch/look'), 'eval')
def c4(r, g, b, a=1): return '(R=%g,G=%g,B=%g,A=%g)' % (r, g, b, a)
def v4(x, y, z, w=1): return '(X=%g,Y=%g,Z=%g,W=%g)' % (x, y, z, w)
def fcol(r, g, b): return '(B=%d,G=%d,R=%d,A=255)' % (round(255 * b), round(255 * g), round(255 * r))
BASE = dict(sun=44000, sky=8.0, tint=(0.88, 0.94, 1.0), gi=3.2, glow=1.0, ao=0.35, fog=1.0, off=(0.008, 0.006, 0.004), sat=(1.1, 1.08, 1.05), con=1.08, gsh=(0.93, 0.97, 1.08),
            toe=0.5, bclip=0.0, bias=0.95, lo=70, hi=98, slope=0.92, ray=0.03, hg=0.8)
FOG = (0.26, 0.2, 0.2)
def V(**k):
    d = dict(BASE); d.update(k)
    return ['set Sun - Intensity %g' % d['sun'], 'set SkyLight - Intensity %g' % d['sky'], 'set SkyLight - LightColor ' + fcol(*d['tint']),
            'post IndirectLightingIntensity %g' % d['gi'],
            'set CityGlowEast - Intensity %g' % (20 * d['glow']), 'set CityGlowSouth - Intensity %g' % (6 * d['glow']), 'set CityGlowNorth - Intensity %g' % (6 * d['glow']),
            'post AmbientOcclusionIntensity %g' % d['ao'],
            'set HeightFog - FogInscatteringLuminance ' + c4(*[x * d['fog'] for x in FOG]),
            'post ColorOffset ' + v4(*d['off'], w=0), 'post ColorSaturation ' + v4(*d['sat']), 'post ColorContrast ' + v4(d['con'], d['con'], d['con']),
            'post ColorGainShadows ' + v4(*d['gsh']), 'post FilmToe %g' % d['toe'], 'post FilmBlackClip %g' % d['bclip'], 'post FilmSlope %g' % d['slope'],
            'post AutoExposureBias %g' % d['bias'], 'post AutoExposureLowPercent %g' % d['lo'], 'post AutoExposureHighPercent %g' % d['hi'],
            'set SkyAtmosphere - RayleighScatteringScale %g' % d['ray'], 'post ColorGainHighlights ' + v4(d['hg'], d['hg'], d['hg'])]
NOLIFT = dict(off=(0, 0, 0))
GRADE = dict(NOLIFT, sat=(1.35, 1.32, 1.28), con=1.18)
COOL = dict(tint=(0.62, 0.8, 1.0), gsh=(0.86, 0.96, 1.2))
variants = {
    'a0_base': V(),
    'a1_grade': V(**GRADE),                                         # black lift removed + saturation / contrast: what the grade alone does
    'a2_fill_mid': V(gi=2.0, sky=5.0, **GRADE),
    'a3_fill_strong': V(gi=1.3, sky=3.0, bias=1.15, **GRADE),
    'a4_fill_xstrong': V(gi=0.9, sky=2.0, bias=1.35, **GRADE),
    'a5_strong_sky_only': V(gi=3.2, sky=2.5, bias=1.1, **GRADE),      # isolates the sky light
    'a6_strong_gi_only': V(gi=1.0, sky=8.0, bias=1.1, **GRADE),       # isolates the bounce
    'a7_strong_cool': V(gi=1.3, sky=3.0, bias=1.15, **dict(GRADE, **COOL)),
    'a8_strong_sun60': V(gi=1.3, sky=3.0, sun=60000, bias=0.75, **GRADE),
    'a9_strong_ao_fog': V(gi=1.3, sky=3.0, ao=0.8, fog=0.5, glow=0.0, bias=1.15, **GRADE),
    'b0_combo': V(gi=1.3, sky=3.0, ao=0.7, fog=0.5, glow=0.0, bias=1.2, **dict(GRADE, **COOL)),
    'b1_combo_sun56': V(gi=1.3, sky=3.0, sun=56000, ao=0.7, fog=0.5, glow=0.0, bias=0.9, **dict(GRADE, **COOL)),
    'b2_combo_meter': V(gi=1.3, sky=3.0, ao=0.7, fog=0.5, glow=0.0, bias=1.0, lo=50, hi=95, **dict(GRADE, **COOL)),
    'b3_combo_toe': V(gi=1.3, sky=3.0, ao=0.7, fog=0.5, glow=0.0, bias=1.3, toe=0.62, bclip=0.02, **dict(GRADE, **COOL)),
    'b4_combo_dark': V(gi=0.9, sky=2.2, ao=0.7, fog=0.4, glow=0.0, bias=1.45, **dict(GRADE, **COOL)),
    'b5_combo_sat': V(gi=1.3, sky=3.0, ao=0.7, fog=0.5, glow=0.0, bias=1.2, **dict(GRADE, sat=(1.5, 1.45, 1.35), con=1.22, **COOL)),
    # c: a bluer sky (Rayleigh scale .03 in v2: the zenith is not blue, so the "cool sky fill" is a beige one), mid fill levels, S7 highlight handling
    'c0_ray15': V(gi=1.3, sky=2.4, ray=0.15, bias=1.15, **GRADE),
    'c1_ray30': V(gi=1.3, sky=1.8, ray=0.30, bias=1.15, **GRADE),
    'c2_ray15_dark': V(gi=0.9, sky=1.6, ray=0.15, ao=0.7, fog=0.5, glow=0.0, bias=1.35, **GRADE),
    'c3_mid_cool': V(gi=0.8, sky=2.5, ao=0.6, fog=0.5, glow=0.0, bias=1.3, **dict(GRADE, **COOL)),
    'c4_hg65': V(gi=1.3, sky=3.0, ao=0.7, fog=0.5, glow=0.0, bias=1.2, hg=0.65, **dict(GRADE, **COOL)),
    'c5_hg65_sun60': V(gi=1.3, sky=3.0, sun=60000, ao=0.7, fog=0.5, glow=0.0, bias=0.9, hg=0.65, **dict(GRADE, **COOL)),
    'c6_slope': V(gi=1.3, sky=3.0, ao=0.7, fog=0.5, glow=0.0, bias=1.3, slope=1.0, toe=0.6, **dict(GRADE, **COOL)),
    'c7_meter_dark': V(gi=0.9, sky=2.2, ao=0.7, fog=0.4, glow=0.0, bias=0.9, lo=50, hi=95, **dict(GRADE, **COOL)),
}
if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, 'v_g6.json')
    os.makedirs(os.path.dirname(out), exist_ok=True); json.dump({'variants': variants}, open(out, 'w'), indent=1); print('wrote', out, len(variants), 'variants')
    names = list(variants)   # two halves: one game session each (a session of 16 variants x 8 poses could pass the 40 min slot hold when shaders recompile)
    for tag, part in (('a', names[:8]), ('b', names[8:16]), ('c', names[16:])):
        p = out.replace('.json', tag + '.json'); json.dump({'variants': {n: variants[n] for n in part}}, open(p, 'w'), indent=1); print('wrote', p, len(part), 'variants')
