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
import json as _json0, math as _m

# ---- paths (round 04: relocatable; nothing is tied to one worktree or scratch dir) ------------------------------------
#   repo root   ARGS['wt']     | env P2_WT      | default: this project's dir (unreal/WebHomage) + ../..
#   art dir     ARGS['art']    | env P2_ART     | default: <repo>/art/night1/characters   (git-ignored PNG/FBX made by 'prep')
#   GLB inputs  ARGS['inputs'] | env P2_INPUTS  | default: <P2_SCRATCH>/ueimport          (stripped GLBs made by 'prep')
#   scratch     ARGS['scratch']| env P2_SCRATCH | default: <repo>/unreal/WebHomage/Saved/P2Build (tools/ue_char/p2paths.py)
# Legacy: build_manhattan.py (round 01) text-substitutes the 4 constant lines below; a substituted value is kept as is.
WT = '/Users/midir/sm2-n1/characters'
ART = WT + '/art/night1/characters'
GLB = '/Users/midir/sm2-n1/_scratch/characters/ueimport'
CIT = ART + '/export/citizens'
# round 04: 12 distinct crowd people (no raw person shared with an enemy; graphic tees left out), each with its own walk style
CITIZENS = ['03_white_tee', '12_sundress_mom', '13_construction_worker', '15_executive', '04_blue_sweatshirt', '08_black_suit',
            '10_silver_tie', '14_teen_skater', '18_dapper_elder', '19_marathon_runner', '01_retired_gent', '20_punk_artist',
            # round 05: six more distinct people (near lane of the crowd shots; graphic tees still left out)
            '02_leather_jacket', '05_black_tee', '06_chrome_shades', '09_kurta_waistcoat', '16_lumberjack_hipster', '17_hijabi_student']
CIT_WALK = {'03_white_tee': 'walk', '12_sundress_mom': 'walkF', '13_construction_worker': 'walkStroll', '15_executive': 'walkBrisk',
            '04_blue_sweatshirt': 'walkF', '08_black_suit': 'walkBrisk', '10_silver_tie': 'walk', '14_teen_skater': 'walk',
            '18_dapper_elder': 'walkOld', '19_marathon_runner': 'walkBrisk', '01_retired_gent': 'walkOld', '20_punk_artist': 'walkF',
            '02_leather_jacket': 'walk', '05_black_tee': 'walkBrisk', '06_chrome_shades': 'walkStroll', '09_kurta_waistcoat': 'walk',
            '16_lumberjack_hipster': 'walkStroll', '17_hijabi_student': 'walkF'}
# natural ground speeds (cm/s) of the time-warped crowd walks: tools/ue_char/eval/crowd_gait.py (planted-ankle speed)
CIT_SPEED = {'walk': 117.3, 'walkF': 113.7, 'walkBrisk': 147.9, 'walkStroll': 76.0, 'walkOld': 58.4}
PEOPLE = ['Thug', 'Brute', 'Hood', 'Tee', 'Beard']                       # street enemies (tools/ue_char/people)
PEOPLE_TINTS = [('Thug', 'Oxblood'), ('Hood', 'Grey')]                   # tint variants: same mesh, other atlas
PEOPLE_ARMED = [('Thug', 'Bat'), ('Thug', 'Pistol'), ('Brute', 'Pipe'), ('Hood', 'Pistol'), ('Tee', 'Bat'), ('Beard', 'Pipe')]
SUITS = ['Claude', 'Codex', 'Gemini', 'Kimi', 'Qwen']
try:
    ARGS  # noqa: F821  (set by uebox.py)
except NameError:
    import json
    ARGS = json.loads(os.environ.get('CHAR_BUILD_ARGS', '{}'))
_LEGACY = '/Users/midir/sm2-n1/' + 'characters'   # the pre-round-04 hard-coded values (spelled so the legacy substitution skips it)
_LEGACY_ART, _LEGACY_GLB = _LEGACY + '/art/night1/characters', '/Users/midir/sm2-n1/_scratch/' + 'characters/ueimport'
def _cfg(key, env, cur, legacy, default):
    v = ARGS.get(key) or os.environ.get(env)
    if v: return os.path.abspath(v)
    return cur if cur != legacy else default()   # substituted by a caller -> keep; untouched -> derive
_PROJ = os.path.abspath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
WT = _cfg('wt', 'P2_WT', WT, _LEGACY, lambda: os.path.abspath(os.path.join(_PROJ, '..', '..')))
SCRATCH = os.path.abspath(ARGS.get('scratch') or os.environ.get('P2_SCRATCH') or os.path.join(WT, 'unreal', 'WebHomage', 'Saved', 'P2Build'))
ART = _cfg('art', 'P2_ART', ART, _LEGACY_ART, lambda: WT + '/art/night1/characters')
GLB = _cfg('inputs', 'P2_INPUTS', GLB, _LEGACY_GLB, lambda: SCRATCH + '/ueimport')
CIT = ART + '/export/citizens'
_ENV = dict(os.environ, P2_WT=WT, P2_SCRATCH=SCRATCH)   # the 'prep' tools read these (tools/ue_char/p2paths.py)
STEPS = set((ARGS.get('steps') or 'prep,clean,tex,mat,mesh,citizens,rename,abp,map,maps5,mapkey').split(','))
ROOT, TESTS = '/Game/Characters', '/Game/Tests/Characters'
EAL = unreal.EditorAssetLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
T0 = time.time()
def log(*a): print('[build_characters %5.0fs]' % (time.time() - T0), *a)
log('paths: wt=%s art=%s inputs=%s scratch=%s' % (WT, ART, GLB, SCRATCH))
def load(p): return unreal.load_asset(p)

# ------------------------------------------------------------------------------------------------ prep (outside UE)
if 'prep' in STEPS:
    subprocess.run(['python3', WT + '/tools/ue_char/prep_glbs.py'], check=True, capture_output=True, env=_ENV)
    subprocess.run(['python3', WT + '/tools/ue_char/extract_textures.py'], check=True, capture_output=True, env=_ENV)
    subprocess.run(['python3', WT + '/tools/ue_char/hero_hand_fix.py'], check=True, capture_output=True, env=_ENV)
    # round 05: hero suit quality (smooth panel borders, raised thread normal / orm, twill detail) + domed lens in the UE-only hero GLB
    subprocess.run(['python3', WT + '/tools/ue_char/hero_suit_r5.py'], check=True, capture_output=True, env=_ENV)
    subprocess.run(['python3', WT + '/tools/ue_char/hero_lens_r5.py', GLB + '/SK_Hero.glb'], check=True, capture_output=True, env=_ENV)
    # round 05: citizen under-layer hulls (CH18 cracks) then the FBX export with them
    subprocess.run(['python3', WT + '/tools/ue_char/eval/underlayer.py'] + CITIZENS, check=True, capture_output=True, env=_ENV)
    # round 06: the citizens are refit from the raw Tripo meshes with welded skin weights (no seam cracks / coat flaps / finger claws); the pack LOD0 + hull is the fallback
    subprocess.run(['python3', WT + '/tools/ue_char/eval/refit.py'] + CITIZENS, check=True, capture_output=True, env=_ENV)
    subprocess.run(['python3', WT + '/tools/ue_char/eval/weights_r6.py'] + CITIZENS, check=True, capture_output=True, env=_ENV)
    # brute base colour painted on the thug UV layout (+ face/hands region mask for the test captures); rewrites the webp deterministically
    subprocess.run(['bash', WT + '/tools/ue_char/brute/build_brute.sh'], check=True, capture_output=True, env=_ENV)
    # street thug + brute: raw Tripo people (~/sm2-assets/raw) dressed, fitted to the hero skeleton (cached), textures + stripped GLBs
    subprocess.run(['bash', WT + '/tools/ue_char/people/build_people.sh'], check=True, capture_output=True, env=_ENV)
    if ARGS.get('force_citizens') or not all(os.path.exists('%s/%s.fbx' % (CIT, c)) for c in CITIZENS):
        subprocess.run(['bash', WT + '/tools/ue_char/eval/export_citizens.sh'] + CITIZENS, check=True, capture_output=True, env=dict(_ENV, PATH='/Applications/Blender.app/Contents/MacOS:' + os.environ.get('PATH', '')))
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
    # round 04: hand white paint inpainted (tools/ue_char/hero_hand_fix.py, run in 'prep'); falls back to the extracted texture
    # round 05: r5 maps (smooth panel borders, raised threads, glossy crests) when tools/ue_char/hero_suit_r5.py has run
    r5 = os.path.exists(H + '/suit_basecolor_r5.png')
    import_tex(H + ('/suit_basecolor_r5.png' if r5 else '/suit_basecolor_r4.png' if os.path.exists(H + '/suit_basecolor_r4.png') else '/suit_basecolor.png'), ROOT + '/Hero/Textures', 'T_Hero_BaseColor', 'srgb')
    import_tex(H + ('/suit_normal_r5.png' if r5 else '/suit_normal.png'), ROOT + '/Hero/Textures', 'T_Hero_Normal', 'normal_gl')   # glTF = OpenGL (curl test)
    import_tex(H + ('/suit_orm_r5.png' if r5 else '/suit_orm.png'), ROOT + '/Hero/Textures', 'T_Hero_ORM', 'linear')
    if os.path.exists(ART + '/shared/suit_twill_n.png'):
        import_tex(ART + '/shared/suit_twill_n.png', ROOT + '/Shared/Textures', 'T_Fabric_Twill_N', 'normal_gl')   # fine 2/2 twill (0.45 mm yarn), OpenGL
    # fabric micro-normal (browser detail maps; curl test says DirectX convention -> no flip)
    import_tex(ART + '/shared/white.png', ROOT + '/Shared/Textures', 'T_White_Masks', 'linear')
    import_tex(WT + '/public/assets/tex/suit_weave_knit.png', ROOT + '/Shared/Textures', 'T_Fabric_Knit_N', 'normal_dx')
    import_tex(WT + '/public/assets/tex/suit_weave_hex.png', ROOT + '/Shared/Textures', 'T_Fabric_Hex_N', 'normal_dx')
    for v in ('', '_b', '_c'):
        import_tex(TH + '/thug_basecolor%s.png' % v, ROOT + '/Thug/Textures', 'T_Thug_BaseColor' + v.upper(), 'srgb')
    import_tex(TH + '/brute_basecolor.png', ROOT + '/Thug/Textures', 'T_Brute_BaseColor', 'srgb')
    if os.path.exists(TH + '/brute_regions.png'):   # R face skin, G hands, B everything else: for the skin/white capture test
        import_tex(TH + '/brute_regions.png', ROOT + '/Thug/Textures', 'T_Brute_Regions', 'linear')
    import_tex(TH + '/thug_normal.png', ROOT + '/Thug/Textures', 'T_Thug_Normal', 'normal_gl')
    import_tex(TH + '/thug_orm.png', ROOT + '/Thug/Textures', 'T_Thug_ORM', 'linear')
    for k in PEOPLE:
        import_tex(ART + '/people/%s_basecolor.png' % k.lower(), ROOT + '/People/Textures', 'T_Street_%s_BaseColor' % k, 'srgb')
    for k, v in PEOPLE_TINTS:
        import_tex(ART + '/people/%s_%s_basecolor.png' % (k.lower(), v), ROOT + '/People/Textures', 'T_Street_%s%s_BaseColor' % (k, v), 'srgb')
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

