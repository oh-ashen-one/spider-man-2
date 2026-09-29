# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# Piece C (integrated Manhattan map): idempotent, headless rebuild of every piece's Unreal content in dependency order,
# then /Game/Maps/Manhattan (+ _Midday / _Night / _View_S1|S2|S4 / _Actors).
#
# Two modes in one file:
#   * plain python3 (orchestrator, run from anywhere, YOUR editor closed):
#         python3 unreal/WebHomage/Scripts/build_manhattan.py [--steps a,b,...]
#     steps (default = all, always run in this order):
#         cpp          Scripts/build_editor.sh (C++ module)
#         city_export  vite on :5208 (this worktree) + tools/export/export_city.mjs -> <SCR>/export/midtown3x3
#         city_prep    P1 tools: patch_export, prep_textures (IP sanitiser), gen_street_signs, street_kit, street_props, gen_shaders
#         city         P1 Scripts/build_city.py headless: pass 1 clean,tex,mat,mesh,proto,map; pass 2 kit (needs the geo level)
#         traversal    P3 Scripts/build_traversal.py headless (HeroDev hero + clips + Trav_Canyon)
#         characters   P2 Scripts/build_characters.py headless WITHOUT its prep step, on a staged copy of P2's derived inputs
#                      (see stage_characters: P2's build hard-codes its own worktree + scratch paths)
#         look         P4 Scripts/build_look.py headless: geo (traversal boxes, city components WorldDynamic), rigs, maps
#         map          this file inside Unreal (commandlet): /Game/Maps/Manhattan*
#     Every Unreal process is a headless commandlet (-nullrhi -RenderOffScreen -NoSound) of THIS worktree's project and waits
#     while 3+ Unreal instances run (RULES.md).
#   * inside Unreal (-run=pythonscript -script=<this file>): builds the maps (step 'map'). Env SM2_MANHATTAN_PRESETS.
#
# What the map is (all sublevels always loaded; nothing here is committed as .umap, see unreal/WebHomage/CONTENT.md):
#   /Game/Maps/Manhattan            persistent: City_Midtown_Geo (P1, patched by P4 geo) + Look_Boxes (P4) + Look_Rig_golden (P4)
#                                   + Manhattan_Actors; game mode WebTravGameMode (P3 hero, HeroDev mesh + UWebTravAnimInstance)
#   /Game/Maps/Manhattan_Midday, Manhattan_Night    the same with the midday / night rig (switch = open the other map)
#   /Game/Maps/Manhattan_Actors     PlayerStart on the avenue (x 249, y 178 m, facing north) + street people (P2 walkers)
#   /Game/Maps/Manhattan_View_<S1|S2|S4>   golden map + the P1 shot camera (Scripts/city_shots.json), for stills
import os, sys, json, subprocess, time, shutil

HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/Users/midir/sm2-n1/manhattan/unreal/WebHomage/Scripts'
PROJ = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(PROJ))
UPROJECT = os.path.join(PROJ, 'WebHomage.uproject')
UE = '/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
SCR = os.environ.get('SM2_MANHATTAN_SCR', '/Users/midir/sm2-n1/_scratch/manhattan')
EXPORT = os.path.join(SCR, 'export', 'midtown3x3')
TEX = os.path.join(SCR, 'tex')
CHAR_STAGE = os.path.join(SCR, 'chars')
DEV_PORT = 5208
STEPS_ALL = ['cpp', 'city_export', 'city_prep', 'city', 'traversal', 'characters', 'look', 'map']
PRESETS = ['golden', 'midday', 'night']
VIEWS = ['S1', 'S2', 'S4']

try:
    import unreal  # noqa: F401
    IN_UE = hasattr(unreal, 'EditorAssetLibrary')  # (a bare 'unreal/' folder in the cwd imports as an empty namespace package)
except ImportError:
    IN_UE = False


# ================================================================================================ orchestrator (plain python3)
def log(*a):
    print('[build_manhattan %s]' % time.strftime('%H:%M:%S'), *a, flush=True)


def sh(cmd, cwd=WT, env=None, log_name=None):
    log('$', cmd if isinstance(cmd, str) else ' '.join(cmd))
    out = open(os.path.join(SCR, 'logs', log_name), 'w') if log_name else None
    r = subprocess.run(cmd, cwd=cwd, env={**os.environ, **(env or {})}, shell=isinstance(cmd, str),
                       stdout=out or None, stderr=subprocess.STDOUT if out else None)
    if r.returncode != 0:
        raise SystemExit('command failed (%d): %s%s' % (r.returncode, cmd, ('  log: ' + out.name) if out else ''))


