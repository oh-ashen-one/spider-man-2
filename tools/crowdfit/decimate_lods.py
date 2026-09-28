# Blender headless: import one Tripo GLB, join its meshes, and export 3 decimated LODs as GLB (geometry + UV only).
# usage: blender -b --factory-startup --python decimate_lods.py -- IN.glb OUT_PREFIX 5000,1500,400
import bpy, sys
argv = sys.argv[sys.argv.index('--') + 1:]
src, out, targets = argv[0], argv[1], [int(t) for t in argv[2].split(',')]
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1: bpy.ops.object.join()
base = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
tri = base.modifiers.new('tri', 'TRIANGULATE'); bpy.ops.object.modifier_apply(modifier=tri.name)
n0 = len(base.data.polygons)
for i, tgt in enumerate(targets):
    bpy.ops.object.select_all(action='DESELECT'); base.select_set(True); bpy.context.view_layer.objects.active = base
    bpy.ops.object.duplicate(); lod = bpy.context.view_layer.objects.active
    if tgt < n0:
        d = lod.modifiers.new('dec', 'DECIMATE'); d.decimate_type = 'COLLAPSE'; d.ratio = tgt / n0
        d.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=d.name)
    bpy.ops.object.select_all(action='DESELECT'); lod.select_set(True)
    bpy.ops.export_scene.gltf(filepath=f'{out}{i}.glb', export_format='GLB', use_selection=True, export_materials='NONE',
                              export_texcoords=True, export_normals=True, export_apply=True)
    print('LOD', i, len(lod.data.polygons), 'tris')
    bpy.data.objects.remove(lod, do_unlink=True)
