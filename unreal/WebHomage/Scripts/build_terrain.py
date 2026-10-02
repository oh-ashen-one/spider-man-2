# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Piece E (terrain): idempotent rebuild of /Game/Terrain from committed sources. Content is generated, never committed (unreal/WebHomage/CONTENT.md).
#   sources: browser export  tools/export/export_terrain.mjs   -> <EXPORT>/manifest.json, terrain.json, mesh/<group>/*.glb, proto/*.glb, parkmask.rgba
#            prep            tools/terrain/prep_terrain.py     -> <PREP>/pathmask.png, tuft.glb, tufts.bin, stats.json, Shaders/Terrain/ParkData.ush
#            shaders         tools/export/gen_terrain_shaders.mjs -> Shaders/Terrain/Park.ush (GLSL of ground.js createGrassMaterial, translated)
#            textures        public/assets/city/tex (grass_col, noise, asphalt_col, water_nrm)
#   steps (default all, in this order):  clean, tex, mat, mesh, foliage, trees, map, views
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
STEPS = set((ARGS.get('steps') or os.environ.get('SM2_TERRAIN_STEPS') or 'clean,tex,mat,mesh,foliage,trees,map,views').split(','))
ROOT = '/Game/Terrain'
at = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
T0 = time.time()
def log(*a): print('[build_terrain %5.0fs]' % (time.time() - T0), *a, flush=True)
def load(p): return unreal.load_asset(p)
import traceback
def step(name):
    """run a build step now if selected; a failure is logged with its traceback and the next steps still run (each step only needs the saved output of the earlier ones)"""
    def deco(fn):
        if name in STEPS:
            try: fn()
            except Exception:
                log('STEP %s FAILED' % name); traceback.print_exc()
        return fn
    return deco
def soft(label, fn, *a):
    try: return fn(*a)
    except Exception:
        log('SECTION %s FAILED' % label); traceback.print_exc(); return None
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

def mesh_pipeline(nanite=False):
    p = unreal.InterchangeGenericAssetsPipeline()
    p.common_meshes_properties.set_editor_properties({'recompute_normals': False, 'recompute_tangents': False, 'use_full_precision_u_vs': True,
        'remove_degenerates': False, 'vertex_color_import_option': unreal.InterchangeVertexColorImportOption.IVCIO_REPLACE})
    p.mesh_pipeline.set_editor_properties({'generate_lightmap_u_vs': False, 'build_nanite': nanite})
    p.material_pipeline.set_editor_property('import_materials', False)
    p.material_pipeline.texture_pipeline.set_editor_property('import_textures', False)
    return p

sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
def finish_mesh(sm, mat, collide, nanite=False):
    sm.set_material(0, mat)
    ns = sm.get_editor_property('nanite_settings')
    if ns.enabled != nanite: ns.enabled = nanite; sm.set_editor_property('nanite_settings', ns)
    bs = sms.get_lod_build_settings(sm, 0)
    bs.set_editor_property('use_full_precision_u_vs', True); bs.set_editor_property('generate_lightmap_u_vs', False)
    bs.set_editor_property('recompute_normals', False); bs.set_editor_property('recompute_tangents', False)
    sms.set_lod_build_settings(sm, 0, bs)
    bsetup = sm.get_editor_property('body_setup')
    if bsetup:
        bsetup.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE if collide else unreal.CollisionTraceFlag.CTF_USE_DEFAULT)

# ------------------------------------------------------------------------------------------------ clean
@step('clean')
def _step_clean():
    unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    if EAL.does_directory_exist(ROOT): EAL.delete_directory(ROOT)
    log('cleaned')

