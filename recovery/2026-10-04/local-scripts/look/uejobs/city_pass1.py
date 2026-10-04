import os, unreal
os.environ["SM2_CITY_EXPORT"] = "/Users/midir/sm2-n1/_scratch/look/export/midtown3x3"; os.environ["SM2_CITY_TEX"] = "/Users/midir/sm2-n1/_scratch/look/tex"
unreal.SystemLibrary.execute_console_command(None, "Module Load StaticMeshEditor")
JOB_ARGS = {"steps": "clean,tex,mat,mesh,proto,kit,fsky,map"}
__file__ = '/Users/midir/sm2-n1/look/unreal/WebHomage/Scripts/build_city.py'
exec(compile(open(__file__).read(), __file__, "exec"))
