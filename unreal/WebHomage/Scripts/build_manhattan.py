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
#         look         P4 Scripts/build_look.py headless: geo (traversal boxes, city components WorldDynamic), rigs, night, maps
#         water        Scripts/build_water.py: inputs (python3) + the in-Unreal build -> /Game/Water/Maps/Water_River
#         life         Scripts/build_life.py: prep (python3), content + map in Unreal -> /Game/Tests/Life/Life_Actors
#         map          this file inside Unreal (commandlet): /Game/Maps/Manhattan*
#         terrain      Scripts/build_terrain.py in Unreal with SM2_TERRAIN_ROOT=/Game/Terrain (never /Game/TerrainR5b); needs the map step's Manhattan_Actors
#         showcase     this file inside Unreal (SM2_MANHATTAN_MODE=showcase): /Game/Showcase/Maps/Manhattan_Showcase[_Midday|_Night]
#         validate     tools/showcase/check.py (offline) + this file inside Unreal (SM2_MANHATTAN_MODE=validate) -> Saved/Showcase/validate.json
#     Every Unreal process is a headless commandlet (-nullrhi -RenderOffScreen -NoSound) of THIS worktree's project, one at a time, launched
#     through tools/gpu/gpu_slot.sh capture on the shared coordinator ~/.cache/gpu-slot. The orchestrator sets SM2_STRICT=1 for every child:
#     a builder that could not produce a required asset prints SM2_BUILD_FAILED and raises; every builder prints 'SM2_BUILD_OK: <script>' last.
#   * inside Unreal (-run=pythonscript -script=<this file>): builds the maps (step 'map'). Env SM2_MANHATTAN_PRESETS.
#
# What the map is (all sublevels always loaded; nothing here is committed as .umap, see unreal/WebHomage/CONTENT.md):
#   /Game/Maps/Manhattan            persistent: City_Midtown_Geo (P1, patched by P4 geo) + Look_Boxes (P4) + Look_Rig_golden (P4)
#                                   + Manhattan_Actors; game mode WebTravGameMode (P3 hero, HeroDev mesh + UWebTravAnimInstance)
#   /Game/Maps/Manhattan_Midday, Manhattan_Night    the same with the midday / night rig (switch = open the other map)
#   /Game/Maps/Manhattan_Actors     PlayerStart on the avenue (x 249, y 178 m, facing north) + street people (P2 walkers)
#   /Game/Maps/Manhattan_View_<S1|S2|S4>   golden map + the P1 shot camera (Scripts/city_shots.json), for stills
import os, sys, json, subprocess, time, shutil, fcntl

HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/Users/midir/sm2-n1/manhattan/unreal/WebHomage/Scripts'
PROJ = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(PROJ))
UPROJECT = os.path.join(PROJ, 'WebHomage.uproject')
sys.path.insert(0, os.environ.get('SM2_SCRIPTS_DIR') or HERE)
import sm2_common  # noqa: E402
_B = sm2_common.Build('build_manhattan.py')
UE = '/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor'
SCR = os.environ.get('SM2_MANHATTAN_SCR', '/Users/midir/sm2-n1/_scratch/manhattan')
WATER_SCR = os.environ.get('SM2_WATER_SCR', os.path.expanduser('~/sm2-n1/_scratch/showcase/water'))
LIFE_SCR = os.environ.get('SM2_LIFE_SCR', os.path.expanduser('~/sm2-n1/_scratch/showcase/life'))
GPU_ROOT = os.path.join(os.path.expanduser('~'), '.cache', 'gpu-slot')
GPU_SLOT = os.path.join(WT, 'tools', 'gpu', 'gpu_slot.sh')
GPU_WAIT_TIMEOUT = int(os.environ.get('SM2_GPU_WAIT_TIMEOUT', '3600'))
EXPORT = os.path.join(SCR, 'export', 'midtown3x3')
TEX = os.path.join(SCR, 'tex')
CHAR_STAGE = os.path.join(SCR, 'chars')
DEV_PORT = 5208
STEPS_ALL = ['cpp', 'city_export', 'city_prep', 'city_extra', 'city', 'traversal', 'characters', 'look', 'water', 'life', 'map', 'terrain', 'showcase', 'validate']
TERRAIN_STEPS = 'clean,tex,mat,mesh,foliage,trees,map'
CHARACTER_STEPS = 'clean,tex,mat,mesh,citizens,rename,fightclips,abp,skins,map'
LOOK_STEPS = 'geo,rigs,night,maps'
WANT = []
# P1's tools default to THEIR scratch/export; every one honours these, so point them at this build's dirs.
os.environ.setdefault('SM2_CITY_SCRATCH', SCR); os.environ.setdefault('SM2_CITY_EXPORT', EXPORT); os.environ.setdefault('SM2_CITY_TEX', TEX)
PRESETS = ['golden', 'midday', 'night']
VIEWS = ['S1', 'S2', 'S4']

