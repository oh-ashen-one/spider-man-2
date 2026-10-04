import os, sys, re
os.environ['SM2_WATER_SCR'] = '/Users/midir/sm2-n1/_scratch/water'
sys.path.insert(0, '/Users/midir/sm2-n1/water/unreal/WebHomage/Scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('bw', '/Users/midir/sm2-n1/water/unreal/WebHomage/Scripts/build_water.py'); bw = importlib.util.module_from_spec(spec); spec.loader.exec_module(bw)
code = bw.hlsl_ps().replace('VARK', '%.3f' % bw.VAR_K) % dict(SCAT='%.4f, %.4f, %.4f' % bw.SCAT, ABS='%.4f, %.4f, %.4f' % bw.ABS)
vs = bw.hlsl_vs()
open('ps_r04.hlsl', 'w').write(code)
params = ''.join(', float %s' % k for k in bw.PARAMS)
hdr = r'''
#define Texture2DSample(T, S, UV) T.Sample(S, UV)
#define Texture2DSampleLevel(T, S, UV, L) T.SampleLevel(S, UV, L)
#define Texture2DSampleBias(T, S, UV, B) T.SampleBias(S, UV, B)
#define Texture2DSampleGrad(T, S, UV, X, Y) T.SampleGrad(S, UV, X, Y)
struct FView { float3 ViewForward; }; static FView View;
'''
fn = hdr + 'float3 WaterPS(float3 Lag, float3 WPos, float3 Cam, float T, Texture2D tN, SamplerState tNSampler, Texture2D tS, SamplerState tSSampler, float3 SunDir, float3 SunE, float DNW, float PD, float GlitterK, float Dbg, float DbgK, Texture2D tW, SamplerState tWSampler, Texture2D tC, SamplerState tCSampler, Texture2D tK, SamplerState tKSampler' + params + ', inout float3 NormalW, inout float Rough, inout float Opac, inout float3 Emis, inout float Spec, inout float3 Scat, inout float3 Abs)\n{\n' + code + '\n}\n'
fn += 'float3 WaterVS(float3 WPos, float3 Cam, float T, inout float3 Lag)\n{\n' + vs + '\n}\n'
fn += 'Texture2D tN, tS, tW, tC, tK; SamplerState sN, sS, sW, sC, sK;\n'
fn += 'float4 main(float3 lag : TEXCOORD0, float3 wp : TEXCOORD1) : SV_Target { float3 n = 0, e = 0, sc = 0, ab = 0; float r = 0, o = 0, sp = 0; float3 l2 = 0;\n'
fn += ' float3 v = WaterVS(wp, wp * 2, 1.0, l2);\n'
fn += ' float3 b = WaterPS(lag + l2, wp, wp + 100, 1.0, tN, sN, tS, sS, float3(0, 0.5, 0.5), 1, 100, 50, 0.5, 0, 0, tW, sW, tC, sC, tK, sK' + ', 1' * len(bw.PARAMS) + ', n, r, o, e, sp, sc, ab);\n'
fn += ' return float4(b + n + e + sc + ab + v * 0.001, r + o + sp); }\n'
open('wrap.hlsl', 'w').write(fn)
import dxc_check as d
st, msg = d.compile(fn, vt_off=3)
print('status', hex(st & 0xffffffff)); print(msg[:4000])
