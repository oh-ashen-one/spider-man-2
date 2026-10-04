from gen_g3 import G, dump, col
CGH = lambda v: "post ColorGainHighlights (X=%g,Y=%g,Z=%g,W=1)" % (v, v, v)
def X(cgh=1.0, extra=(), **k):
    d = dict(aniso=0.7); d.update(k)
    return G(**d) + [CGH(cgh)] + list(extra)
dump('v_g4', {
    'w1_cgh9': X(0.9),
    'w2_cgh8': X(0.8),
    'w3_cgh8_sh2': X(0.8, ["post FilmShoulder 0.2"]),
    'w4_cgh8_b85': X(0.8, bias=0.85),
    'w5_cgh7_sh15': X(0.7, ["post FilmShoulder 0.15"]),
    'w6_cgh8_slf': X(0.8, slf=(0.93, 0.96, 1.06))})