try:
    import unreal  # noqa: F401
    IN_UE = hasattr(unreal, 'EditorAssetLibrary')  # (a bare 'unreal/' folder in the cwd imports as an empty namespace package)
except ImportError:
    IN_UE = False

if not IN_UE:
    os.environ['SM2_STRICT'] = '1'
    os.environ['SM2_SCRIPTS_DIR'] = HERE


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


def gpu_root():
    """the shared coordinator root; gpu_slot.py's own DEFAULT_DIR is a historical M3 path and is never used"""
    root = os.environ.get('GPU_SLOT_DIR') or GPU_ROOT
    if os.path.realpath(root) != os.path.realpath(GPU_ROOT):
        raise SystemExit('refusing GPU_SLOT_DIR=%s: the only shared coordinator root is %s' % (root, GPU_ROOT))
    return GPU_ROOT


def wait_slot():
    """admission refusals (the queueing coordinator client does the waiting): PAUSED, a missing coordinator, a stuck-exiting Unreal"""
    root = gpu_root()
    if os.path.exists(os.path.join(root, 'PAUSED')):
        raise SystemExit('shared GPU PAUSED (%s); this build never clears it' % os.path.join(root, 'PAUSED'))
    if not all(os.path.isdir(os.path.join(root, d)) for d in ('locks', 'holders', 'queue')):
        raise SystemExit('shared coordinator %s is unavailable; do not create a parallel namespace' % root)
    stuck = []
    for line in subprocess.check_output(['ps', '-axo', 'pid=,stat=,comm='], text=True).splitlines():
        parts = line.split(None, 2)
        if len(parts) == 3 and 'UnrealEditor' in parts[2] and ('E' in parts[1] or 'Z' in parts[1]): stuck.append(line.strip())
    if stuck:
        raise SystemExit('an UnrealEditor process is stuck exiting (stat E/Z); review ownership first:\n' + '\n'.join(stuck))


def stop_ours(proc):
    """our own child only: SIGTERM, wait up to 60 s, SIGKILL as the last resort"""
    if proc.poll() is not None: return
    proc.terminate()
    t = time.monotonic()
    while proc.poll() is None and time.monotonic() - t < 60: time.sleep(0.5)
    if proc.poll() is None:
        log('child ignored SIGTERM for 60 s: SIGKILL (last resort)'); proc.kill(); proc.wait()


