"""Render deliberate motion review frames from the task-owned Blender scene."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/heroanim'))
import importlib, bake_hero
importlib.reload(bake_hero)
from bake_hero import action,frame
scene=bpy.context.scene
assert scene.get('session_owner')=='sm2-astra-anim'
rig=next(o for o in scene.objects if o.type=='ARMATURE')
engines=[e.identifier for e in scene.render.bl_rna.properties['engine'].enum_items]
scene.render.engine=next(e for e in engines if 'EEVEE' in e)
for name,loc,power,color,size in [('HeroKey',(3,-4,5),1100,(1,.88,.78),4),('HeroFill',(-4,-2,3),700,(.6,.75,1),4),('HeroRim',(2,3,4),1400,(.7,.83,1),3)]:
    light=bpy.data.objects.get(name)
    if not light:
        data=bpy.data.lights.new(name,'AREA');light=bpy.data.objects.new(name,data);scene.collection.objects.link(light)
    light.location=loc;light.data.energy=power;light.data.color=color;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
if not bpy.data.objects.get('HeroReviewFloor'):
    bpy.ops.mesh.primitive_plane_add(size=20,location=(0,0,-.035));floor=bpy.context.object;floor.name='HeroReviewFloor'
    mat=bpy.data.materials.new('HeroReviewFloor');mat.diffuse_color=(.045,.052,.07,1);mat.use_nodes=True;shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');shader.inputs['Base Color'].default_value=mat.diffuse_color;shader.inputs['Roughness'].default_value=.78;floor.data.materials.append(mat)
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='TEXTURE'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.background_type='WORLD'
scene.world.color=(.04,.045,.055)
scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
camera=bpy.data.objects.get('HeroReviewCamera')
if not camera:
 data=bpy.data.cameras.new('HeroReviewCamera');camera=bpy.data.objects.new('HeroReviewCamera',data);scene.collection.objects.link(camera)
camera.data.type='ORTHO';camera.data.ortho_scale=3.25;scene.camera=camera
manifest=json.loads((ROOT/'docs/anim/hero/clip-manifest.json').read_text())
out=ROOT/'docs/anim/hero/poses';out.mkdir(parents=True,exist_ok=True)
for name,meta in manifest.items():
 action(rig,name)
 for view,loc in [('threequarter',(3,-6,2.5)),('side',(6,0,1.5))]:
  center=Vector((.5,0,1.3)) if name=='heroSuitEnter' else Vector((0,0,.98))
  camera.location=center+Vector(loc);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
  camera.data.ortho_scale=5.4 if name=='heroSuitEnter' else 3.25
  for k,u in enumerate((0,.18,.36,.54,.72,.9)):
   t=meta['duration']*u;frame(t)
   scene.render.filepath=str(out/f'{name}-{view}-{k}.png')
   bpy.ops.render.render(write_still=True)
 print('REVIEW_RENDERED',name)
action(rig,'heroShowcaseIdle');frame(0)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/anim/hero.blend'))
