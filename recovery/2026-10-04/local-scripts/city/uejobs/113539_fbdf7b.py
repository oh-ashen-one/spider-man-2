JOB_ARGS = {"name": "X2", "pos": "244,1.7,60", "target": "232,3,20", "fov": "70"}
# JOB_ARGS: name, pos (x,y,z browser metres), target, fov -> saves /Game/Tests/City/City_View_<name> from the S1 map with the shot camera moved
import unreal, math
name = JOB_ARGS['name']; pos = [float(v) for v in JOB_ARGS['pos'].split(',')]; tgt = [float(v) for v in JOB_ARGS['target'].split(',')]
fov = float(JOB_ARGS.get('fov', 75)); sun = JOB_ARGS.get('sun')
src = JOB_ARGS.get('src', 'S1_avenue_street')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Tests/City/City_View_' + src)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def U(x, y, z): return unreal.Vector(x * 100.0, z * 100.0, y * 100.0)
p, t = U(*pos), U(*tgt)
d = unreal.Vector(t.x - p.x, t.y - p.y, t.z - p.z)
rot = unreal.Rotator(roll=0.0, pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), yaw=math.degrees(math.atan2(d.y, d.x)))
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith('ShotCam_'):
        a.set_actor_location_and_rotation(p, rot, False, True)
        a.camera_component.set_editor_property('field_of_view', fov)
    if sun and a.get_actor_label() == 'Sun':
        s = [float(v) for v in sun.split(',')]
        a.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=s[0], yaw=s[1]), False)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.EditorLoadingAndSavingUtils.save_map(world, '/Game/Tests/City/City_View_' + name)
print('saved view', name)