def ue_python(name, code, env=None, timeout=7200, sentinel='build_manhattan.py'):
    """run python code in a headless commandlet of THIS worktree's project through tools/gpu/gpu_slot.sh capture (one at a time).
    Fails on: nonzero rc (75 = GPU admission timed out, 124 = max hold exceeded), SM2_BUILD_FAILED, LogPython: Error, Traceback, or no 'SM2_BUILD_OK: <sentinel>'."""
    if subprocess.run(['pgrep', '-f', UPROJECT], capture_output=True).returncode == 0:
        raise SystemExit('an Unreal process of this worktree is running; stop your launch driver, then terminate it gracefully (SIGTERM, wait up to 60 s): ' + UPROJECT)
    wait_slot()
    lock = open(os.path.join(SCR, 'commandlet.lock'), 'a+')
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: raise SystemExit('another commandlet of this build is already running')
    jobs = os.path.join(SCR, 'jobs'); os.makedirs(jobs, exist_ok=True)
    job = os.path.join(jobs, name + '.py')
    open(job, 'w').write(code)
    lg = os.path.join(SCR, 'logs', name + '.log')
    if os.path.exists(lg): os.remove(lg)
    cmd = [GPU_SLOT, 'capture', '--label', 'sm2-showcase-' + name, '--timeout', str(GPU_WAIT_TIMEOUT), '--', UE, UPROJECT, '-run=pythonscript',
           '-script=' + job, '-unattended', '-nullrhi', '-nosplash', '-RenderOffScreen', '-NoSound', '-NoCrashReports', '-abslog=' + lg]
    child_env = {**os.environ, **(env or {}), 'GPU_SLOT_DIR': gpu_root(), 'GPU_SLOT_CAPTURE_MAX_HOLD': str(int(timeout)),
                 'SM2_STRICT': '1', 'SM2_SCRIPTS_DIR': HERE}
    log('UE commandlet', name, '-> log', lg, '(gpu_slot capture, max hold %d s)' % timeout)
    t0 = time.time()
    proc = None
    try:
        with open(lg + '.stdout', 'w') as so:
            proc = subprocess.Popen(cmd, env=child_env, stdout=so, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + GPU_WAIT_TIMEOUT + timeout + 120
            while proc.poll() is None:
                if time.monotonic() > deadline:
                    stop_ours(proc); raise SystemExit('commandlet %s exceeded its deadline and was stopped (log %s)' % (name, lg))
                time.sleep(1)
    except BaseException:
        if proc is not None: stop_ours(proc)
        raise
    finally:
        lock.close()
    rc = proc.returncode
    txt = open(lg, errors='replace').read() if os.path.exists(lg) else ''
    bad = [l for l in txt.splitlines() if 'LogPython: Error' in l or 'Traceback' in l or 'SM2_BUILD_FAILED' in l]
    ok = ('SM2_BUILD_OK: ' + sentinel) in txt
    log('UE commandlet %s: rc %d, %.0f s, %d error lines, success sentinel %s' % (name, rc, time.time() - t0, len(bad), 'yes' if ok else 'NO'))
    if rc == 75: raise SystemExit('GPU admission timed out after %d s (command %s not run; not a build failure). Not retrying.' % (GPU_WAIT_TIMEOUT, name))
    if rc == 124: raise SystemExit('commandlet %s exceeded its max hold of %d s and was stopped by gpu_slot (log %s)' % (name, timeout, lg))
    if bad: print('\n'.join(bad[:30]))
    if rc != 0: raise SystemExit('commandlet %s failed: rc %d (log %s, stdout %s.stdout)' % (name, rc, lg, lg))
    if bad: raise SystemExit('python error in %s (log %s)' % (name, lg))
    if not ok: raise SystemExit('commandlet %s did not print its success sentinel "SM2_BUILD_OK: %s" (log %s)' % (name, sentinel, lg))
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


def step_city_extra():
    """P1 placement tools added after round 01 (tools/export/build_city.sh order, r08-r10): parked cars, trees, traffic, far skyline, sun height mask"""
    e = EXPORT
    os.makedirs(os.path.join(SCR, 'r09'), exist_ok=True)   # bake_sunmask.py writes its preview PNG to <SM2_CITY_SCRATCH>/r09/
    for name, cmd in (('export_vehicles', ['python3', 'tools/export/export_vehicles.py', e]), ('street_cars', ['python3', 'tools/export/street_cars.py', e]),
                      ('street_trees', ['python3', 'tools/export/street_trees.py', e]), ('street_traffic', ['python3', 'tools/export/street_traffic.py', e]),
                      ('far_skyline', ['python3', 'tools/export/far_skyline.py']), ('bake_sunmask', ['python3', 'tools/export/bake_sunmask.py', e, TEX])):
        sh(cmd, log_name='city_extra_%s.log' % name)


# In a -run=pythonscript commandlet StaticMeshEditorSubsystem is None until its module is loaded (build_city.py assumes an editor).
LOAD_SME = 'import unreal\nunreal.SystemLibrary.execute_console_command(None, "Module Load StaticMeshEditor")\n'


def step_city():
    env = {'SM2_CITY_EXPORT': EXPORT, 'SM2_CITY_TEX': TEX}
    bc = os.path.join(HERE, 'build_city.py')
    # one pass in build_city.py's own default order (tools/export/build_city.sh): the map step spawns the kit + far-skyline actors
    ue_python('city_pass1', exec_wrapper(bc, LOAD_SME + 'JOB_ARGS = %r' % {'steps': os.environ.get('SM2_CITY_ONLY') or 'clean,tex,mat,mesh,proto,kit,fsky,map'}), env, sentinel='build_city.py')   # SM2_CITY_ONLY=mat rebuilds the materials only


def step_traversal():
    ue_python('traversal', exec_wrapper(os.path.join(HERE, 'build_traversal.py'), ''), sentinel='build_traversal.py')


P2_WT = os.environ.get('P2_WT', WT)
P2_SCR = os.environ.get('P2_SCRATCH', os.path.expanduser('~/sm2-n1/_scratch/characters'))


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
    ue_python('characters', exec_wrapper(patched, 'ARGS = %r' % {'steps': CHARACTER_STEPS}), sentinel='build_characters.py')


def step_look():
    if 'night' in LOOK_STEPS.split(','):   # packs the author's night lights (fails clearly when the exporter output is missing)
        sh(['python3', os.path.join(WT, 'tools/night/prep_night.py')], log_name='night_prep.log')
        sh(['python3', os.path.join(WT, 'tools/night/board_check.py'), '--write'], log_name='night_boards.log')   # boards onto OUR facade planes (drops those with no building within 3 m / outside the detailed region)
    env = {'SM2_CITY_EXPORT': EXPORT, 'SM2_LOOK_STEPS': LOOK_STEPS, 'SM2_LOOK_PRESETS': 'midday,golden,night'}
    ue_python('look', exec_wrapper(os.path.join(HERE, 'build_look.py'), ''), env, sentinel='build_look.py')


def step_water():
    """build_water.py's own 'ue' step (M3 gpu_slot path, no admission) is replaced by this file's guarded ue_python; its fresh-/Game/Water wipe is kept"""
    env = {'SM2_WATER_SCR': WATER_SCR, 'SM2_WATER_EXPORT': EXPORT}
    bw = os.path.join(HERE, 'build_water.py')
    os.makedirs(os.path.join(WATER_SCR, 'logs'), exist_ok=True)
    sh(['python3', bw, '--steps', 'inputs'], env=env, log_name='water_inputs.log')
    safe_rmtree(os.path.join(PROJ, 'Content', 'Water'))
    ue_python('water', exec_wrapper(bw, ''), env, timeout=5400, sentinel='build_water.py')
    if not os.path.isfile(os.path.join(PROJ, 'Content/Water/Maps/Water_River.umap')): raise SystemExit('water step did not produce /Game/Water/Maps/Water_River')


def step_life():
    env = {'SM2_LIFE_SCR': LIFE_SCR, 'SM2_LIFE_EXPORT': os.environ.get('SM2_LIFE_EXPORT', EXPORT)}
    bl = os.path.join(HERE, 'build_life.py')
    os.makedirs(os.path.join(LIFE_SCR, 'logs'), exist_ok=True)
    sh(['python3', bl, '--steps', 'prep'], env=env, log_name='life_prep.log')
    if 'cpp' not in WANT: sh(['python3', bl, '--steps', 'cpp'], env=env, log_name='life_cpp.log')
    ue_python('life_content', exec_wrapper(bl, ''), {**env, 'SM2_LIFE_STEPS': 'clean,vehicles,citizens,signals'}, sentinel='build_life.py')
    ue_python('life_map', exec_wrapper(bl, ''), {**env, 'SM2_LIFE_STEPS': 'map'}, sentinel='build_life.py')
    if not os.path.isfile(os.path.join(PROJ, 'Content/Tests/Life/Life_Actors.umap')): raise SystemExit('life step did not produce /Game/Tests/Life/Life_Actors')


def guard_terrain_root(root):
    r = '/' + root.strip('/').lower()
    if r == '/game/terrainr5b' or r.startswith('/game/terrainr5b/'):
        raise SystemExit('refusing terrain root %s: /Game/TerrainR5b is the preserved baseline' % root)
    if r != sm2_common.TERRAIN_ROOT.lower(): raise SystemExit('terrain root must be %s, got %s' % (sm2_common.TERRAIN_ROOT, root))


def step_terrain():
    guard_terrain_root(os.environ.get('SM2_TERRAIN_ROOT') or sm2_common.TERRAIN_ROOT)
    exp = os.environ.get('SM2_TERRAIN_EXPORT') or os.path.join(os.environ.get('SM2_TERRAIN_SCRATCH', ''), 'export')
    prep = os.environ.get('SM2_TERRAIN_PREP') or os.path.join(os.environ.get('SM2_TERRAIN_SCRATCH', ''), 'prep')
    need = [os.path.join(exp, 'manifest.json'), os.path.join(exp, 'terrain.json'), os.path.join(prep, 'pathmask.json')]
    gone = [n for n in need if not os.path.isfile(n)]
    if gone: raise SystemExit('terrain inputs missing (source tools/m5/env.sh; export/prep first): %s' % gone)
    if not os.path.isfile(os.path.join(PROJ, 'Content/Maps/Manhattan_Actors.umap')): raise SystemExit('terrain needs /Game/Maps/Manhattan_Actors: run the map step first')
    env = {'SM2_TERRAIN_ROOT': sm2_common.TERRAIN_ROOT, 'SM2_TERRAIN_WT': WT, 'SM2_TERRAIN_EXPORT': exp, 'SM2_TERRAIN_PREP': prep}
    # Shaders/Terrain/ParkData.ush (gitignored) is generated from the export by prep_terrain.py: M_TerrainPark / M_TerrainLawn include it
    sh(['python3', os.path.join(WT, 'tools/terrain/prep_terrain.py'), exp, prep], env={'SM2_TERRAIN_SCRATCH': os.path.dirname(prep)}, log_name='terrain_prep.log')
    if not os.path.isfile(os.path.join(PROJ, 'Shaders/Terrain/ParkData.ush')): raise SystemExit('terrain prep did not produce Shaders/Terrain/ParkData.ush')
    ue_python('terrain', exec_wrapper(os.path.join(HERE, 'build_terrain.py'), 'JOB_ARGS = %r' % {'steps': os.environ.get('SM2_TERRAIN_ONLY') or TERRAIN_STEPS}), env, sentinel='build_terrain.py')
    for f in ('Terrain_Land.umap', 'City_Geo_T.umap'):
        if not os.path.isfile(os.path.join(PROJ, 'Content/Terrain', f)): raise SystemExit('terrain step did not produce /Game/Terrain/' + f)


def step_map():
    txt = ue_python('manhattan_map', exec_wrapper(os.path.abspath(__file__), ''), {'SM2_MANHATTAN_PRESETS': ','.join(PRESETS), 'SM2_MANHATTAN_MODE': 'map'})
    for l in txt.splitlines():
        if '[manhattan' in l: print(l.split('LogPython: ')[-1])


def step_showcase():
    txt = ue_python('showcase_maps', exec_wrapper(os.path.abspath(__file__), ''), {'SM2_MANHATTAN_PRESETS': ','.join(PRESETS), 'SM2_MANHATTAN_MODE': 'showcase'})
    for l in txt.splitlines():
        if '[manhattan' in l: print(l.split('LogPython: ')[-1])


def step_lighting():
    txt = ue_python('showcase_lighting', exec_wrapper(os.path.abspath(__file__), ''), {'SM2_MANHATTAN_MODE': 'lighting'})
    for l in txt.splitlines():
        if '[manhattan lighting]' in l: print(l.split('LogPython: ')[-1])


def step_validate():
    sh(['python3', os.path.join(WT, 'tools/showcase/check.py')], log_name='showcase_check.log')
    txt = ue_python('showcase_validate', exec_wrapper(os.path.abspath(__file__), ''), {'SM2_MANHATTAN_PRESETS': ','.join(PRESETS), 'SM2_MANHATTAN_MODE': 'validate'})
    for l in txt.splitlines():
        if '[manhattan' in l: print(l.split('LogPython: ')[-1])
    rep = json.load(open(os.path.join(PROJ, 'Saved/Showcase/validate.json')))
    if not rep.get('passed'): raise SystemExit('showcase validation failed: see Saved/Showcase/validate.json')


def main():
    import argparse
    ap = argparse.ArgumentParser(description='Piece C: rebuild all piece content + /Game/Maps/Manhattan (headless)')
    ap.add_argument('--steps', default=','.join(STEPS_ALL))
    a = ap.parse_args()
    want = a.steps.split(',')
    WANT[:] = want
    bad = [s for s in want if s not in STEPS_ALL + ['lighting']]
    if bad: raise SystemExit('unknown steps %s (known: %s)' % (bad, STEPS_ALL))
    os.makedirs(os.path.join(SCR, 'logs'), exist_ok=True)
    t0 = time.time()
    for s in STEPS_ALL + ['lighting']:
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
        if not ok: MISS.append('save_map failed: ' + path)

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
    for m in MISS: _B.fail(m)
    mlog('DONE')
    _B.finish()


# ================================================================================================ inside Unreal: the showcase maps
def showcase_presets():
    presets = [p for p in os.environ.get('SM2_MANHATTAN_PRESETS', ','.join(PRESETS)).split(',') if p]
    unknown = [p for p in presets if p not in sm2_common.SHOWCASE_MAPS]
    if unknown: raise RuntimeError('unknown showcase presets %s' % unknown)
    return presets


def package_of(obj):
    return obj.get_path_name().split('.')[0]


def build_showcase():
    EAL = unreal.EditorAssetLibrary
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    T0 = time.time()
    KEEP = ('WorldSettings', 'Brush', 'DefaultPhysicsVolume', 'GameplayDebuggerCategoryReplicator', 'WorldDataLayers', 'WorldPartitionMiniMap')

    def mlog(*a): print('[manhattan %5.0fs]' % (time.time() - T0), *a)

    def editor_world(): return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

    presets = showcase_presets()
    missing = sorted({lp for p in presets for lp in sm2_common.showcase_levels(p) if not EAL.does_asset_exist(lp)})
    if missing: raise RuntimeError('missing sublevels, run the earlier steps first: %s' % missing)
    gm = unreal.load_class(None, sm2_common.GAME_MODE_CLASS)
    if not gm: raise RuntimeError('WebTravGameMode class missing (build the C++ module)')
    EAL.make_directory(os.path.dirname(sm2_common.SHOWCASE_MAPS['golden']))

    for preset in presets:
        path = sm2_common.SHOWCASE_MAPS[preset]
        want = sm2_common.showcase_levels(preset)
        if EAL.does_asset_exist(path):
            unreal.EditorLoadingAndSavingUtils.load_map(path)
            for a in eas.get_all_level_actors():
                if a.get_class().get_name() not in KEEP and package_of(a) == path: eas.destroy_actor(a)
        else:
            les.new_level(path)
        world = editor_world()
        for lv in list(unreal.EditorLevelUtils.get_levels(world)):
            pk = package_of(lv)
            if pk != path and pk not in want:
                unreal.EditorLevelUtils.remove_level_from_world(lv); mlog('removed stale sublevel', pk)
        have = {package_of(lv) for lv in unreal.EditorLevelUtils.get_levels(world)}
        for lp in want:
            if lp not in have:
                if unreal.EditorLevelUtils.add_level_to_world(world, lp, unreal.LevelStreamingAlwaysLoaded) is None:
                    raise RuntimeError('could not add sublevel %s to %s' % (lp, path))
        les.set_current_level_by_name(str(world.get_name()))
        world.get_world_settings().set_editor_property('default_game_mode', gm)
        if not unreal.EditorLoadingAndSavingUtils.save_map(world, path): raise RuntimeError('save_map failed: ' + path)
        got = {package_of(lv) for lv in unreal.EditorLevelUtils.get_levels(editor_world())} - {path}
        if got != set(want): raise RuntimeError('%s sublevels %s != expected %s' % (path, sorted(got), sorted(want)))
        mlog('showcase map', path, 'preset', preset, 'sublevels', len(got))
    mlog('DONE')
    _B.finish()


LIGHT_CLASSES = ('DirectionalLight', 'SkyLight', 'SkyAtmosphere', 'ExponentialHeightFog', 'PostProcessVolume', 'VolumetricCloud', 'LevelSequenceActor')


def lighting_inventory(eas):
    """every sky / lighting / post actor of the loaded world, grouped by the level package that owns it, with the properties that decide the look"""
    inv = {}
    for a in eas.get_all_level_actors():
        cn = a.get_class().get_name()
        if cn not in LIGHT_CLASSES:
            continue
        d = {'class': cn, 'label': a.get_actor_label()}
        try:
            if cn == 'DirectionalLight':
                c = a.get_component_by_class(unreal.DirectionalLightComponent)
                d.update(intensity=c.get_editor_property('intensity'), atmosphere_sun=bool(c.get_editor_property('atmosphere_sun_light')),
                         atmosphere_sun_index=int(c.get_editor_property('atmosphere_sun_light_index')), pitch=round(a.get_actor_rotation().pitch, 1), yaw=round(a.get_actor_rotation().yaw, 1))
            elif cn == 'SkyLight':
                c = a.get_component_by_class(unreal.SkyLightComponent)
                d.update(intensity=c.get_editor_property('intensity'), real_time_capture=bool(c.get_editor_property('real_time_capture')))
            elif cn == 'ExponentialHeightFog':
                d.update(density=a.get_component_by_class(unreal.ExponentialHeightFogComponent).get_editor_property('fog_density'))
            elif cn == 'PostProcessVolume':
                st = a.get_editor_property('settings')
                d.update(unbound=bool(a.get_editor_property('unbound')), priority=a.get_editor_property('priority'), blend_weight=a.get_editor_property('blend_weight'), enabled=bool(a.get_editor_property('enabled')),
                         exposure_method=str(st.get_editor_property('auto_exposure_method')) if st.get_editor_property('override_auto_exposure_method') else 'not overridden',
                         exposure_min=st.get_editor_property('auto_exposure_min_brightness') if st.get_editor_property('override_auto_exposure_min_brightness') else None,
                         exposure_max=st.get_editor_property('auto_exposure_max_brightness') if st.get_editor_property('override_auto_exposure_max_brightness') else None,
                         exposure_bias=st.get_editor_property('auto_exposure_bias') if st.get_editor_property('override_auto_exposure_bias') else None)
            elif cn == 'LevelSequenceActor':
                sq = a.get_editor_property('level_sequence_asset')
                d.update(sequence=sq.get_name() if sq else None)
        except Exception as e:
            d['error'] = str(e)[:100]
        inv.setdefault(package_of(a), []).append(d)
    return inv


def dump_lighting():
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    out = {}
    for preset, path in sm2_common.SHOWCASE_MAPS.items():
        unreal.EditorLoadingAndSavingUtils.load_map(path)
        out[preset] = lighting_inventory(eas)
        for pk, lst in out[preset].items():
            for d in lst:
                print('[manhattan lighting] %-8s %-44s %s' % (preset, pk, json.dumps(d)))
    p = os.path.join(PROJ, 'Saved', 'Showcase', 'lighting_dump.json')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(out, open(p, 'w'), indent=1)
    _B.finish()


def night_self_tests(binp, count, night_dir, check, mlog):
    """AWHCityLights SelfTest (no component spawned) at three reference positions, cross-checked against an independent pass over CityLights.bin"""
    import struct
    ref = json.load(open(os.environ.get('SM2_NIGHT_REF', os.path.expanduser('~/sm2-n1/_scratch/night/ref/ref_shots.json'))))['shots']
    pos = {s['name']: s['ue_cm']['pos'] for s in ref}
    spots = {'times_square': pos['view_times_square_street'], 'midtown_street': pos['shot_street'], 'skyline_high': pos['view_skyline_high']}
    cfg = json.load(open(os.path.join(night_dir, 'CityLights.json')))
    raw = open(binp, 'rb').read()
    recs = [struct.unpack_from('<3f', raw, 52 + i * 68) + (raw[52 + i * 68 + 64],) for i in range(count)]
    out = {}
    for name, p in spots.items():
        res = json.loads(unreal.WHCityLightsLibrary.self_test(unreal.Vector(p[0], p[1], p[2])))
        check('SelfTest %s loads' % name, res.get('ok') is True, pos=p)
        if not res.get('ok'): out[name] = res; continue
        for g in cfg['groups']:
            R, R0 = g['radius_m'] * 100.0, g.get('min_radius_m', 0.0) * 100.0
            exp = sum(1 for x, y, z, cat in recs if cat in g['categories'] and R0 <= ((x - p[0]) ** 2 + (y - p[1]) ** 2 + (z - p[2]) ** 2) ** 0.5 <= R)
            r = res['groups'][g['name']]
            ok = (r['selected'] > 0 or exp == 0) and (abs(r['candidates'] - exp) <= 2 if 'tile_radius_m' not in g else r['candidates'] <= exp + 2 and (r['candidates'] > 0 or exp == 0))
            check('SelfTest %s group %s selects what the export has near it' % (name, g['name']), ok, selected=r['selected'], candidates=r['candidates'], expected_near=exp)
            r['expected_near'] = exp
        out[name] = res
        mlog('SelfTest', name, json.dumps({k: (v['candidates'], v['selected']) for k, v in res['groups'].items()}), 'total K intensity', res['total_intensity_k'])
    return out


def validate_showcase():
    EAL = unreal.EditorAssetLibrary
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    T0 = time.time()
    checks = []
    NIGHT = sm2_common.NIGHT_LIGHTS_LEVEL

    def mlog(*a): print('[manhattan %5.0fs]' % (time.time() - T0), *a)

    def check(name, ok, **detail):
        checks.append(dict(name=name, passed=bool(ok), **detail))
        mlog('CHECK', 'PASS' if ok else 'FAIL', name, detail if detail else '')
        if not ok: _B.fail('validate: ' + name)

    def loads(path):
        try: return unreal.load_asset(path) is not None
        except Exception: return False

    trav_gm = unreal.load_class(None, sm2_common.GAME_MODE_CLASS)
    check('WebTravGameMode class loads', trav_gm is not None)
    night_dir = os.path.join(PROJ, 'Content', 'Night')
    night_meta = json.load(open(os.path.join(night_dir, 'CityLights.meta.json')))
    binp = os.path.join(night_dir, 'CityLights.bin')
    with open(binp, 'rb') as f: head = f.read(52)
    import struct
    magic, ver, cnt = struct.unpack('<4sII', head[:12])
    check('CityLights.bin header and size match the meta', magic == b'SM2L' and ver == 1 and cnt == night_meta['count'] == sum(night_meta['counts'].values()) and os.path.getsize(binp) == 52 + cnt * 84,
          count=cnt, meta_count=night_meta['count'], bytes=os.path.getsize(binp))
    check('CityLights.json tuning copy matches Scripts/night_city.json', open(os.path.join(night_dir, 'CityLights.json')).read() == open(os.path.join(HERE, 'night_city.json')).read())
    self_tests = night_self_tests(binp, cnt, night_dir, check, mlog)
    for preset in showcase_presets():
        path = sm2_common.SHOWCASE_MAPS[preset]
        want = sm2_common.showcase_levels(preset)
        tag = preset + ': '
        check(tag + 'map exists', EAL.does_asset_exist(path), map=path)
        try:
            loaded = unreal.EditorLoadingAndSavingUtils.load_map(path) is not None
        except Exception as e:
            loaded = False
        check(tag + 'map loads', loaded)
        if not loaded: continue
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        pkgs = [package_of(lv) for lv in unreal.EditorLevelUtils.get_levels(world)]
        subs = sorted(set(pkgs) - {path})
        check(tag + 'streaming levels are exactly the composition', subs == sorted(want), levels=subs, expected=sorted(want))
        for lp in want:
            check(tag + 'level package exists and loads: ' + lp, EAL.does_asset_exist(lp) and loads(lp))
        gm = world.get_world_settings().get_editor_property('default_game_mode')
        check(tag + 'game mode is WebTravGameMode', gm is not None and trav_gm is not None and gm == trav_gm, game_mode=str(gm))
        actors = eas.get_all_level_actors()
        n_ps = sum(1 for a in actors if isinstance(a, unreal.PlayerStart))
        check(tag + 'PlayerStart present', n_ps > 0, count=n_ps)
        in_pkg = lambda pk: [a for a in actors if package_of(a) == pk]
        ground = [a for a in in_pkg(sm2_common.TERRAIN_ROOT + '/Terrain_Land') if a.actor_has_tag('WHGround')]
        check(tag + 'Terrain_Land has WHGround actors', len(ground) > 0, count=len(ground))
        water = [a for a in in_pkg('/Game/Water/Maps/Water_River') if a.get_actor_label() == 'RiverWater']
        check(tag + 'Water_River has the water actor', len(water) > 0, count=len(water))
        life = in_pkg('/Game/Tests/Life/Life_Actors')
        veh = [a for a in life if isinstance(a, unreal.WHLifeTraffic) and len(a.get_editor_property('vehicle_meshes')) > 0]
        cit = [a for a in life if isinstance(a, unreal.WHLifeCrowd) and len(a.get_editor_property('meshes')) > 0]
        check(tag + 'Life_Actors has vehicle actors', len(veh) > 0, count=len(veh))
        check(tag + 'Life_Actors has citizen actors', len(cit) > 0, count=len(cit))
        check(tag + 'never composes the legacy Look_NightLights', sm2_common.LEGACY_NIGHT_LEVEL not in pkgs)
        inv = lighting_inventory(eas)
        rig = '/Game/Look/Rigs/Look_Rig_' + preset
        flat = [(pk, d) for pk, lst in inv.items() for d in lst]
        count = lambda cls, pred=lambda d: True: sum(1 for _, d in flat if d['class'] == cls and pred(d))
        check(tag + 'exactly one atmosphere sun, one SkyLight, one SkyAtmosphere, one height fog',
              count('DirectionalLight', lambda d: d.get('atmosphere_sun')) == 1 and count('SkyLight') == 1 and count('SkyAtmosphere') == 1 and count('ExponentialHeightFog') == 1,
              sun=count('DirectionalLight', lambda d: d.get('atmosphere_sun')), skylight=count('SkyLight'), atmosphere=count('SkyAtmosphere'), fog=count('ExponentialHeightFog'))
        check(tag + 'the rig PostProcessVolume is the only unbound one', count('PostProcessVolume') == 1 and count('PostProcessVolume', lambda d: d.get('unbound')) == 1, ppv=count('PostProcessVolume'))
        leaks = sorted({pk for pk, d in flat if pk != rig})
        check(tag + 'all sky / light / post actors come from the rig level only', not leaks, leaking_levels=leaks)
        n_cl = sum(1 for a in actors if isinstance(a, unreal.WHCityLights))
        if preset == 'night':
            check(tag + 'night level present', NIGHT in pkgs, level=NIGHT)
            check(tag + 'exactly one AWHCityLights', n_cl == 1, count=n_cl)
            em = [a for a in in_pkg(NIGHT) if a.get_actor_label() == 'NightEmissive']
            check(tag + 'one NightEmissive actor', len(em) == 1, count=len(em))
            got = {}
            for c in (em[0].get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent) if em else []):
                tags = c.get_editor_property('component_tags'); got[str(tags[0]) if tags else '?'] = c.get_instance_count()
            gc = night_meta['geometry_counts']
            want = {'nc_tubes': gc['tube_segments'], 'nc_words': gc['words'], 'nc_boards': gc['boards'], 'nc_blades': gc['blade_faces'], 'nc_signals': gc['signals'], 'nc_lamp_heads': gc['lamp_heads']}
            check(tag + 'HISM instance counts equal the export counts', got == want, got=got, expected=want)
        else:
            check(tag + 'does not include the night lights level', NIGHT not in pkgs and not any(p.endswith('/Look_NightLights') for p in pkgs))
            check(tag + 'has no AWHCityLights', n_cl == 0, count=n_cl)

    check('SK_Hero loads', loads('/Game/Characters/Hero/SK_Hero'))
    da = unreal.load_asset('/Game/Characters/Hero/Suits/DA_HeroSuits')
    check('DA_HeroSuits loads', da is not None)
    suits = list(da.get_editor_property('suits')) if da is not None else []
    check('DA_HeroSuits has >= 2 suits', len(suits) >= 2, count=len(suits))
    for en in suits:
        sid = str(en.get_editor_property('id'))
        for slot, req in (('material', True), ('lens_material', False), ('frame_material', False)):
            m = en.get_editor_property(slot)
            if m is None:
                check('suit %s %s set' % (sid, slot), not req); continue
            ok, n_tex, cur = True, 0, m
            try:
                while isinstance(cur, unreal.MaterialInstance):
                    ok = ok and EAL.does_asset_exist(package_of(cur))
                    for tp in cur.get_editor_property('texture_parameter_values'):
                        t = tp.get_editor_property('parameter_value'); n_tex += 1
                        ok = ok and t is not None and (not package_of(t).startswith('/Game/') or EAL.does_asset_exist(package_of(t)))
                    cur = cur.get_editor_property('parent')
                ok = ok and cur is not None
            except Exception as e:
                ok = False
            check('suit %s %s and its parent chain / textures load' % (sid, slot), ok, textures=n_tex)

    failed = [c['name'] for c in checks if not c['passed']]
    out = os.path.join(PROJ, 'Saved', 'Showcase', 'validate.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({'passed': not failed, 'failed': failed, 'checked': len(checks), 'self_tests': self_tests, 'checks': checks, 'time': time.strftime('%Y-%m-%d %H:%M:%S')}, open(out, 'w'), indent=1)
    mlog('validate.json', out, 'failed', len(failed), 'of', len(checks))
    if failed and not sm2_common.STRICT: raise RuntimeError('showcase validation failed: %s' % failed[:6])
    _B.finish()


if IN_UE:
    {'map': build_maps, 'showcase': build_showcase, 'validate': validate_showcase, 'lighting': dump_lighting}[os.environ.get('SM2_MANHATTAN_MODE', 'map')]()
elif __name__ == '__main__':
    main()
