# terrain piece: ONE editor session that runs the integrator's base steps (city -> traversal -> look -> map) in fresh namespaces,
# so the single GPU slot is taken once instead of four times. Not committed to the repo (scratch helper).
import os, sys, time, traceback
import unreal
WT = '/Users/midir/sm2-n1/terrain'
SC = WT + '/unreal/WebHomage/Scripts'
def run(name, path, pre=None, env=None):
    t = time.time()
    for k, v in (env or {}).items(): os.environ[k] = v
    ns = {'__file__': path, '__name__': '__main__'}
    if pre: ns.update(pre)
    print('[base_all] ===== %s start' % name, flush=True)
    try:
        exec(compile(open(path).read(), path, 'exec'), ns)
        print('[base_all] ===== %s done in %.0f s' % (name, time.time() - t), flush=True)
    except Exception:
        print('[base_all] ===== %s FAILED' % name, flush=True); traceback.print_exc()
unreal.SystemLibrary.execute_console_command(None, 'Module Load StaticMeshEditor')
run('city', SC + '/build_city.py', {'JOB_ARGS': {'steps': 'clean,tex,mat,mesh,proto,kit,fsky,map'}})
run('traversal', SC + '/build_traversal.py')
run('look', SC + '/build_look.py', None, {'SM2_LOOK_STEPS': 'geo,rigs,maps', 'SM2_LOOK_PRESETS': 'midday,golden,night'})
run('map', SC + '/build_manhattan.py', None, {'SM2_MANHATTAN_PRESETS': 'golden,midday,night'})
run('terrain', SC + '/build_terrain.py', None, {'SM2_TERRAIN_SCRATCH': '/Users/midir/sm2-n1/_scratch/terrain'})
print('[base_all] ALL DONE', flush=True)
