"""r05: offline DXC check of the generated WaterPS custom-node code (UE's own libdxcompiler, ps_6_0)."""
import os, sys, importlib.util
sys.path.insert(0, '/Users/midir/sm2-n1/_scratch/water/r04')
import dxc_check
os.environ.setdefault('SM2_WATER_SCR', '/Users/midir/sm2-n1/_scratch/water')
spec = importlib.util.spec_from_file_location('bw', '/Users/midir/sm2-n1/water/unreal/WebHomage/Scripts/build_water.py')
bw = importlib.util.module_from_spec(spec); spec.loader.exec_module(bw)
code = bw.hlsl_ps().replace('VARK', '%.3f' % bw.VAR_K) % dict(SCAT='%.4f, %.4f, %.4f' % bw.SCAT, ABS='%.4f, %.4f, %.4f' % bw.ABS)
tex = ['tN', 'tS', 'tW', 'tC', 'tK', 'tC2', 'tC3']
f3 = ['Lag', 'WPos', 'Cam', 'SunDir', 'SunE']
args = []
for n in ['Lag', 'WPos', 'Cam', 'T', 'tN', 'tS', 'SunDir', 'SunE', 'DNW', 'PD', 'GlitterK', 'Dbg', 'DbgK', 'tW', 'tC', 'tK', 'tC2', 'tC3'] + list(bw.PARAMS):
    if n in tex: args += ['Texture2D %s' % n, 'SamplerState %sSampler' % n]
    elif n in f3: args.append('float3 %s' % n)
    else: args.append('float %s' % n)
outs = 'inout float3 NormalW, inout float Rough, inout float Opac, inout float3 Emis, inout float Spec, inout float3 Scat, inout float3 Abs'
hdr = '''#define Texture2DSample(T, S, UV) T.Sample(S, UV)
#define Texture2DSampleLevel(T, S, UV, L) T.SampleLevel(S, UV, L)
#define Texture2DSampleGrad(T, S, UV, X, Y) T.SampleGrad(S, UV, X, Y)
struct FView { float3 ViewForward; float4 ViewSizeAndInvSize; }; static FView View;
struct FMaterialPixelParameters { float4 SvPosition; };
'''
src = hdr + 'float3 WaterPS(FMaterialPixelParameters Parameters, ' + ', '.join(args) + ', ' + outs + ')\n{\n' + code + '\n}\n'
src += 'Texture2D gT; SamplerState gS;\nfloat4 main(float4 pos : SV_Position) : SV_Target { FMaterialPixelParameters P; P.SvPosition = pos; float3 n = 0, e = 0, sc = 0, ab = 0; float r = 0, o = 0, sp = 0;\n'
call = []
for a in args:
    t, n = a.split()
    call.append('gT' if t == 'Texture2D' else ('gS' if t == 'SamplerState' else ('pos.xyz' if t == 'float3' else 'pos.x')))
src += ' float3 c = WaterPS(P, ' + ', '.join(call) + ', n, r, o, e, sp, sc, ab); return float4(c + n + e + sc + ab + r + o + sp, 1); }\n'
open('/Users/midir/sm2-n1/_scratch/water/r05/ps_r05.hlsl', 'w').write(src)
st, msg = dxc_check.compile(src, vt_off=3)
print('status', hex(st & 0xffffffff)); print(msg[:4000])
