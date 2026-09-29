# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 Look: idempotent rebuild of /Game/Look and /Game/Tests/Look from committed sources.
#   sources: Scripts/look_presets.json (time-of-day presets), Scripts/city_shots.json (the S1..S8 views),
#            the city content of piece P1 (/Game/City + /Game/Tests/City/City_Midtown_Geo, built by Scripts/build_city.py),
#            the export's collision.json (building boxes for the traversal, <SM2_CITY_EXPORT>/collision.json)
#   run:     tools/perf_ue/rebuild_look.sh [steps] [presets]   (headless, editor closed: UnrealEditor <uproject> -run=pythonscript
#            -script=<this file> -unattended -nullrhi; env SM2_LOOK_STEPS / SM2_LOOK_PRESETS select parts), or in the P4 editor:
#            tools/perf_ue/uejob.py unreal/WebHomage/Scripts/build_look.py [steps=geo,rigs,maps] [presets=midday,golden,night]
# What it owns:
#   /Game/Look/Look_Boxes                invisible traversal building boxes (see step geo); the city geometry level itself is P1's
#   /Game/Look/Rigs/Look_Rig_<preset>    ALL lighting of a preset: SkyAtmosphere, sun (+moon), SkyLight (real-time capture),
#                                        VolumetricCloud, ExponentialHeightFog (+volumetric fog, +haze layer), PostProcessVolume,
#                                        star dome (night), MPC_City night parameters through a Level Sequence (see step rigs)
#   /Game/Tests/Look/Look_Midtown[_golden|_night]     playable maps (traversal game mode): city geometry + Look_Boxes + rig + PlayerStart
#   /Game/Tests/Look/Look_View_<preset>_<S#>          the city shot views (Scripts/city_shots.json) under each preset
import unreal, os, json, math, time

EXPORT = os.environ.get('SM2_CITY_EXPORT', '/Users/midir/sm2-n1/_scratch/look/export/midtown3x3')
HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/Users/midir/sm2-n1/look/unreal/WebHomage/Scripts'
try: ARGS = JOB_ARGS  # noqa: F821 (set by tools/perf_ue/uejob.py)
except NameError: ARGS = {}
STEPS = set((ARGS.get('steps') or os.environ.get('SM2_LOOK_STEPS') or 'geo,rigs,maps').split(','))
PRESETS_JSON = json.load(open(os.path.join(HERE, 'look_presets.json')))
ORDER = [p for p in PRESETS_JSON['order'] if p in (ARGS.get('presets') or os.environ.get('SM2_LOOK_PRESETS') or ','.join(PRESETS_JSON['order'])).split(',')]
PRE = PRESETS_JSON['presets']
SHOTS = json.load(open(os.path.join(HERE, 'city_shots.json')))
CITY_GEO = '/Game/Tests/City/City_Midtown_Geo'
LOOK, RIGS, TESTS = '/Game/Look', '/Game/Look/Rigs', '/Game/Tests/Look'
MPC = '/Game/City/Materials/MPC_City'
EAL = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
T0 = time.time()
MISS = []
def log(*a): print('[build_look %5.0fs]' % (time.time() - T0), *a)

# ------------------------------------------------------------------------------------------------ helpers
def conv(v):
    """json value -> unreal value (lists of 3/4 numbers become LinearColor)"""
    if isinstance(v, list) and len(v) in (3, 4) and all(isinstance(x, (int, float)) for x in v):
        return unreal.LinearColor(*[float(x) for x in v]) if len(v) == 4 else unreal.Vector(*[float(x) for x in v])
    return v

ALIAS = {'aerial_perspective_distance_scale': 'aerial_pespective_view_distance_scale',  # (sic) the engine property name has a typo
         'volumetric_fog': 'enable_volumetric_fog'}
