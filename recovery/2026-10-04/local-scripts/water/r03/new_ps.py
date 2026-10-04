def hlsl_ps():
    """round 03: the 5 longest Gerstner waves analytically (they match the vertex geometry) + 3 layers of the baked random-phase wind-sea slope
    spectrum (T_WaterSlope, 21 / 6.7 / 2.2 m tiles) + the resolved 0.15-0.5 m wind-chop layer (T_WaterChop, two realizations scrolling in two
    directions). Near field (<= NEAR_M): both realizations, the chop, contact / whitecap foam; textures sampled with their true gradients (no
    mip bias) and the BRDF roughness stays <= 0.08 (r02 turned mip-biased variance into roughness ~0.4 here: the flat look). Beyond NEAR_M:
    one realization per layer, no chop sample (its variance -> GGX roughness x FarVarK), no foam, no contact-map lookup (perf)."""
    CONTACT = json.load(open(os.path.join(SCR, 'water_contact.json')))
    W = [w for w in waves() if w['L'] >= PS_WAVE_MIN_L]
    big = '\n'.join('sincos(%.6f * dot(float2(%.6f, %.6f), p) - %.6f * t + %.4f, s, c); f = 1.0 - smoothstep(0.12, 0.35, foot * %.6f); '
                    'sl2 += float2(%.6f, %.6f) * (%.6f * c / max(1.0 - %.6f * s, 0.35)) * f; varU += %.8f * (1.0 - f); h += %.6f * s;'
                    % (w['k'], w['dx'], w['dy'], w['w'], w['ph'], w['k'] / math.pi, w['dx'], w['dy'], w['k'] * w['A'], w['Q'] * w['k'] * w['A'],
                       0.5 * (w['k'] * w['A']) ** 2, w['A']) for w in W)
    def rot(c, s_): return 'float2(%.6f, %.6f)' % (c, s_), 'float2(%.6f, %.6f)' % (-s_, c)
    lay = []
    for i, (sc, aA, aB, amp) in enumerate(LAYERS):
        lc = sc / 8.5
        kc = 2 * math.pi / lc
        spd = math.sqrt(GRAV / kc + 7.28e-5 * kc)
        tA, tB = math.radians(WIND_DEG + aA), math.radians(WIND_DEG + aB)
        cA, sA, cB, sB = math.cos(tA), math.sin(tA), math.cos(tB), math.sin(tB)
        sc2 = sc * 0.87
        uA, vA = rot(cA, sA); uB, vB = rot(cB, sB)
        lay.append(('{ float2 qa = float2(dot(p, %(uA)s), dot(p, %(vA)s)) / %(sc).4f - float2(%(va).6f * t, 0.0);\n'
                    '  float2 ga = (Texture2DSampleGrad(tW, tWSampler, qa, float2(dot(dpx, %(uA)s), dot(dpx, %(vA)s)) / %(sc).4f, float2(dot(dpy, %(uA)s), dot(dpy, %(vA)s)) / %(sc).4f).rg - 0.5) * %(enc).2f;\n'
                    '  ga = float2(ga.x * %(cA).6f - ga.y * %(sA).6f, ga.x * %(sA).6f + ga.y * %(cA).6f);\n'
                    '  float2 g = ga * waR;\n'
                    '  [branch] if (nearW > 0.0) {\n'
                    '    float2 qb = float2(dot(p, %(uB)s), dot(p, %(vB)s)) / %(sc2).4f - float2(%(vb).6f * t, 0.0) + float2(0.37, %(off).3f);\n'
                    '    float2 gb = (Texture2DSampleGrad(tW, tWSampler, qb, float2(dot(dpx, %(uB)s), dot(dpx, %(vB)s)) / %(sc2).4f, float2(dot(dpy, %(uB)s), dot(dpy, %(vB)s)) / %(sc2).4f).ba - 0.5) * %(enc).2f;\n'
                    '    g += float2(gb.x * %(cB).6f - gb.y * %(sB).6f, gb.x * %(sB).6f + gb.y * %(cB).6f) * wbR; }\n'
                    '  slT += g * %(amp).5f; varL += %(amp2).7f * saturate(log2(2.0 * foot / %(lmin).5f) / 3.0); }')
                   % dict(uA=uA, vA=vA, uB=uB, vB=vB, cA=cA, sA=sA, cB=cB, sB=sB, sc=sc, sc2=sc2, va=spd / sc, vb=spd * 1.07 / sc2, off=0.61 * (i + 1),
                          enc=SLOPE_ENC, amp=amp, amp2=amp * amp, lmin=sc2 / 24.0))
    chop = []
    for j, (sc, ang, vf) in enumerate(CHOP):
        lc = sc / 5.5; kc = 2 * math.pi / lc
        spd = math.sqrt(GRAV / kc + 7.28e-5 * kc) * vf
        th = math.radians(WIND_DEG + ang); c_, s_ = math.cos(th), math.sin(th); u, v = rot(c_, s_)
        ch = 'rg' if j == 0 else 'ba'
        chop.append(('{ float2 q = float2(dot(p, %(u)s), dot(p, %(v)s)) / %(sc).4f - float2(%(vv).6f * t, %(off).3f);\n'
                     '    float2 g = (Texture2DSampleGrad(tK, tKSampler, q, float2(dot(dpx, %(u)s), dot(dpx, %(v)s)) / %(sc).4f, float2(dot(dpy, %(u)s), dot(dpy, %(v)s)) / %(sc).4f).%(ch)s - 0.5) * %(enc).2f;\n'
                     '    slC += float2(g.x * %(c).6f - g.y * %(s).6f, g.x * %(s).6f + g.y * %(c).6f); lostC += 0.5 * saturate(log2(2.0 * foot / %(lmin).5f) / 1.74); }')
                    % dict(u=u, v=v, sc=sc, vv=spd / sc, off=0.29 * (j + 1), ch=ch, enc=SLOPE_ENC, c=c_, s=s_, lmin=sc / 10.0))
    return PS_TEMPLATE % dict(wx=WIND[0], wy=WIND[1], sx=SHORE_BOX[0], sz=SHORE_BOX[1], sw=SHORE_BOX[2], sh=SHORE_BOX[3], big=big, lay='\n'.join(lay),
                              chop='\n    '.join(chop), crms=CHOP_RMS, near=NEAR_M,
                              hmax=WAVE_MAX * 0.5, ss='%(SCAT)s', sa='%(ABS)s', cx=CONTACT['box'][0], cz=CONTACT['box'][1], cw=CONTACT['box'][2],
                              ch=CONTACT['box'][3], cmax=CONTACT_MAX)


