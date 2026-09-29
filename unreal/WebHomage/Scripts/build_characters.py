# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P2 Characters: idempotent rebuild of /Game/Characters and /Game/Tests/Characters from committed sources.
#   sources: public/assets/spiderman.glb, thug.glb, skins/*.glb, public/assets/tex/*, public/assets/enemies/*,
#            public/assets/city/npc/citizens.* + people.* (-> tools/ue_char/eval/export_citizens.sh FBX)
#   derived (git-ignored): tools/ue_char/prep_glbs.py (webp-free GLBs), tools/ue_char/extract_textures.py (PNGs),
#            suit PBR maps from tools/ue_char/suitmaps (art/night1/characters/suits/<suit>_{basecolor,normal_ogl,orm}.png)
#   run in the P2 editor: tools/ue_char/uebox.py unreal/WebHomage/Scripts/build_characters.py [--args '{"steps":"..."}']
#   or headless: UnrealEditor <uproject> -run=pythonscript -script=<this file> -unattended
# Steps: prep,clean,tex,mat,mesh,citizens,rename,abp,map   (default all)
import unreal, os, subprocess, time, glob

WT = '/Users/midir/sm2-n1/characters'
ART = WT + '/art/night1/characters'
GLB = '/Users/midir/sm2-n1/_scratch/characters/ueimport'
CIT = ART + '/export/citizens'
CITIZENS = ['03_white_tee', '12_sundress_mom', '13_construction_worker', '15_executive']
SUITS = ['Claude', 'Codex', 'Gemini', 'Kimi', 'Qwen']
try:
    ARGS  # noqa: F821  (set by uebox.py)
except NameError:
    import json
    ARGS = json.loads(os.environ.get('CHAR_BUILD_ARGS', '{}'))
STEPS = set((ARGS.get('steps') or 'prep,clean,tex,mat,mesh,citizens,rename,abp,map').split(','))
ROOT, TESTS = '/Game/Characters', '/Game/Tests/Characters'
EAL = unreal.EditorAssetLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
T0 = time.time()
def log(*a): print('[build_characters %5.0fs]' % (time.time() - T0), *a)
def load(p): return unreal.load_asset(p)

# ------------------------------------------------------------------------------------------------ prep (outside UE)
if 'prep' in STEPS:
    subprocess.run(['python3', WT + '/tools/ue_char/prep_glbs.py'], check=True, capture_output=True)
    subprocess.run(['python3', WT + '/tools/ue_char/extract_textures.py'], check=True, capture_output=True)
    if not all(os.path.exists('%s/%s.fbx' % (CIT, c)) for c in CITIZENS):
        subprocess.run(['bash', WT + '/tools/ue_char/eval/export_citizens.sh'] + CITIZENS, check=True, capture_output=True)
    log('prep ok')

if 'clean' in STEPS:
    for d in (ROOT, TESTS):
        if EAL.does_directory_exist(d):
            try: EAL.delete_directory(d)
            except Exception as e: log('clean: delete failed (headless script wipes on disk first)', str(e)[:120])
    log('clean ok')

# ------------------------------------------------------------------------------------------------ textures
def import_tex(png, dest, name, kind):
    """kind: srgb | linear | normal_gl (OpenGL +Y, flipped to UE) | normal_dx"""
    t = unreal.AssetImportTask(); t.filename = png; t.destination_path = dest; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    AT.import_asset_tasks([t])
    tex = load(dest + '/' + name)
    if kind.startswith('normal'):
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property('srgb', False)
        tex.set_editor_property('flip_green_channel', kind == 'normal_gl')
    elif kind == 'linear':
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
        tex.set_editor_property('srgb', False)
    else:
        tex.set_editor_property('srgb', True)
    tex.set_editor_property('lod_group', unreal.TextureGroup.TEXTUREGROUP_CHARACTER)
    return tex

def suit_maps(s):
    """Prefer the suitmaps bake (basecolor/normal_ogl/orm); fall back to what the GLB carries."""
    lo = s.lower(); d = ART + '/suits'
    bc = d + '/%s_basecolor.png' % lo if os.path.exists(d + '/%s_basecolor.png' % lo) else d + '/%s/tex/%sSuit_basecolor.png' % (s, s)
    n = d + '/%s_normal_ogl.png' % lo if os.path.exists(d + '/%s_normal_ogl.png' % lo) else None
    orm = d + '/%s_orm.png' % lo if os.path.exists(d + '/%s_orm.png' % lo) else None
    return bc, n, orm

