import unreal
unreal.SystemLibrary.execute_console_command(None, "Module Load StaticMeshEditor")
import time as _t, os as _o
_o.environ["SM2_ISLAND_DEADLINE"] = str(_t.time() + float(_o.environ.get("SM2_ISLAND_BUDGET_S", "0") or 0)) if _o.environ.get("SM2_ISLAND_BUDGET_S") else ""
JOB_ARGS = {"steps": 'clean,tex', "wp_map": '/Game/Maps/Manhattan_WP'}
__file__ = '/Users/midir/sm2-n1/island/unreal/WebHomage/Scripts/build_city.py'
exec(compile(open(__file__).read(), __file__, "exec"))