def fix_type(name, v):
    if isinstance(v, unreal.LinearColor):
        if name.endswith('albedo'): return unreal.Color(*[int(round(255 * c)) for c in (v.r, v.g, v.b, v.a)])
        if name.startswith('color_'): return unreal.Vector4(v.r, v.g, v.b, v.a)
    return v
def setp(obj, name, value, what=''):
    """set_editor_property that never aborts the build: unknown / rejected properties are collected in MISS"""
    name = ALIAS.get(name, name); value = fix_type(name, value)
    try:
        obj.set_editor_property(name, value); return True
    except Exception as e:
        MISS.append('%s.%s (%s)' % (what or type(obj).__name__, name, str(e).split('\n')[0][:90])); return False

def U(x, y, z): return unreal.Vector(x * 100.0, z * 100.0, y * 100.0)  # browser metres (x east, y up, z south) -> UE cm

def look_rot(p, t):
    d = unreal.Vector(t.x - p.x, t.y - p.y, t.z - p.z)
    return unreal.Rotator(roll=0.0, pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x)))

def sun_rotator(elev, az):
    """light travel direction for a sun at elevation elev above the horizon, compass azimuth az (clockwise from north, east = 90).
    UE frame of the city export: X east, Y south (north = -Y), Z up."""
    e, a = math.radians(elev), math.radians(az)
    to_sun = (math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))
    d = tuple(-c for c in to_sun)
    return unreal.Rotator(roll=0.0, pitch=math.degrees(math.asin(max(-1.0, min(1.0, d[2])))), yaw=math.degrees(math.atan2(d[1], d[0])))

def spawn(cls, loc=unreal.Vector(0, 0, 0), rot=unreal.Rotator(0, 0, 0), label=None, folder=None):
    a = eas.spawn_actor_from_class(cls, loc, rot)
    if label: a.set_actor_label(label)
    if folder: a.set_folder_path(folder)
    return a

KEEP = ('WorldSettings', 'Brush', 'DefaultPhysicsVolume', 'GameplayDebuggerCategoryReplicator', 'WorldDataLayers', 'WorldPartitionMiniMap')
def open_level(path):
    """idempotent: an existing map is opened and emptied (deleting maps pops a modal dialog), else created"""
    if EAL.does_asset_exist(path):
        unreal.EditorLoadingAndSavingUtils.load_map(path)
        for a in eas.get_all_level_actors():
            if a.get_class().get_name() not in KEEP: eas.destroy_actor(a)
    else:
        les.new_level(path)
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

def open_level_keep(path):
    unreal.EditorLoadingAndSavingUtils.load_map(path)
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