def build_hero_lens():
    """M_Char_HeroLens (round 04, critic: 'flat white lenses, no specular'): glossy lacquered lens. The lens triangles are flat, so the
    dome is suggested in shading: the base colour falls off toward grazing angles (Fresnel) and the roughness is low for a sharp highlight.
    (Clear coat is not reachable from Python in UE 5.8: MP_CustomData0/1 are hidden enum values.)"""
    m = new_material(ROOT + '/Shared/Materials', 'M_Char_HeroLens', skeletal=True)
    c = vector(m, 'Color', (0.82, 0.84, 0.86, 1), -700, -250)
    fr = E(m, unreal.MaterialExpressionFresnel, -700, -80)
    fr.set_editor_property('exponent', 2.2); fr.set_editor_property('base_reflect_fraction', 0.0)
    edge = E(m, unreal.MaterialExpressionMultiply, -450, -120)
    MEL.connect_material_expressions(c, 'RGB', edge, 'A'); MEL.connect_material_expressions(scalar(m, 'EdgeDarken', 0.55, -700, 40), '', edge, 'B')
    lp = E(m, unreal.MaterialExpressionLinearInterpolate, -250, -200)
    MEL.connect_material_expressions(c, 'RGB', lp, 'A'); MEL.connect_material_expressions(edge, '', lp, 'B'); MEL.connect_material_expressions(fr, '', lp, 'Alpha')
    MEL.connect_material_property(lp, '', unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(scalar(m, 'Roughness', 0.07, -500, 120), '', unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(scalar(m, 'Specular', 1.0, -500, 200), '', unreal.MaterialProperty.MP_SPECULAR)
    em = E(m, unreal.MaterialExpressionMultiply, -250, 440)
    MEL.connect_material_expressions(lp, '', em, 'A'); MEL.connect_material_expressions(scalar(m, 'Emissive', 0.03, -500, 460), '', em, 'B')
    MEL.connect_material_property(em, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m)
    return m

def build_idmask():
    """M_Char_IDMask: unlit emissive of a region texture (test captures only: brute face/hands/cloth masks)."""
    m = new_material(ROOT + '/Shared/Materials', 'M_Char_IDMask', skeletal=True)
    m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    t = tex_param(m, 'Regions', ROOT + '/Thug/Textures/T_Brute_Regions', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, -600, 0)
    MEL.connect_material_property(t, 'RGB', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m)
    return m

def build_maskother():
    """M_Char_MaskOther: unlit yellow. In the mask map every OTHER character uses it: it occludes the brute exactly as in the beauty run and marks
    where another character (and its motion blur) may contaminate pixels."""
    m = new_material(ROOT + '/Shared/Materials', 'M_Char_MaskOther', skeletal=True)
    m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    z = E(m, unreal.MaterialExpressionConstant3Vector, -400, 0); z.set_editor_property('constant', unreal.LinearColor(1, 1, 0, 1))
    MEL.connect_material_property(z, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
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

BRUTE_TINT = float(ARGS.get('brute_tint', 0.85))
if 'mat' in STEPS:
    suit = build_suit_master()
    lens = build_simple('M_Char_Lens', emissive=True)
    lensf = build_simple('M_Char_LensFrame')
    MP = ROOT + '/Shared/Materials'
    # round 05: the chunky knit (tiling 48 = 3 mm ribs) is replaced by a fine twill: 32 yarns per tile, 0.45 mm per yarn -> tiling 122 from the
    # mesh's UV density (0.569 UV units per metre, tools/ue_char/hero_suit_r5.py)
    _fine = EAL.does_asset_exist(ROOT + '/Shared/Textures/T_Fabric_Twill_N')
    _hj = ART + '/hero/tex/suit_r5.json'
    _tile = float(_json0.load(open(_hj))['detail_tiling']) if (_fine and os.path.exists(_hj)) else 48.0
    mi('MI_Hero_Suit', ROOT + '/Hero/Materials', suit,
       tex={'BaseColor': ROOT + '/Hero/Textures/T_Hero_BaseColor', 'ORM': ROOT + '/Hero/Textures/T_Hero_ORM',
            'Normal': ROOT + '/Hero/Textures/T_Hero_Normal',
            'DetailNormal': ROOT + ('/Shared/Textures/T_Fabric_Twill_N' if _fine else '/Shared/Textures/T_Fabric_Knit_N')},
       scal={'DetailTiling': _tile, 'DetailStrength': 0.8 if _fine else 0.6, 'Cloth': 0.55, 'Specular': 0.6}, switches={'HasORM': True})
    try:   # round 04: glossy lens with a grazing-angle falloff; the old simple lens stays as the fallback
        hlens = build_hero_lens()
        mi('MI_Hero_Lens', ROOT + '/Hero/Materials', hlens, scal={'Roughness': 0.05, 'Specular': 1.0, 'EdgeDarken': 0.6, 'Emissive': 0.02}, vec={'Color': (0.64, 0.66, 0.70, 1)})   # round 05: domed lens (hero_lens_r5.py) - darker base so the sky / sun reflections read as highlights
        log('hero lens: glossy + fresnel falloff')
    except Exception as e:
        log('hero lens: glossy lens failed, simple lens', str(e)[:160])
        mi('MI_Hero_Lens', ROOT + '/Hero/Materials', lens, scal={'Roughness': 0.12, 'Specular': 0.9, 'Emissive': 0.04}, vec={'Color': (0.82, 0.84, 0.86, 1)})
    mi('MI_Hero_LensFrame', ROOT + '/Hero/Materials', lensf, scal={'Roughness': 0.35}, vec={'Color': (0.02, 0.02, 0.025, 1)})
    th = {'Normal': ROOT + '/Thug/Textures/T_Thug_Normal', 'ORM': ROOT + '/Thug/Textures/T_Thug_ORM'}
    for v, t in (('', 'T_Thug_BaseColor'), ('_B', 'T_Thug_BaseColor_B'), ('_C', 'T_Thug_BaseColor_C'), ('Brute', 'T_Brute_BaseColor')):
        n = 'MI_Brute' if v == 'Brute' else 'MI_Thug' + v
        sc_ = {'Cloth': 0.3, 'DetailStrength': 0.0}
        if v == 'Brute': sc_.update({'Cloth': 0.12, 'Specular': 0.15})   # dark cloth in bright daylight: keep spec/sheen from veiling the albedo
        vc_ = {}
        if v == 'Brute': vc_['Tint'] = (BRUTE_TINT, BRUTE_TINT, BRUTE_TINT, 1.0)   # test stage renders albedo ~3x brighter (sRGB); UE-only, the browser texture is untouched
        mi(n, ROOT + '/Thug/Materials', suit, tex=dict(th, BaseColor=ROOT + '/Thug/Textures/' + t), scal=sc_, vec=vc_, switches={'HasORM': True})
    for k in PEOPLE + [a + b for a, b in PEOPLE_TINTS]:   # street people: one 4096 atlas each (skin, cloth, mask, cap / weapon strip); Cloth shading, light sheen
        mi('MI_Street_' + k, ROOT + '/People/Materials', suit, tex={'BaseColor': ROOT + '/People/Textures/T_Street_%s_BaseColor' % k},
           scal={'Roughness': 0.78, 'Cloth': 0.16, 'DetailStrength': 0.0, 'Specular': 0.35}, switches={'HasORM': False})
    if EAL.does_asset_exist(ROOT + '/Thug/Textures/T_Brute_Regions'):
        mi('MI_BruteMask', ROOT + '/Thug/Materials', build_idmask(), tex={'Regions': ROOT + '/Thug/Textures/T_Brute_Regions'})
        mi('MI_MaskOther', ROOT + '/Shared/Materials', build_maskother())
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
if CIT_TMP == _LEGACY_GLB + '/citizens': CIT_TMP = GLB + '/citizens'   # untouched legacy value -> next to the GLB inputs
MESHES = [('SK_Hero', ROOT + '/Hero', None, True), ('SK_Thug', ROOT + '/Thug', HERO_SKEL, True)] + \
         [('SK_Suit_' + s, ROOT + '/Suits/' + s, HERO_SKEL, False) for s in SUITS] + \
         [('SK_Street_' + k, ROOT + '/People', HERO_SKEL, False) for k in PEOPLE] + \
         [('SK_Street_%s_%s' % kw, ROOT + '/People', HERO_SKEL, False) for kw in PEOPLE_ARMED]
if 'mesh' in STEPS:
    for name, dest, skel, anims in MESHES:
        got = do_import('%s/%s.glb' % (GLB, name), dest, skeleton=skel, anims=anims)
        log('imported', name, len(got), [g for g in got if 'Anim' not in g][:4])
if 'mesh' in STEPS:   # walk clips for the street people (a copy of the thug mesh rides along in the GLB and is deleted again)
    do_import('%s/SK_Street_Walks.glb' % GLB, ROOT + '/People', skeleton=HERO_SKEL, anims=True)
    log('imported street walks', [p.split('.')[-1] for p in EAL.list_assets(ROOT + '/People', recursive=True) if 'Walks' in p])
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
        if 'Armature_' in clip: clip = clip.split('Armature_')[-1]   # FBX takes: SK_Citizen_Armature_<take> / SK_CitizenArmature_<take>
        if not EAL.rename_asset(p, '%s/Anims/%s%s' % (folder, out_prefix, clip)): log('RENAME FAIL', p)
    for cls, suffix in ((unreal.SkeletalMesh, ''), (unreal.Skeleton, ''), (unreal.PhysicsAsset, '')):
        for p in find_class(folder, cls):
            if p.rsplit('/', 1)[0] != folder:
                if not EAL.rename_asset(p, folder + '/' + p.split('/')[-1]): log('RENAME FAIL', p)

if 'rename' in STEPS:
    for s_ in SUITS: rename_anims(ROOT + '/Suits/' + s_, 'SK_Suit_' + s_, 'A_Suit_')
    rename_anims(ROOT + '/Hero', 'SK_Hero', 'A_Hero_')
    rename_anims(ROOT + '/Thug', 'SK_Thug', 'A_Thug_')
    rename_anims(ROOT + '/Citizens', 'SK_Citizen', 'A_Citizen_')   # FBX takes land as SK_Citizen(_)Armature_<take> (rounds 01-03 kept
    # 'Armature_' in the name, so ABP_Citizen_Lineup loaded None for every clip and the citizens slid in the bind pose)
    rename_anims(ROOT + '/People', 'SK_Street_Walks', 'A_Street_')
    for junk in (ROOT + '/People/SK_Street_Walks',):   # the mesh that carried the clips
        if EAL.does_asset_exist(junk): EAL.delete_asset(junk)
    # the first citizen FBX names the mesh SK_Citizen: give it its citizen name like the others
    if EAL.does_asset_exist(ROOT + '/Citizens/SK_Citizen'):
        EAL.rename_asset(ROOT + '/Citizens/SK_Citizen', ROOT + '/Citizens/SK_Citizen_' + CITIZENS[0])
    log('hero slots', set_slots(ROOT + '/Hero/SK_Hero', {'SpiderSuit': ROOT + '/Hero/Materials/MI_Hero_Suit',
        'Lens': ROOT + '/Hero/Materials/MI_Hero_Lens', 'LensFrame': ROOT + '/Hero/Materials/MI_Hero_LensFrame'}))
    set_slots(ROOT + '/Thug/SK_Thug', {'*': ROOT + '/Thug/Materials/MI_Thug'})
    load(ROOT + '/Thug/SK_Thug').set_editor_property('physics_asset', load(HERO_PHYS))
    for k in PEOPLE + ['%s_%s' % kw for kw in PEOPLE_ARMED]:
        set_slots(ROOT + '/People/SK_Street_' + k, {'*': ROOT + '/People/Materials/MI_Street_' + k.split('_')[0]})
        load(ROOT + '/People/SK_Street_' + k).set_editor_property('physics_asset', load(HERO_PHYS))
    for s in SUITS:
        set_slots(ROOT + '/Suits/%s/SK_Suit_%s' % (s, s), {'*': ROOT + '/Suits/%s/Materials/MI_Suit_%s' % (s, s)})
        load(ROOT + '/Suits/%s/SK_Suit_%s' % (s, s)).set_editor_property('physics_asset', load(HERO_PHYS))
    for c in CITIZENS:
        set_slots(ROOT + '/Citizens/SK_Citizen_' + c, {'*': ROOT + '/Citizens/Materials/MI_Cit_' + c})
    EAL.save_directory(ROOT, only_if_is_dirty=True, recursive=True)
    log('rename ok', sorted(p.split('.')[-1] for p in EAL.list_assets(ROOT, recursive=True) if '/Anims/' not in p and 'Textures' not in p and 'Materials' not in p))

# ------------------------------------------------------------------------------------------------ AnimBPs (children of UWHCharAnimInstance)
def make_abp(name, path, skel, idle, loco, jump=None, fall=None, land=None, takeoff=None, seq=None, seq_blend=0.15, jump_variants=None,
             air_blend=None, hold_descent=False, takeoff_hold=None):
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
    if takeoff: cdo.set_editor_property('takeoff', load(takeoff))
    # round 05: staged idle sequence (fight), alternating leaps, air blend timing
    if seq: cdo.set_editor_property('sequence', [load(c) for c in seq]); cdo.set_editor_property('sequence_blend', float(seq_blend))
    if jump_variants: cdo.set_editor_property('jump_variants', [load(c) for c in jump_variants])
    if air_blend: cdo.set_editor_property('air_blend_in', float(air_blend))
    if takeoff_hold: cdo.set_editor_property('takeoff_hold_time', float(takeoff_hold))
    if hold_descent:
        try: cdo.set_editor_property('jump_holds_through_descent', True)
        except Exception as e: log('hold_descent property:', str(e)[:100])
    EAL.save_asset(full)
    return bp

if 'abp' in STEPS:
    HA = ROOT + '/Hero/Anims/A_Hero_'
    # natural speeds (cm/s) of the hero clips = planted-foot (stance) speed of each clip (round 04; tools/ue_char/heroanim/foot_speed.py):
    # walk 1.14, jog 3.10, run 5.70 (the 17/30 s round-04 run; median stance speed 5.95, 5.70 minimises the worst plant's slide: 2.8 cm), sprint 8.99 m/s. The browser's LOCO anchors (walk 1.6, jog 4.5,
    # run 8.5, sprint 14 m/s, src/player/anim/animator.js) make the feet slide; the lineup plays every clip at its own foot speed.
    hero_loco = [(HA + 'walk', 114.0), (HA + 'jog', 310.0), (HA + 'run', 570.0), (HA + 'sprint', 899.0)]
    # round 04: jumps start with the grounded runTakeoff crouch (the walker holds the actor on the ground for TakeoffTime), the air
    # pose after the jump clip is fallCalm (the old `fall` is a horizontal skydive pose: the round-03 critic's 'belly dive')
    make_abp('ABP_Hero_Lineup', ROOT + '/Hero', HERO_SKEL, HA + 'idle', hero_loco, HA + 'jump', HA + 'fallCalm', HA + 'landLight', HA + 'runTakeoff')
    make_abp('ABP_Thug_Lineup', ROOT + '/Thug', HERO_SKEL, ROOT + '/Thug/Anims/A_Thug_thugIdle', hero_loco, HA + 'jump', HA + 'fall', HA + 'landLight')
    PA = ROOT + '/People/Anims/A_Street_'
    idle_t = ROOT + '/Thug/Anims/A_Thug_thugIdle'
    make_abp('ABP_Street_Thug', ROOT + '/People', HERO_SKEL, idle_t, [(PA + 'walkStreet', 114.0)] + hero_loco[1:], HA + 'jump', HA + 'fall', HA + 'landLight')
    make_abp('ABP_Street_Brute', ROOT + '/People', HERO_SKEL, idle_t, [(PA + 'walkBrute', 110.0)] + hero_loco[1:], HA + 'jump', HA + 'fall', HA + 'landLight')   # walkBrute foot speed 1.018 m/s x actor scale 1.08
    CA = ROOT + '/Citizens/Anims/A_Citizen_'
    # crowd clips: walk stride 1.1543 m / (32/30 s) = 1.08 m/s, run stride 3.4181 m / (19/30 s) = 5.40 m/s (people.json)
    make_abp('ABP_Citizen_Lineup', ROOT + '/Citizens', CIT_SKEL, CA + 'idle', [(CA + 'walk', CIT_SPEED['walk']), (CA + 'run', 540.0)])
    for wk, spd in CIT_SPEED.items():   # one AnimBP per walk style, the clip at its natural (foot-locked) speed
        make_abp('ABP_Citizen_' + wk, ROOT + '/Citizens', CIT_SKEL, CA + 'idle', [(CA + wk, spd)])
    TA = ROOT + '/Thug/Anims/A_Thug_'
    make_abp('ABP_Street_GunAim', ROOT + '/People', HERO_SKEL, TA + 'thugGunAim', [(PA + 'walkStreet', 114.0)])
    # standing lineup: the hero's standing idles (thugIdle is a deep boxing crouch with the hands at the face)
    make_abp('ABP_Street_Stand', ROOT + '/People', HERO_SKEL, HA + 'idle', [(PA + 'walkStreet', 114.0)])
    make_abp('ABP_Street_StandLook', ROOT + '/People', HERO_SKEL, HA + 'idleLook', [(PA + 'walkStreet', 114.0)])
    # ---- round 05: running leap (takeoff crouch -> open stride -> tuck -> reach, alternating legs), staged fight sequences
    make_abp('ABP_Hero_Leap', ROOT + '/Hero', HERO_SKEL, HA + 'idle', hero_loco, HA + 'runLeap', HA + 'fallCalm', HA + 'landLight', HA + 'runTakeoff',
             jump_variants=[HA + 'runLeap', HA + 'runLeapB'], air_blend=7.0, hold_descent=True, takeoff_hold=0.18)
    make_abp('ABP_Hero_Fight', ROOT + '/Hero', HERO_SKEL, HA + 'fightIdle', hero_loco, seq_blend=0.12,
             seq=[HA + 'fightIdle', HA + 'punch1', HA + 'punch2', HA + 'kick', HA + 'fightIdle', HA + 'punch3'])
    FA_ = ROOT + '/Thug/Anims/A_Thug_'
    # each enemy: guard (thugIdle: boxing stance, chin tucked, head never above the horizon) between one action; heads stay <= 10 deg up
    # armed enemies (bat, pipe, pistol) stand relaxed with the weapon hanging (the hero's standing idle, head +6 deg) until they swing; the unarmed ones
    # keep the boxing guard (thugIdle) between punches / kicks / hit reactions.  'H:' = a hero clip.
    fights = {'Thug': ['H:idle', 'thugPunch1', 'thugPunch2'], 'Brute': ['H:idle', 'thugPunch2', 'thugPunch1'], 'Hood': ['H:idle', 'thugStumbleBack'],
              'Tee': ['thugKick', 'thugIdle', 'thugPunch2'], 'Beard': ['thugPunch2', 'thugPunch1', 'thugIdle'], 'Oxblood': ['thugIdle', 'thugStumbleLeft', 'thugPunch1']}
    for k, clips in fights.items():
        make_abp('ABP_Fight_' + k, ROOT + '/People', HERO_SKEL, FA_ + 'thugIdle', [(PA + 'walkStreet', 114.0)],
                 seq=[(HA + c[2:]) if c.startswith('H:') else (FA_ + c) for c in clips], seq_blend=0.14)
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

def walker(label, mesh, abp, loc, mode, speed, rx=0, ry=0, start=0, hop=0, scale=1.0, mat=None, yaw=0, girth=1.0, anim_offset=0.0):
    a = spawn(unreal.WHCharLoopWalker, loc, (yaw, 0, 0), label)
    m = a.get_editor_property('mesh')
    m.set_skeletal_mesh_asset(load(mesh))
    m.set_editor_property('animation_mode', unreal.AnimationMode.ANIMATION_BLUEPRINT)
    m.set_anim_instance_class(load(abp).generated_class())
    m.set_relative_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=MESH_YAW), False, False)
    if mat: m.set_material(0, load(mat))
    a.set_actor_scale3d(unreal.Vector(scale * girth, scale * girth, scale))   # girth: extra X/Y build without extra height
    for k, v in (('mode', mode), ('speed', speed), ('radius_x', rx), ('radius_y', ry), ('start_angle', start), ('hop_interval', hop)):
        a.set_editor_property(k, v)
    if anim_offset: a.set_editor_property('anim_offset', float(anim_offset))
    return a

import json as _json
_SZ = _json.load(open(WT + '/tools/ue_char/people/people.json'))['brute']
BRUTE_SCALE = float(ARGS.get('brute_scale', _SZ['scale']))   # brute height scale on the fitted Tripo mesh (hero height 1.79 m)
BRUTE_GIRTH = float(ARGS.get('brute_girth', _SZ['girth']))   # extra X/Y scale (heavy-set build) on top of it
LANE = (3000.0, 0.0)                                  # straight lane for the side-tracking clips
LANE_SPEED = 135.0
MESH_YAW = float(ARGS.get('mesh_yaw', -90.0))   # glTF +Z forward -> UE: mesh faces +Y after import; walker moves along +X
if 'map' in STEPS:
    variants = [(TESTS + '/Char_Lineup', False)]
    if ARGS.get('mask_map', False) and EAL.does_asset_exist(ROOT + '/Thug/Materials/MI_BruteMask'):   # round-02 test map (old brute); off by default
        variants.append((TESTS + '/Char_Lineup_BruteMask', True))   # test-only twin: brute drawn with the unlit region mask (R face skin, G hands, B cloth)
    for MAP, MASK in variants:
        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        les.new_level('/Temp/Char_Lineup_Build_%d_%d' % (int(time.time()), int(MASK)))   # built in a temp level, then saved over MAP (idempotent)
        W = unreal.WHWalkerMode
        # light: neutral daylight
        sun = spawn(unreal.DirectionalLight, (0, 0, 1000), (-35, -40, 0), 'Sun')
        sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
        sc.set_editor_property('intensity', 8.0); sc.set_editor_property('atmosphere_sun_light', True)
        # round 06: the round-05 'black shards' in the thug hoodie collar are hard-edged SUN shadows of the hood rim / mask hem (they vanish with shadows
        # off, docs/night1/characters/round-06/evidence/collar_shadow_test.jpg), not geometry: a wider sun disc gives a real penumbra
        sc.set_editor_property('light_source_angle', float(ARGS.get('sun_angle', 3.0)))
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
        # characters (round 04 layout: hero lanes on the road, enemy lineup on the north sidewalk, enemy lanes at x 1500..4500 on y 0,
        # civilians on the south sidewalk, AI suits parked at x -3500; no hero-suit mesh anywhere near the civilian or enemy cameras)
        H = ROOT + '/Hero/'; T = ROOT + '/Thug/'; PP = ROOT + '/People/'
        hero_tt = walker('Hero_Turntable', H + 'SK_Hero', H + 'ABP_Hero_Lineup', (-2400, -900, 0), W.TURNTABLE, 114.0)
        def line(label, mesh, abp, loc, speed, length, start, yaw=0.0, scale=1.0, girth=1.0, mat=None):
            """Line walker: moves along its yaw from loc - length/2; `start` = world distance from that end at BeginPlay / restart."""
            a = walker(label, mesh, abp, loc, W.LINE, speed, scale=scale, girth=girth, mat=mat, yaw=yaw)
            a.set_editor_property('line_length', float(length)); a.set_editor_property('line_start', float(start))
            return a
        # hero side run (no hop) and run -> jump (grounded anticipation crouch, then the jump), both at the run clip's foot speed
        RUN_V = 570.0
        hero_run = line('Hero_RunLane', H + 'SK_Hero', H + 'ABP_Hero_Lineup', (0, -400, 0), RUN_V, 9000, 4500 - 2600)
        hero_jump = line('Hero_JumpLane', H + 'SK_Hero', H + 'ABP_Hero_Lineup', (0, 400, 0), RUN_V, 9000, 4500 - 1200, yaw=180.0)
        for k, v in (('hop_interval', 2.6), ('first_hop_delay', 1.3), ('takeoff_time', 0.25), ('hop_velocity', 470.0)):
            hero_jump.set_editor_property(k, v)
        # enemy lanes (side-tracking at 4.2 m and 3 m): thug with a bat, brute with a pipe, each at its walk clip's foot speed
        def lane(label, mesh, abp, mat, start, speed, scale=1.0, girth=1.0):
            return line(label, mesh, abp, (LANE[0], LANE[1], 0), speed, 3000.0, start, scale=scale, girth=girth, mat=mat)
        thug_l = lane('Thug_Lane', PP + 'SK_Street_Thug_Bat', PP + 'ABP_Street_Thug', PP + 'Materials/MI_Street_Thug', 1500.0 + 640.0, 114.0)   # round 05: 6 m ahead of the brute (the face close-ups no longer share a frame)
        brute_l = lane('Brute_Lane', PP + 'SK_Street_Brute_Pipe', PP + 'ABP_Street_Brute', PP + 'Materials/MI_Street_Brute', 1500.0 - 40.0, 110.0, scale=BRUTE_SCALE, girth=BRUTE_GIRTH)
        track = spawn(unreal.WHCharLoopWalker, (LANE[0], LANE[1], 0), (0, 0, 0), 'Lane_Track')
        track.set_editor_property('mode', W.LINE); track.set_editor_property('speed', 112.0)
        track.set_editor_property('line_length', 3000.0); track.set_editor_property('line_start', 1500.0)
        # enemy lineup: 7 enemies, 5 outfits (leather hooded jacket, puffer vest + beanie, hoodie + cargo + shades, tee + cap,
        # tee + chains), 2 tint variants, 3 weapon types (bat, pipe, pistol); two staggered rows facing the road (-Y)
        LX, LY = 2050.0, 1900.0
        GA, TH, TL = PP + 'ABP_Street_GunAim', PP + 'ABP_Street_Stand', PP + 'ABP_Street_StandLook'
        # round 04b: thugGunAim is a deep crouch aiming ~40 deg up (reads as a pose bug in the lineup, and drops the head out of the
        # face close-up); pistol holders stand with the pistol lowered unless ARGS gun_aim is set
        if not ARGS.get('gun_aim'): GA = TL
        TL = TH   # round 05: idleLook raises the head up to 39 deg (the 'craned up' heads of round 04); every standing enemy uses the plain idle
        if not ARGS.get('gun_aim'): GA = TL
        crew = [('Crew_ThugBat', 'SK_Street_Thug_Bat', TH, 'Thug', 1.0, 1.0),
                ('Crew_HoodPistol', 'SK_Street_Hood_Pistol', GA, 'Hood', 1.0, 1.0),
                ('Crew_BrutePipe', 'SK_Street_Brute_Pipe', TL, 'Brute', BRUTE_SCALE, BRUTE_GIRTH),
                ('Crew_TeeBat', 'SK_Street_Tee_Bat', TH, 'Tee', 1.0, 1.0),
                ('Crew_BeardPipe', 'SK_Street_Beard_Pipe', TH, 'Beard', 1.0, 1.0),
                ('Crew_ThugPistol', 'SK_Street_Thug_Pistol', GA, 'ThugOxblood', 1.0, 1.0)]   # round 05: the grey-hoodie twin of the hood is gone
        enemies = []
        for i, (lbl, mesh, abp, mat, sc_, g_) in enumerate(crew):
            x = LX + (i - 2.5) * 105.0
            y = LY + (60.0 if i % 2 else -60.0)
            e = walker(lbl, PP + mesh, abp, (x, y, 0), W.STAND, 0.0, scale=sc_, girth=g_, mat=PP + 'Materials/MI_Street_' + mat, yaw=-90.0 + (i - 3) * 6.0)
            enemies.append(e)
        crew_center = spawn(unreal.TargetPoint, (LX, LY, 0), label='CrewCenter')
        chan = unreal.LightingChannels(); chan.set_editor_property('channel0', True); chan.set_editor_property('channel1', True)
        for enemy in [thug_l, brute_l] + enemies:
            enemy.get_editor_property('mesh').set_editor_property('lighting_channels', chan)
        # enemy fill: 4 shadowless directional lights on lighting channel 1 only (the sun alone leaves the camera side of an enemy near black)
        only1 = unreal.LightingChannels(); only1.set_editor_property('channel0', False); only1.set_editor_property('channel1', True)
        for fi, fyaw in enumerate((0, 90, 180, 270)):
            fl = spawn(unreal.DirectionalLight, (0, 0, 1500), (fyaw, -30, 0), 'EnemyFill_%d' % fi)   # rot = (yaw, pitch, roll)
            fc = fl.get_component_by_class(unreal.DirectionalLightComponent)
            fc.set_editor_property('intensity', float(ARGS.get('enemy_fill', 1.4))); fc.set_editor_property('cast_shadows', False)
            fc.set_editor_property('lighting_channels', only1)
        # civilians: 12 distinct crowd people on the south sidewalk, each its own walk style at that style's foot-locked speed, both
        # directions, gait phases spread by start position; a mesh-less tracker walks with them for the tracking camera
        CY = -1950.0
        civ = []
        plan = [  # (citizen, lateral offset cm, start x (world, at restart), direction)
            ('03_white_tee', 150, -300, 1), ('12_sundress_mom', -120, 200, 1), ('13_construction_worker', 60, 700, 1),
            ('15_executive', -200, -650, 1), ('04_blue_sweatshirt', 230, 450, 1), ('08_black_suit', -40, -900, 1),
            ('18_dapper_elder', 120, 1000, 1), ('19_marathon_runner', -260, -1200, 1),
            ('10_silver_tie', -150, 1500, -1), ('14_teen_skater', 200, 1900, -1), ('01_retired_gent', 40, 1300, -1), ('20_punk_artist', -230, 2300, -1)]
        L_CIV = 9000.0
        CIV_SPREAD = float(ARGS.get('civ_spread', 0.45))   # round 04b: start positions pulled together so >= 8 fit the tracking shot
        for c, dy, x0, dr in plan:
            x0 = x0 * CIV_SPREAD
            wk = CIT_WALK[c]
            start = (x0 + L_CIV / 2) if dr > 0 else (L_CIV / 2 - x0)
            civ.append(line('Citizen_' + c, ROOT + '/Citizens/SK_Citizen_' + c, ROOT + '/Citizens/ABP_Citizen_' + wk, (0, CY + dy, 0),
                            CIT_SPEED[wk], L_CIV, start, yaw=0.0 if dr > 0 else 180.0))
        civ_track = spawn(unreal.WHCharLoopWalker, (0, CY, 0), (0, 0, 0), 'Citizens_Track')
        civ_track.set_editor_property('mode', W.LINE); civ_track.set_editor_property('speed', 110.0)
        civ_track.set_editor_property('line_length', L_CIV); civ_track.set_editor_property('line_start', L_CIV / 2)
        cit_center = spawn(unreal.TargetPoint, (500, CY, 0), label='CitizensCenter')
        suits = []
        for i, s in enumerate(SUITS):
            suits.append(walker('Suit_' + s, ROOT + '/Suits/%s/SK_Suit_%s' % (s, s), H + 'ABP_Hero_Lineup', (-3500, 300 + i * 260, 0), W.TURNTABLE, 114.0, start=0))
        suit_center = spawn(unreal.TargetPoint, (-3500, 820, 0), label='SuitsCenter')
        # capture director (shot list; times are cumulative in tools/ue_char/capture_lineup.sh)
        d = spawn(unreal.WHCharShowDirector, (0, 0, 0), label='CaptureDirector')
        K = unreal.WHShotKind
        def shot(t, kind, dur, dist, aim=100.0, camh=10.0, fov=40.0, orbit=40.0, az=0.0, wl=(0, 0, 0), label='', restart=()):
            s = unreal.WHShot()
            for k, v in (('target', t), ('kind', kind), ('duration', dur), ('distance', dist), ('aim_height', aim), ('cam_height', camh),
                         ('fov', fov), ('orbit_deg_per_sec', orbit), ('azimuth', az), ('world_location', unreal.Vector(*wl)), ('label', label), ('restart_walkers', list(restart))):
                s.set_editor_property(k, v)
            return s
        civ_all = civ + [civ_track]
        shots = [shot(hero_tt, K.ORBIT, 6, 340, 100, 20, 40, 45, 0, label='hero moving turntable'),                               # 0  @0
                 shot(hero_run, K.SIDE, 6, 560, 95, 0, 40, restart=[hero_run], label='hero run side (no hop)'),                       # 1  @6
                 shot(hero_run, K.THREE_QUARTER, 5, 480, 95, 25, 40, restart=[hero_run], label='hero run 3/4'),                       # 2  @12
                 shot(hero_jump, K.SIDE, 6.5, 620, 110, 0, 42, restart=[hero_jump], label='hero run -> jump side'),                   # 3  @17
                 shot(hero_tt, K.CLOSEUP, 4, 95, 135, 5, 30, label='suit fabric close-up (chest)'),                                   # 4  @23.5
                 shot(crew_center, K.WIDE, 6, 0, 95, 0, 55, wl=(LX, LY - 950, 165), label='enemy lineup (7) wide'),                  # 5  @27.5
                 shot(crew_center, K.WIDE, 5, 0, 95, 0, 50, wl=(LX - 900, LY - 780, 175), label='enemy lineup 3/4'),                  # 6  @33.5
                 shot(track, K.SIDE, 6, 420, 95, 10, 64, restart=[thug_l, brute_l, track], label='thug + brute side tracking (4.2 m)'),  # 7  @38.5
                 shot(thug_l, K.SIDE, 5, 300, 92, 5, 62, restart=[thug_l], label='thug side tracking 3 m'),                          # 8  @44.5
                 shot(brute_l, K.SIDE, 5, 300, 100, 5, 66, restart=[brute_l], label='brute side tracking 3 m'),                      # 9  @49.5
                 shot(thug_l, K.CLOSEUP, 4, 105, 160, 0, 28, restart=[thug_l], label='thug face close-up'),                          # 10 @54.5
                 shot(brute_l, K.CLOSEUP, 4, 115, 168, 0, 28, restart=[brute_l], label='brute face close-up'),                       # 11 @58.5
                 shot(enemies[1], K.CLOSEUP, 6, 105, 160, 0, 28, label='hood face close-up'),                                         # 12 @62.5
                 shot(enemies[3], K.CLOSEUP, 6, 105, 160, 0, 28, label='tee + cap face close-up'),                                    # 13 @65.5
                 shot(enemies[4], K.CLOSEUP, 6, 105, 160, 0, 28, label='beard face close-up'),                                        # 14 @68.5
                 shot(civ_track, K.SIDE, 8, 1150, 100, 45, 64, restart=civ_all, label='civilians walking past a tracking camera'),      # 15 @71.5
                 shot(cit_center, K.WIDE, 6, 0, 110, 0, 50, wl=(-1400, CY + 420, 175), restart=civ_all, label='civilians wide'),      # 16 @79.5
                 shot(suit_center, K.WIDE, 5, 0, 100, 0, 50, wl=(-2300, 820, 170), label='AI suits walking in place')]                # 17 @85.5 (ends 90.5)
        d.set_editor_property('shots', shots)
        if MASK:
            eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            for act in list(eas.get_all_level_actors()):
                cls = act.get_class().get_name()
                if act.get_actor_label() == 'Brute_Walk':
                    act.get_editor_property('mesh').set_material(0, load(T + 'Materials/MI_BruteMask'))
                elif not ARGS.get('mask_keep_scene') and cls in ('DirectionalLight', 'SkyAtmosphere', 'SkyLight', 'ExponentialHeightFog'):
                    eas.destroy_actor(act)                       # black background: only the unlit mask is visible
                elif not ARGS.get('mask_keep_scene') and isinstance(act, unreal.StaticMeshActor):
                    act.set_actor_hidden_in_game(True)           # backdrop
                elif not ARGS.get('mask_keep_scene') and isinstance(act, unreal.WHCharLoopWalker):
                    m_ = act.get_editor_property('mesh')         # other characters: unlit yellow, so they occlude the brute like in the beauty run
                    for slot in range(m_.get_num_materials()):
                        m_.set_material(slot, load(ROOT + '/Shared/Materials/MI_MaskOther'))
                elif isinstance(act, unreal.PostProcessVolume) and ARGS.get('mask_ev', 'auto') != 'auto':
                    ps = act.get_editor_property('settings')     # fixed exposure so the mask colours do not drift
                    ps.set_editor_property('override_auto_exposure_method', True); ps.set_editor_property('auto_exposure_method', unreal.AutoExposureMethod.AEM_MANUAL)
                    ps.set_editor_property('override_auto_exposure_bias', True); ps.set_editor_property('auto_exposure_bias', float(ARGS.get('mask_ev', 0.0)))
                    act.set_editor_property('settings', ps)
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        ok = unreal.EditorLoadingAndSavingUtils.save_map(world, MAP)
        log('map saved', ok, world.get_path_name(), len(unreal.EditorLevelLibrary.get_all_level_actors()), 'actors')
    log('map ok', MAP, 'shots', [(s.get_editor_property('label'), s.get_editor_property('duration')) for s in shots])
# ------------------------------------------------------------------------------------------------ round-05 maps: hero / fight / crowd
# Three separate maps instead of one lineup: the hero shots have no second hero or thugs in the background (critic r04: 'a second hero walking
# through hero captures'), the fight is a staged street fight (5-7 enemies around the hero), the crowd is two-way flow with walkers near the camera.
if 'maps5' in STEPS:
    W5 = unreal.WHWalkerMode
    K5 = unreal.WHShotKind
    H5 = ROOT + '/Hero/'; PP5 = ROOT + '/People/'

    NEWLEVEL_N = [0]

    def new_stage(tag, fills=False):
        """Level with the round-04 test-stage lighting + street; returns the level's fill-light state (enemy fills on lighting channel 1 only)."""
        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        NEWLEVEL_N[0] += 1
        les.new_level('/Temp/Char_%s_Build_%d_%d' % (tag, int(time.time()), NEWLEVEL_N[0]))   # unique per call (two maps built within one second collided)
        sun = spawn(unreal.DirectionalLight, (0, 0, 1000), (-35, -40, 0), 'Sun')
        sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
        sc.set_editor_property('intensity', 8.0); sc.set_editor_property('atmosphere_sun_light', True)
        spawn(unreal.SkyAtmosphere, (0, 0, 0), label='SkyAtmosphere')
        sky = spawn(unreal.SkyLight, (0, 0, 300), label='SkyLight')
        skc = sky.get_component_by_class(unreal.SkyLightComponent); skc.set_editor_property('real_time_capture', True); skc.set_editor_property('mobility', unreal.ComponentMobility.MOVABLE)
        spawn(unreal.ExponentialHeightFog, (0, 0, 0), label='Fog')
        ppv = spawn(unreal.PostProcessVolume, (0, 0, 0), label='Post'); ppv.set_editor_property('unbound', True)
        spawn(unreal.PlayerStart, (-6000, -6000, 120), label='PlayerStart_OffStage')
        box((0, 0, -10), (80, 30, 0.2), 'M_Env_Asphalt', 'Road')
        box((0, 1900, 0), (80, 8, 0.3), 'M_Env_Sidewalk', 'Sidewalk_N')
        box((0, -1900, 0), (80, 8, 0.3), 'M_Env_Sidewalk', 'Sidewalk_S')
        for i in range(10):
            x = -3600 + i * 800
            h = 1800 + (i * 530) % 1500
            box((x, 2700, h / 2), (7.6, 8, h / 100), ('M_Env_Brick', 'M_Env_Stone')[i % 2], 'Facade_%d' % i)
            for f in range(1, int(h / 350)):
                box((x, 2295, f * 350), (5.5, 0.1, 1.6), 'M_Env_Glass', 'Win_%d_%d' % (i, f))
            box((x, -2700, h / 2), (7.6, 8, h / 100), ('M_Env_Stone', 'M_Env_Brick')[i % 2], 'FacadeS_%d' % i)
        for k in range(8):
            box((1900, -600 + k * 170, -8), (4, 0.7, 0.05), 'M_Env_Paint', 'Crosswalk_%d' % k)
        if fills:
            only1 = unreal.LightingChannels(); only1.set_editor_property('channel0', False); only1.set_editor_property('channel1', True)
            for fi, fyaw in enumerate((0, 90, 180, 270)):
                fl = spawn(unreal.DirectionalLight, (0, 0, 1500), (fyaw, -30, 0), 'CharFill_%d' % fi)
                fc = fl.get_component_by_class(unreal.DirectionalLightComponent)
                fc.set_editor_property('intensity', float(ARGS.get('enemy_fill', 0.8))); fc.set_editor_property('cast_shadows', False)
                fc.set_editor_property('lighting_channels', only1)

    def both_channels(actors):
        chan = unreal.LightingChannels(); chan.set_editor_property('channel0', True); chan.set_editor_property('channel1', True)
        for a in actors: a.get_editor_property('mesh').set_editor_property('lighting_channels', chan)

    def mkshot(t, kind, dur, dist, aim=100.0, camh=10.0, fov=40.0, orbit=40.0, az=0.0, wl=(0, 0, 0), label='', restart=()):
        sh = unreal.WHShot()
        for k, v in (('target', t), ('kind', kind), ('duration', dur), ('distance', dist), ('aim_height', aim), ('cam_height', camh),
                     ('fov', fov), ('orbit_deg_per_sec', orbit), ('azimuth', az), ('world_location', unreal.Vector(*wl)), ('label', label), ('restart_walkers', list(restart))):
            sh.set_editor_property(k, v)
        return sh

    def save_map(MAP, shots, managed=()):
        d = spawn(unreal.WHCharShowDirector, (0, 0, 0), label='CaptureDirector')
        d.set_editor_property('shots', shots)
        if managed:   # round 05: per-shot visibility (only the shot's target is shown): no second hero in a hero capture
            try: d.set_editor_property('managed_actors', list(managed))
            except Exception as e: log('managed_actors not available (rebuild the editor module):', str(e)[:100])
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        ok = unreal.EditorLoadingAndSavingUtils.save_map(world, MAP)
        log('map saved', MAP, ok, len(unreal.EditorLevelLibrary.get_all_level_actors()), 'actors', [(x.get_editor_property('label'), x.get_editor_property('duration')) for x in shots])

    def line5(label, mesh, abp, loc, speed, length, start, yaw=0.0, scale=1.0, girth=1.0, mat=None, hop=None):
        a = walker(label, mesh, abp, loc, W5.LINE, speed, scale=scale, girth=girth, mat=mat, yaw=yaw)
        a.set_editor_property('line_length', float(length)); a.set_editor_property('line_start', float(start))
        return a

    # ================= Char_Hero: hero only (no other character anywhere) =================
    new_stage('Hero')
    hero_tt = walker('Hero_Turntable', H5 + 'SK_Hero', H5 + 'ABP_Hero_Lineup', (-1500, -900, 0), W5.TURNTABLE, 114.0)
    RUN_V = 570.0
    hero_run = line5('Hero_RunLane', H5 + 'SK_Hero', H5 + 'ABP_Hero_Leap', (0, -400, 0), RUN_V, 9000, 4500 - 2600)
    hero_jump = line5('Hero_JumpLane', H5 + 'SK_Hero', H5 + 'ABP_Hero_Leap', (0, 400, 0), RUN_V, 9000, 4500 - 1200, yaw=180.0)
    for k, v in (('hop_interval', 2.6), ('first_hop_delay', 1.3), ('takeoff_time', 0.25), ('hop_velocity', 470.0)):
        hero_jump.set_editor_property(k, v)
    hero_shots = [
        mkshot(hero_tt, K5.ORBIT, 6, 520, 95, 20, 40, 45, 0, label='hero moving turntable (whole body)'),                                      # 0  @0   (r05: 3.4 m cut the legs off)
        mkshot(hero_run, K5.SIDE, 6, 560, 95, 0, 40, restart=[hero_run], label='hero run side'),                                              # 1  @6
        mkshot(hero_run, K5.THREE_QUARTER, 5, 480, 95, 25, 40, restart=[hero_run], label='hero run 3/4'),                                     # 2  @12
        mkshot(hero_jump, K5.SIDE, 6.5, 820, 115, 0, 42, restart=[hero_jump], label='hero run -> leap side (whole jump in frame)'),            # 3  @17
        mkshot(hero_tt, K5.CLOSEUP, 6, 95, 135, 5, 30, label='suit fabric close-up (chest)'),                                                 # 4  @23.5
        mkshot(hero_tt, K5.CLOSEUP, 6, 72, 160, 0, 26, label='hero face + lens close-up'),                                                    # 5  @27.5
        # round 05: gameplay-style cameras (CH1 / CH2 were unproven: no clip used a chase camera): behind the runner (Front kind, azimuth 180) and toward the camera
        mkshot(hero_run, K5.FRONT, 6, 500, 95, 65, 62, 0, 180, restart=[hero_run], label='hero run chase camera (3rd person, behind)'),       # 6  @33.5
        mkshot(hero_run, K5.FRONT, 6, 560, 95, 40, 62, 0, 0, restart=[hero_run], label='hero run toward the camera')]                          # 7  @39.5
    save_map(TESTS + '/Char_Hero', hero_shots, managed=[hero_tt, hero_run, hero_jump])

    # ================= Char_Fight: a staged street fight, hero in the middle of 6 enemies =================
    new_stage('Fight', fills=True)
    FX, FY = 0.0, 0.0
    hero_f = walker('Fight_Hero', H5 + 'SK_Hero', H5 + 'ABP_Hero_Fight', (FX, FY, 0), W5.STAND, 0.0, yaw=245.0)   # faces the thug at 235 deg
    ring = [('Fight_Thug', 'SK_Street_Thug_Bat', 'Thug', 'Thug', 235, 265, 1.0, 1.0, 2.4),
            ('Fight_Brute', 'SK_Street_Brute_Pipe', 'Brute', 'Brute', 312, 285, BRUTE_SCALE, BRUTE_GIRTH, 3.0),
            ('Fight_Hood', 'SK_Street_Hood_Pistol', 'Hood', 'Hood', 188, 270, 1.0, 1.0, 1.6),
            ('Fight_Tee', 'SK_Street_Tee', 'Tee', 'Tee', 358, 275, 1.0, 1.0, 0.0),
            ('Fight_Beard', 'SK_Street_Beard', 'Beard', 'Beard', 128, 290, 1.0, 1.0, 0.7),
            ('Fight_Oxblood', 'SK_Street_Thug', 'Oxblood', 'ThugOxblood', 58, 300, 1.0, 1.0, 1.3)]
    fight_actors = [hero_f]
    for lbl, mesh, abpk, mat, ang, rad, sc_, g_, off in ring:
        x = FX + rad * _m.cos(_m.radians(ang)); y = FY + rad * _m.sin(_m.radians(ang))
        e = walker(lbl, PP5 + mesh, PP5 + 'ABP_Fight_' + abpk, (x, y, 0), W5.STAND, 0.0, scale=sc_, girth=g_, mat=PP5 + 'Materials/MI_Street_' + mat,
                   yaw=ang + 180.0, anim_offset=off)
        fight_actors.append(e)
    both_channels(fight_actors)
    fc_ = spawn(unreal.TargetPoint, (FX, FY, 0), label='FightCenter')
    fight_shots = [
        mkshot(fc_, K5.WIDE, 8, 0, 95, 0, 52, wl=(-120, -1050, 330), label='street fight wide (hero + 6 enemies)'),                           # 0 @0
        mkshot(fc_, K5.WIDE, 8, 0, 95, 0, 48, wl=(-760, -800, 330), label='street fight 3/4'),                                               # 1 @8
        mkshot(fc_, K5.ORBIT, 8, 1000, 95, 230, 48, 16, 250, label='street fight orbit')]                                                      # 2 @16
    save_map(TESTS + '/Char_Fight', fight_shots)

    # ================= Char_Crowd: two-way flow, walkers passing near the camera =================
    CY5 = -1900.0
    L5 = 9000.0
    # round 07 layout (tools/ue_char/crowd/layout_search.py --seed 1 --iters 14000 --flip): (citizen, lane offset dy in cm from the street centre line, start x0 at the
    # start of the shot in cm, direction).  The tracking camera follows x = 0 at 1.1 m/s on the +Y side, 11.5 m from the mid lane; the near lane (dy 690-740) is
    # 4.1-4.6 m from it.  Straight-line paths of every pair stay >= 130 cm apart for 2 s beyond both shots (so the runtime avoidance has nothing to do in them);
    # the mid lane is two-way flow, the near lane walks one way (with the camera) so no two near-lane silhouettes ever overlap on screen; ~11 people in the tracking frame.
    MID7 = [('03_white_tee', 90, -620, 1), ('12_sundress_mom', 80, -180, 1), ('13_construction_worker', -30, 460, 1), ('15_executive', -340, 680, 1),
            ('04_blue_sweatshirt', -320, 530, 1), ('19_marathon_runner', -200, 2110, 1),
            ('10_silver_tie', 300, 650, -1), ('14_teen_skater', -70, 70, -1), ('01_retired_gent', -340, 390, -1), ('20_punk_artist', -240, 60, -1),
            ('18_dapper_elder', 240, 780, -1), ('08_black_suit', -160, 1880, -1)]
    NEAR7 = [('02_leather_jacket', 690, 1370, 1), ('06_chrome_shades', 690, 550, 1), ('16_lumberjack_hipster', 740, 2710, 1),
             ('05_black_tee', 690, -1930, 1), ('17_hijabi_student', 690, -160, 1), ('09_kurta_waistcoat', 720, -10, 1)]
    # the round-06 layout (walkers passing through each other): used ONLY by Char_CrowdAvoid, the engine test of the avoidance itself
    MID6 = [('03_white_tee', 150, -560, 1), ('12_sundress_mom', -140, -160, 1), ('13_construction_worker', 190, 150, 1), ('15_executive', -220, 420, 1),
            ('04_blue_sweatshirt', 60, -820, 1), ('19_marathon_runner', -60, 620, 1),
            ('10_silver_tie', -160, -420, -1), ('14_teen_skater', 200, 20, -1), ('01_retired_gent', -40, 520, -1), ('20_punk_artist', 120, 1050, -1),
            ('18_dapper_elder', -200, 1600, -1), ('08_black_suit', 40, 2200, -1)]
    NEAR6 = [('02_leather_jacket', 690, -230, -1), ('06_chrome_shades', 730, 420, -1), ('16_lumberjack_hipster', 700, 1250, -1),
             ('05_black_tee', 720, -330, 1), ('17_hijabi_student', 680, 160, 1), ('09_kurta_waistcoat', 710, -640, 1)]

    def crowd_map(map_name, mid, near, avoid=True):
        new_stage('Crowd')
        civ5 = []
        for grp, pre in ((mid, 'Citizen_'), (near, 'CitizenNear_')):
            for c, dy, x0, dr in grp:
                wk = CIT_WALK[c]; start = (x0 + L5 / 2) if dr > 0 else (L5 / 2 - x0)
                a = line5(pre + c, ROOT + '/Citizens/SK_Citizen_' + c, ROOT + '/Citizens/ABP_Citizen_' + wk, (0, CY5 + dy, 0), CIT_SPEED[wk], L5, start, yaw=0.0 if dr > 0 else 180.0)
                a.set_editor_property('anim_offset', (0.61803 * (len(civ5) + 1)) % 1.0)   # CH19: gait phases spread by the golden ratio
                if avoid:   # round 07: capsule avoidance (r = 40 cm >= the 35 cm asked for) with 2 s look-ahead; C++ AWHCharLoopWalker::StepAvoidGroup
                    a.set_editor_property('avoid', True); a.set_editor_property('avoid_radius', 40.0)
                civ5.append(a)
        civ_track5 = spawn(unreal.WHCharLoopWalker, (0, CY5, 0), (0, 0, 0), 'Citizens_Track')
        civ_track5.set_editor_property('mode', W5.LINE); civ_track5.set_editor_property('speed', 110.0)
        civ_track5.set_editor_property('line_length', L5); civ_track5.set_editor_property('line_start', L5 / 2)
        cit_center5 = spawn(unreal.TargetPoint, (500, CY5, 0), label='CitizensCenter')
        civ_all5 = civ5 + [civ_track5]
        crowd_shots = [
            mkshot(civ_track5, K5.SIDE, 8, 1150, 100, 45, 64, restart=civ_all5, label='crowd walking past a tracking camera'),                      # 0 @0
            mkshot(cit_center5, K5.WIDE, 6, 0, 110, 0, 50, wl=(-1400, CY5 + 420, 175), restart=civ_all5, label='crowd wide')]                        # 1 @8
        save_map(TESTS + '/' + map_name, crowd_shots)
    crowd_map('Char_Crowd', MID7, NEAR7)
    if 'mapavoid' in STEPS:      # only when asked: telemetry test of the avoidance on the OLD (colliding) layout, nullrhi run, no captures
        crowd_map('Char_CrowdAvoid', MID6, NEAR6)
    log('maps5 ok')

# ------------------------------------------------------------------------------------------------ CH18 chroma-key test maps (round 05, keyer replaced in round 07)
# Round 05/06 keyed the STREET: the street, facades and windows were an unlit pure-green material.  Its bounce light (and the sky light captured from the
# green scene) tinted every garment green, so a `G > R + 40` test flagged whole legs and coats that were perfectly solid (round-06 critic: the rear jeans leg of
# `crowd_key_c_4k`, 19.5k px of "key green" was jeans in shade lit only by the green bounce).  Round 07 keys the PICTURE, not the world: Char_CrowdKey is a
# copy of Char_Crowd (same sun, sky, fog, street: identical lighting) whose citizens write custom-depth STENCIL, and a post-process material
# (before bloom, with the material's own stencil test == 0) replaces every pixel that is not a citizen by the key colour.  A citizen pixel is never modified, so a green pixel
# inside a citizen silhouette is a real hole in the mesh and a garment is never tinted.  Char_CrowdID writes the per-walker stencil id (R = 12 x id) instead
# of the picture: exact per-walker masks (who is in front of whom, a floating polygon's owner).  Needs `r.CustomDepth 3` (capture_r5.sh passes it).
if 'mapkey' in STEPS:
    # UE 5.8 (PostProcessMaterial.cpp): custom stencil cannot be read AFTER tonemapping ("target size differences": the first attempt, SceneTexture lookups at
    # BL_SCENE_COLOR_AFTER_TONEMAPPING, came out with a 90 px smeared border and no key).  So the key material sits BEFORE bloom and uses the material's own stencil test
    # (enable_stencil_test, compare Equal, ref 0): it draws the key colour ONLY where no citizen wrote stencil and never touches a citizen pixel.  Bloom and vignette are
    # switched off in the map's post-process volume so the key colour cannot spill onto a garment; the key level is whatever the tonemapper makes of (0, 1, 0).
    def pick(cls, pred):
        names = [n for n in dir(cls) if n.isupper() and pred(n)]
        log('enum', cls.__name__, '->', names, 'of', [n for n in dir(cls) if n.isupper()][:30])
        return getattr(cls, names[0])

    def build_pp_key(name, ids):
        m = new_material(TESTS + '/Materials', name)
        m.set_editor_property('material_domain', pick(unreal.MaterialDomain, lambda n: 'POST_PROCESS' in n))
        m.set_editor_property('blendable_location', pick(unreal.BlendableLocation, lambda n: n.endswith('BEFORE_BLOOM')))
        if not ids:
            m.set_editor_property('enable_stencil_test', True)
            m.set_editor_property('stencil_compare', pick(unreal.MaterialStencilCompare, lambda n: n.endswith('EQUAL') and not any(k in n for k in ('NOT', 'LESS', 'GREATER'))))
            m.set_editor_property('stencil_ref_value', 0)
            key = E(m, unreal.MaterialExpressionConstant3Vector, -400, 0); key.set_editor_property('constant', unreal.LinearColor(0.0, 1.0, 0.0, 1.0))
            MEL.connect_material_property(key, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        else:       # id colours: id = r + 3 g + 9 b with r, g, b in {0, 1, 2}; output (r, g, b) / 2 (levels 0, .5, 1); background (id 0) black
            sten = E(m, unreal.MaterialExpressionSceneTexture, -1000, 0); sten.set_editor_property('scene_texture_id', pick(unreal.SceneTextureId, lambda n: n == 'PPI_CUSTOM_STENCIL'))
            sten.set_editor_property('filtered', False)
            idn = E(m, unreal.MaterialExpressionComponentMask, -800, 0)
            idn.set_editor_property('r', True); idn.set_editor_property('g', False); idn.set_editor_property('b', False); idn.set_editor_property('a', False)
            MEL.connect_material_expressions(sten, 'Color', idn, '')
            def const(v, x, y):
                c = E(m, unreal.MaterialExpressionConstant, x, y); c.set_editor_property('r', v); return c
            def binop(cls, a_, b_, x, y):
                e = E(m, cls, x, y); MEL.connect_material_expressions(a_, '', e, 'A'); MEL.connect_material_expressions(b_, '', e, 'B'); return e
            def un(cls, a_, x, y):
                e = E(m, cls, x, y); MEL.connect_material_expressions(a_, '', e, ''); return e
            three = const(3.0, -800, 120); nine = const(9.0, -800, 200); half = const(0.5, -800, 280)
            r_ = binop(unreal.MaterialExpressionFmod, idn, three, -600, 0)
            d3 = un(unreal.MaterialExpressionFloor, binop(unreal.MaterialExpressionDivide, idn, three, -700, 100), -500, 100)
            g_ = binop(unreal.MaterialExpressionFmod, d3, three, -400, 100)
            b_ = un(unreal.MaterialExpressionFloor, binop(unreal.MaterialExpressionDivide, idn, nine, -600, 200), -400, 200)
            rgb = []
            for ch, yy in ((r_, 0), (g_, 100), (b_, 200)):
                rgb.append(binop(unreal.MaterialExpressionMultiply, ch, half, -200, yy))
            a1 = E(m, unreal.MaterialExpressionAppendVector, -50, 40); MEL.connect_material_expressions(rgb[0], '', a1, 'A'); MEL.connect_material_expressions(rgb[1], '', a1, 'B')
            a2 = E(m, unreal.MaterialExpressionAppendVector, 100, 80); MEL.connect_material_expressions(a1, '', a2, 'A'); MEL.connect_material_expressions(rgb[2], '', a2, 'B')
            MEL.connect_material_property(a2, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        MEL.recompile_material(m)
        return m

    def key_map(map_name, mat):
        if EAL.does_asset_exist(TESTS + '/' + map_name): EAL.delete_asset(TESTS + '/' + map_name)
        EAL.duplicate_asset(TESTS + '/Char_Crowd', TESTS + '/' + map_name)      # a COPY: Char_Crowd itself must stay untouched
        unreal.EditorLoadingAndSavingUtils.load_map(TESTS + '/' + map_name)
        n_st = 0
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            lab = a.get_actor_label()
            if isinstance(a, unreal.WHCharLoopWalker) and lab.startswith(('Citizen_', 'CitizenNear_')):
                n_st += 1
                mc = a.get_editor_property('mesh')
                mc.set_editor_property('render_custom_depth', True)
                mc.set_editor_property('custom_depth_stencil_value', n_st)     # unique id per walker (1..18); the key material only tests == 0
            elif lab == 'Post':
                st = a.get_editor_property('settings')
                wb = unreal.WeightedBlendable(); wb.set_editor_property('weight', 1.0); wb.set_editor_property('object', mat)
                wbs = unreal.WeightedBlendables(); wbs.set_editor_property('array', [wb])
                st.set_editor_property('weighted_blendables', wbs)
                for ov, val in (('bloom_intensity', 0.0), ('vignette_intensity', 0.0), ('film_grain_intensity', 0.0)):
                    try:
                        st.set_editor_property('override_' + ov, True); st.set_editor_property(ov, val)
                    except Exception as e: log('post setting', ov, 'not set:', str(e)[:80])
                a.set_editor_property('settings', st)
        log(map_name, 'saved', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(), n_st, 'walkers write stencil')

    mk = build_pp_key('M_PP_Key', False); mid_ = build_pp_key('M_PP_KeyID', True)
    EAL.save_directory(TESTS + '/Materials', only_if_is_dirty=True, recursive=True)
    key_map('Char_CrowdKey', mk)
    key_map('Char_CrowdID', mid_)

log('done')
