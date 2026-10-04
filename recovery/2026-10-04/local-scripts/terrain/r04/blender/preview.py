import bpy, sys, math, random, bmesh
from mathutils import Vector, Matrix
random.seed(3)
argv = sys.argv[sys.argv.index('--') + 1:]
out = argv[0]; cam_h = float(argv[1]); cam_pitch = float(argv[2]); nx = int(argv[3]) if len(argv) > 3 else 22
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.engine = 'CYCLES'; scn.cycles.device = 'CPU'; scn.cycles.samples = 24; scn.cycles.use_denoising = False
scn.render.resolution_x = 960; scn.render.resolution_y = 540
P = '/Users/midir/sm2-n1/_scratch/terrain/prep/'
# materials: vertex colour R = height along blade, G blade random, B clump random (glTF COLOR_0 -> attribute 'Col')
def blade_mat():
    m = bpy.data.materials.new('blade'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    attr = nt.nodes.new('ShaderNodeAttribute'); attr.attribute_name = 'Col'
    sep = nt.nodes.new('ShaderNodeSeparateColor')
    nt.links.new(attr.outputs['Color'], sep.inputs['Color'])
    # colour: root (0.018,0.045,0.002) -> mid (0.07,0.17,0.004) -> tip (0.115,0.27,0.006), per blade 0.72..1.28
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0.018, 0.045, 0.002, 1)
    e = ramp.color_ramp.elements.new(0.45); e.color = (0.07, 0.17, 0.004, 1)
    e = ramp.color_ramp.elements.new(1.0); e.color = (0.115, 0.27, 0.006, 1)
    nt.links.new(sep.outputs['Red'], ramp.inputs['Fac'])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY_ADD'; mul.inputs[1].default_value = 1.1; mul.inputs[2].default_value = 1.5
    nt.links.new(sep.outputs['Green'], mul.inputs[0])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1.0
    nt.links.new(ramp.outputs['Color'], mix.inputs[6]); 
    # scalar to colour
    comb = nt.nodes.new('ShaderNodeCombineColor'); nt.links.new(mul.outputs['Value'], comb.inputs[0]); nt.links.new(mul.outputs['Value'], comb.inputs[1]); nt.links.new(mul.outputs['Value'], comb.inputs[2])
    nt.links.new(comb.outputs['Color'], mix.inputs[7])
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); bsdf.inputs['Roughness'].default_value = 0.8
    nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    try: bsdf.inputs['Subsurface Weight'].default_value = 0.0
    except Exception: pass
    # translucent part (light through the blade)
    tr = nt.nodes.new('ShaderNodeBsdfTranslucent'); nt.links.new(mix.outputs[2], tr.inputs['Color'])
    mixs = nt.nodes.new('ShaderNodeMixShader'); mixs.inputs[0].default_value = 0.35
    nt.links.new(bsdf.outputs['BSDF'], mixs.inputs[1]); nt.links.new(tr.outputs['BSDF'], mixs.inputs[2])
    outn = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(mixs.outputs['Shader'], outn.inputs['Surface'])
    return m
bm_ = blade_mat()
# ground plane with lawn albedo (0.057, 0.131, 0.004)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0)); g = bpy.context.object
gm = bpy.data.materials.new('ground'); gm.use_nodes = True; gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.057, 0.131, 0.004, 1); gm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
g.data.materials.append(gm)
# import patches
objs = []
for k in range(4):
    bpy.ops.import_scene.gltf(filepath=P + 'grass_near_%d.glb' % k)
    o = [x for x in bpy.context.selected_objects if x.type == 'MESH'][0]; o.data.materials.clear(); o.data.materials.append(bm_); objs.append(o)
    o.location = (1000, 1000, 0)
# glTF import converts Y-up to Z-up: blades point +Z (unit height) and horizontal in X/Y: scale z by h (cm) at instance time -> linked duplicates with scale
hdist = 0.14
cells = 1.5
count = 0
for i in range(-nx, nx):
    for j in range(0, 2 * nx):
        x = (i + random.random()) * cells; y = 1.0 + (j + random.random()) * cells * 0.9
        if math.hypot(x, y) > 40: continue
        src = objs[random.randrange(4)]
        d = src.copy(); d.data = src.data; bpy.context.collection.objects.link(d)
        s = random.uniform(0.85, 1.2); h = random.uniform(0.09, 0.22)
        d.location = (x, y, 0); d.rotation_euler = (0, 0, random.uniform(0, 6.283)); d.scale = (s, s, h)
        count += 1
for o in objs: bpy.data.objects.remove(o)
print('patches', count)
# sun: golden hour, 20 deg elevation from behind-left
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 5.0; sun.color = (1.0, 0.78, 0.55); sun.angle = math.radians(1.5)
so = bpy.data.objects.new('sun', sun); bpy.context.collection.objects.link(so); so.rotation_euler = (math.radians(70), 0, math.radians(35))
w = bpy.data.worlds.new('w'); scn.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.35, 0.5, 0.8, 1); bg.inputs['Strength'].default_value = 0.9
cam = bpy.data.cameras.new('cam'); cam.lens = 24; cam.sensor_width = 36
co = bpy.data.objects.new('cam', cam); bpy.context.collection.objects.link(co); co.location = (0, 0, cam_h); co.rotation_euler = (math.radians(90 - cam_pitch), 0, 0)
scn.camera = co
scn.view_settings.view_transform = 'Filmic' if 'Filmic' in [v.identifier for v in scn.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Standard'
scn.render.filepath = out; bpy.ops.render.render(write_still=True)