# ------------------------------------------------------------------------------------------------ textures
TEXD = ROOT + '/Textures'
@step('tex')
def _step_tex():
    srcs = [(os.path.join(PUB, 'grass_col.png'), 'grass_col', True), (os.path.join(PUB, 'noise.png'), 'noise', False), (os.path.join(PUB, 'asphalt_col.png'), 'asphalt_col', True),
            (os.path.join(PUB, 'water_nrm.png'), 'water_nrm', False), (os.path.join(PREP, 'pathmask.png'), 'pathmask', False)] + \
            [(os.path.join(PREP, 'leaf_' + n + '.png'), 'leaf_' + n, True) for n in ('oak', 'ash', 'aspen', 'pine')] + [(os.path.join(PREP, 'leaf_atlas.png'), 'leaf_atlas', False)]
    import_files([s[0] for s in srcs], TEXD)
    for f, n, srgb in srcs:
        t = load(f'{TEXD}/{n}')
        if t is None: log('MISSING texture', n); continue
        if n == 'noise': tex_settings(t, False, unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
        elif n == 'pathmask':
            tex_settings(t, False, unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP, wrap=False); t.set_editor_property('never_stream', True)
        elif n == 'leaf_atlas': tex_settings(t, False, unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)   # data atlas (G >= 0.97 = twig): linear, uncompressed, tiled
        elif n.startswith('leaf_'): tex_settings(t, True, wrap=False)
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

def make_material(name, include, code, inputs, outputs, two_sided=False, world_normal=True, blend='opaque', foliage=False, nanite=False):
    """inputs: list of (name, kind, arg): kind in tex|uv|vc|wpos|wn|cam|scalar|vector|time|pir.  outputs: list of (name, n, property); the first is the return value."""
    path = f'{MAT}/{name}'
    if EAL.does_asset_exist(path):
        m = load(path); mel.delete_all_material_expressions(m)
    else:
        m = at.create_asset(name, MAT, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property('tangent_space_normal', not world_normal)
    m.set_editor_property('two_sided', two_sided)
    if blend == 'masked': m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
    if foliage: m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
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
        elif kind == 'texparam':
            e = mel.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, -900, y)
            e.set_editor_property('parameter_name', n); t = load(arg); e.set_editor_property('texture', t); e.set_editor_property('sampler_type', sampler_for(t))
        elif kind == 'uv':
            e = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -900, y); e.set_editor_property('coordinate_index', arg)
        elif kind == 'pcd':
            e = mel.create_material_expression(m, unreal.MaterialExpressionPerInstanceCustomData, -900, y); e.set_editor_property('data_index', arg)
        elif kind == 'vc':
            e = mel.create_material_expression(m, unreal.MaterialExpressionVertexColor, -900, y)
        elif kind == 'wpos':
            e = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, y)
        elif kind == 'wn':
            e = mel.create_material_expression(m, unreal.MaterialExpressionVertexNormalWS, -900, y)
        elif kind == 'cam':
            e = mel.create_material_expression(m, unreal.MaterialExpressionCameraPositionWS, -900, y)
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
    # Nanite usage flag (ez-tree L1 meshes are Nanite): without it the game logs 'missing usage flag Nanite! Default Material will be used in game' and draws the grey default material (r01 warm-up log)
    for u in (unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES,) + ((unreal.MaterialUsage.MATUSAGE_NANITE,) if nanite else ()):
        mel.set_material_usage(m, u)
    mel.recompile_material(m)
    EAL.save_asset(path)
    return m

MP = unreal.MaterialProperty
def _materials_module():
    here = os.path.join(WT, 'unreal', 'WebHomage', 'Scripts', 'terrain_materials.py')
    ns = {'__file__': here}; exec(compile(open(here).read(), here, 'exec'), ns); return ns

