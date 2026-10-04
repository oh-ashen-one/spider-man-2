JOB_ARGS = {"box": "-46,-14,-236,-196,0,40"}
import unreal
x0,x1,z0,z1,y0,y1=[float(v) for v in JOB_ARGS['box'].split(',')]  # browser metres
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Tests/City/City_Midtown_Geo')
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n=0
for a in eas.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor): continue
    o,e=a.get_actor_bounds(False)   # UE cm: X=100x, Y=100z, Z=100y
    bx0,bx1=(o.x-e.x)/100,(o.x+e.x)/100; bz0,bz1=(o.y-e.y)/100,(o.y+e.y)/100; by0,by1=(o.z-e.z)/100,(o.z+e.z)/100
    if bx1<x0 or bx0>x1 or bz1<z0 or bz0>z1 or by1<y0 or by0>y1: continue
    sm=a.static_mesh_component.static_mesh
    mats=[m.get_name() for m in a.static_mesh_component.get_materials()] if sm else []
    print(a.get_actor_label(), sm.get_name() if sm else None, mats, 'x[%.0f,%.0f] z[%.0f,%.0f] y[%.0f,%.0f]'%(bx0,bx1,bz0,bz1,by0,by1)); n+=1
print('count',n)
