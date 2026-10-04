import traceback
import unreal
unreal.SystemLibrary.execute_console_command(None, 'Module Load StaticMeshEditor')
ns = {'__file__': '/Users/midir/sm2-n1/_scratch/terrain/r03/build_terrain_r02.py', '__name__': '__main__', 'JOB_ARGS': {'steps': 'clean,tex,mat,mesh,foliage,trees,map,views'}}
try: exec(compile(open(ns['__file__']).read(), ns['__file__'], 'exec'), ns)
except Exception: traceback.print_exc()