@step('mat')
def _step_mat():
    # the editor caches shader source files: reload the regenerated /Project/Terrain/*.ush includes
    unreal.SystemLibrary.execute_console_command(None, 'recompileshaders changed')
    for d in _materials_module()['materials'](PM):
        make_material(d['name'], d['include'], d['code'], [(n, k, (f'{TEXD}/{a}' if k in ('tex', 'texparam') else a)) for n, k, a in d['inputs']],
                      [(n, k, getattr(MP, p)) for n, k, p in d['outputs']], two_sided=d.get('two_sided', False), blend='masked' if d.get('blend') == 'masked' else 'opaque', foliage=bool(d.get('foliage')), nanite=bool(d.get('nanite')))
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
SKIP_MESH = ('park_ballfield_fences', 'park_setpieces', 'parkPaths', 'park_drives', 'plazaPaving', 'park_water_shallows', 'wetBands', 'coastPickets')   # paths / drives = baked mask; plaza paving is the city's; shallows / wet bands / pickets: later rounds
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

@step('mesh')
def _step_mesh():
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
@step('foliage')
def _step_foliage():
    extra = ['tuft'] + [n for n in ('shore_patch', 'park_rocks') if os.path.exists(os.path.join(PREP, n + '.glb'))]
    files = [os.path.join(PREP, n + '.glb') for n in extra] + [os.path.join(EXPORT, p['file']) for p in MAN['protos'] if p['name'] in PROTOS]
    import_files(files, PROD + '/_in', mesh_pipeline())
    for nm in extra + [p['name'] for p in MAN['protos'] if p['name'] in PROTOS]:
        src = f'{PROD}/_in/{nm}/StaticMeshes/{nm}'; dst = f'{PROD}/SM_{nm}'
        if not EAL.does_asset_exist(src): log('MISSING proto', src); continue
        EAL.rename_asset(src, dst); sm = load(dst)
        if nm == 'tuft': finish_mesh(sm, load(f'{MAT}/M_TerrainGrass'), False)
        elif nm == 'park_rocks': finish_mesh(sm, mi('P_park_rocks', 'M_TerrainVC', {'usevc': 1.0, 'roughp': 0.9}, {'tint': (1.0, 1.0, 1.0, 1.0)}), False)   # schist outcrops (vertex-coloured, museum triangles dropped in prep)
        elif nm == 'shore_patch': finish_mesh(sm, mi('P_shore_patch', 'M_TerrainVC', {'usevc': 0.0, 'roughp': 0.85}, {'tint': (0.2, 0.19, 0.17, 1.0)}), False)   # granite bulkhead blocks closing the shoreline gaps (tools/terrain/shore_audit.py)
        else:
            rec = [p for p in MAN['protos'] if p['name'] == nm][0]; m = rec.get('mat') or {}
            col = m.get('color') or [1, 1, 1]
            if nm == 'parklamp': col = [0.045, 0.047, 0.05]
            two = nm in ('parkReeds', 'park_blankets')
            finish_mesh(sm, mi('P_' + nm, 'M_TerrainVC2' if two else 'M_TerrainVC', {'usevc': 0.0, 'roughp': m.get('roughness') or 0.8, 'metalp': 0.4 if nm == 'parklamp' else 0.0}, {'tint': (col[0], col[1], col[2], 1.0)}), False)
        EAL.save_asset(dst)
    if EAL.does_directory_exist(PROD + '/_in'): EAL.delete_directory(PROD + '/_in')
    # three wind classes of the tuft material (tall tufts sway more)
    for nm, amp in (('TuftLow', 3.0), ('TuftMid', 7.0), ('TuftHigh', 12.0)): mi(nm, 'M_TerrainGrass', {'windamp': amp, 'gain': 1.7})   # v2 stills: tufts read darker than the lawn (browser blades are lit yellow-green)
    log('foliage prototypes done')

