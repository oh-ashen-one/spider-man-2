import re
base='/Users/midir/sm2-n1/terrain/'
p=base+'unreal/WebHomage/Shaders/Terrain/Lawn.ush'
s=open(p).read()
old=[l for l in s.split('\n') if l.strip().startswith('float mott =')][0]
new="  float mott = (d1.r - 0.5f) * 0.54f + (d2.r - 0.5f) * 1.20f + (d3.r - 0.5f) * 0.45f + (d1.a - 0.5f) * 0.30f;"
s=s.replace(old,new)
s=s.replace("fine scales x1.5 again","fine scales x1.5 again; hold 3: guard p9 6.8 (its sigma-6 SD sits at ~4.8 independent of the detail): mid scales + the 16 m patches up, albedo +25 %")
open(p,'w').write(s)
p=base+'unreal/WebHomage/Scripts/terrain_materials.py'
s=open(p).read()
s=s.replace("LAWN_GRADE = (0.60, 1.32, 0.10, 1.0)","LAWN_GRADE = (0.86, 1.62, 0.12, 1.0)")
s=s.replace("""float3 tip = float3(0.125, 0.29, 0.006);
float3 mid = float3(0.077, 0.185, 0.004);
float3 root = float3(0.02, 0.049, 0.002);""","""float3 tip = float3(0.17, 0.35, 0.007);
float3 mid = float3(0.105, 0.225, 0.0045);
float3 root = float3(0.027, 0.06, 0.0025);""")
s=s.replace("float3 yel = float3(0.18, 0.27, 0.012);","float3 yel = float3(0.22, 0.32, 0.014);")
open(p,'w').write(s)
print('applied')
