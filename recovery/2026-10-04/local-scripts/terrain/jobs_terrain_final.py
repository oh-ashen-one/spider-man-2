import os, traceback
import unreal
unreal.SystemLibrary.execute_console_command(None, 'Module Load StaticMeshEditor')
ns = {'__file__': '/Users/midir/sm2-n1/terrain/unreal/WebHomage/Scripts/build_terrain.py', '__name__': '__main__', 'JOB_ARGS': {'steps': 'clean,tex,mat,mesh,foliage,trees,map,views'}}
try: exec(compile(open(ns['__file__']).read(), ns['__file__'], 'exec'), ns)
except Exception: traceback.print_exc()
