# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Piece E: the Custom-HLSL material definitions of /Game/Terrain as plain data (no `unreal` import), shared by
#   * unreal/WebHomage/Scripts/build_terrain.py   (creates the material assets from them)
#   * tools/terrain/check_hlsl.py                 (offline DXC compile of every body, so a typo costs seconds instead of a GPU-lock turn)
# Each entry: name, include (virtual shader path or None), code (the Custom node body; Rough / NormalW / Metal / Wpo are additional outputs),
# inputs [(name, kind, arg)] with kind tex|vc|wpos|scalar|vector|time|pir, outputs [(name, floats, material property name)], two_sided.
# Frames: wpos is the UE world position in cm; the browser frame is (x, y up, z) metres = (X, Z, Y) / 100.

PARK_INC = '/Project/Terrain/Park.ush'


def materials(pm):
    """pm: pathmask.json (x0, z0, w_m, h_m of the path-mask rectangle, browser metres)"""
    consts = 'float2 mo = float2(%.4f, %.4f); float2 ms = float2(%.4f, %.4f);' % (pm['x0'], pm['z0'], pm['w_m'], pm['h_m'])
    BASE = [('', 3, 'MP_BASE_COLOR'), ('Rough', 1, 'MP_ROUGHNESS'), ('NormalW', 3, 'MP_NORMAL')]
    M = []
    # park ground: the browser's park lawn shader (meadows / groves / ball fields / pond banks / Reservoir track / schist) + the path overlay and the dark park drives
    # (the browser draws the paths as alpha-blended ribbons; here they are a baked mask so there is no z-fight and the edges stay soft)
    M.append(dict(name='M_TerrainPark', include=PARK_INC, code='''
float r; float3 n;
float3 c = TerrainParkEntry(tCol, tColSampler, tNoise, tNoiseSampler, wpos, 0.0, r, n);
float2 p = wpos.xy * 0.01;
''' + consts + '''
float4 pm = Texture2DSample(tPath, tPathSampler, (p - mo) / ms);
float3 n1 = Texture2DSample(tNoise, tNoiseSampler, fl2(p / 9.0)).rgb;
float3 n2 = Texture2DSample(tNoise, tNoiseSampler, fl2(p / 2.3)).rgb;
float e = pm.r * 0.5;
float edge = smoothstep(0.02, 0.2 + 0.12 * n1.r, e + 0.08 * (n2.g - 0.5)) * smoothstep(0.0, 0.6, pm.g);
float3 pc = Texture2DSample(tAsph, tAsphSampler, fl2(p / 4.0)).rgb * float3(0.7157, 0.6514, 0.5395);
pc *= lerp(float3(1.0, 1.0, 1.0), float3(1.08, 1.0, 0.86), n1.b) * (0.9 + 0.2 * n2.r);
pc = lerp(pc, float3(0.4, 0.38, 0.34) * (0.9 + 0.2 * n1.r), 0.45);
c = lerp(c, pc, edge);
float dr = smoothstep(0.35, 0.65, pm.b);
c = lerp(c, float3(0.0742, 0.0704, 0.0648) * (0.9 + 0.2 * n2.r), dr);
r = lerp(r, 0.9, max(edge, dr));
Rough = r; NormalW = lerp(n, float3(0.0, 0.0, 1.0), max(edge, dr)); return c * gain;''',
        inputs=[('tCol', 'tex', 'grass_col'), ('tNoise', 'tex', 'noise'), ('tAsph', 'tex', 'asphalt_col'), ('tPath', 'tex', 'pathmask'), ('wpos', 'wpos', None), ('gain', 'scalar', 1.0)], outputs=BASE))
    # coast / plaza lawns: the same lawn shader, lawn variant (meadow everywhere, no ball fields / ponds / woodland floor)
    M.append(dict(name='M_TerrainLawn', include=PARK_INC, code='''
float r; float3 n;
float3 c = TerrainParkEntry(tCol, tColSampler, tNoise, tNoiseSampler, wpos, 1.0, r, n);
Rough = r; NormalW = n; return c * gain;''',
        inputs=[('tCol', 'tex', 'grass_col'), ('tNoise', 'tex', 'noise'), ('wpos', 'wpos', None), ('gain', 'scalar', 1.0)], outputs=BASE))
    # City Hall Park / Bowling Green / Battery lawns (ground.js 'mapLawns': grass_col at 7 m x tint 0xb4b89a)
    M.append(dict(name='M_TerrainMapLawn', include=None, code='''
float2 p = wpos.xy * 0.01;
float3 c = Texture2DSample(tCol, tColSampler, float2(p.x / 7.0, 1.0 - p.y / 7.0)).rgb * float3(0.4564, 0.4793, 0.3231) * (0.85 + 0.3 * Texture2DSample(tNoise, tNoiseSampler, float2(p.x / 53.0, 1.0 - p.y / 53.0)).r);
Rough = 0.95; NormalW = float3(0.0, 0.0, 1.0); return c * gain;''',
        inputs=[('tCol', 'tex', 'grass_col'), ('tNoise', 'tex', 'noise'), ('wpos', 'wpos', None), ('gain', 'scalar', 1.0)], outputs=BASE))
    # still tannin-green pond / Reservoir water (browser: createRiverMaterial body (0.045, 0.06, 0.05), roughness 0.06): glossy, two drifting normal layers
    M.append(dict(name='M_TerrainPond', include=None, code='''
float2 p = wpos.xy * 0.01;
float2 q1 = p / 7.0 + float2(0.011, 0.007) * t;
float2 q2 = p / 2.3 - float2(0.013, 0.009) * t;
float3 a = Texture2DSample(tNrm, tNrmSampler, q1).rgb * 2.0 - 1.0;
float3 b = Texture2DSample(tNrm, tNrmSampler, q2).rgb * 2.0 - 1.0;
float2 d = (a.xy + b.xy) * 0.5 * 0.28;
Rough = 0.05; NormalW = normalize(float3(d.x, d.y, 1.0));
return float3(0.045, 0.06, 0.05) * gain;''',
        inputs=[('tNrm', 'tex', 'water_nrm'), ('wpos', 'wpos', None), ('t', 'time', None), ('gain', 'scalar', 1.0)], outputs=BASE))
    # vertex-coloured / flat-coloured furniture (benches, lamps, fences, posts, coping)
    for nm, two in (('M_TerrainVC', False), ('M_TerrainVC2', True)):
        M.append(dict(name=nm, include=None, code='''
float3 c = lerp(tint.rgb, vc.rgb * tint.rgb, usevc);
Rough = roughp; Metal = metalp; return c;''',
            inputs=[('vc', 'vc', None), ('tint', 'vector', (1, 1, 1, 1)), ('usevc', 'scalar', 0.0), ('roughp', 'scalar', 0.8), ('metalp', 'scalar', 0.0)],
            outputs=[('', 3, 'MP_BASE_COLOR'), ('Rough', 1, 'MP_ROUGHNESS'), ('Metal', 1, 'MP_METALLIC')], two_sided=two))
    # grass tuft (grass.js: darker root, sunlit tips, olive / yellow-green mix with the odd straw blade, lit like the lawn, wind sways the tips)
    M.append(dict(name='M_TerrainGrass', include=None, code='''
float2 p = wpos.xy * 0.01;
float ph = 0.5 + 0.5 * sin(p.x * 0.43 + 1.7 * sin(p.y * 0.31)) * cos(p.y * 0.37 + 0.9 * sin(p.x * 0.29));
float3 g = lerp(float3(0.17, 0.2, 0.045), float3(0.23, 0.26, 0.06), ph) * lerp(0.85, 1.12, frac(rnd * 3.7));
g = lerp(g, float3(0.34, 0.27, 0.1), step(0.92, frac(rnd * 11.3)) * 0.8);
float h = vc.r;
float wo = 6.2831 * (0.5 + 0.5 * sin(p.x * 0.35 + p.y * 0.27));
float gust = 0.5 + 0.5 * sin(p.x * 0.1 - t * 0.5) * cos(p.y * 0.08);
float sway = h * h * windamp * (0.4 + 0.9 * gust) * sin(t * 1.6 + wo);
Wpo = float3(sway, sway * 0.7, 0.0);
Rough = 0.85; NormalW = float3(0.0, 0.0, 1.0);
return g * lerp(0.8, 1.04, h) * gain;''',
        inputs=[('vc', 'vc', None), ('wpos', 'wpos', None), ('t', 'time', None), ('rnd', 'pir', None), ('windamp', 'scalar', 10.0), ('gain', 'scalar', 1.0)],
        outputs=BASE + [('Wpo', 3, 'MP_WORLD_POSITION_OFFSET')], two_sided=True))
    return M