# ------------------------------------------------------------------------------------------------ park woodland (ez-trees + the browser's tree distance chain, per-instance autumn tints)
# browser (trees.js / eztrees.js / pool.js): ez L0 < 20 m -> ez L1 < 44 m -> `trees-*-near` leaf-card canopies 44-165 m (shadows) -> `trees-*-crown` lumpy clump crowns 165-520 m ->
# `trees-*-crownfar` blobs >= 520 m, trunks `trunks-*` (near / mid / far LODs) under the card + crown LODs. UE draws every HISM instance at every distance, so each pool is a HISM whose
# material clips by camera distance with the pool's dithered band (Foliage.ush tfBand; the band comes from the export: near / far / fadeIn / fadeOut).
TREED = ROOT + '/Trees'
TREE_RE = re.compile(r'^ez_(park|elm|conifer)\d_l[01]_(leaves|bark)$')
CHAIN_RE = re.compile(r'^(trees_(park|elm|conifer)_(near|crown)|trunks_(park|elm|conifer)(_mid|_far)?)$')
POOL_RE = re.compile(r'^(ez-(park|elm|conifer)\d-l[01]-(leaves|bark)|trees-(park|elm|conifer)-(near|crown|crownfar)|trunks-(park|elm|conifer)(-mid|-far)?)$')
def leaf_name(rec):
    u = (rec.get('mat') or {}).get('map') or ''
    return os.path.basename(u).split('.')[0] or 'oak'
def pool_band(d):
    """(in0, in1, out0, out1) metres, exactly pool.js aLod: fade in over [near - fadeIn, near], out over [far - fadeOut, far]"""
    near, far = float(d.get('near') or 0.0), float(d.get('far') or 3200.0)
    fi, fo = float(d.get('fadeIn') or 0.0), float(d.get('fadeOut') or 0.0)
    return (near - fi if near > 0 else 0.0, near, far - fo if fo > 0 else far, far)
@step('trees')
def _step_trees():
    recs = [p for p in MAN['protos'] if TREE_RE.match(p['name'])]
    for nan in (False, True):    # LOD1 (and only LOD1) is Nanite, like the city's ez-tree props
        grp = [p for p in recs if (p['name'].split('_')[2] == 'l1') == nan]
        import_files([os.path.join(EXPORT, p['file']) for p in grp], TREED + '/_in', mesh_pipeline(nan))
    chain = [p for p in MAN['protos'] if CHAIN_RE.match(p['name'])]
    import_files([os.path.join(EXPORT, p['file']) for p in chain], TREED + '/_in', mesh_pipeline(False))
    for p in recs + chain:
        nm = p['name']; src = f'{TREED}/_in/{nm}/StaticMeshes/{nm}'; dst = f'{TREED}/SM_{nm}'
        if not EAL.does_asset_exist(src): log('MISSING tree proto', src); continue
        EAL.rename_asset(src, dst); sm = load(dst)
        if TREE_RE.match(nm):
            nan = nm.split('_')[2] == 'l1'
            if nm.endswith('_leaves'): finish_mesh(sm, load(f'{MAT}/M_TerrainLeaves'), False, nanite=nan)
            else: finish_mesh(sm, load(f'{MAT}/M_TerrainBark'), False, nanite=nan)
        elif nm.startswith('trunks_'): finish_mesh(sm, load(f'{MAT}/M_TerrainBark'), False)
        elif nm.endswith('_near'): finish_mesh(sm, load(f'{MAT}/M_TerrainCards'), False)
        else: finish_mesh(sm, load(f'{MAT}/M_TerrainClump'), False)
        EAL.save_asset(dst)
    if EAL.does_directory_exist(TREED + '/_in'): EAL.delete_directory(TREED + '/_in')
    log('tree prototypes', len(recs), '+ chain', len(chain))

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

def lite(c, indirect=False):
    """keep a component out of the distance-field scene (and out of Lumen's dynamic indirect lighting): every HISM instance would otherwise become a distance-field object
    (181 k tufts + 19 k tree instances pinned the GPU at 100 % and starved WindowServer on the first run, 2026-10-01 20:43); world-space ground meshes also trip the DF origin precision ensure"""
    for k, v in (('affect_distance_field_lighting', False), ('affect_dynamic_indirect_lighting', bool(indirect))):
        try: c.set_editor_property(k, v)
        except Exception as ex: log('WARN', k, str(ex)[:100])