def safe_rmtree(p):
    """hard limit (RULES.md): deletes only inside this worktree or this piece's scratch dir"""
    p = os.path.realpath(p)
    if not (p.startswith(WT + '/') or p.startswith(SCR + '/')):
        raise SystemExit('refusing to delete outside the worktree / scratch: ' + p)
    if os.path.isdir(p): shutil.rmtree(p)


def wait_slot():
    while True:
        n = subprocess.run("pgrep -f 'MacOS/UnrealEditor( |$)' | wc -l", shell=True, capture_output=True, text=True).stdout.strip()
        if int(n or 0) < 3: return
        log('3+ Unreal instances running, waiting 60 s'); time.sleep(60)


def ue_python(name, code, env=None, timeout=7200):
    """run python code in a headless commandlet of THIS worktree's project; fails on a Python error in the log"""
    if subprocess.run(['pgrep', '-f', UPROJECT], capture_output=True).returncode == 0:
        raise SystemExit('an Unreal process of this worktree is running; stop it first: pkill -9 -f "%s"' % UPROJECT)
    jobs = os.path.join(SCR, 'jobs'); os.makedirs(jobs, exist_ok=True)
    job = os.path.join(jobs, name + '.py')
    open(job, 'w').write(code)
    lg = os.path.join(SCR, 'logs', name + '.log')
    wait_slot()
    log('UE commandlet', name, '-> log', lg)
    t0 = time.time()
    with open(lg + '.stdout', 'w') as so:
        r = subprocess.run([UE, UPROJECT, '-run=pythonscript', '-script=' + job, '-unattended', '-nullrhi', '-nosplash', '-RenderOffScreen',
                            '-NoSound', '-NoCrashReports', '-abslog=' + lg], env={**os.environ, **(env or {})}, stdout=so, stderr=subprocess.STDOUT,
                           timeout=timeout)
    txt = open(lg, errors='replace').read() if os.path.exists(lg) else ''
    bad = [l for l in txt.splitlines() if 'LogPython: Error' in l or 'Traceback' in l]
    log('UE commandlet %s: rc %d, %.0f s, %d python error lines' % (name, r.returncode, time.time() - t0, len(bad)))
    if bad:
        print('\n'.join(bad[:30]))
        raise SystemExit('python error in ' + name + ' (log ' + lg + ')')
    return txt


def exec_wrapper(script, prelude):
    """code that sets globals (JOB_ARGS / ARGS / __file__) and runs a piece's build script unchanged"""
    return '%s\n__file__ = %r\nexec(compile(open(__file__).read(), __file__, "exec"))\n' % (prelude, script)


def step_cpp():
    sh([os.path.join(HERE, 'build_editor.sh')], log_name='build_editor.log')


def step_city_export():
    import urllib.request
    try:
        urllib.request.urlopen('http://127.0.0.1:%d/' % DEV_PORT, timeout=3)
    except Exception:
        if not os.path.isdir(os.path.join(WT, 'node_modules')): sh('npm ci', log_name='npm.log')
        subprocess.Popen('nohup npx vite --port %d --host 127.0.0.1 --strictPort > %s/logs/vite.log 2>&1 &' % (DEV_PORT, SCR), shell=True, cwd=WT)
        time.sleep(6)
    sh(['node', 'tools/export/export_city.mjs', '--url', 'http://127.0.0.1:%d/' % DEV_PORT, '--out', EXPORT,
        '--profile', os.path.join(SCR, 'chrome-profile')], log_name='city_export.log')


def step_city_prep():
    man = os.path.join(EXPORT, 'manifest.json')
    s = open(man).read()
    open(man, 'w').write(s.replace('127.0.0.1:%d/' % DEV_PORT, '127.0.0.1:5202/'))  # P1 tools key texture paths on '5202/'
    e = EXPORT + '/'
    sh(['python3', 'tools/export/patch_export.py', EXPORT], log_name='city_patch_export.log')
    sh(['python3', 'tools/export/prep_textures.py', TEX, man], log_name='city_prep_textures.log')
    sh(['python3', 'tools/export/gen_street_signs.py', os.path.join(TEX, 'street_signs.png')], log_name='city_street_signs.log')
    sh(['python3', 'tools/export/street_kit.py', e], log_name='city_street_kit.log')
    sh(['python3', 'tools/export/street_props.py', e], log_name='city_street_props.log')
    sh(['node', 'tools/export/gen_shaders.mjs'], log_name='city_gen_shaders.log')  # regenerates the committed Shaders/City/*.ush


