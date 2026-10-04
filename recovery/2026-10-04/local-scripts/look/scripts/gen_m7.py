from gen_m5 import M, dump
def X(extra=(), **k):
    d = dict(bias=0.7, sky=1.4, offs=0.008); d.update(k)
    return M(**d) + list(extra)
WC = ["post FilmWhiteClip 0"]
dump('v_m7', {
    'k1': X(),
    'k2': X(WC),
    'k3': X(WC + ["post FilmShoulder 0.2"]),
    'k4': X(WC + ["set Sun - Intensity 11000"], sl=2.3),
    'k5': X(WC + ["set Sun - Intensity 11000"], sl=2.3, aps=4.0, fogamb=3.5),
    'k6': X(WC + ["post ColorGainHighlights (X=0.9,Y=0.9,Z=0.9,W=1)"]),
    'k7': X(WC + ["set Sun - Intensity 11000"], sl=2.3, sky=1.6, bias=0.6),
    'k8': X(WC + ["set Sun - Intensity 11000"], sl=2.3, sky=1.4, bias=0.75, lo=60)})