if 'tex' in STEPS:
    H = ART + '/hero/tex'; TH = ART + '/thug/tex'
    import_tex(H + '/suit_basecolor.png', ROOT + '/Hero/Textures', 'T_Hero_BaseColor', 'srgb')
    import_tex(H + '/suit_normal.png', ROOT + '/Hero/Textures', 'T_Hero_Normal', 'normal_gl')   # glTF = OpenGL (curl test)
    import_tex(H + '/suit_orm.png', ROOT + '/Hero/Textures', 'T_Hero_ORM', 'linear')
    # fabric micro-normal (browser detail maps; curl test says DirectX convention -> no flip)
    import_tex(ART + '/shared/white.png', ROOT + '/Shared/Textures', 'T_White_Masks', 'linear')
    import_tex(WT + '/public/assets/tex/suit_weave_knit.png', ROOT + '/Shared/Textures', 'T_Fabric_Knit_N', 'normal_dx')
    import_tex(WT + '/public/assets/tex/suit_weave_hex.png', ROOT + '/Shared/Textures', 'T_Fabric_Hex_N', 'normal_dx')
    for v in ('', '_b', '_c'):
        import_tex(TH + '/thug_basecolor%s.png' % v, ROOT + '/Thug/Textures', 'T_Thug_BaseColor' + v.upper(), 'srgb')
    import_tex(TH + '/brute_basecolor.png', ROOT + '/Thug/Textures', 'T_Brute_BaseColor', 'srgb')
    import_tex(TH + '/thug_normal.png', ROOT + '/Thug/Textures', 'T_Thug_Normal', 'normal_gl')
    import_tex(TH + '/thug_orm.png', ROOT + '/Thug/Textures', 'T_Thug_ORM', 'linear')
    for s in SUITS:
        bc, n, orm = suit_maps(s)
        import_tex(bc, ROOT + '/Suits/%s/Textures' % s, 'T_Suit_%s_BaseColor' % s, 'srgb')
        if n: import_tex(n, ROOT + '/Suits/%s/Textures' % s, 'T_Suit_%s_Normal' % s, 'normal_gl')
        if orm: import_tex(orm, ROOT + '/Suits/%s/Textures' % s, 'T_Suit_%s_ORM' % s, 'linear')
    for c in CITIZENS:
        import_tex('%s/%s_basecolor.png' % (CIT, c), ROOT + '/Citizens/Textures', 'T_Cit_%s_BaseColor' % c, 'srgb')
    EAL.save_directory(ROOT, only_if_is_dirty=True, recursive=True)
    log('tex ok')

# ------------------------------------------------------------------------------------------------ materials
def new_material(path, name, skeletal=False):
    if EAL.does_asset_exist(path + '/' + name):
        EAL.delete_asset(path + '/' + name)
    m = AT.create_asset(name, path, unreal.Material, unreal.MaterialFactoryNew())
    if skeletal:   # -game can't add usage flags at runtime: without this the default material is drawn
        m.set_editor_property('used_with_skeletal_mesh', True)
    return m

def E(m, cls, x, y):
    return MEL.create_material_expression(m, cls, x, y)

