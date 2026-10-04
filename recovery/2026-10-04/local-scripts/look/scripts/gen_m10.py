from gen_m5 import M, dump
def X(sun=26000, ang=5, extra=(), **k):
    d = dict(sky=1.5, sl=2.3, aps=4.0, fogamb=3.5, offs=0.008, lo=10, hi=90, bias=-0.7); d.update(k)
    return M(**d) + ["post FilmWhiteClip 0", "set Sun - Intensity %g" % sun, "set Sun - LightSourceAngle %g" % ang] + list(extra)
CGH = lambda v: "post ColorGainHighlights (X=%g,Y=%g,Z=%g,W=1)" % (v, v, v)
dump('v_m10', {
    'r1_ang5': X(),
    'r2_sh2': X(extra=["post FilmShoulder 0.2"]),
    'r3_cgh9': X(extra=[CGH(0.9)]),
    'r4_sh2_cgh9': X(extra=["post FilmShoulder 0.2", CGH(0.9)]),
    'r5_slope': X(extra=["post FilmSlope 0.85", "post FilmShoulder 0.2"]),
    'r6_sun32': X(32000, bias=-0.8),
    'r7_sh1': X(extra=["post FilmShoulder 0.1"]),
    'r8_sh2_cgh85': X(extra=["post FilmShoulder 0.2", CGH(0.85)])})
