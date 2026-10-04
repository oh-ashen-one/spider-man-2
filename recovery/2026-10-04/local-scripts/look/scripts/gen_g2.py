from gen_g1 import G, dump, col
c = dict(wt=7800, mie_col=(1.0, 0.72, 0.45), mie=0.03, aps=5.0, wclip=0.0)
def X(extra=(), **k):
    d = dict(c); d.update(k); return G(**d) + list(extra)
SLF = lambda r, g, b: "set SkyAtmosphere - SkyLuminanceFactor " + col(r, g, b)
dump('v_g2', {
    'h0_wc0': X(),
    'h1_hi995': X(["post AutoExposureHighPercent 99.5"]),
    'h2_lo40': X(["post AutoExposureLowPercent 40"], bias=0.55),
    'h3_avg_a': X(["post AutoExposureLowPercent 10", "post AutoExposureHighPercent 90"], bias=-0.3),
    'h4_avg_b': X(["post AutoExposureLowPercent 10", "post AutoExposureHighPercent 90"], bias=-0.6),
    'h5_slf': X([SLF(0.9, 0.95, 1.1)]),
    'h6_slf_avg': X([SLF(0.9, 0.95, 1.1), "post AutoExposureLowPercent 10", "post AutoExposureHighPercent 90"], bias=-0.45),
    'h7_aniso': X(["set SkyAtmosphere - MieAnisotropy 0.7", "set HeightFog - DirectionalInscatteringLuminance " + col(0.15, 0.075, 0.03)])})
