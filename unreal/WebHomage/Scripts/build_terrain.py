# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Piece E (terrain): idempotent rebuild of /Game/Terrain from committed sources. Content is generated, never committed (unreal/WebHomage/CONTENT.md).
#   sources: browser export  tools/export/export_terrain.mjs   -> <EXPORT>/manifest.json, terrain.json, mesh/<group>/*.glb, proto/*.glb, parkmask.rgba
#            prep            tools/terrain/prep_terrain.py     -> <PREP>/pathmask.png, tuft.glb, tufts.bin, stats.json, Shaders/Terrain/ParkData.ush
#            shaders         tools/export/gen_terrain_shaders.mjs -> Shaders/Terrain/Park.ush (GLSL of ground.js createGrassMaterial, translated)
#            textures        public/assets/city/tex (grass_col, noise, asphalt_col, water_nrm)
#   steps (default all, in this order):  clean, tex, mat, mesh, foliage, map
#     clean     delete /Game/Terrain
#     tex       textures + the path mask
#     mat       Custom-HLSL materials (park lawn / path / drive overlay, coast lawn, pond, vertex-coloured furniture, grass tuft)
#     mesh      park ground / lawns / ponds / furniture GLBs -> static meshes (complex-as-simple collision on the ground)
#     foliage   grass tuft + prop prototypes
#     map       /Game/Terrain/Terrain_Land (always-loaded sublevel: ground actors tagged WHGround, 3 tuft HISMs, instanced props) and
#               /Game/Terrain/Maps/Manhattan_Terrain = the integrated Manhattan sublevels + Terrain_Land; the city's own flat park paths / lawns are hidden
# Frame: browser metres (x east, y up, z south) -> UE cm: X = 100 x, Y = 100 z, Z = 100 y (north = -Y).
import unreal, os, json, math, time, re, struct
try: unreal.SystemLibrary.execute_console_command(None, 'Module Load StaticMeshEditor')
except Exception as _ex: print('WARN Module Load StaticMeshEditor:', _ex)

WT = os.environ.get('SM2_TERRAIN_WT', os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(globals()['__file__'])))))) if '__file__' in globals() else os.environ.get('SM2_TERRAIN_WT', '/Users/midir/sm2-n1/terrain')
SCR = os.environ.get('SM2_TERRAIN_SCRATCH', '/Users/midir/sm2-n1/_scratch/terrain')
EXPORT = os.environ.get('SM2_TERRAIN_EXPORT', os.path.join(SCR, 'export'))
PREP = os.environ.get('SM2_TERRAIN_PREP', os.path.join(SCR, 'prep'))
PUB = os.path.join(WT, 'public', 'assets', 'city', 'tex')
try: ARGS = JOB_ARGS  # noqa: F821 (set by a job wrapper)
except NameError: ARGS = {}
STEPS = set((ARGS.get('steps') or os.environ.get('SM2_TERRAIN_STEPS') or 'clean,tex,mat,mesh,foliage,map').split(','))
ROOT = '/Game/Terrain'
at = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
T0 = time.time()
def log(*a): print('[build_terrain %5.0fs]' % (time.time() - T0), *a, flush=True)
def load(p): return unreal.load_asset(p)
TJ = json.load(open(os.path.join(EXPORT, 'terrain.json')))
MAN = json.load(open(os.path.join(EXPORT, 'manifest.json')))
PM = json.load(open(os.path.join(PREP, 'pathmask.json')))

# ------------------------------------------------------------------------------------------------ helpers
def import_files(files, dest, pipeline=None):
    tasks = []
    for f in files:
        t = unreal.AssetImportTask(); t.filename = f; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = False
        if pipeline: t.options = pipeline
        tasks.append(t)
    at.import_asset_tasks(tasks)
    return tasks