PS_TEMPLATE = r'''
#define NZG(uv, s) Texture2DSampleGrad(tN, tNSampler, (uv), dpx * (s), dpy * (s))
float2 p = Lag.xy; float t = T;
float3 wp = WPos * 0.01, cm = Cam * 0.01;
float3 Vv = cm - wp; float dist = length(Vv); float3 V = Vv / max(dist, 1e-3);
float2 dpx = ddx(p), dpy = ddy(p);
float foot = max(length(abs(dpx) + abs(dpy)), 1e-4);
// r03: near field (<= %(near).0f m): two realizations per layer, the resolved wind chop, foam, contact map; beyond: one realization
float nearW = 1.0 - smoothstep(%(near).1f * 0.73, %(near).1f, dist);
float wbR = 0.70711 * nearW, waR = sqrt(1.0 - wbR * wbR);
// ---- wind gusts (broad, wind-aligned patches of rougher water). r03: wind-streak and slick terms deleted (pale comet streaks)
float2 wdir = float2(%(wx).6f, %(wy).6f);
float4 nA = NZG(p / 620.0, 1.0 / 620.0), nB = NZG(p / 230.0 + float2(t * 0.0009, 0.37), 1.0 / 230.0);
float gust = saturate((nA.r * 0.62 + nB.g * 0.38 - 0.5) * 2.4 + 0.5);
float2 su = (p - float2(%(sx).1f, %(sz).1f)) / float2(%(sw).1f, %(sh).1f);
float shore = (all(su > 0.0) && all(su < 1.0)) ? Texture2DSampleGrad(tS, tSSampler, su, dpx / float2(%(sw).1f, %(sh).1f), dpy / float2(%(sw).1f, %(sh).1f)).r * 400.0 : 400.0;
float gk = lerp(0.75, 1.25, gust);
// ---- the long Gerstner waves (waves.js waveSlope: resolved -> slope, unresolved -> slope variance)
float2 sl2 = 0; float varU = 0, h = 0, s, c, f;
%(big)s
float crest = h / %(hmax).5f;
sl2 *= lerp(0.85, 1.1, gust); varU *= 1.2;
// ---- wind-sea spectrum layers (baked random-phase slopes, true texture gradients: what the mips drop is counted in varL)
float2 slT = 0; float varL = 0;
%(lay)s
// ---- r03 resolved wind chop 0.15-0.5 m: two realizations, two scroll directions (near field only; beyond, all of it is sub-pixel variance)
float2 slC = 0; float lostC = 1.0;
[branch] if (nearW > 0.0) {
    lostC = 0.0;
    %(chop)s
    slC *= nearW * 0.70711;
    lostC = lerp(1.0, lostC, nearW);
}
float ck = ChopK * gk, mk = ChopK * MicroK * gk * %(crms).4f;
slT *= ck; varL *= ck * ck;
float2 slope = sl2 + slT + slC * mk;
float varF = varL + lostC * mk * mk;      // per-axis slope variance the shading cannot resolve
// ---- foam (near field only, faded to zero by %(near).0f m): contact (the water line against anything below it), rare whitecaps
float cf = 0.0, wf = 0.0;
[branch] if (nearW > 0.0) {
    float fn = NZG(p / 7.0 + float2(t * 0.01, -t * 0.007), 1.0 / 7.0).b;
    float lap = 0.55 + 0.225 * sin(dot(p, float2(0.11, -0.17)) + t * 1.1) + 0.35 * crest + 0.15 * (slT.x - slT.y);
    float dnw = max(DNW - PD, 0.0) * 0.01;
    float lr = dnw / max(dot(-V, View.ViewForward), 0.2);
    cf = 1.0 - smoothstep(0.04, 0.25 + 1.1 * fn + 0.6 * lap, lr);
    float2 cu = (p - float2(%(cx).2f, %(cz).2f)) / float2(%(cw).2f, %(ch).2f);
    float cdm = (all(cu > 0.0) && all(cu < 1.0)) ? Texture2DSampleLevel(tC, tCSampler, cu, 0).r * %(cmax).1f : %(cmax).1f;
    cf = max(cf, 1.0 - smoothstep(0.12, 0.45 + 1.5 * fn + 0.9 * lap, cdm));
    float foam = cf * (0.4 + 0.45 * lap) * smoothstep(0.25, 0.6, NZG(p / 3.1 + float2(-t * 0.02, t * 0.013), 1.0 / 3.1).r + 0.25 * lap) * FoamK;
    foam = max(foam, smoothstep(0.8, 1.0, crest) * smoothstep(0.55, 0.9, gust) * 0.2);
    float cov = saturate(foam);
    float pat = NZG(p / 1.9 + float2(t * 0.004, 0.0), 1.0 / 1.9).r * 0.62 + NZG(p / 0.63 + float2(0.0, t * 0.006), 1.0 / 0.63).g * 0.5;
    wf = saturate(smoothstep(1.05 - cov, 1.3 - cov, pat) * smoothstep(0.0, 0.25, cov)) * nearW;
}
// ---- normal / roughness. Near field: GGX alpha from RoughN only (<= 0.08: the resolved facets carry the slope variance);
//      beyond: + the unresolved variance x FarVarK (Cox-Munk alpha^2 = 2 sigma^2 per axis)
float3 N = normalize(float3(-slope.x, -slope.y, 1.0));
{ float3 Rr = reflect(-V, N); float wl = saturate((0.05 - Rr.z) * 8.0); N = normalize(lerp(N, float3(0, 0, 1), wl * BendK));
  Rr = reflect(-V, N); wl = saturate((0.03 - Rr.z) * 12.0); N = normalize(lerp(N, float3(0, 0, 1), wl * BendK)); }
float farW = smoothstep(%(near).1f * 0.4, %(near).1f, dist);
float r4 = RoughN * RoughN; r4 *= r4;
float a2 = r4 + VARK * FarVarK * farW * (varU + 2.0 * varF);
float rcap = lerp(0.08, 0.7, smoothstep(%(near).1f, %(near).1f * 2.7, dist));
Rough = lerp(clamp(pow(a2, 0.25), 0.03, rcap), 0.6, wf);
NormalW = normalize(lerp(N, float3(0, 0, 1), wf * 0.6));
Spec = 0.25 * SpecK;     // F0 = 0.02 (IOR 1.333) x SpecK
Opac = wf * 0.92;
// ---- turbid river optics (per cm): olive-grey Hudson body (ScatK), siltier / browner along the bulkheads
float silt = (1.0 - smoothstep(10.0, 120.0, shore)) * 0.75;
float turb = 0.85 + 0.3 * NZG(p / 900.0 + float2(0.0, t * 0.0015), 1.0 / 900.0).r;
float3 sS = float3(%(ss)s) * ScatK * turb * (1.0 + float3(0.9, 0.6, 0.3) * silt);
float3 sA = float3(%(sa)s) * (1.0 + float3(0.1, 0.2, 0.5) * silt);
Scat = sS * 0.01; Abs = sA * 0.01;
// ---- sun glitter: sparse facets that face the sun get their normal tilted onto the sun half-vector (beyond 25 m; the near field glints
//      off its own resolved facets with the sharp GGX lobe)
float3 Ls = normalize(SunDir);
float3 Hh = normalize(Ls + V);
float gw = 0.0;
[branch] if (dist < 900.0 && dist > 20.0 && Ls.z > 0.0) {
    float2 gn = (NZG(p / 2.3 + float2(t * 0.05, t * 0.034), 1.0 / 2.3).ga - 0.5) * 2.0 + 0.8 * (NZG(float2(-p.y, p.x) / 3.7 + float2(-t * 0.041, t * 0.02), 1.0 / 3.7).ga - 0.5) * 2.0;
    float3 nG = normalize(N + float3(gn * 0.22, 0.0));
    float gl = pow(saturate(dot(nG, Hh)), 700.0);
    float spark = smoothstep(0.62, 0.9, NZG(p / 5.0 + float2(t * 0.02, 0.0), 1.0 / 5.0).r);
    gw = saturate(gl * spark * (1.0 - smoothstep(600.0, 900.0, dist)) * smoothstep(20.0, 40.0, dist) * (1.0 - wf) * saturate(Ls.z * 8.0) * 3.0 * GlitterK);
}
NormalW = normalize(lerp(NormalW, Hh, gw));
Rough = lerp(Rough, 0.06, gw);
Emis = 0;
if (Dbg > 0.5) { float3 dv = Dbg < 1.5 ? float3(frac(p / 10.0), 0.0) : (Dbg < 2.5 ? N * 0.5 + 0.5 : (Dbg < 3.5 ? Rough.xxx : (Dbg < 4.5 ? float3(wf, cf, gust) : Lag.zzz))); Emis = 0; Opac = 1.0; return dv; }
return float3(0.62, 0.6, 0.55);   // r03: cream foam albedo (r02 0.74 clipped at the seawall in the golden key)
#undef NZG
'''