def hism(actor, mesh_path, transforms, cull=None, shadows=False, material=None, label=None):
    c = add_component(actor, unreal.HierarchicalInstancedStaticMeshComponent)
    c.set_static_mesh(load(mesh_path))
    if material is not None: c.set_material(0, material)
    if cull:
        try: c.set_editor_property('instance_end_cull_distance', int(cull))
        except Exception as ex: log('WARN instance_end_cull_distance', str(ex)[:100])
    c.set_cast_shadow(shadows)
    lite(c)
    for i in range(0, len(transforms), 20000): c.add_instances(transforms[i:i + 20000], False, True)
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return c

def build_land(path):
    world = open_level(path)
    P = TJ['G']['PARK']; INS = TJ.get('instances') or {}
    def T_matrix(r): return unreal.Transform(U(r[0], r[1], r[2]), unreal.Rotator(0.0, 0.0, -math.degrees(r[3])), unreal.Vector(r[4], r[6], r[5]))

    def _sec_meshes():
        n = 0
        # ground / water / lawns / furniture: one static-mesh actor per exported mesh (vertices are world-space: the actor sits at the origin)
        for r in MAN['meshes']:
            if not keep(r): continue
            sp = f'{MESHD}/{r["kind"]}/SM_{r["name"]}'
            if not EAL.does_asset_exist(sp): continue
            # park lawn + city-park lawns sit 3 cm above the city's own flat ribbons / lawns (same height 0.17 m): they are covered, never z-fighting, and the city assets stay untouched
            zoff = 3.0 if r['name'] in ('park', 'mapLawns') else 0.0
            if r['name'].startswith('parkWater'):   # the city's flat land polygon (y -0.06) runs under every pond and would hide water below it: water surfaces are raised to y -0.03
                wi = 0 if r['name'] == 'parkWater' else int(r['name'].split('_n')[1]) - 1
                zoff = (-0.03 - TJ['water'][wi]['y']) * 100.0
            a = spawn(unreal.StaticMeshActor, unreal.Vector(0, 0, zoff), label=r['name'], folder='Terrain/' + r['kind'])
            a.static_mesh_component.set_static_mesh(load(sp)); a.set_mobility(unreal.ComponentMobility.STATIC)
            if r['name'] == 'park' or r['name'].startswith(('mapLawns', 'coastLawn', 'parkWater')): a.tags = [unreal.Name('WHGround')]
            if r['kind'] in ('ground', 'water'): a.static_mesh_component.set_cast_shadow(False)   # flat surfaces: nothing to cast
            lite(a.static_mesh_component, indirect=True)   # world-space meshes: out of the distance-field scene, still lit by Lumen
            n += 1
        log('land: %d mesh actors' % n)
        if EAL.does_asset_exist(f'{PROD}/SM_park_rocks'):
            a = spawn(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), label='park_rocks', folder='Terrain/Props')
            a.static_mesh_component.set_static_mesh(load(f'{PROD}/SM_park_rocks')); a.set_mobility(unreal.ComponentMobility.STATIC); lite(a.static_mesh_component, indirect=True)
        if EAL.does_asset_exist(f'{PROD}/SM_shore_patch'):
            a = spawn(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), label='shore_patch', folder='Terrain/shore')
            a.static_mesh_component.set_static_mesh(load(f'{PROD}/SM_shore_patch')); a.set_mobility(unreal.ComponentMobility.STATIC)
            a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); lite(a.static_mesh_component, indirect=True)

    def _sec_tufts():
            # grass tufts: browser grass.js density / height mask, scattered by prep_terrain.py (x, z, yaw, width scale, height m), three wind classes, culled at 45 m
        tp = os.path.join(PREP, 'tufts.bin')
        if os.path.exists(tp) and EAL.does_asset_exist(f'{PROD}/SM_tuft'):
            import array
            buf = array.array('f'); buf.frombytes(open(tp, 'rb').read())
            recs = [buf[i:i + 5] for i in range(0, len(buf), 5)]          # x, z, yaw, width scale, height m
            classes = [('TuftLow', [r for r in recs if r[4] < 0.11]), ('TuftMid', [r for r in recs if 0.11 <= r[4] < 0.2]), ('TuftHigh', [r for r in recs if r[4] >= 0.2])]
            a = spawn(unreal.Actor, unreal.Vector(0, 0, 0), label='ISM_grass_tufts', folder='Terrain/Grass')
            gy = TJ['GY']['GRASS'] + 0.03   # + the 3 cm the park ground is raised
            for nm, S in classes:
                xs = [unreal.Transform(U(x, gy - 0.01, z), unreal.Rotator(0.0, 0.0, -math.degrees(yw)), unreal.Vector(w, w, h / 0.85)) for x, z, yw, w, h in S]
                hism(a, f'{PROD}/SM_tuft', xs, cull=4500, material=load(f'{MAT}/Inst/MI_{nm}'))
                log('tufts', nm, len(xs))

    def _sec_props():
        # instanced props: reeds + picnic blankets (matrix records [x,y,z,ry,sx,sy,sz,(r,g,b)]), park lamps inside the park (pool items {x,y,z,ry,s})
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

    def _sec_trees():
        # park woodland: one HISM per browser pool (full island item lists), aTintA / aTintB as custom data 0..5, per-pool LOD band in the material (see the trees step)
        nt = 0; counts = {}
        def pool_material(pool, d):
            """a material instance per pool: parent by pool kind, LOD band from the export"""
            b = pool_band(d); vec = {'band': (b[0], b[1], b[2], b[3])}
            nm = 'Pool_' + pool.replace('-', '_')
            if pool.startswith('ez-') and pool.endswith('-leaves'):
                rec = [p for p in MAN['protos'] if p['name'] == pool.replace('-', '_')][0]; ln = leaf_name(rec)
                m = mi(nm, 'M_TerrainLeaves', {'gain': 1.0}, vec)
                mel.set_material_instance_texture_parameter_value(m, 'tLeaf', load(f'{TEXD}/leaf_{ln}')); EAL.save_asset(f'{MAT}/Inst/MI_{nm}')
                return m
            if pool.startswith(('ez-', 'trunks-')): return mi(nm, 'M_TerrainBark', {'usevc': 1.0, 'roughp': 0.92}, dict(vec, tint=(0.33, 0.29, 0.25, 1.0)))
            if pool.endswith('-near'): return mi(nm, 'M_TerrainCards', {'gain': 1.0}, vec)
            if pool.endswith('-crownfar'): return mi(nm, 'M_TerrainCrown', {'gain': 1.0}, vec)
            return mi(nm, 'M_TerrainClump', {'gain': 1.0, 'bump': 1.0}, vec)
        order = sorted(INS.keys(), key=lambda k: (0 if k.startswith('ez-') else 1, k))
        for pool in order:
            d = INS[pool]
            if not POOL_RE.match(pool) or not d.get('items'): continue
            nmu = pool.replace('-', '_'); crownfar = pool.endswith('-crownfar')
            if crownfar:      # the city's own far-crown blob mesh (20-tri lobes); only drawn >= 520 m by the material band
                sp = None
                for suf in ['', '_v2', '_v3', '_v4', '_v5', '_v6']:
                    if EAL.does_asset_exist(f'/Game/City/Props/SM_{nmu}{suf}'): sp = f'/Game/City/Props/SM_{nmu}{suf}'
                if sp is None: sp = f'{TREED}/SM_{nmu}' if EAL.does_asset_exist(f'{TREED}/SM_{nmu}') else None
                if sp is None: log('no far-crown asset for', pool); continue
            else:
                sp = f'{TREED}/SM_{nmu}'
                if not EAL.does_asset_exist(sp): log('no mesh for', pool); continue
            tinted = pool.startswith(('ez-',)) and pool.endswith('leaves') or pool.startswith('trees-')
            l1 = '-l1-' in pool
            a = spawn(unreal.Actor, unreal.Vector(0, 0, 0), label='ISM_' + pool, folder='Terrain/Trees')
            c = add_component(a, unreal.HierarchicalInstancedStaticMeshComponent)
            c.set_static_mesh(load(sp))
            if tinted: c.set_editor_property('num_custom_data_floats', 6)
            try: c.set_material(0, pool_material(pool, d))
            except Exception as ex: log('WARN material', pool, str(ex)[:160])
            # per-instance cull distance: only a cost optimisation for pools that need no shadow / Lumen presence beyond their band (the band itself is the material clip)
            cull = None
            if pool.startswith('ez-'): cull = (4800 if l1 else 2500)
            elif pool in ('trunks-park', 'trunks-elm', 'trunks-conifer'): cull = 7200
            elif pool.endswith('-mid'): cull = 20000
            if cull:
                try: c.set_editor_property('instance_end_cull_distance', int(cull))
                except Exception as ex: log('WARN cull distance', str(ex)[:100])
            casts = not (pool.endswith(('-crown', '-crownfar', '-far')))       # browser: crown LODs and far trunks cast no shadows; cards / ez / near + mid trunks do
            c.set_cast_shadow(casts)
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            lite(c, indirect=(l1 or pool.endswith(('-crown', '-crownfar'))))   # the crown hulls (low poly) stand in for the canopy in Lumen's scene; cards / trunks / ez L0 stay out of it
            xs = []
            for it in d['items']:
                s_ = it.get('s', 1.0); s3 = it.get('s3') or [1, 1, 1]
                rot = unreal.Rotator(roll=math.degrees(it.get('rz', 0.0)), pitch=-math.degrees(it.get('rx', 0.0)), yaw=-math.degrees(it.get('ry', 0.0)))
                xs.append(unreal.Transform(U(it['x'], it['y'], it['z']), rot, unreal.Vector(s_ * s3[0], s_ * s3[2], s_ * s3[1])))
            ids = c.add_instances(xs, True, True)
            if tinted:
                for k, it in enumerate(d['items']):
                    e = it.get('e') or {}; ta = e.get('aTintA') or [0.15, 0.2, 0.08]; tb = e.get('aTintB') or ta
                    for j, v in enumerate(list(ta) + list(tb)): c.set_custom_data_value(k, j, float(v), False)
            nt += len(xs); counts[pool] = len(xs)
        log('park woodland instances', nt, 'in', len(counts), 'pools')

    for nm_, fn_ in (('meshes', _sec_meshes), ('tufts', _sec_tufts), ('props', _sec_props), ('trees', _sec_trees)): soft(nm_, fn_)
    return world

