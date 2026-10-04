import unreal, math
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Tests/City/City_View_S4_perch_skyline')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
P = (182*100.0, -92*100.0, 306*100.0); T = (-120*100.0, -470*100.0, 150*100.0)
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mul(a,k): return tuple(x*k for x in a)
def norm(a):
    l = math.sqrt(sum(x*x for x in a)); return tuple(x/l for x in a)
def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
f = norm(sub(T,P)); right = norm(cross((0,0,1.0),f)); up = cross(right,f)
tan = math.tan(math.radians(75)/2)
def ray(px,py,W=1920,H=1080):
    x=(px/W*2-1)*tan; y=(1-py/H*2)*tan*H/W
    return norm(add(add(f,mul(right,x)),mul(up,y)))
pts = [(100,320),(300,300),(600,310),(900,300),(1200,250),(300,230),(600,220),(900,215),(150,200),(450,190),(1300,215),(700,250),(500,340),(200,350),(1500,260),(1700,235),(900,270),(1100,300)]
for (px,py) in pts:
    d = ray(px,py); s0 = unreal.Vector(*P); e0 = unreal.Vector(*add(P, mul(d, 6000000.0)))
    h = unreal.SystemLibrary.line_trace_single(world, s0, e0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if h:
        t = h.to_tuple(); a = t[9]
        print(px, py, round(t[3]/100.0), a.get_actor_label(), [round(v/100) for v in (t[4].x,t[4].y,t[4].z)])
    else: print(px, py, 'no hit')
