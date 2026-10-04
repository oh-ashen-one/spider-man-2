# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Piece E: the Custom-HLSL material definitions of /Game/Terrain as plain data (no `unreal` import), shared by
#   * unreal/WebHomage/Scripts/build_terrain.py   (creates the material assets from them)
#   * tools/terrain/check_hlsl.py                 (offline DXC compile of every body, so a typo costs seconds instead of a GPU-lock turn)
# Each entry: name, include (virtual shader path or None), code (the Custom node body; Rough / NormalW / Metal / Wpo are additional outputs),
# inputs [(name, kind, arg)] with kind tex|vc|wpos|scalar|vector|time|pir, outputs [(name, floats, material property name)], two_sided.
# Frames: wpos is the UE world position in cm; the browser frame is (x, y up, z) metres = (X, Z, Y) / 100.

PARK_INC = '/Project/Terrain/Park.ush'
LAWN_GRADE = (0.54, 1.20, 0.46, 1.0)   # r02 lawn albedo grade (R, G, B): greener, more saturated (critic r1 secondary: G/R >= 1.05, saturation >= 0.55)
FOLI_INC = '/Project/Terrain/Foliage.ush'   # round 2: LOD bands + the browser's clump-crown / leaf-card shaders (hand-written, committed)


def materials(pm):
    """pm: pathmask.json (x0, z0, w_m, h_m of the path-mask rectangle, browser metres)"""
    consts = 'float2 mo = float2(%.4f, %.4f); float2 ms = float2(%.4f, %.4f);' % (pm['x0'], pm['z0'], pm['w_m'], pm['h_m'])
    BASE = [('', 3, 'MP_BASE_COLOR'), ('Rough', 1, 'MP_ROUGHNESS'), ('NormalW', 3, 'MP_NORMAL')]
    M = []
    # park ground: the browser's park lawn shader (meadows / groves / ball fields / pond banks / Reservoir track / schist) + the path overlay and the dark park drives
    # (the browser draws the paths as alpha-blended ribbons; here they are a baked mask so there is no z-fight and the edges stay soft)
    M.append(dict(name='M_TerrainPark', include=PARK_INC, code='''
float r; float3 n;
float3 c = TerrainParkEntry(tCol, tColSampler, tNoise, tNoiseSampler, wpos, 0.0, r, n) * grade.rgb;   // r02: lawn grade (critic r1: the lawn reads khaki, G/R 0.81-0.97 vs 1.14-1.17 on the reference)
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
float Lk = dot(c, float3(0.2126, 0.7152, 0.0722));   // soft luma knee: sunlit light gravel must not clip under the golden rig (same idea as the city sidewalk's SunK)
c *= lerp(1.0, min(1.0, (0.30 + (Lk - 0.30) * 0.3) / max(Lk, 0.0001)), step(0.30, Lk));
Rough = r; NormalW = lerp(n, float3(0.0, 0.0, 1.0), max(edge, dr)); return c * gain;''',
        inputs=[('tCol', 'tex', 'grass_col'), ('tNoise', 'tex', 'noise'), ('tAsph', 'tex', 'asphalt_col'), ('tPath', 'tex', 'pathmask'), ('wpos', 'wpos', None), ('gain', 'scalar', 1.0), ('grade', 'vector', LAWN_GRADE)], outputs=BASE))
    # coast / plaza lawns: the same lawn shader, lawn variant (meadow everywhere, no ball fields / ponds / woodland floor)
    M.append(dict(name='M_TerrainLawn', include=PARK_INC, code='''
float r; float3 n;
float3 c = TerrainParkEntry(tCol, tColSampler, tNoise, tNoiseSampler, wpos, 1.0, r, n) * grade.rgb;
Rough = r; NormalW = n; return c * gain;''',
        inputs=[('tCol', 'tex', 'grass_col'), ('tNoise', 'tex', 'noise'), ('wpos', 'wpos', None), ('gain', 'scalar', 1.0), ('grade', 'vector', LAWN_GRADE)], outputs=BASE))
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
    # ez-tree leaf cards (eztrees.js ezLeafMaterial): the photo spray becomes a value map + twig mask, recoloured per instance with the autumn palette (aTintA -> aTintB,
    # custom data 0..2 / 3..5), crown self-occlusion from the per-leaf exposure (uv1.x), the odd dry brown spray; two-sided foliage (light passes through the leaves)
    M.append(dict(name='M_TerrainLeaves', include=FOLI_INC, code='''
float4 tx = Texture2DSample(tLeaf, tLeafSampler, float2(uv0.x, 1.0 - uv0.y));
float lum = dot(tx.rgb, float3(0.3, 0.59, 0.11));
float twig = 1.0 - smoothstep(-0.03, 0.02, tx.g - max(tx.r, tx.b) - 0.015);
float hsel = uv1.y * 0.7 + lum * 0.6 - 0.2;
float3 leaf = lerp(float3(a0, a1, a2), float3(b0, b1, b2), smoothstep(0.15, 0.85, hsel));
float odd = frac(uv1.y * 13.7);
leaf = lerp(leaf, float3(0.13, 0.06, 0.025), step(0.95, odd));
leaf *= 0.5 + 1.25 * lum;
float expo = saturate(uv1.x);
float occ = lerp(0.36, 1.05, pow(expo, 1.3));
float3 c = lerp(leaf, float3(0.085, 0.06, 0.042), twig) * occ * gain;
float bnd = tfBand(length(wpos - cam) * 0.01f, band, Parameters.SvPosition.xy, t);   // r02: the ez-tree LOD band (L0 < 20 m, L1 20-44 m): UE drew L1 out to 520 m
Op = tx.a * bnd; Sub = c * 0.85; Rough = 0.78;
Emis = c * 1800.0 * (0.4 + 0.6 * expo);   // r02 ambient fill (the browser's emissive sky fill): crowns in the sun's shadow were near black (luma 20-60). Units: the golden rig is physical (sun 44000 lux, EV 8-13): sunlit albedo A radiates ~10000 A cd/m2, so a ~15 % fill is ~1800 A (pass 2 used 0.65 A: no visible effect)
return c;''',
        inputs=[('tLeaf', 'texparam', 'leaf_oak'), ('uv0', 'uv', 0), ('uv1', 'uv', 1), ('a0', 'pcd', 0), ('a1', 'pcd', 1), ('a2', 'pcd', 2), ('b0', 'pcd', 3), ('b1', 'pcd', 4), ('b2', 'pcd', 5),
                ('wpos', 'wpos', None), ('cam', 'cam', None), ('band', 'vector', (0, 0, 0, 0)), ('t', 'time', None), ('gain', 'scalar', 1.0)],
        outputs=[('', 3, 'MP_BASE_COLOR'), ('Op', 1, 'MP_OPACITY_MASK'), ('Sub', 3, 'MP_SUBSURFACE_COLOR'), ('Rough', 1, 'MP_ROUGHNESS'), ('Emis', 3, 'MP_EMISSIVE_COLOR')], two_sided=True, blend='masked', foliage=True, nanite=True))
    # ez-tree bark / park trunks (vertex colour = ambient occlusion, flat bark tint) with the same LOD band clip
    M.append(dict(name='M_TerrainBark', include=FOLI_INC, code='''
float3 c = lerp(tint.rgb, vc.rgb * tint.rgb, usevc);
Op = tfBand(length(wpos - cam) * 0.01f, band, Parameters.SvPosition.xy, t);
Rough = roughp; return c;''',
        inputs=[('vc', 'vc', None), ('tint', 'vector', (0.33, 0.29, 0.25, 1)), ('usevc', 'scalar', 1.0), ('roughp', 'scalar', 0.92), ('wpos', 'wpos', None), ('cam', 'cam', None),
                ('band', 'vector', (0, 0, 0, 0)), ('t', 'time', None)],
        outputs=[('', 3, 'MP_BASE_COLOR'), ('Op', 1, 'MP_OPACITY_MASK'), ('Rough', 1, 'MP_ROUGHNESS')], blend='masked', nanite=True))
    # near leaf-card canopies (browser pool `trees-*-near`, 44-165 m, casts shadows): the city's leaf atlas + the lobe-fitted card / core geometry, per-instance autumn tints
    M.append(dict(name='M_TerrainCards', include=FOLI_INC, code='''
float op; float3 sub;
float3 c = TerrainLeafCards(tAtlas, tAtlasSampler, uv0, uv1, float3(a0, a1, a2), float3(b0, b1, b2), wn, wpos, cam, band, Parameters.SvPosition.xy, t, op, sub);
Op = op; Sub = sub * gain; Rough = 0.78;
float ex = saturate(uv1.x >= 1.5 ? uv1.x - 2.0 : uv1.x);
Emis = c * gain * 1800.0 * (0.4 + 0.6 * ex);   // r02 ambient fill, see M_TerrainLeaves
return c * gain;''',
        inputs=[('tAtlas', 'tex', 'leaf_atlas'), ('uv0', 'uv', 0), ('uv1', 'uv', 1), ('a0', 'pcd', 0), ('a1', 'pcd', 1), ('a2', 'pcd', 2), ('b0', 'pcd', 3), ('b1', 'pcd', 4), ('b2', 'pcd', 5),
                ('wn', 'wn', None), ('wpos', 'wpos', None), ('cam', 'cam', None), ('band', 'vector', (0, 0, 0, 0)), ('t', 'time', None), ('gain', 'scalar', 1.0)],
        outputs=[('', 3, 'MP_BASE_COLOR'), ('Op', 1, 'MP_OPACITY_MASK'), ('Sub', 3, 'MP_SUBSURFACE_COLOR'), ('Rough', 1, 'MP_ROUGHNESS'), ('Emis', 3, 'MP_EMISSIVE_COLOR')], two_sided=True, blend='masked', foliage=True))
    # lumpy clump crowns (browser pool `trees-*-crown`, 165-520 m, crownMaterial): procedural clumps of leaf speckle, ragged see-through silhouette, normal from the clump height field
    M.append(dict(name='M_TerrainClump', include=FOLI_INC, code='''
float op; float3 nW;
float3 c = TerrainClumpCrown(wpos, cam, wn, uv1, float3(a0, a1, a2), float3(b0, b1, b2), rnd, band, Parameters.SvPosition.xy, t, bump, op, nW);
Op = op; NormalW = nW; Rough = 0.88;
return c * gain;''',
        inputs=[('uv1', 'uv', 1), ('a0', 'pcd', 0), ('a1', 'pcd', 1), ('a2', 'pcd', 2), ('b0', 'pcd', 3), ('b1', 'pcd', 4), ('b2', 'pcd', 5), ('rnd', 'pir', None),
                ('wn', 'wn', None), ('wpos', 'wpos', None), ('cam', 'cam', None), ('band', 'vector', (0, 0, 0, 0)), ('t', 'time', None), ('gain', 'scalar', 1.0), ('bump', 'scalar', 1.0)],
        outputs=[('', 3, 'MP_BASE_COLOR'), ('Op', 1, 'MP_OPACITY_MASK'), ('Rough', 1, 'MP_ROUGHNESS'), ('NormalW', 3, 'MP_NORMAL')], blend='masked'))
    # far crowns: the city's opaque canopy-mass blobs. They are ONLY wanted beyond the ez-tree range (browser: 520 m); per-instance cull distances did not hide them in UE (v1 / v2 stills),
    # so the material clips them by camera distance (fade-in 480 .. 560 m) and tints them with the tree's own autumn palette (custom data = aTintA / aTintB)
    M.append(dict(name='M_TerrainCrown', include=FOLI_INC, code='''
float d = length(wpos - cam) * 0.01;
Op = tfBand(d, band, Parameters.SvPosition.xy, t);   // r02: the browser's dithered hand-over (crown -> crownfar over 478-520 m), nothing nearer
float nz = 0.5 + 0.5 * sin(wpos.x * 0.011 + 1.7 * sin(wpos.y * 0.0093)) * cos(wpos.y * 0.0127);
float3 c = lerp(float3(a0, a1, a2), float3(b0, b1, b2), 0.5) * lerp(0.7, 1.15, nz) * gain;
Rough = 0.95;
return c;''',
        inputs=[('wpos', 'wpos', None), ('cam', 'cam', None), ('a0', 'pcd', 0), ('a1', 'pcd', 1), ('a2', 'pcd', 2), ('b0', 'pcd', 3), ('b1', 'pcd', 4), ('b2', 'pcd', 5),
                ('band', 'vector', (520, 3200, 0, 0)), ('t', 'time', None), ('gain', 'scalar', 1.0)],
        outputs=[('', 3, 'MP_BASE_COLOR'), ('Op', 1, 'MP_OPACITY_MASK'), ('Rough', 1, 'MP_ROUGHNESS')], blend='masked', nanite=True))
    return M