def city_geo_copy(src):
    """a private copy of the city geometry level in which the city's flat park ribbons / lawns and its ez-tree LOD1 park woodland are hidden in game (terrain supersedes them: tinted trees,
    LOD0, real ground); the original level (and the baseline maps VB_*) stay untouched"""
    dst = ROOT + '/City_Geo_T'
    if EAL.does_asset_exist(dst): return dst
    try:
        if not EAL.duplicate_asset(src, dst): raise RuntimeError('could not duplicate ' + src)
        unreal.EditorLoadingAndSavingUtils.load_map(dst)
        hid = 0
        for a in eas.get_all_level_actors():
            lb = a.get_actor_label()
            if lb.startswith(('ISM_ez_park', 'ISM_ez_elm', 'ISM_ez_conifer', 'ISM_trees_park_crownfar', 'ISM_trees_elm_crownfar', 'ISM_trees_conifer_crownfar')) or (isinstance(a, unreal.StaticMeshActor) and lb.startswith(('parkPaths', 'mapLawns'))):
                a.set_actor_hidden_in_game(True); hid += 1
        les.save_current_level()
        log('City_Geo_T: hid', hid, 'city actors (park ribbons / lawns / ez park trees)')
        return dst
    except Exception:
        log('city_geo_copy FAILED: falling back to the original city geometry level (the city park trees stay visible)'); traceback.print_exc()
        return src