def tex_settings(t, srgb, comp=unreal.TextureCompressionSettings.TC_BC7, wrap=True):
    t.set_editor_property('srgb', srgb)
    t.set_editor_property('compression_settings', comp)
    if not wrap:
        t.set_editor_property('address_x', unreal.TextureAddress.TA_CLAMP); t.set_editor_property('address_y', unreal.TextureAddress.TA_CLAMP)

def mesh_pipeline():
    p = unreal.InterchangeGenericAssetsPipeline()
    p.common_meshes_properties.set_editor_properties({'recompute_normals': False, 'recompute_tangents': False, 'use_full_precision_u_vs': True,
        'remove_degenerates': False, 'vertex_color_import_option': unreal.InterchangeVertexColorImportOption.IVCIO_REPLACE})
    p.mesh_pipeline.set_editor_properties({'generate_lightmap_u_vs': False, 'build_nanite': False})
    p.material_pipeline.set_editor_property('import_materials', False)
    p.material_pipeline.texture_pipeline.set_editor_property('import_textures', False)
    return p

sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
def finish_mesh(sm, mat, collide):
    sm.set_material(0, mat)
    ns = sm.get_editor_property('nanite_settings')
    if ns.enabled: ns.enabled = False; sm.set_editor_property('nanite_settings', ns)
    bs = sms.get_lod_build_settings(sm, 0)
    bs.set_editor_property('use_full_precision_u_vs', True); bs.set_editor_property('generate_lightmap_u_vs', False)
    bs.set_editor_property('recompute_normals', False); bs.set_editor_property('recompute_tangents', False)
    sms.set_lod_build_settings(sm, 0, bs)
    bsetup = sm.get_editor_property('body_setup')
    if bsetup:
        bsetup.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE if collide else unreal.CollisionTraceFlag.CTF_USE_DEFAULT)

# ------------------------------------------------------------------------------------------------ clean
if 'clean' in STEPS:
    unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    if EAL.does_directory_exist(ROOT): EAL.delete_directory(ROOT)
    log('cleaned')

