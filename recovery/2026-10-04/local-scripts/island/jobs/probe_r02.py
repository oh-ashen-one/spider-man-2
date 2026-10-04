import unreal
sm = unreal.load_asset('/Game/City/Meshes/detail/SM_detail__t-1_-1')
print('PROBE sm', sm)
ns = sm.get_editor_property('nanite_settings')
for k in ('enabled','fallback_target','fallback_percent_triangles','fallback_relative_error','keep_percent_triangles'):
    try: print('PROBE nanite', k, ns.get_editor_property(k))
    except Exception as ex: print('PROBE nanite missing', k, ex)
print('PROBE NaniteFallbackTarget', getattr(unreal,'NaniteFallbackTarget',None), [x for x in dir(getattr(unreal,'NaniteFallbackTarget',object)) if x.isupper()])
bs = sm.get_editor_property('body_setup'); print('PROBE body', bs, bs.get_editor_property('collision_trace_flag') if bs else None)
print('PROBE QUERY_ONLY', unreal.CollisionEnabled.QUERY_ONLY)
print('PROBE has create_body_setup', hasattr(sm,'create_body_setup'))
