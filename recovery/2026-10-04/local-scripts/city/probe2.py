import unreal
EX='/Users/midir/sm2-n1/_scratch/city/export/midtown3x3'
print(unreal.EditorAssetLibrary.list_assets('/Game/City', recursive=True))
at=unreal.AssetToolsHelpers.get_asset_tools()
p=unreal.InterchangeGenericAssetsPipeline()
p.common_meshes_properties.set_editor_properties({'recompute_normals':False,'recompute_tangents':False,'use_full_precision_u_vs':True,'remove_degenerates':False,'vertex_color_import_option':unreal.InterchangeVertexColorImportOption.IVCIO_REPLACE})
p.mesh_pipeline.set_editor_properties({'generate_lightmap_u_vs':False,'build_nanite':False})
p.material_pipeline.set_editor_property('import_materials', False)
p.material_pipeline.texture_pipeline.set_editor_property('import_textures', False)
t=unreal.AssetImportTask(); t.filename=EX+'/mesh/facade/facade__t0_-1.glb'; t.destination_path='/Game/City/_probe'; t.automated=True; t.replace_existing=True; t.save=False; t.options=p
at.import_asset_tasks([t])
print('imported', t.imported_object_paths)
for op in unreal.EditorAssetLibrary.list_assets('/Game/City/_probe', recursive=True):
    a=unreal.load_asset(op); print(type(a).__name__, op)
    if isinstance(a, unreal.StaticMesh):
        b=a.get_bounding_box(); print('bbox', b.min, b.max, 'uvch', unreal.StaticMeshEditorSubsystem and unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_num_uv_channels(a,0))