def tex_param(m, name, default, stype, x, y, uv=None):
    e = E(m, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
    e.set_editor_property('parameter_name', name)
    e.set_editor_property('texture', load(default))
    e.set_editor_property('sampler_type', stype)
    if uv is not None:
        MEL.connect_material_expressions(uv, '', e, 'UVs')
    return e

def scalar(m, name, v, x, y):
    e = E(m, unreal.MaterialExpressionScalarParameter, x, y); e.set_editor_property('parameter_name', name); e.set_editor_property('default_value', v); return e

def vector(m, name, v, x, y):
    e = E(m, unreal.MaterialExpressionVectorParameter, x, y); e.set_editor_property('parameter_name', name); e.set_editor_property('default_value', unreal.LinearColor(*v)); return e

def build_suit_master():
    """M_Char_Suit: basecolor x tint, ORM (or constants), macro normal + tiled fabric micro-normal
    (BlendAngleCorrectedNormals), Cloth shading model for a fabric sheen (fuzz colour + cloth amount)."""
    m = new_material(ROOT + '/Shared/Materials', 'M_Char_Suit', skeletal=True)
    m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_CLOTH)
    ST = unreal.MaterialSamplerType
    bc = tex_param(m, 'BaseColor', '/Engine/EngineResources/WhiteSquareTexture', ST.SAMPLERTYPE_COLOR, -900, -300)
    tint = vector(m, 'Tint', (1, 1, 1, 1), -900, -520)
    bcm = E(m, unreal.MaterialExpressionMultiply, -600, -350)
    MEL.connect_material_expressions(bc, 'RGB', bcm, 'A'); MEL.connect_material_expressions(tint, 'RGB', bcm, 'B')
    MEL.connect_material_property(bcm, '', unreal.MaterialProperty.MP_BASE_COLOR)
    # ORM switch
    orm = tex_param(m, 'ORM', ROOT + '/Shared/Textures/T_White_Masks', ST.SAMPLERTYPE_MASKS, -900, 0)
    rs = scalar(m, 'RoughnessScale', 1.0, -900, 250); ro = scalar(m, 'Roughness', 0.7, -900, 330)
    rmul = E(m, unreal.MaterialExpressionMultiply, -600, 60)
    MEL.connect_material_expressions(orm, 'G', rmul, 'A'); MEL.connect_material_expressions(rs, '', rmul, 'B')
    sw_r = E(m, unreal.MaterialExpressionStaticSwitchParameter, -350, 60); sw_r.set_editor_property('parameter_name', 'HasORM')
    MEL.connect_material_expressions(rmul, '', sw_r, 'True'); MEL.connect_material_expressions(ro, '', sw_r, 'False')
    MEL.connect_material_property(sw_r, '', unreal.MaterialProperty.MP_ROUGHNESS)
    one = E(m, unreal.MaterialExpressionConstant, -600, 200); one.set_editor_property('r', 1.0)
    zero = E(m, unreal.MaterialExpressionConstant, -600, 260); zero.set_editor_property('r', 0.0)
    sw_ao = E(m, unreal.MaterialExpressionStaticSwitchParameter, -350, 180); sw_ao.set_editor_property('parameter_name', 'HasORM')
    MEL.connect_material_expressions(orm, 'R', sw_ao, 'True'); MEL.connect_material_expressions(one, '', sw_ao, 'False')
    MEL.connect_material_property(sw_ao, '', unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    sw_m = E(m, unreal.MaterialExpressionStaticSwitchParameter, -350, 300); sw_m.set_editor_property('parameter_name', 'HasORM')
    MEL.connect_material_expressions(orm, 'B', sw_m, 'True'); MEL.connect_material_expressions(zero, '', sw_m, 'False')
    MEL.connect_material_property(sw_m, '', unreal.MaterialProperty.MP_METALLIC)
    # normals
    nrm = tex_param(m, 'Normal', '/Engine/EngineMaterials/FlatNormal', ST.SAMPLERTYPE_NORMAL, -900, 450)
    uv = E(m, unreal.MaterialExpressionTextureCoordinate, -1300, 700)
    til = scalar(m, 'DetailTiling', 60.0, -1300, 800)
    uvm = E(m, unreal.MaterialExpressionMultiply, -1100, 720)
    MEL.connect_material_expressions(uv, '', uvm, 'A'); MEL.connect_material_expressions(til, '', uvm, 'B')
    det = tex_param(m, 'DetailNormal', '/Engine/EngineMaterials/FlatNormal', ST.SAMPLERTYPE_NORMAL, -900, 700, uv=uvm)
    ds = scalar(m, 'DetailStrength', 0.5, -900, 950)
    ap = E(m, unreal.MaterialExpressionAppendVector, -700, 900)
    one1 = E(m, unreal.MaterialExpressionConstant, -900, 1030); one1.set_editor_property('r', 1.0)
    ap2 = E(m, unreal.MaterialExpressionAppendVector, -600, 950)
    MEL.connect_material_expressions(ds, '', ap, 'A'); MEL.connect_material_expressions(ds, '', ap, 'B')
    MEL.connect_material_expressions(ap, '', ap2, 'A'); MEL.connect_material_expressions(one1, '', ap2, 'B')
    dmul = E(m, unreal.MaterialExpressionMultiply, -450, 750)
    MEL.connect_material_expressions(det, 'RGB', dmul, 'A'); MEL.connect_material_expressions(ap2, '', dmul, 'B')
    blend = E(m, unreal.MaterialExpressionMaterialFunctionCall, -250, 500)
    blend.set_editor_property('material_function', load('/Engine/Functions/Engine_MaterialFunctions02/Utility/BlendAngleCorrectedNormals'))
    MEL.connect_material_expressions(nrm, 'RGB', blend, 'BaseNormal')
    MEL.connect_material_expressions(dmul, '', blend, 'AdditionalNormal')
    MEL.connect_material_property(blend, '', unreal.MaterialProperty.MP_NORMAL)
    # cloth sheen
    fz = vector(m, 'FuzzColor', (0.55, 0.45, 0.45, 1), -350, -600)
    fzm = E(m, unreal.MaterialExpressionMultiply, -150, -560)
    MEL.connect_material_expressions(fz, 'RGB', fzm, 'A'); MEL.connect_material_expressions(bcm, '', fzm, 'B')
    # 'Cloth' input (CustomData0) is not exposed to Python's MaterialProperty enum and defaults to 1, so the sheen
    # amount is carried by the fuzz colour: fuzz = FuzzColor * basecolor * Cloth
    cl = scalar(m, 'Cloth', 0.6, -150, -420)
    fzc = E(m, unreal.MaterialExpressionMultiply, 50, -520)
    MEL.connect_material_expressions(fzm, '', fzc, 'A'); MEL.connect_material_expressions(cl, '', fzc, 'B')
    MEL.connect_material_property(fzc, '', unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
    spec = scalar(m, 'Specular', 0.5, -150, -330)
    MEL.connect_material_property(spec, '', unreal.MaterialProperty.MP_SPECULAR)
    MEL.recompile_material(m)
    try: log('M_Char_Suit compile errors:', list(MEL.get_material_compile_errors(m)) if hasattr(MEL, 'get_material_compile_errors') else 'n/a')
    except Exception as e: log('compile error query failed', e)
    return m

def build_simple(name, shading=None, emissive=False):
    m = new_material(ROOT + '/Shared/Materials', name, skeletal=True)
    c = vector(m, 'Color', (0.8, 0.8, 0.8, 1), -500, -200)
    MEL.connect_material_property(c, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(scalar(m, 'Roughness', 0.3, -500, 0), '', unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(scalar(m, 'Metallic', 0.0, -500, 100), '', unreal.MaterialProperty.MP_METALLIC)
    MEL.connect_material_property(scalar(m, 'Specular', 0.5, -500, 200), '', unreal.MaterialProperty.MP_SPECULAR)
    if emissive:
        em = E(m, unreal.MaterialExpressionMultiply, -250, 300)
        MEL.connect_material_expressions(c, 'RGB', em, 'A'); MEL.connect_material_expressions(scalar(m, 'Emissive', 0.0, -500, 350), '', em, 'B')
        MEL.connect_material_property(em, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m)
    return m

def mi(name, path, parent, tex=None, scal=None, vec=None, switches=None):
    full = path + '/' + name
    if EAL.does_asset_exist(full): EAL.delete_asset(full)
    i = AT.create_asset(name, path, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(i, parent)
    for k, v in (tex or {}).items(): MEL.set_material_instance_texture_parameter_value(i, k, load(v))
    for k, v in (scal or {}).items(): MEL.set_material_instance_scalar_parameter_value(i, k, v)
    for k, v in (vec or {}).items(): MEL.set_material_instance_vector_parameter_value(i, k, unreal.LinearColor(*v))
    for k, v in (switches or {}).items(): MEL.set_material_instance_static_switch_parameter_value(i, k, v)
    MEL.update_material_instance(i)
    return i

def build_ground_materials():
    out = {}
    for n, col, r in (('M_Env_Asphalt', (0.05, 0.05, 0.055, 1), 0.85), ('M_Env_Sidewalk', (0.32, 0.31, 0.29, 1), 0.8),
                      ('M_Env_Brick', (0.28, 0.12, 0.08, 1), 0.85), ('M_Env_Stone', (0.45, 0.42, 0.37, 1), 0.75),
                      ('M_Env_Glass', (0.04, 0.05, 0.06, 1), 0.08), ('M_Env_Paint', (0.9, 0.85, 0.2, 1), 0.6)):
        m = new_material(TESTS + '/Materials', n)
        MEL.connect_material_property(vector(m, 'Color', col, -400, -100), 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
        MEL.connect_material_property(scalar(m, 'Roughness', r, -400, 50), '', unreal.MaterialProperty.MP_ROUGHNESS)
        MEL.recompile_material(m); out[n] = m
    return out

if 'mat' in STEPS:
    suit = build_suit_master()
    lens = build_simple('M_Char_Lens', emissive=True)
    lensf = build_simple('M_Char_LensFrame')
    MP = ROOT + '/Shared/Materials'
    mi('MI_Hero_Suit', ROOT + '/Hero/Materials', suit,
       tex={'BaseColor': ROOT + '/Hero/Textures/T_Hero_BaseColor', 'ORM': ROOT + '/Hero/Textures/T_Hero_ORM',
            'Normal': ROOT + '/Hero/Textures/T_Hero_Normal', 'DetailNormal': ROOT + '/Shared/Textures/T_Fabric_Knit_N'},
       scal={'DetailTiling': 48.0, 'DetailStrength': 0.6, 'Cloth': 0.55}, switches={'HasORM': True})
    mi('MI_Hero_Lens', ROOT + '/Hero/Materials', lens, scal={'Roughness': 0.12, 'Specular': 0.9, 'Emissive': 0.04}, vec={'Color': (0.82, 0.84, 0.86, 1)})
    mi('MI_Hero_LensFrame', ROOT + '/Hero/Materials', lensf, scal={'Roughness': 0.35}, vec={'Color': (0.02, 0.02, 0.025, 1)})
    th = {'Normal': ROOT + '/Thug/Textures/T_Thug_Normal', 'ORM': ROOT + '/Thug/Textures/T_Thug_ORM'}
    for v, t in (('', 'T_Thug_BaseColor'), ('_B', 'T_Thug_BaseColor_B'), ('_C', 'T_Thug_BaseColor_C'), ('Brute', 'T_Brute_BaseColor')):
        n = 'MI_Brute' if v == 'Brute' else 'MI_Thug' + v
        mi(n, ROOT + '/Thug/Materials', suit, tex=dict(th, BaseColor=ROOT + '/Thug/Textures/' + t), scal={'Cloth': 0.3, 'DetailStrength': 0.0}, switches={'HasORM': True})
    for s in SUITS:
        P = ROOT + '/Suits/%s/Textures/T_Suit_%s_' % (s, s)
        tex = {'BaseColor': P + 'BaseColor', 'DetailNormal': ROOT + '/Shared/Textures/T_Fabric_Knit_N'}
        has_orm = EAL.does_asset_exist(P + 'ORM')
        if EAL.does_asset_exist(P + 'Normal'): tex['Normal'] = P + 'Normal'
        if has_orm: tex['ORM'] = P + 'ORM'
        mi('MI_Suit_' + s, ROOT + '/Suits/%s/Materials' % s, suit, tex=tex, scal={'Roughness': 0.6, 'DetailTiling': 48.0, 'DetailStrength': 0.5, 'Cloth': 0.5}, switches={'HasORM': has_orm})
    for c in CITIZENS:
        mi('MI_Cit_' + c, ROOT + '/Citizens/Materials', suit, tex={'BaseColor': ROOT + '/Citizens/Textures/T_Cit_%s_BaseColor' % c},
           scal={'Roughness': 0.8, 'Cloth': 0.0, 'DetailStrength': 0.0}, switches={'HasORM': False})
    build_ground_materials()
    EAL.save_directory(ROOT, only_if_is_dirty=True, recursive=True)
    EAL.save_directory(TESTS, only_if_is_dirty=True, recursive=True)
    log('mat ok')

# ------------------------------------------------------------------------------------------------ meshes (Interchange glTF)
def pipeline(skeleton=None, anims=True, physics=True):
    p = unreal.InterchangeGenericAssetsPipeline()
    mp = p.get_editor_property('mesh_pipeline')
    mp.set_editor_property('build_nanite', False)
    mp.set_editor_property('create_physics_asset', physics and skeleton is None)
    mp.set_editor_property('import_static_meshes', False)
    mp.set_editor_property('use_high_precision_skin_weights', True)
    cm = p.get_editor_property('common_meshes_properties')
    cm.set_editor_property('recompute_normals', False)        # keep authored normals
    cm.set_editor_property('recompute_tangents', True)        # hero GLB has no TANGENT -> MikkTSpace
    cm.set_editor_property('use_mikk_t_space', True)
    cm.set_editor_property('use_high_precision_tangent_basis', True)
    cm.set_editor_property('use_full_precision_u_vs', True)
    if skeleton:
        p.get_editor_property('common_skeletal_meshes_and_animations_properties').set_editor_property('skeleton', load(skeleton))
    ap = p.get_editor_property('animation_pipeline')
    ap.set_editor_property('import_animations', anims)
    ap.set_editor_property('custom_bone_animation_sample_rate', 30)   # source keys are exactly 1/30 s
    mat = p.get_editor_property('material_pipeline')
    mat.set_editor_property('import_materials', False)
    mat.get_editor_property('texture_pipeline').set_editor_property('import_textures', False)
    return p

def do_import(path, dest, **kw):
    # AssetImportTask + pipeline object as options. (InterchangeManager.import_asset only ever completed the
    # first import of a session here, UE 5.8.3 2026-09-29; AssetImportTask imports complete synchronously.)
    t = unreal.AssetImportTask(); t.filename = path; t.destination_path = dest
    t.automated = True; t.replace_existing = True; t.save = False
    stack = unreal.InterchangePipelineStackOverride()   # AssetImportTask only honours Interchange pipelines via this wrapper
    stack.add_pipeline(pipeline(**kw))
    t.options = stack
    AT.import_asset_tasks([t])
    return list(t.imported_object_paths)

def set_slots(mesh_path, mapping):
    sk = load(mesh_path)
    out = []
    for sm in sk.get_editor_property('materials'):   # array elements come back as copies: rebuild the list
        slot = str(sm.get_editor_property('material_slot_name'))
        tgt = mapping.get(slot, mapping.get('*'))
        if tgt:
            sm.set_editor_property('material_interface', load(tgt))
        out.append(sm)
    sk.set_editor_property('materials', out)
    EAL.save_asset(mesh_path)
    return [(str(m.get_editor_property('material_slot_name')), m.get_editor_property('material_interface').get_name()) for m in load(mesh_path).get_editor_property('materials')]

# Interchange gotcha (UE 5.8.3, seen 2026-09-29): InterchangeManager.import_asset(+override_pipelines) only ever
# completed the FIRST import of a session; AssetImportTask with an InterchangePipelineStackOverride completes every
# import synchronously. Final names are chosen at the source (prep_glbs.py writes SK_*.glb); only clips get renamed.
HERO_SKEL = ROOT + '/Hero/SK_Hero_Skeleton'
CIT_SKEL = ROOT + '/Citizens/SK_Citizen_Skeleton'
HERO_PHYS = ROOT + '/Hero/SK_Hero_PhysicsAsset'
CIT_TMP = '/Users/midir/sm2-n1/_scratch/characters/ueimport/citizens'
MESHES = [('SK_Hero', ROOT + '/Hero', None, True), ('SK_Thug', ROOT + '/Thug', HERO_SKEL, True)] + \
         [('SK_Suit_' + s, ROOT + '/Suits/' + s, HERO_SKEL, False) for s in SUITS]
if 'mesh' in STEPS:
    for name, dest, skel, anims in MESHES:
        got = do_import('%s/%s.glb' % (GLB, name), dest, skeleton=skel, anims=anims)
        log('imported', name, len(got), [g for g in got if 'Anim' not in g][:4])
if 'citizens' in STEPS:
    import shutil
    os.makedirs(CIT_TMP, exist_ok=True)
    for i, c in enumerate(CITIZENS):
        f = '%s/SK_Citizen%s.fbx' % (CIT_TMP, '' if i == 0 else '_' + c)
        shutil.copyfile('%s/%s.fbx' % (CIT, c), f)
        do_import(f, ROOT + '/Citizens', skeleton=None if i == 0 else CIT_SKEL, anims=(i == 0), physics=False)
        log('imported citizen', c, len(EAL.list_assets(ROOT + '/Citizens', recursive=False)))

def find_class(folder, cls):
    return [p.split('.')[0] for p in EAL.list_assets(folder, recursive=True)
            if '/Anims/' not in p and isinstance(load(p.split('.')[0]), cls)]

def rename_anims(folder, prefix, out_prefix):
    """glTF/FBX imports may land in <dest>/<file>/<Type>/ subfolders: flatten to <folder>/SK_*, <folder>/Anims/A_*."""
    for p in find_class(folder, unreal.AnimSequence):
        base = p.split('/')[-1]
        clip = base[len(prefix):].lstrip('_') if base.startswith(prefix) else base
        if not EAL.rename_asset(p, '%s/Anims/%s%s' % (folder, out_prefix, clip)): log('RENAME FAIL', p)
    for cls, suffix in ((unreal.SkeletalMesh, ''), (unreal.Skeleton, ''), (unreal.PhysicsAsset, '')):
        for p in find_class(folder, cls):
            if p.rsplit('/', 1)[0] != folder:
                if not EAL.rename_asset(p, folder + '/' + p.split('/')[-1]): log('RENAME FAIL', p)

if 'rename' in STEPS:
    for s_ in SUITS: rename_anims(ROOT + '/Suits/' + s_, 'SK_Suit_' + s_, 'A_Suit_')
    rename_anims(ROOT + '/Hero', 'SK_Hero', 'A_Hero_')
    rename_anims(ROOT + '/Thug', 'SK_Thug', 'A_Thug_')
    rename_anims(ROOT + '/Citizens', 'SK_Citizen', 'A_Citizen_')
    # the first citizen FBX names the mesh SK_Citizen: give it its citizen name like the others
    if EAL.does_asset_exist(ROOT + '/Citizens/SK_Citizen'):
        EAL.rename_asset(ROOT + '/Citizens/SK_Citizen', ROOT + '/Citizens/SK_Citizen_' + CITIZENS[0])
    log('hero slots', set_slots(ROOT + '/Hero/SK_Hero', {'SpiderSuit': ROOT + '/Hero/Materials/MI_Hero_Suit',
        'Lens': ROOT + '/Hero/Materials/MI_Hero_Lens', 'LensFrame': ROOT + '/Hero/Materials/MI_Hero_LensFrame'}))
    set_slots(ROOT + '/Thug/SK_Thug', {'*': ROOT + '/Thug/Materials/MI_Thug'})
    load(ROOT + '/Thug/SK_Thug').set_editor_property('physics_asset', load(HERO_PHYS))
    for s in SUITS:
        set_slots(ROOT + '/Suits/%s/SK_Suit_%s' % (s, s), {'*': ROOT + '/Suits/%s/Materials/MI_Suit_%s' % (s, s)})
        load(ROOT + '/Suits/%s/SK_Suit_%s' % (s, s)).set_editor_property('physics_asset', load(HERO_PHYS))
    for c in CITIZENS:
        set_slots(ROOT + '/Citizens/SK_Citizen_' + c, {'*': ROOT + '/Citizens/Materials/MI_Cit_' + c})
    EAL.save_directory(ROOT, only_if_is_dirty=True, recursive=True)
    log('rename ok', sorted(p.split('.')[-1] for p in EAL.list_assets(ROOT, recursive=True) if '/Anims/' not in p and 'Textures' not in p and 'Materials' not in p))

# ------------------------------------------------------------------------------------------------ AnimBPs (children of UWHCharAnimInstance)
def make_abp(name, path, skel, idle, loco, jump=None, fall=None, land=None):
    full = path + '/' + name
    if EAL.does_asset_exist(full): EAL.delete_asset(full)
    f = unreal.AnimBlueprintFactory()
    f.set_editor_property('target_skeleton', load(skel))
    f.set_editor_property('parent_class', unreal.WHCharAnimInstance)
    bp = AT.create_asset(name, path, unreal.AnimBlueprint, f)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    cdo = unreal.get_default_object(bp.generated_class())
    samples = []
    for clip, spd in loco:
        s = unreal.WHLocoSample(); s.set_editor_property('clip', load(clip)); s.set_editor_property('speed', spd); samples.append(s)
    cdo.set_editor_property('loco', samples)
    cdo.set_editor_property('idle', load(idle))
    if jump: cdo.set_editor_property('jump_up', load(jump))
    if fall: cdo.set_editor_property('fall', load(fall))
    if land: cdo.set_editor_property('land', load(land))
    EAL.save_asset(full)
    return bp

if 'abp' in STEPS:
    HA = ROOT + '/Hero/Anims/A_Hero_'
    # natural speeds (cm/s) = browser LOCO anchors (src/player/anim/animator.js: walk 1.6, jog 4.5, run 8.5, sprint 14 m/s)
    hero_loco = [(HA + 'walk', 160.0), (HA + 'jog', 450.0), (HA + 'run', 850.0), (HA + 'sprint', 1400.0)]
    make_abp('ABP_Hero_Lineup', ROOT + '/Hero', HERO_SKEL, HA + 'idle', hero_loco, HA + 'jump', HA + 'fall', HA + 'landLight')
    make_abp('ABP_Thug_Lineup', ROOT + '/Thug', HERO_SKEL, ROOT + '/Thug/Anims/A_Thug_thugIdle', hero_loco, HA + 'jump', HA + 'fall', HA + 'landLight')
    CA = ROOT + '/Citizens/Anims/A_Citizen_'
    # crowd clips: walk stride 1.1543 m / (32/30 s) = 1.08 m/s, run stride 3.4181 m / (19/30 s) = 5.40 m/s (people.json)
    make_abp('ABP_Citizen_Lineup', ROOT + '/Citizens', CIT_SKEL, CA + 'idle', [(CA + 'walk', 108.0), (CA + 'run', 540.0)])
    log('abp ok')

# ------------------------------------------------------------------------------------------------ test map
def spawn(cls, loc, rot=(0, 0, 0), label=None):
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator(roll=rot[2], pitch=rot[1], yaw=rot[0]))
    if label: a.set_actor_label(label)
    return a

def box(loc, scale, mat, label):
    a = spawn(unreal.StaticMeshActor, loc)
    a.static_mesh_component.set_static_mesh(load('/Engine/BasicShapes/Cube'))
    a.set_actor_scale3d(unreal.Vector(*scale)); a.set_actor_label(label)
    a.static_mesh_component.set_material(0, load(TESTS + '/Materials/' + mat))
    return a

def walker(label, mesh, abp, loc, mode, speed, rx=0, ry=0, start=0, hop=0, scale=1.0, mat=None, yaw=0):
    a = spawn(unreal.WHCharLoopWalker, loc, (yaw, 0, 0), label)
    m = a.get_editor_property('mesh')
    m.set_skeletal_mesh_asset(load(mesh))
    m.set_editor_property('animation_mode', unreal.AnimationMode.ANIMATION_BLUEPRINT)
    m.set_anim_instance_class(load(abp).generated_class())
    m.set_relative_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=MESH_YAW), False, False)
    if mat: m.set_material(0, load(mat))
    a.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    for k, v in (('mode', mode), ('speed', speed), ('radius_x', rx), ('radius_y', ry), ('start_angle', start), ('hop_interval', hop)):
        a.set_editor_property(k, v)
    return a

MESH_YAW = float(ARGS.get('mesh_yaw', -90.0))   # glTF +Z forward -> UE: mesh faces +Y after import; walker moves along +X
if 'map' in STEPS:
    MAP = TESTS + '/Char_Lineup'
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.new_level('/Temp/Char_Lineup_Build_%d' % int(time.time()))   # built in a temp level, then saved over MAP (idempotent)
    W = unreal.WHWalkerMode
    # light: neutral daylight
    sun = spawn(unreal.DirectionalLight, (0, 0, 1000), (-35, -40, 0), 'Sun')
    sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sc.set_editor_property('intensity', 8.0); sc.set_editor_property('atmosphere_sun_light', True)
    spawn(unreal.SkyAtmosphere, (0, 0, 0), label='SkyAtmosphere')
    sky = spawn(unreal.SkyLight, (0, 0, 300), label='SkyLight')
    skc = sky.get_component_by_class(unreal.SkyLightComponent); skc.set_editor_property('real_time_capture', True); skc.set_editor_property('mobility', unreal.ComponentMobility.MOVABLE)
    spawn(unreal.ExponentialHeightFog, (0, 0, 0), label='Fog')
    ppv = spawn(unreal.PostProcessVolume, (0, 0, 0), label='Post'); ppv.set_editor_property('unbound', True)
    spawn(unreal.PlayerStart, (-6000, -6000, 120), label='PlayerStart_OffStage')
    # street backdrop: asphalt road along X, sidewalk + curb, a row of facades behind (+Y), crosswalk stripes
    box((0, 0, -10), (80, 30, 0.2), 'M_Env_Asphalt', 'Road')
    box((0, 1900, 0), (80, 8, 0.3), 'M_Env_Sidewalk', 'Sidewalk_N')
    box((0, -1900, 0), (80, 8, 0.3), 'M_Env_Sidewalk', 'Sidewalk_S')
    for i in range(10):
        x = -3600 + i * 800
        mat = ('M_Env_Brick', 'M_Env_Stone')[i % 2]
        h = 1800 + (i * 530) % 1500
        box((x, 2700, h / 2), (7.6, 8, h / 100), mat, 'Facade_%d' % i)
        for f in range(1, int(h / 350)):
            box((x, 2295, f * 350), (5.5, 0.1, 1.6), 'M_Env_Glass', 'Win_%d_%d' % (i, f))
        box((x, -2700, h / 2), (7.6, 8, h / 100), ('M_Env_Stone', 'M_Env_Brick')[i % 2], 'FacadeS_%d' % i)
    for k in range(8):
        box((1900, -600 + k * 170, -8), (4, 0.7, 0.05), 'M_Env_Paint', 'Crosswalk_%d' % k)
    # characters
    H = ROOT + '/Hero/'; T = ROOT + '/Thug/'
    hero = walker('Hero_Loop', H + 'SK_Hero', H + 'ABP_Hero_Lineup', (0, 0, 0), W.LOOP, 560.0, 900, 420, 0, hop=5.0)
    hero_tt = walker('Hero_Turntable', H + 'SK_Hero', H + 'ABP_Hero_Lineup', (-2400, -900, 0), W.TURNTABLE, 160.0)
    thug = walker('Thug_Walk', T + 'SK_Thug', T + 'ABP_Thug_Lineup', (0, 1100, 0), W.LOOP, 150.0, 500, 250, 90)
    brute = walker('Brute_Walk', T + 'SK_Thug', T + 'ABP_Thug_Lineup', (0, 1100, 0), W.LOOP, 130.0, 500, 250, 270, scale=1.24, mat=T + 'Materials/MI_Brute')
    cits = []
    for i, c in enumerate(CITIZENS):
        cits.append(walker('Citizen_' + c, ROOT + '/Citizens/SK_Citizen_' + c, ROOT + '/Citizens/ABP_Citizen_Lineup', (600, -1250, 0), W.LOOP,
                           105.0 + 10 * i, 1300, 380, i * 90.0))
    cit_center = spawn(unreal.TargetPoint, (600, -1250, 0), label='CitizensCenter')
    suits = []
    for i, s in enumerate(SUITS):
        suits.append(walker('Suit_' + s, ROOT + '/Suits/%s/SK_Suit_%s' % (s, s), H + 'ABP_Hero_Lineup', (-2400, 300 + i * 260, 0), W.TURNTABLE, 160.0, start=0))
    suit_center = spawn(unreal.TargetPoint, (-2400, 820, 0), label='SuitsCenter')
    # capture director (shot list; times are cumulative in CAPTURE notes)
    d = spawn(unreal.WHCharShowDirector, (0, 0, 0), label='CaptureDirector')
    K = unreal.WHShotKind
    def shot(t, kind, dur, dist, aim=100.0, camh=10.0, fov=40.0, orbit=40.0, az=0.0, wl=(0, 0, 0), label=''):
        s = unreal.WHShot()
        for k, v in (('target', t), ('kind', kind), ('duration', dur), ('distance', dist), ('aim_height', aim), ('cam_height', camh),
                     ('fov', fov), ('orbit_deg_per_sec', orbit), ('azimuth', az), ('world_location', unreal.Vector(*wl)), ('label', label)):
            s.set_editor_property(k, v)
        return s
    shots = [shot(hero_tt, K.ORBIT, 6, 340, 100, 20, 40, 45, 0, label='hero moving turntable'),
             shot(hero, K.SIDE, 5, 520, 95, 0, 40, label='hero run side'),
             shot(hero, K.THREE_QUARTER, 5, 460, 95, 25, 40, label='hero run 3/4'),
             shot(hero_tt, K.CLOSEUP, 4, 95, 135, 5, 30, label='suit fabric close-up (chest)'),
             shot(thug, K.THREE_QUARTER, 4, 380, 95, 15, 40, label='thug walk 3/4'),
             shot(brute, K.SIDE, 3, 480, 110, 10, 40, label='brute walk side'),
             shot(cit_center, K.WIDE, 5, 0, 90, 0, 45, wl=(1900, -2150, 230), label='citizens walking wide'),
             shot(cits[0], K.SIDE, 4, 380, 95, 5, 40, label='citizen side'),
             shot(cits[2], K.THREE_QUARTER, 4, 380, 95, 10, 40, label='citizen 3/4'),
             shot(suit_center, K.WIDE, 5, 0, 100, 0, 50, wl=(-1200, 820, 170), label='AI suits walking in place')]
    d.set_editor_property('shots', shots)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    ok = unreal.EditorLoadingAndSavingUtils.save_map(world, MAP)
    log('map saved', ok, world.get_path_name(), len(unreal.EditorLevelLibrary.get_all_level_actors()), 'actors')
    log('map ok', MAP, 'shots', [(s.get_editor_property('label'), s.get_editor_property('duration')) for s in shots])
log('done')