# In a -run=pythonscript commandlet StaticMeshEditorSubsystem is None until its module is loaded (build_city.py assumes an editor).
LOAD_SME = 'import unreal\nunreal.SystemLibrary.execute_console_command(None, "Module Load StaticMeshEditor")\n'


def step_city():
    env = {'SM2_CITY_EXPORT': EXPORT, 'SM2_CITY_TEX': TEX}
    bc = os.path.join(HERE, 'build_city.py')
    ue_python('city_pass1', exec_wrapper(bc, LOAD_SME + 'JOB_ARGS = {"steps": "clean,tex,mat,mesh,proto,map"}'), env)
    ue_python('city_pass2_kit', exec_wrapper(bc, LOAD_SME + 'JOB_ARGS = {"steps": "kit"}'), env)


def step_traversal():
    ue_python('traversal', exec_wrapper(os.path.join(HERE, 'build_traversal.py'), ''))


P2_WT = '/Users/midir/sm2-n1/characters'
P2_SCR = '/Users/midir/sm2-n1/_scratch/characters'


def stage_characters():
    """P2's build hard-codes WT=/Users/midir/sm2-n1/characters and _scratch/characters for its derived (git-ignored) inputs, and its
    prep step writes into both. Piece C never runs that prep: it copies (read-only) P2's current derived inputs into its own scratch."""
    src_art, src_glb = os.path.join(P2_WT, 'art/night1/characters'), os.path.join(P2_SCR, 'ueimport')
    for p in (src_art, src_glb):
        if not os.path.isdir(p): raise SystemExit('P2 derived inputs missing (run P2 prep in its own worktree first): ' + p)
    os.makedirs(CHAR_STAGE, exist_ok=True)
    sh(['rsync', '-a', '--delete', src_art + '/', os.path.join(CHAR_STAGE, 'art') + '/'], log_name='chars_stage_art.log')
    sh(['rsync', '-a', '--delete', '--exclude', 'citizens', src_glb + '/', os.path.join(CHAR_STAGE, 'ueimport') + '/'], log_name='chars_stage_glb.log')
    head = subprocess.run(['git', '-C', P2_WT, 'log', '-1', '--format=%h %s'], capture_output=True, text=True).stdout.strip()
    json.dump({'p2_head': head, 'staged_at': time.strftime('%Y-%m-%d %H:%M:%S')}, open(os.path.join(CHAR_STAGE, 'STAGED.json'), 'w'))
    log('staged P2 inputs from', head)


def step_characters():
    stage_characters()
    for d in ('Content/Characters', 'Content/Tests/Characters'):  # P2's own headless wrapper wipes these on disk first
        safe_rmtree(os.path.join(PROJ, d))
    src = open(os.path.join(HERE, 'build_characters.py')).read()
    subs = [("WT = '/Users/midir/sm2-n1/characters'", 'WT = %r' % WT),
            ("ART = WT + '/art/night1/characters'", 'ART = %r' % os.path.join(CHAR_STAGE, 'art')),
            ("GLB = '/Users/midir/sm2-n1/_scratch/characters/ueimport'", 'GLB = %r' % os.path.join(CHAR_STAGE, 'ueimport')),
            ("CIT_TMP = '/Users/midir/sm2-n1/_scratch/characters/ueimport/citizens'", 'CIT_TMP = %r' % os.path.join(CHAR_STAGE, 'ueimport', 'citizens'))]
    for a, b in subs:
        if src.count(a) != 1: raise SystemExit('build_characters.py changed (cannot relocate): ' + a)
        src = src.replace(a, b)
    patched = os.path.join(SCR, 'jobs', 'build_characters_relocated.py')
    os.makedirs(os.path.dirname(patched), exist_ok=True); open(patched, 'w').write(src)
    ue_python('characters', exec_wrapper(patched, 'ARGS = {"steps": "clean,tex,mat,mesh,citizens,rename,abp,map"}'))


def step_look():
    env = {'SM2_CITY_EXPORT': EXPORT, 'SM2_LOOK_STEPS': 'geo,rigs,maps', 'SM2_LOOK_PRESETS': 'midday,golden,night'}
    ue_python('look', exec_wrapper(os.path.join(HERE, 'build_look.py'), ''), env)