def build_persistent(path):
    """the integrated Manhattan map (golden) + the terrain sublevel (the terrain ground sits 3 cm above the city's flat park ribbons / lawns, which stay untouched)"""
    MAPS = '/Game/Maps'; CITY_GEO = '/Game/Tests/City/City_Midtown_Geo'; BOXES = '/Game/Look/Look_Boxes'; RIG = '/Game/Look/Rigs/Look_Rig_golden'; ACTORS = MAPS + '/Manhattan_Actors'
    for need in (CITY_GEO, BOXES, RIG, ACTORS):
        if not EAL.does_asset_exist(need): raise RuntimeError('missing base content %s: run the base Manhattan build first (build_manhattan.py)' % need)
    CITY_GEO = city_geo_copy(CITY_GEO)
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

def build_views():
    """still maps for the shot list: golden Manhattan sublevels (+ Terrain_Land for V_*, without it for the baseline VB_*) + a shot camera (no game mode: the camera is the view)"""
    SH = json.load(open(os.path.join(WT, 'docs', 'night1', 'terrain', 'shots.json')))['shots']
    CITY_GEO = '/Game/Tests/City/City_Midtown_Geo'; BOXES = '/Game/Look/Look_Boxes'; RIG = '/Game/Look/Rigs/Look_Rig_golden'; ACTORS = '/Game/Maps/Manhattan_Actors'
    CITY_GEO_V = city_geo_copy(CITY_GEO)
    for sh in SH:
        for pre, land in (('V_', True), ('VB_', False)):
            path = ROOT + '/Maps/' + pre + sh['id']
            world = open_level(path)
            have = [l.get_path_name() for l in unreal.EditorLevelUtils.get_levels(world)]
            for lp in [CITY_GEO_V if land else CITY_GEO, BOXES, RIG, ACTORS] + ([ROOT + '/Terrain_Land'] if land else []):
                if not any(('/' + lp.split('/')[-1] + ':') in h or h.endswith(lp.split('/')[-1]) for h in have):
                    unreal.EditorLevelUtils.add_level_to_world(world, lp, unreal.LevelStreamingAlwaysLoaded)
            les.set_current_level_by_name(str(world.get_name()))
            p0 = unreal.Vector(*[v * 100.0 for v in sh['pos']]); t0 = unreal.Vector(*[v * 100.0 for v in sh['target']])
            d = unreal.Vector(t0.x - p0.x, t0.y - p0.y, t0.z - p0.z)
            rot = unreal.Rotator(roll=0.0, pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x)))
            ca = eas.spawn_actor_from_class(unreal.CameraActor, p0, rot)
            ca.set_actor_label('ShotCam_' + sh['id'])
            ca.camera_component.set_editor_property('field_of_view', sh.get('fov', 66))
            ca.camera_component.set_editor_property('constrain_aspect_ratio', False)
            ca.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.PLAYER0)
            unreal.EditorLoadingAndSavingUtils.save_map(world, path)
        log('view', sh['id'])

@step('map')
def _step_map():
    EAL.make_directory(ROOT + '/Maps')
    build_land(ROOT + '/Terrain_Land')
    unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), ROOT + '/Terrain_Land')
    log('Terrain_Land saved')
    build_persistent(ROOT + '/Maps/Manhattan_Terrain')
@step('views')
def _step_views(): build_views()
log('DONE')
