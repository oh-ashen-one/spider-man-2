# Blender headless: import one Tripo GLB, join its meshes, orient it, and export decimated LODs as GLB (geometry + UV).
# usage: blender -b --factory-startup --python decimate_lods.py -- IN.glb OUT_PREFIX 5000,1500,400 [auto|<yaw degrees>]
#   auto: characters are turned so they face Blender -Y (= glTF +Z, the crowd's forward). Tripo multi-view models often
#         come out facing +X; the facing is read from the feet (toes stick out forward of the body's vertical axis).
#   <yaw>: a fixed turn about Z in degrees (accessories: Tripo's front is +X, so usually -90).
import bpy, sys, math
import numpy as np
from mathutils import Matrix
argv = sys.argv[sys.argv.index('--') + 1:]
src, out, targets = argv[0], argv[1], [int(t) for t in argv[2].split(',')]
orient = argv[3] if len(argv) > 3 else 'auto'
# optional ':weld' suffix (e.g. -90:weld): weld seams + split non-manifold edges first (fur-card meshes that stall the collapse)
orient, _, flag = orient.partition(':'); weld = flag == 'weld'
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1: bpy.ops.object.join()
base = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# weld: glTF splits vertices at every uv seam (uvs are per-loop in Blender, so welding keeps the seams); non-manifold
# fur cards (3+ faces per edge) block the collapse entirely, so they are split into open borders. Only for meshes that
# need it: on clean meshes the welded collapse is worse at low triangle counts.
import bmesh
if weld:
  _bm = bmesh.new(); _bm.from_mesh(base.data); bmesh.ops.remove_doubles(_bm, verts=_bm.verts, dist=1e-5)
  _nm = [e for e in _bm.edges if not e.is_manifold and not e.is_boundary]
  if _nm: bmesh.ops.split_edges(_bm, edges=_nm)
  _bm.to_mesh(base.data); _bm.free()
co = np.array([v.co[:] for v in base.data.vertices])
if orient == 'auto':
    # the A-pose arm span is always sideways: its direction (PCA of the shoulder band, XY plane) is the lateral axis,
    # so the character faces one of its two perpendiculars. The feet pick the sign when they can; crowdfit.py then
    # tests front vs back by fit quality anyway, so a weak feet signal is harmless.
    z0, h = co[:, 2].min(), co[:, 2].max() - co[:, 2].min()
    band = co[(co[:, 2] > z0 + 0.62 * h) & (co[:, 2] < z0 + 0.85 * h)][:, :2]
    band = band - band.mean(0)
    lat = np.linalg.svd(band, full_matrices=False)[2][0]
    fwd = np.array([-lat[1], lat[0]])
    feet = co[co[:, 2] < z0 + 0.04 * h][:, :2] - np.median(co[:, :2], 0)
    if feet.mean(0) @ fwd < 0: fwd = -fwd
    ang = math.atan2(fwd[1], fwd[0])
    yaw = -math.pi / 2 - ang                         # turn the facing to -Y
    print('FACING', round(math.degrees(ang), 1), 'turn', round(math.degrees(yaw), 1))
else:
    yaw = math.radians(float(orient))
base.data.transform(Matrix.Rotation(yaw, 4, 'Z'))
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