# ------------------------------------------------------------------------------------------------ textures
TEXD = ROOT + '/Textures'
if 'tex' in STEPS:
    srcs = [(os.path.join(PUB, 'grass_col.png'), 'grass_col', True), (os.path.join(PUB, 'noise.png'), 'noise', False), (os.path.join(PUB, 'asphalt_col.png'), 'asphalt_col', True),
            (os.path.join(PUB, 'water_nrm.png'), 'water_nrm', False), (os.path.join(PREP, 'pathmask.png'), 'pathmask', False)]
    import_files([s[0] for s in srcs], TEXD)
    for f, n, srgb in srcs:
        t = load(f'{TEXD}/{n}')
        if t is None: log('MISSING texture', n); continue
        if n == 'noise': tex_settings(t, False, unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
        elif n == 'pathmask':
            tex_settings(t, False, unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP, wrap=False); t.set_editor_property('never_stream', True)
        else: tex_settings(t, srgb)
    EAL.save_directory(TEXD, only_if_is_dirty=False, recursive=True)
    log('textures done')

# ------------------------------------------------------------------------------------------------ materials
MAT = ROOT + '/Materials'
_LIT = re.compile(r'(^|[^\w.])(\d+\.\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)(?![\w.])')
def fix_literals(code):
    """bare float literals -> 'f' suffix (DXC types bare literals in ternaries as 'literal float' -> FP64 on Metal; same rule as tools/export/glsl2hlsl.mjs)"""
    return '\n'.join(l if l.lstrip().startswith('//') else _LIT.sub(lambda m: m.group(1) + m.group(2) + 'f', l) for l in code.split('\n'))

def sampler_for(t):
    return unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if t.get_editor_property('srgb') else unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR

def make_material(name, include, code, inputs, outputs, two_sided=False, world_normal=True, blend='opaque'):
    """inputs: list of (name, kind, arg): kind in tex|uv|vc|wpos|wn|cam|scalar|vector|time|pir.  outputs: list of (name, n, property); the first is the return value."""
    path = f'{MAT}/{name}'
    if EAL.does_asset_exist(path):
        m = load(path); mel.delete_all_material_expressions(m)
    else:
        m = at.create_asset(name, MAT, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property('tangent_space_normal', not world_normal)
    m.set_editor_property('two_sided', two_sided)
    if blend == 'masked': m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
    c = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -400, 0)
    c.set_editor_property('code', fix_literals(code))
    c.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    c.set_editor_property('description', name)
    if include: c.set_editor_property('include_file_paths', [include])
    ins = []
    for n, kind, arg in inputs:
        ci = unreal.CustomInput(); ci.set_editor_property('input_name', n); ins.append(ci)
    c.set_editor_property('inputs', ins)
    outs = []
    for n, k, _ in outputs[1:]:
        co = unreal.CustomOutput(); co.set_editor_property('output_name', n)
        co.set_editor_property('output_type', [None, unreal.CustomMaterialOutputType.CMOT_FLOAT1, unreal.CustomMaterialOutputType.CMOT_FLOAT2, unreal.CustomMaterialOutputType.CMOT_FLOAT3][k])
        outs.append(co)
    c.set_editor_property('additional_outputs', outs)
    y = -1200
    for n, kind, arg in inputs:
        y += 90
        if kind == 'tex':
            e = mel.create_material_expression(m, unreal.MaterialExpressionTextureObject, -900, y)
            t = load(arg); e.set_editor_property('texture', t); e.set_editor_property('sampler_type', sampler_for(t))
        elif kind == 'uv':
            e = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -900, y); e.set_editor_property('coordinate_index', arg)
        elif kind == 'vc':
            e = mel.create_material_expression(m, unreal.MaterialExpressionVertexColor, -900, y)
        elif kind == 'wpos':
            e = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, y)
        elif kind == 'wn':
            e = mel.create_material_expression(m, unreal.MaterialExpressionVertexNormalWS, -900, y)
        elif kind == 'scalar':
            e = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -900, y)
            e.set_editor_property('parameter_name', n); e.set_editor_property('default_value', arg)
        elif kind == 'vector':
            e = mel.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -900, y)
            e.set_editor_property('parameter_name', n); e.set_editor_property('default_value', unreal.LinearColor(*arg))
        elif kind == 'time':
            e = mel.create_material_expression(m, unreal.MaterialExpressionTime, -900, y)
        elif kind == 'pir':
            e = mel.create_material_expression(m, unreal.MaterialExpressionPerInstanceRandom, -900, y)
        mel.connect_material_expressions(e, '', c, n)
    for i, (n, k, prop) in enumerate(outputs):
        if prop is None: continue
        mel.connect_material_property(c, '' if i == 0 else n, prop)
    for u in (unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES,):
        mel.set_material_usage(m, u)
    mel.recompile_material(m)
    EAL.save_asset(path)
    return m

MP = unreal.MaterialProperty
TEXA = lambda n: f'{TEXD}/{n}'
def pathmask_consts():
    return 'float2 mo = float2(%.4f, %.4f); float2 ms = float2(%.4f, %.4f);' % (PM['x0'], PM['z0'], PM['w_m'], PM['h_m'])

