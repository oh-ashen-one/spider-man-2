import unreal
EX='/Users/midir/sm2-n1/_scratch/city/export/midtown3x3'
at=unreal.AssetToolsHelpers.get_asset_tools()
t=unreal.AssetImportTask(); t.filename=EX+'/mesh/facade/facade__t0_-1.glb'; t.destination_path='/Game/City/_probe'; t.automated=True; t.replace_existing=True; t.save=False
p=unreal.InterchangeGenericAssetsPipeline()
print([x for x in dir(p.mesh_pipeline) if not x.startswith('_')][:200])
print([x for x in dir(p.common_meshes_properties) if not x.startswith('_')])
at.import_asset_tasks([t])
print(t.imported_object_paths)
for op in t.imported_object_paths:
    a=unreal.load_asset(op); print(type(a).__name__, op)
    if isinstance(a, unreal.StaticMesh):
        b=a.get_bounding_box(); print('bbox', b.min, b.max, 'uvch', a.get_num_uv_channels(0), 'nanite', a.get_editor_property('nanite_settings').enabled)
print([x for x in dir(unreal) if 'Texture2DArray' in x])
