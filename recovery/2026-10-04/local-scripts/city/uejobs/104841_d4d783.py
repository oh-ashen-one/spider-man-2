JOB_ARGS = {}
import unreal, math
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Tests/City/City_View_S1_avenue_street')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
P = (246*100.0, 150*100.0, 2*100.0); T = (251*100.0, -300*100.0, 16*100.0)
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
def hit(o,e,O,d):
    tmin=-1e30; tmax=1e30
    for i in range(3):
        if abs(d[i])<1e-9:
            if O[i]<o[i]-e[i] or O[i]>o[i]+e[i]: return False,0
            continue
        t1=(o[i]-e[i]-O[i])/d[i]; t2=(o[i]+e[i]-O[i])/d[i]
        if t1>t2: t1,t2=t2,t1
        tmin=max(tmin,t1); tmax=min(tmax,t2)
    return tmax>=max(tmin,0), tmin


world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
names = {}
for (px, py) in [(1600, 465), (1650, 470), (1700, 480), (1560, 470), (1500, 300)]:
    d = ray(px, py); s0 = unreal.Vector(*P); e0 = unreal.Vector(*add(P, mul(d, 30000.0)))
    h = unreal.SystemLibrary.line_trace_single(world, s0, e0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    if h:
        t = h.to_tuple(); a = t[9]
        print(px, py, round(t[3]/100,1), a.get_actor_label(), [round(v/100,1) for v in (t[4].x, t[4].y, t[4].z)])
    else: print(px, py, 'no hit')