# ------------------------------------------------------------------------------------------------ step geo
# Prepares the city geometry (P1's City_Midtown_Geo, patched IN PLACE in this worktree's content) and builds Look_Boxes for the
# traversal hero (piece P3): its world queries index every WorldStatic primitive by its bounds as a "building box".
#  * every city component becomes WorldDynamic (still blocks traces and the camera): a merged 256 m facade tile or a whole-city
#    instanced prop component would otherwise be one giant solid;
#  * the bare ground (asphalt, sidewalks, water) is tagged WHGround (floor that never holds a web);
#  * /Game/Look/Look_Boxes: the browser's own collision boxes (collision.json: wall / glass / hero / spire / bulkhead / watertower)
#    as invisible WorldStatic box actors = the building boxes of the traversal (anchors, wall-run, perch points, capsule push-out).
# Re-run this step after every Scripts/build_city.py run (it recreates the city level).
BOX_KINDS = {0: 'wall', 7: 'bulkhead', 8: 'watertower', 13: 'spire', 14: 'hero', 17: 'glass'}
BOXES = LOOK + '/Look_Boxes'
def build_geo():
    if not EAL.does_asset_exist(CITY_GEO): raise RuntimeError('city geometry level missing: run Scripts/build_city.py first')
    world = open_level_keep(CITY_GEO)
    n_dyn = n_gnd = 0
    for a in eas.get_all_level_actors():
        if a.get_class().get_name() in KEEP: continue
        lab = a.get_actor_label()
        for c in a.get_components_by_class(unreal.PrimitiveComponent):
            c.set_collision_object_type(unreal.CollisionChannel.ECC_WORLD_DYNAMIC); n_dyn += 1
        if lab.startswith(('asphalt', 'sidewalk')) or lab == 'WaterPlane':
            a.tags = [unreal.Name('WHGround')]; n_gnd += 1
    les.save_current_level()
    world = open_level(BOXES)
    C = json.load(open(os.path.join(EXPORT, 'collision.json')))
    cube = unreal.load_asset('/Engine/BasicShapes/Cube')
    n_box = 0
    for s in C['solids']:
        if s['t'] != 0 or s['k'] not in BOX_KINDS: continue
        x0, y0, z0, x1, y1, z1 = s['bb']  # browser metres: x east, y up, z south
        if (y1 - y0) < 3.0 or ((x1 - x0) < 1.2 and (z1 - z0) < 1.2): continue
        a = eas.spawn_actor_from_class(unreal.StaticMeshActor, U((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
        a.set_actor_label('WHBox_%d' % n_box); a.set_folder_path('Look/TraversalBoxes')
        c = a.static_mesh_component; c.set_static_mesh(cube)
        a.set_actor_scale3d(unreal.Vector((x1 - x0), (z1 - z0), (y1 - y0)))  # the cube is 100 cm: scale = size in metres
        c.set_collision_profile_name('BlockAll'); c.set_visibility(False); c.set_cast_shadow(False)
        a.set_mobility(unreal.ComponentMobility.STATIC)
        n_box += 1
    unreal.EditorLoadingAndSavingUtils.save_map(world, BOXES)
    log('geo: %d components -> WorldDynamic, %d ground actors tagged, %d traversal boxes in %s' % (n_dyn, n_gnd, n_box, BOXES))

# ------------------------------------------------------------------------------------------------ step rigs
def build_rig(name):
    P = PRE[name]
    path = '%s/Look_Rig_%s' % (RIGS, name)
    world = open_level(path)
    sun_d, moon_d = P['sun'], P.get('moon')
    # --- sun (atmosphere sun light 0). Physical units: illuminance in lux, exposure comes from the post volume.
    sun = spawn(unreal.DirectionalLight, unreal.Vector(0, 0, 50000), sun_rotator(sun_d['elev'], sun_d['az']), 'Sun', 'Lighting')
    lc = sun.light_component
    lc.set_mobility(unreal.ComponentMobility.MOVABLE)
    for k, v in (('intensity', sun_d['lux']), ('use_temperature', True), ('temperature', sun_d['temp']), ('light_source_angle', sun_d['angle']),
                 ('atmosphere_sun_light', True), ('atmosphere_sun_light_index', 0), ('cast_shadows', True), ('cast_volumetric_shadow', True),
                 ('cast_cloud_shadows', bool(sun_d.get('cloud_shadows', True))), ('cloud_shadow_strength', 0.8), ('per_pixel_atmosphere_transmittance', True),
                 ('atmosphere_sun_disk_color_scale', unreal.LinearColor(sun_d.get('disk', 1.0), sun_d.get('disk', 1.0), sun_d.get('disk', 1.0), 1.0))):
        setp(lc, k, v, 'Sun')
    if moon_d:
        moon = spawn(unreal.DirectionalLight, unreal.Vector(0, 0, 50000), sun_rotator(moon_d['elev'], moon_d['az']), 'Moon', 'Lighting')
        mc = moon.light_component; mc.set_mobility(unreal.ComponentMobility.MOVABLE)
        for k, v in (('intensity', moon_d['lux']), ('use_temperature', True), ('temperature', moon_d['temp']), ('light_source_angle', moon_d['angle']),
                     ('atmosphere_sun_light', True), ('atmosphere_sun_light_index', 1), ('cast_shadows', True), ('cast_volumetric_shadow', True),
                     ('cast_cloud_shadows', False), ('per_pixel_atmosphere_transmittance', True)):
            setp(mc, k, v, 'Moon')
    # --- sky atmosphere (aerial perspective) + real-time captured sky light
    sa = spawn(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), label='SkyAtmosphere', folder='Lighting')
    for k, v in P['atmosphere'].items():
        if k == 'ground_albedo': v = unreal.Color(*[int(x) for x in v])
        else: v = conv(v)
        setp(sa.get_component_by_class(unreal.SkyAtmosphereComponent), k, v, 'SkyAtmosphere')
    sl = spawn(unreal.SkyLight, unreal.Vector(0, 0, 3000), label='SkyLight', folder='Lighting')
    slc = sl.light_component
    slc.set_mobility(unreal.ComponentMobility.MOVABLE)
    for k, v in (('real_time_capture', True), ('intensity', P['sky']['intensity']), ('cloud_ambient_occlusion', False),
                 ('light_color', unreal.Color(*[int(255 * c) for c in P['sky']['tint']] + [255])), ('lower_hemisphere_is_black', False)):
        setp(slc, k, v, 'SkyLight')
    # --- volumetric clouds
    vc = spawn(unreal.VolumetricCloud, unreal.Vector(0, 0, 0), label='Clouds', folder='Lighting')
    vcc = vc.get_component_by_class(unreal.VolumetricCloudComponent)
    cl = P['clouds']
    mat = unreal.load_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst')
    if mat: setp(vcc, 'material', mat, 'Clouds')
    else: MISS.append('Clouds: m_SimpleVolumetricCloud_Inst missing')
    for k in ('layer_bottom_altitude', 'layer_height', 'tracing_max_distance'): setp(vcc, k, float(cl[k]), 'Clouds')
    setp(vcc, 'view_sample_count_scale', 0.6, 'Clouds'); setp(vcc, 'shadow_view_sample_count_scale', 0.3, 'Clouds')
    setp(vcc, 'reflection_view_sample_count_scale_value', 0.5, 'Clouds')
    # --- exponential height fog: near-clear canyon, aerial haze band, volumetric fog for light shafts, a second high haze layer
    fog = spawn(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), label='HeightFog', folder='Lighting')
    fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    for k, v in P['fog'].items():
        if k == 'haze':
            sf = fc.get_editor_property('second_fog_data')
            for hk, hv in v.items(): setp(sf, hk, hv, 'Fog.second')
            setp(fc, 'second_fog_data', sf, 'Fog')
        else:
            setp(fc, k, conv(v), 'Fog')
    # --- post process: exposure, Lumen, bloom / lens, filmic tonemapper, grade, motion blur, AO
    ppv = spawn(unreal.PostProcessVolume, unreal.Vector(0, 0, 0), label='PostProcess', folder='Lighting')
    ppv.set_editor_property('unbound', True); ppv.set_editor_property('priority', 10.0)
    st = ppv.get_editor_property('settings')
    ex = P['exposure']
    post = {'auto_exposure_min_brightness': ex['min_ev'], 'auto_exposure_max_brightness': ex['max_ev'],
            'auto_exposure_bias': ex['bias'], 'auto_exposure_speed_up': 6.0, 'auto_exposure_speed_down': 3.0, 'auto_exposure_low_percent': 70.0,
            'auto_exposure_high_percent': 98.0, 'auto_exposure_apply_physical_camera_exposure': False,
            'ambient_occlusion_quality': 60.0, 'ambient_occlusion_power': 1.6}
    for k, en, names in (('auto_exposure_method', 'AutoExposureMethod', ('AEM_HISTOGRAM',)), ('dynamic_global_illumination_method', 'DynamicGlobalIlluminationMethod', ('LUMEN', 'DGIM_LUMEN')),
                         ('reflection_method', 'ReflectionMethod', ('LUMEN', 'RM_LUMEN')), ('bloom_method', 'BloomMethod', ('BM_SOG',))):
        cls = getattr(unreal, en, None); v = next((getattr(cls, n) for n in names if cls is not None and hasattr(cls, n)), None)
        if v is None: MISS.append('enum %s.%s missing' % (en, names))
        else: post[k] = v
    for k, v in P['post'].items(): post[k] = conv(v) if isinstance(v, list) else v
    for k, v in post.items():
        if setp(st, 'override_' + k, True, 'PostProcess'): setp(st, k, v, 'PostProcess')
    ppv.set_editor_property('settings', st)
    # --- night: procedural star dome (additive, unlit) so the sky is not an empty black gradient
    if P['mpc'].get('NightK', 0.0) > 0.5: build_stars()
    # --- MPC_City through a Level Sequence (auto-plays at level start): night lights of the city materials
    build_mpc_sequence(name, P['mpc'], world)
    unreal.EditorLoadingAndSavingUtils.save_map(world, path)
    log('rig', name)

def build_stars():
    MAT_PATH = LOOK + '/M_LookStars'
    mel = unreal.MaterialEditingLibrary
    if EAL.does_asset_exist(MAT_PATH): EAL.delete_asset(MAT_PATH)
    m = unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_LookStars', LOOK, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT); m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
    m.set_editor_property('two_sided', True)
    code = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -600, 0)
    code.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    ci = unreal.CustomInput(); ci.set_editor_property('input_name', 'D'); code.set_editor_property('inputs', [ci])
    code.set_editor_property('code', r"""
float3 d = normalize(D);
float3 g = d * 260.0; float3 c = floor(g); float3 f = frac(g) - 0.5;
float h = frac(sin(dot(c, float3(12.9898, 78.233, 37.719))) * 43758.5453);
float h2 = frac(h * 91.7 + 0.31);
float star = step(0.9935, h) * smoothstep(0.42, 0.0, length(f));
float3 tint = lerp(float3(0.75, 0.85, 1.0), float3(1.0, 0.85, 0.7), h2);
float horizon = smoothstep(0.02, 0.35, d.z);
return tint * star * (0.4 + 1.6 * h2) * horizon * 6.0;""")
    wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, 0)
    cam = mel.create_material_expression(m, unreal.MaterialExpressionCameraPositionWS, -900, 120)
    sub = mel.create_material_expression(m, unreal.MaterialExpressionSubtract, -750, 0)
    mel.connect_material_expressions(wp, '', sub, 'A'); mel.connect_material_expressions(cam, '', sub, 'B')
    mel.connect_material_expressions(sub, '', code, 'D')
    mel.connect_material_property(code, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m); EAL.save_asset(MAT_PATH)
    dome = spawn(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), label='StarDome', folder='Lighting')
    dome.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Sphere'))
    dome.static_mesh_component.set_material(0, m)
    dome.set_actor_scale3d(unreal.Vector(6000, 6000, 6000))  # 300 km radius: outside the atmosphere shell, inside the far plane
    dome.static_mesh_component.set_cast_shadow(False)
    dome.static_mesh_component.set_collision_profile_name('NoCollision')  # a 600 km WorldStatic sphere would be one giant traversal "building box"
    dome.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    dome.static_mesh_component.set_editor_property('cast_dynamic_shadow', False)