def step_map():
    txt = ue_python('manhattan_map', exec_wrapper(os.path.abspath(__file__), ''), {'SM2_MANHATTAN_PRESETS': ','.join(PRESETS)})
    for l in txt.splitlines():
        if '[manhattan' in l: print(l.split('LogPython: ')[-1])


def main():
    import argparse
    ap = argparse.ArgumentParser(description='Piece C: rebuild all piece content + /Game/Maps/Manhattan (headless)')
    ap.add_argument('--steps', default=','.join(STEPS_ALL))
    a = ap.parse_args()
    want = a.steps.split(',')
    bad = [s for s in want if s not in STEPS_ALL]
    if bad: raise SystemExit('unknown steps %s (known: %s)' % (bad, STEPS_ALL))
    os.makedirs(os.path.join(SCR, 'logs'), exist_ok=True)
    t0 = time.time()
    for s in STEPS_ALL:
        if s in want:
            log('=== step', s); t = time.time()
            globals()['step_' + s]()
            log('=== step %s done in %.0f s' % (s, time.time() - t))
    log('all done in %.0f s' % (time.time() - t0))


# ================================================================================================ inside Unreal: the maps
def build_maps():
    import math
    EAL = unreal.EditorAssetLibrary
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    T0 = time.time()
    MISS = []

    def mlog(*a): print('[manhattan %5.0fs]' % (time.time() - T0), *a)

    MAPS = '/Game/Maps'
    ACTORS = MAPS + '/Manhattan_Actors'
    CITY_GEO = '/Game/Tests/City/City_Midtown_Geo'
    BOXES = '/Game/Look/Look_Boxes'
    RIG = '/Game/Look/Rigs/Look_Rig_%s'
    CH = '/Game/Characters'
    SHOTS = {s['id'].split('_')[0]: s for s in json.load(open(os.path.join(HERE, 'city_shots.json')))}
    presets = [p for p in os.environ.get('SM2_MANHATTAN_PRESETS', ','.join(PRESETS)).split(',') if p]
    for need in (CITY_GEO, BOXES) + tuple(RIG % p for p in presets):
        if not EAL.does_asset_exist(need): raise RuntimeError('missing piece content %s (run the earlier steps)' % need)
    KEEP = ('WorldSettings', 'Brush', 'DefaultPhysicsVolume', 'GameplayDebuggerCategoryReplicator', 'WorldDataLayers', 'WorldPartitionMiniMap')

    def open_level(path):
        """idempotent: an existing map is opened and emptied (deleting maps pops a modal dialog), else created"""
        if EAL.does_asset_exist(path):
            unreal.EditorLoadingAndSavingUtils.load_map(path)
            for a in eas.get_all_level_actors():  # only this map's own actors, never the always-loaded sublevels' (city, rig, boxes)
                if a.get_class().get_name() not in KEEP and a.get_path_name().startswith(path + '.'): eas.destroy_actor(a)
        else:
            les.new_level(path)
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

    def U(x, y, z): return unreal.Vector(x * 100.0, y * 100.0, z * 100.0)  # UE metres (X east, Y south, Z up) -> cm

    def spawn(cls, loc, yaw=0.0, label=None, folder=None):
        a = eas.spawn_actor_from_class(cls, loc, unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        if label: a.set_actor_label(label)
        if folder: a.set_folder_path(folder)
        return a

    # ---------------------------------------------------------------- street people + player start (one sublevel shared by every map)
    open_level(ACTORS)
    ps = SHOTS['S1']['player']  # browser metres [x, y, z] -> UE (x, z, y)
    spawn(unreal.PlayerStart, U(ps[0], ps[2], ps[1] + 1.0), -90.0, 'PlayerStart', 'Manhattan')
    W = unreal.WHCharLoopWalker
    WM = unreal.WHWalkerMode
    SIDEWALK_Z = 0.15  # P1 sidewalk top (browser y 0.15 m); avenue x 239..261 m, sidewalks x 234.5..239 (west) / 261..265.5 (east)
    people = json.load(open(os.path.join(WT, 'tools/ue_char/people/people.json')))['brute']
    PP = CH + '/People/'
    CIT = CH + '/Citizens/'
    cit_names = sorted(p.split('.')[0].split('SK_Citizen_')[-1] for p in EAL.list_assets(CH + '/Citizens', recursive=False)
                       if p.split('.')[0].split('/')[-1].startswith('SK_Citizen_') and isinstance(unreal.load_asset(p.split('.')[0]), unreal.SkeletalMesh))
    if not cit_names: MISS.append('no citizens in /Game/Characters/Citizens')
    kinds = {
        'thug': (PP + 'SK_Street_Thug', PP + 'ABP_Street_Thug', PP + 'Materials/MI_Street_Thug', 160.0, 1.0, 1.0),
        'brute': (PP + 'SK_Street_Brute', PP + 'ABP_Street_Brute', PP + 'Materials/MI_Street_Brute', 142.2, float(people['scale']), float(people['girth'])),
    }
    for c in cit_names:
        kinds['cit_' + c] = (CIT + 'SK_Citizen_' + c, CIT + 'ABP_Citizen_Lineup', None, 108.0, 1.0, 1.0)

    def person(label, kind, x, y, mode, yaw=0.0, length=0.0, start=0.0, clockwise=False):
        if kind not in kinds: MISS.append('person kind %s missing' % kind); return None
        mesh, abp, mat, speed, scale, girth = kinds[kind]
        if not (EAL.does_asset_exist(mesh) and EAL.does_asset_exist(abp)): MISS.append('%s: %s / %s missing' % (label, mesh, abp)); return None
        a = spawn(W, U(x, y, SIDEWALK_Z), yaw, label, 'Manhattan/People')
        m = a.get_editor_property('mesh')
        m.set_skeletal_mesh_asset(unreal.load_asset(mesh))
        m.set_editor_property('animation_mode', unreal.AnimationMode.ANIMATION_BLUEPRINT)
        m.set_anim_instance_class(unreal.load_asset(abp).generated_class())
        m.set_relative_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0), False, False)  # P2 MESH_YAW: glTF +Z forward -> actor +X
        if mat: m.set_material(0, unreal.load_asset(mat))
        a.set_actor_scale3d(unreal.Vector(scale * girth, scale * girth, scale))
        if mode == 'pace':
            # P2's Line mode walks along world X only, whatever the actor yaw; north-south sidewalks use a 0.3 x L/2 m ellipse (Loop mode)
            for k, v in (('mode', WM.LOOP), ('speed', speed), ('radius_x', 30.0), ('radius_y', length * 50.0), ('start_angle', start),
                         ('clockwise', clockwise)):
                try: a.set_editor_property(k, v)
                except Exception as e: MISS.append('%s.%s: %s' % (label, k, str(e)[:80]))
        else:
            a.set_editor_property('mode', WM.STAND); a.set_editor_property('speed', 0.0)
        return a

    # UE metres: west sidewalk x ~236.8, east sidewalk x ~263.2; hero start (249, 178), S1 camera (246, 150) looking north (-Y)
    placed = []
    placed.append(person('Thug_A_Stand', 'thug', 236.6, 112.0, 'stand', yaw=0.0))        # thugs loitering on the west sidewalk
    placed.append(person('Brute_A_Stand', 'brute', 237.2, 114.2, 'stand', yaw=-150.0))
    placed.append(person('Thug_B_Pace', 'thug', 236.9, 70.0, 'pace', length=24.0, start=90.0))
    placed.append(person('Thug_C_Stand', 'thug', 263.4, 40.0, 'stand', yaw=180.0))       # east sidewalk pair
    placed.append(person('Brute_C_Pace', 'brute', 263.0, 58.0, 'pace', length=20.0, start=270.0))
    cits = ['cit_' + c for c in cit_names] or []
    cit_spots = [(236.3, 130.0, 30.0, 0.0), (263.6, 120.0, 36.0, 90.0), (236.2, 30.0, 40.0, 270.0), (263.8, 90.0, 28.0, 180.0),
                 (237.0, -20.0, 30.0, 45.0), (263.1, 5.0, 30.0, 135.0), (236.7, 160.0, 12.0, 200.0), (263.5, 150.0, 16.0, 300.0)]
    for i, (x, y, L, st) in enumerate(cit_spots):
        if cits: placed.append(person('Citizen_%d_%s' % (i, cits[i % len(cits)][4:]), cits[i % len(cits)], x, y, 'pace', length=L, start=st, clockwise=bool(i % 2)))
    placed = [p for p in placed if p]
    unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), ACTORS)
    mlog('actors: PlayerStart + %d street people (%d citizen meshes: %s)' % (len(placed), len(cit_names), ','.join(cit_names)))

    # ---------------------------------------------------------------- persistent maps
    trav_gm = unreal.load_class(None, '/Script/WebHomage.WebTravGameMode')
    if not trav_gm: MISS.append('WebTravGameMode class missing (build the C++ module)')

    def add_sublevels(world, rig):
        have = [l.get_path_name() for l in unreal.EditorLevelUtils.get_levels(world)]
        for lp in (CITY_GEO, BOXES, RIG % rig, ACTORS):
            if not any(lp.split('/')[-1] + '.' in h or h.endswith(lp.split('/')[-1]) or ('/' + lp.split('/')[-1] + ':') in h for h in have):
                unreal.EditorLevelUtils.add_level_to_world(world, lp, unreal.LevelStreamingAlwaysLoaded)
        les.set_current_level_by_name(str(world.get_name()))

    def make_map(path, rig, game_mode=True, cam=None):
        world = open_level(path)
        add_sublevels(world, rig)
        if game_mode and trav_gm: world.get_world_settings().set_editor_property('default_game_mode', trav_gm)
        if cam:
            b = lambda v: U(v[0], v[2], v[1])  # browser metres -> UE
            p, t = b(cam['pos']), b(cam['target'])
            d = unreal.Vector(t.x - p.x, t.y - p.y, t.z - p.z)
            rot = unreal.Rotator(roll=0.0, pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x)))
            ca = eas.spawn_actor_from_class(unreal.CameraActor, p, rot)
            ca.set_actor_label('ShotCam_' + cam['id'])
            ca.camera_component.set_editor_property('field_of_view', cam.get('fov', 70))
            ca.camera_component.set_editor_property('constrain_aspect_ratio', False)
            ca.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.PLAYER0)
        ok = unreal.EditorLoadingAndSavingUtils.save_map(world, path)
        mlog('map', path, 'rig', rig, 'saved' if ok else 'SAVE FAILED', 'levels', len(unreal.EditorLevelUtils.get_levels(world)))

    for rig in presets:
        make_map(MAPS + ('/Manhattan' if rig == 'golden' else '/Manhattan_' + rig.capitalize()), rig)
    for v in VIEWS:
        make_map(MAPS + '/Manhattan_View_' + v, 'golden', game_mode=False, cam=SHOTS[v])

    # ---------------------------------------------------------------- hero swap check (P2 /Game/Characters hero vs P3 HeroDev)
    dev = unreal.load_asset('/Game/Traversal/HeroDev/HeroDev/SkeletalMeshes/SpiderMan')
    p2 = unreal.load_asset(CH + '/Hero/SK_Hero')
    info = {'herodev': bool(dev), 'p2_hero': bool(p2)}
    if dev and p2:
        sd, s2 = dev.get_editor_property('skeleton'), p2.get_editor_property('skeleton')
        info['herodev_skeleton'] = sd.get_path_name() if sd else None
        info['p2_skeleton'] = s2.get_path_name() if s2 else None
        info['same_skeleton_asset'] = bool(sd and s2 and sd.get_path_name() == s2.get_path_name())
        try:
            names = lambda sk: [str(n) for n in unreal.AnimPoseExtensions.get_bone_names(unreal.AnimPoseExtensions.get_reference_pose(sk))]
            nd, n2 = names(sd), names(s2)
            info['herodev_bones'], info['p2_bones'] = len(nd), len(n2)
            info['same_bone_names_ci'] = [x.lower() for x in nd] == [x.lower() for x in n2]
            info['bone_name_diff'] = sorted(set(x.lower() for x in nd) ^ set(x.lower() for x in n2))[:20]
            info['p3_code_bones_present_in_p2'] = {b: b.lower() in set(x.lower() for x in n2) for b in ('hips', 'head', 'toe_L', 'foot_L', 'hand_L', 'upperArm_R')}
        except Exception as e:
            info['bone_compare_error'] = str(e)[:200]
    json.dump(info, open(os.path.join(SCR, 'hero_swap_check.json'), 'w'), indent=1)
    mlog('hero swap check', info)
    if MISS:
        mlog('WARNINGS (%d):' % len(MISS))
        for m in MISS: print('    ', m)
    mlog('DONE')


if IN_UE:
    build_maps()
elif __name__ == '__main__':
    main()