if 'mat' in STEPS:
    # the editor caches shader source files: reload the regenerated /Project/Terrain/*.ush includes
    unreal.SystemLibrary.execute_console_command(None, 'recompileshaders changed')
    PARK_INC = '/Project/Terrain/Park.ush'
    # park ground: the browser's park lawn shader (meadows / groves / ball fields / pond banks / Reservoir track / schist) + the path overlay and the dark park drives
    # (the browser draws the paths as alpha-blended ribbons; here they are a baked mask so there is no z-fight and the edges stay soft)
    make_material('M_TerrainPark', PARK_INC, '''
float r; float3 n;
float3 c = TerrainParkEntry(tCol, tColSampler, tNoise, tNoiseSampler, wpos, 0.0, r, n);
float2 p = wpos.xy * 0.01;
''' + pathmask_consts() + '''
float4 pm = Texture2DSample(tPath, tPathSampler, (p - mo) / ms);
float3 n1 = Texture2DSample(tNoise, tNoiseSampler, fl2(p / 9.0)).rgb, n2 = Texture2DSample(tNoise, tNoiseSampler, fl2(p / 2.3)).rgb;
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
        [('tCol', 'tex', TEXA('grass_col')), ('tNoise', 'tex', TEXA('noise')), ('tAsph', 'tex', TEXA('asphalt_col')), ('tPath', 'tex', TEXA('pathmask')), ('wpos', 'wpos', None), ('gain', 'scalar', 1.0)],
        [('', 3, MP.MP_BASE_COLOR), ('Rough', 1, MP.MP_ROUGHNESS), ('NormalW', 3, MP.MP_NORMAL)])
    # coast / plaza lawns: the same lawn shader, lawn variant (meadow everywhere, no ball fields / ponds / woodland floor)
    make_material('M_TerrainLawn', PARK_INC, '''
float r; float3 n;
float3 c = TerrainParkEntry(tCol, tColSampler, tNoise, tNoiseSampler, wpos, 1.0, r, n);
Rough = r; NormalW = n; return c * gain;''',
        [('tCol', 'tex', TEXA('grass_col')), ('tNoise', 'tex', TEXA('noise')), ('wpos', 'wpos', None), ('gain', 'scalar', 1.0)],
        [('', 3, MP.MP_BASE_COLOR), ('Rough', 1, MP.MP_ROUGHNESS), ('NormalW', 3, MP.MP_NORMAL)])
    # City Hall Park / Bowling Green / Battery lawns (ground.js 'mapLawns': grass_col at 7 m x tint 0xb4b89a)
    make_material('M_TerrainMapLawn', None, '''
float2 p = wpos.xy * 0.01;
float3 c = Texture2DSample(tCol, tColSampler, fl2(p / 7.0)).rgb * float3(0.4564, 0.4793, 0.3231) * (0.85 + 0.3 * Texture2DSample(tNoise, tNoiseSampler, fl2(p / 53.0)).r);
Rough = 0.95; NormalW = float3(0.0, 0.0, 1.0); return c * gain;''',
        [('tCol', 'tex', TEXA('grass_col')), ('tNoise', 'tex', TEXA('noise')), ('wpos', 'wpos', None), ('gain', 'scalar', 1.0)],
        [('', 3, MP.MP_BASE_COLOR), ('Rough', 1, MP.MP_ROUGHNESS), ('NormalW', 3, MP.MP_NORMAL)])
    # still tannin-green pond / Reservoir water (browser: createRiverMaterial body (0.045, 0.06, 0.05), roughness 0.06): glossy, two drifting normal layers
    make_material('M_TerrainPond', None, '''
float2 p = wpos.xy * 0.01;
float2 q1 = p / 7.0 + float2(0.011, 0.007) * t, q2 = p / 2.3 - float2(0.013, 0.009) * t;
float3 a = Texture2DSample(tNrm, tNrmSampler, q1).rgb * 2.0 - 1.0, b = Texture2DSample(tNrm, tNrmSampler, q2).rgb * 2.0 - 1.0;
float2 d = (a.xy + b.xy) * 0.5 * 0.28;
Rough = 0.05; NormalW = normalize(float3(d.x, d.y, 1.0));
return float3(0.045, 0.06, 0.05) * gain;''',
        [('tNrm', 'tex', TEXA('water_nrm')), ('wpos', 'wpos', None), ('t', 'time', None), ('gain', 'scalar', 1.0)],
        [('', 3, MP.MP_BASE_COLOR), ('Rough', 1, MP.MP_ROUGHNESS), ('NormalW', 3, MP.MP_NORMAL)])
    # vertex-coloured / flat-coloured furniture (benches, lamps, fences, posts, coping)
    for nm, two in (('M_TerrainVC', False), ('M_TerrainVC2', True)):
        make_material(nm, None, '''
float3 c = lerp(tint.rgb, vc.rgb * tint.rgb, usevc);
Rough = roughp; Metal = metalp; return c;''',
            [('vc', 'vc', None), ('tint', 'vector', (1, 1, 1, 1)), ('usevc', 'scalar', 0.0), ('roughp', 'scalar', 0.8), ('metalp', 'scalar', 0.0)],
            [('', 3, MP.MP_BASE_COLOR), ('Rough', 1, MP.MP_ROUGHNESS), ('Metal', 1, MP.MP_METALLIC)], two_sided=two)
    # grass tuft (grass.js: darker root, sunlit tips, olive / yellow-green mix with the odd straw blade, lit like the lawn, wind sways the tips)
    make_material('M_TerrainGrass', None, '''
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
        [('vc', 'vc', None), ('wpos', 'wpos', None), ('t', 'time', None), ('rnd', 'pir', None), ('windamp', 'scalar', 10.0), ('gain', 'scalar', 1.0)],
        [('', 3, MP.MP_BASE_COLOR), ('Rough', 1, MP.MP_ROUGHNESS), ('NormalW', 3, MP.MP_NORMAL), ('Wpo', 3, MP.MP_WORLD_POSITION_OFFSET)], two_sided=True)
    log('materials done')