def build_mpc_sequence(name, values, world):
    """MPC_City parameter values of the preset, applied at level start by a Level Sequence with an MPC track (holds the values)."""
    mpc = unreal.load_asset(MPC)
    if not mpc: MISS.append('MPC_City missing'); return
    seq_path = '%s/LS_Look_%s' % (RIGS, name)
    if EAL.does_asset_exist(seq_path): EAL.delete_asset(seq_path)
    seq = unreal.AssetToolsHelpers.get_asset_tools().create_asset('LS_Look_' + name, RIGS, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    try:
        seq.set_display_rate(unreal.FrameRate(30, 1)); seq.set_playback_start(0); seq.set_playback_end(30 * 60)
        tr = seq.add_track(unreal.MovieSceneMaterialParameterCollectionTrack)
        tr.set_editor_property('mpc', mpc)
        sec = tr.add_section()
        sec.set_range(0, 30 * 60)
        for k, v in values.items():
            sec.add_scalar_parameter_key(k, unreal.FrameNumber(0), float(v))
        EAL.save_asset(seq_path)
        act = spawn(unreal.LevelSequenceActor, unreal.Vector(0, 0, 0), label='MPC_City_' + name, folder='Lighting')
        act.set_editor_property('level_sequence_asset', seq)
        ps = act.get_editor_property('playback_settings'); ps.set_editor_property('auto_play', True); ps.set_editor_property('loop_count', unreal.MovieSceneSequenceLoopCount(value=-1))
        act.set_editor_property('playback_settings', ps)
    except Exception as e:
        MISS.append('mpc sequence %s: %s' % (name, str(e).split('\n')[0][:160]))

# ------------------------------------------------------------------------------------------------ step maps
def rig_path(name): return '%s/Look_Rig_%s' % (RIGS, name)

def add_sublevels(world, name, boxes=False):
    for lp in (CITY_GEO, BOXES, rig_path(name)):
        if lp == BOXES and not (boxes and EAL.does_asset_exist(BOXES)): continue
        if not any(lp.split('/')[-1] in l.get_path_name() for l in unreal.EditorLevelUtils.get_levels(world)):
            unreal.EditorLevelUtils.add_level_to_world(world, lp, unreal.LevelStreamingAlwaysLoaded)
    les.set_current_level_by_name(str(world.get_name()))

def build_maps():
    EAL.make_directory(TESTS)
    trav_gm = unreal.load_class(None, '/Script/WebHomage.WebTravGameMode')
    ps = SHOTS[0]['player']
    for name in ORDER:
        mp = 'Look_Midtown' if name == ORDER[0] and name == 'midday' else 'Look_Midtown_' + name
        world = open_level('%s/%s' % (TESTS, mp))
        add_sublevels(world, name, boxes=True)
        spawn(unreal.PlayerStart, U(ps[0], ps[1] + 1.0, ps[2]), unreal.Rotator(0, 0, -90), 'PlayerStart')
        if trav_gm: world.get_world_settings().set_editor_property('default_game_mode', trav_gm)
        else: MISS.append('WebTravGameMode class missing (build the C++ module)')
        unreal.EditorLoadingAndSavingUtils.save_map(world, '%s/%s' % (TESTS, mp))
        log('map', mp)
        for s in SHOTS:
            mv = '%s/Look_View_%s_%s' % (TESTS, name, s['id'].split('_')[0])
            world = open_level(mv)
            add_sublevels(world, name)
            sp = s.get('player', ps)
            spawn(unreal.PlayerStart, U(sp[0], sp[1] + 1.0, sp[2]), unreal.Rotator(0, 0, -90), 'PlayerStart')
            p, t = U(*s['pos']), U(*s['target'])
            ca = spawn(unreal.CameraActor, p, look_rot(p, t), 'ShotCam_' + s['id'])
            ca.camera_component.set_editor_property('field_of_view', s.get('fov', 70))
            ca.camera_component.set_editor_property('constrain_aspect_ratio', False)
            ca.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.PLAYER0)
            unreal.EditorLoadingAndSavingUtils.save_map(world, mv)
        log('views', name)

# ------------------------------------------------------------------------------------------------ run
EAL.make_directory(RIGS)
if 'geo' in STEPS: build_geo()
if 'rigs' in STEPS:
    for n in ORDER: build_rig(n)
if 'maps' in STEPS: build_maps()
if MISS: log('WARNINGS (%d):' % len(MISS)); [print('   ', m) for m in MISS]
log('DONE')
