import unreal, traceback, os
OUT = '/Users/midir/sm2-n1/_scratch/terrain/r04/'
try:
    tex = unreal.load_asset('/Game/TerrainR4/Textures/blanket_weave')
    print('INSPECT tex', tex.get_name(), 'srgb', tex.get_editor_property('srgb'), 'comp', tex.get_editor_property('compression_settings'), 'lod', tex.get_editor_property('lod_group'),
          'mipgen', tex.get_editor_property('mip_gen_settings'), 'never_stream', tex.get_editor_property('never_stream'), 'size', tex.blueprint_get_size_x(), tex.blueprint_get_size_y())
    t = unreal.AssetExportTask(); t.object = tex; t.filename = OUT + 'blanket_weave_export.png'; t.automated = True; t.prompt = False; t.replace_identical = True
    print('INSPECT export', unreal.Exporter.run_asset_export_task(t))
    tex2 = unreal.load_asset('/Game/TerrainR4/Textures/lawn_detail')
    print('INSPECT tex2', tex2.get_editor_property('compression_settings'), tex2.get_editor_property('lod_group'), tex2.get_editor_property('mip_gen_settings'))
    sm = unreal.load_asset('/Game/TerrainR4/Props/SM_park_blankets')
    md = sm.get_static_mesh_description(0)
    n = md.get_vertex_instance_count()
    print('INSPECT mesh vinst', n, 'uv channels', md.get_num_uv_channels())
    for i in range(min(n, 24)):
        vi = unreal.VertexInstanceID(i)
        print('INSPECT vi', i, md.get_vertex_instance_uv(vi, 0), md.get_vertex_instance_color(vi))
except Exception:
    traceback.print_exc()