def mi(name, parent, scalars=None, vectors=None):
    path = f'{MAT}/Inst/MI_{name}'
    if EAL.does_asset_exist(path):
        m = load(path)
    else:
        m = at.create_asset('MI_' + name, MAT + '/Inst', unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(m, load(f'{MAT}/{parent}'))
    for k, v in (scalars or {}).items(): mel.set_material_instance_scalar_parameter_value(m, k, float(v))
    for k, v in (vectors or {}).items(): mel.set_material_instance_vector_parameter_value(m, k, unreal.LinearColor(*v))
    EAL.save_asset(path)
    return m

# ------------------------------------------------------------------------------------------------ meshes
MESHD = ROOT + '/Meshes'
GROUND_TAG = ('park', 'mapLawns', 'coastLawn', 'parkWater')           # actors tagged WHGround (floors that never hold a web)
SKIP_MESH = ('parkPaths', 'park_drives', 'plazaPaving', 'park_water_shallows', 'wetBands', 'coastPickets')   # paths / drives = baked mask; plaza paving is the city's; shallows / wet bands / pickets: later rounds
def keep(rec):
    n = rec['name']
    return not any(n == s or n.startswith(s) for s in SKIP_MESH)
def mesh_material(rec):
    n = rec['name']; m = rec.get('mat') or {}
    if n == 'park': return load(f'{MAT}/M_TerrainPark')
    if n == 'mapLawns': return load(f'{MAT}/M_TerrainMapLawn')
    if n.startswith('coastLawn'): return load(f'{MAT}/M_TerrainLawn')
    if n.startswith('parkWater'): return load(f'{MAT}/M_TerrainPond')
    col = m.get('color') or [1, 1, 1]
    vc = 1.0 if ('COLOR_0' in rec.get('attrs', []) or rec.get('color')) else 0.0
    two = m.get('side') == 2 or n == 'park_reeds'
    return mi(n, 'M_TerrainVC2' if two else 'M_TerrainVC', {'usevc': vc, 'roughp': m.get('roughness') or 0.8, 'metalp': m.get('metalness') or 0.0}, {'tint': (col[0], col[1], col[2], 1.0)})

if 'mesh' in STEPS:
    recs = [r for r in MAN['meshes'] if keep(r)]
    import_files([os.path.join(EXPORT, r['file']) for r in recs], MESHD + '/_in', mesh_pipeline())
    n = 0
    for r in recs:
        base = r['name']
        src = f'{MESHD}/_in/{base}/StaticMeshes/{base}'; dst = f'{MESHD}/{r["kind"]}/SM_{base}'
        if not EAL.does_asset_exist(src): log('MISSING import', src); continue
        EAL.rename_asset(src, dst)
        sm = load(dst)
        collide = base == 'park' or base.startswith(('mapLawns', 'coastLawn', 'parkWater'))
        finish_mesh(sm, mesh_material(r), collide)
        EAL.save_asset(dst); n += 1
    if EAL.does_directory_exist(MESHD + '/_in'): EAL.delete_directory(MESHD + '/_in')
    log('meshes', n)

# ------------------------------------------------------------------------------------------------ foliage prototypes
PROD = ROOT + '/Props'
PROTOS = ('parkReeds', 'park_blankets', 'parklamp')
if 'foliage' in STEPS:
    files = [os.path.join(PREP, 'tuft.glb')] + [os.path.join(EXPORT, p['file']) for p in MAN['protos'] if p['name'] in PROTOS]
    import_files(files, PROD + '/_in', mesh_pipeline())
    for nm in ['tuft'] + [p['name'] for p in MAN['protos'] if p['name'] in PROTOS]:
        src = f'{PROD}/_in/{nm}/StaticMeshes/{nm}'; dst = f'{PROD}/SM_{nm}'
        if not EAL.does_asset_exist(src): log('MISSING proto', src); continue
        EAL.rename_asset(src, dst); sm = load(dst)
        if nm == 'tuft': finish_mesh(sm, load(f'{MAT}/M_TerrainGrass'), False)
        else:
            rec = [p for p in MAN['protos'] if p['name'] == nm][0]; m = rec.get('mat') or {}
            col = m.get('color') or [1, 1, 1]
            if nm == 'parklamp': col = [0.045, 0.047, 0.05]
            two = nm in ('parkReeds', 'park_blankets')
            finish_mesh(sm, mi('P_' + nm, 'M_TerrainVC2' if two else 'M_TerrainVC', {'usevc': 0.0, 'roughp': m.get('roughness') or 0.8, 'metalp': 0.4 if nm == 'parklamp' else 0.0}, {'tint': (col[0], col[1], col[2], 1.0)}), False)
        EAL.save_asset(dst)
    if EAL.does_directory_exist(PROD + '/_in'): EAL.delete_directory(PROD + '/_in')
    # three wind classes of the tuft material (tall tufts sway more)
    for nm, amp in (('TuftLow', 3.0), ('TuftMid', 7.0), ('TuftHigh', 12.0)): mi(nm, 'M_TerrainGrass', {'windamp': amp})
    log('foliage prototypes done')

# ------------------------------------------------------------------------------------------------ maps
def U(x, y, z): return unreal.Vector(x * 100.0, z * 100.0, y * 100.0)   # browser metres -> UE cm
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
def spawn(cls, loc=unreal.Vector(0, 0, 0), rot=unreal.Rotator(0, 0, 0), label=None, folder=None):
    a = eas.spawn_actor_from_class(cls, loc, rot)
    if label: a.set_actor_label(label)
    if folder: a.set_folder_path(folder)
    return a
def add_component(actor, cls):
    root = sds.k2_gather_subobject_data_for_instance(actor)[0]
    h, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=cls, blueprint_context=None))
    return unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
KEEP = ('WorldSettings', 'Brush', 'DefaultPhysicsVolume', 'GameplayDebuggerCategoryReplicator', 'WorldDataLayers', 'WorldPartitionMiniMap')
def open_level(path):
    """idempotent: an existing map is opened and emptied (deleting maps pops a modal dialog), else created"""
    if EAL.does_asset_exist(path):
        unreal.EditorLoadingAndSavingUtils.load_map(path)
        for a in eas.get_all_level_actors():
            if a.get_class().get_name() not in KEEP and a.get_path_name().startswith(path + '.'): eas.destroy_actor(a)
    else:
        les.new_level(path)
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

def hism(actor, mesh_path, transforms, cull=None, shadows=False, material=None, label=None):
    c = add_component(actor, unreal.HierarchicalInstancedStaticMeshComponent)
    c.set_static_mesh(load(mesh_path))
    if material is not None: c.set_material(0, material)
    for i in range(0, len(transforms), 20000): c.add_instances(transforms[i:i + 20000], False, True)
    if cull: c.set_editor_property('instance_end_cull_distance', int(cull))
    c.set_cast_shadow(shadows)
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return c

def build_land(path):
    world = open_level(path)
    n = 0
    # ground / water / lawns / furniture: one static-mesh actor per exported mesh (vertices are world-space: the actor sits at the origin)
    for r in MAN['meshes']:
        if not keep(r): continue
        sp = f'{MESHD}/{r["kind"]}/SM_{r["name"]}'
        if not EAL.does_asset_exist(sp): continue
        a = spawn(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), label=r['name'], folder='Terrain/' + r['kind'])
        a.static_mesh_component.set_static_mesh(load(sp)); a.set_mobility(unreal.ComponentMobility.STATIC)
        if r['name'] == 'park' or r['name'].startswith(('mapLawns', 'coastLawn', 'parkWater')): a.tags = [unreal.Name('WHGround')]
        if r['kind'] in ('ground', 'water'): a.static_mesh_component.set_cast_shadow(False) if r['kind'] == 'water' else None
        n += 1
    log('land: %d mesh actors' % n)
    # grass tufts: browser grass.js density / height mask, scattered by prep_terrain.py (x, z, yaw, width scale, height m), three wind classes, culled at 45 m
    tp = os.path.join(PREP, 'tufts.bin')
    if os.path.exists(tp) and EAL.does_asset_exist(f'{PROD}/SM_tuft'):
        import numpy as np
        R = np.fromfile(tp, np.float32).reshape(-1, 5)
        classes = [('TuftLow', R[:, 4] < 0.11), ('TuftMid', (R[:, 4] >= 0.11) & (R[:, 4] < 0.2)), ('TuftHigh', R[:, 4] >= 0.2)]
        a = spawn(unreal.Actor, unreal.Vector(0, 0, 0), label='ISM_grass_tufts', folder='Terrain/Grass')
        gy = TJ['GY']['GRASS']
        for nm, sel in classes:
            S = R[sel]
            xs = [unreal.Transform(U(float(x), gy - 0.01, float(z)), unreal.Rotator(0.0, 0.0, -math.degrees(float(yw))), unreal.Vector(float(w), float(w), float(h) / 0.85)) for x, z, yw, w, h in S]
            hism(a, f'{PROD}/SM_tuft', xs, cull=4500, material=load(f'{MAT}/Inst/MI_{nm}'))
            log('tufts', nm, len(xs))
    # instanced props: reeds + picnic blankets (matrix records [x,y,z,ry,sx,sy,sz,(r,g,b)]), park lamps inside the park (pool items {x,y,z,ry,s})
    P = TJ['G']['PARK']; INS = TJ.get('instances') or {}
    def T_matrix(r): return unreal.Transform(U(r[0], r[1], r[2]), unreal.Rotator(0.0, 0.0, -math.degrees(r[3])), unreal.Vector(r[4], r[6], r[5]))
    if 'parkReeds' in INS and EAL.does_asset_exist(f'{PROD}/SM_parkReeds'):
        a = spawn(unreal.Actor, unreal.Vector(0, 0, 0), label='ISM_parkReeds', folder='Terrain/Props')
        hism(a, f'{PROD}/SM_parkReeds', [T_matrix(r) for r in INS['parkReeds']['items']], cull=40000, shadows=False)
    if 'park-blankets' in INS and EAL.does_asset_exist(f'{PROD}/SM_park_blankets'):
        items = INS['park-blankets']['items']
        hue = lambda r: math.atan2(math.sqrt(3) * (r[8] - r[9]), 2 * r[7] - r[8] - r[9]) if len(r) >= 10 else 0.0
        items = sorted(items, key=hue); k = 6; a = spawn(unreal.Actor, unreal.Vector(0, 0, 0), label='ISM_parkBlankets', folder='Terrain/Props')
        for b in range(k):
            chunk = items[b * len(items) // k:(b + 1) * len(items) // k]
            if not chunk: continue
            col = [sum(r[7 + q] for r in chunk) / len(chunk) if len(chunk[0]) >= 10 else 0.4 for q in range(3)]
            m = mi('Blanket%d' % b, 'M_TerrainVC2', {'usevc': 0.0, 'roughp': 0.9}, {'tint': (col[0], col[1], col[2], 1.0)})
            hism(a, f'{PROD}/SM_park_blankets', [T_matrix(r) for r in chunk], cull=15000, shadows=False, material=m)
    if 'parklamp' in INS and EAL.does_asset_exist(f'{PROD}/SM_parklamp'):
        sel = [it for it in INS['parklamp']['items'] if P['x0'] < it['x'] < P['x1'] and P['z0'] < it['z'] < P['z1']]
        a = spawn(unreal.Actor, unreal.Vector(0, 0, 0), label='ISM_parklamps', folder='Terrain/Props')
        hism(a, f'{PROD}/SM_parklamp', [unreal.Transform(U(it['x'], it['y'], it['z']), unreal.Rotator(0.0, 0.0, -math.degrees(it.get('ry', 0.0))), unreal.Vector(*(it.get('s3') or [it.get('s', 1.0)] * 3))) for it in sel], cull=60000, shadows=True)
        log('park lamps', len(sel))
    return world

def build_persistent(path):
    """the integrated Manhattan map (golden) + the terrain sublevel; the city's flat park-path ribbons and lawns are hidden (terrain supersedes them)"""
    MAPS = '/Game/Maps'; CITY_GEO = '/Game/Tests/City/City_Midtown_Geo'; BOXES = '/Game/Look/Look_Boxes'; RIG = '/Game/Look/Rigs/Look_Rig_golden'; ACTORS = MAPS + '/Manhattan_Actors'
    for need in (CITY_GEO, BOXES, RIG, ACTORS):
        if not EAL.does_asset_exist(need): raise RuntimeError('missing base content %s: run the base Manhattan build first (build_manhattan.py)' % need)
    unreal.EditorLoadingAndSavingUtils.load_map(CITY_GEO)
    hid = 0
    for a in eas.get_all_level_actors():
        lb = a.get_actor_label()
        if isinstance(a, unreal.StaticMeshActor) and lb.startswith(('parkPaths', 'mapLawns')):
            a.set_actor_hidden_in_game(True); hid += 1
    les.save_current_level()
    log('city park paths / lawn actors hidden in game:', hid)
    world = open_level(path)
    have = [l.get_path_name() for l in unreal.EditorLevelUtils.get_levels(world)]
    for lp in (CITY_GEO, BOXES, RIG, ACTORS, ROOT + '/Terrain_Land'):
        if not any(('/' + lp.split('/')[-1] + ':') in h or h.endswith(lp.split('/')[-1]) for h in have):
            unreal.EditorLevelUtils.add_level_to_world(world, lp, unreal.LevelStreamingAlwaysLoaded)
    les.set_current_level_by_name(str(world.get_name()))
    gm = unreal.load_class(None, '/Script/WebHomage.WebTravGameMode')
    if gm: world.get_world_settings().set_editor_property('default_game_mode', gm)
    else: log('WARN WebTravGameMode class missing')
    ok = unreal.EditorLoadingAndSavingUtils.save_map(world, path)
    log('map', path, 'saved' if ok else 'SAVE FAILED', 'levels', len(unreal.EditorLevelUtils.get_levels(world)))

if 'map' in STEPS:
    EAL.make_directory(ROOT + '/Maps')
    build_land(ROOT + '/Terrain_Land')
    unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), ROOT + '/Terrain_Land')
    log('Terrain_Land saved')
    build_persistent(ROOT + '/Maps/Manhattan_Terrain')
log('DONE')
