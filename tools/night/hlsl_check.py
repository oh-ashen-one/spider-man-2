#!/usr/bin/env python3
"""Offline HLSL compile check (no Unreal needed): compiles every generated Shaders/City/*.ush and every Custom-node body our builders emit
(build_city.py make_material, build_look.py night materials) with UE's bundled DXC (libdxcompiler via tools/night/dxc.py), as a minimal
pixel shader with ps_6_6 / -HV 2021. UE's material-template symbols (Parameters, ResolvedView, Texture2DSample...) are stubbed in PRELUDE; an
error that names one of those stubs is a harness artefact, anything else is a real error in our HLSL.
  python3 tools/night/hlsl_check.py            # everything, JSON summary, exit 1 on any error
  python3 tools/night/hlsl_check.py -v         # print every message
Builders are loaded under a stub `unreal` module (the code that builds the Custom nodes runs unchanged; make_material records them)."""
import argparse
import json
import os
import sys
import types
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / 'unreal/WebHomage/Scripts'
SHADERS = ROOT / 'unreal/WebHomage/Shaders'
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(SCRIPTS))
import dxc  # noqa: E402

PRELUDE = r'''
// ---- stubs of UE material-template symbols (harness artefacts) ----
#define Texture2DSample(T, S, uv) T.Sample(S, uv)
#define Texture2DSampleLevel(T, S, uv, l) T.SampleLevel(S, uv, l)
#define Texture2DSampleBias(T, S, uv, b) T.SampleBias(S, uv, b)
#define Texture2DSampleGrad(T, S, uv, dx, dy) T.SampleGrad(S, uv, dx, dy)
#define Texture2DArraySample(T, S, uv) T.Sample(S, uv)
#define Texture2DArraySampleLevel(T, S, uv, l) T.SampleLevel(S, uv, l)
#define Texture2DArraySampleGrad(T, S, uv, dx, dy) T.SampleGrad(S, uv, dx, dy)
struct FStubView { float4 DirectionalLightDirection; float4 DirectionalLightColor; float3 WorldCameraOrigin; float3 PreViewTranslation; float PreExposure; float4 BufferSizeAndInvSize; float2 ViewSizeAndInvSize; };
static FStubView ResolvedView;
struct FMaterialPixelParameters { float4 SvPosition; float4 ScreenPosition; float2 ViewBufferUV; float3 WorldPosition_NoOffsets; float3 TangentToWorld0; float4 VertexColor; float3 CameraVector; float3 TranslatedWorldPosition; };
#define SM2_PARAMS_INIT(P, sv) FMaterialPixelParameters P = (FMaterialPixelParameters)0; P.SvPosition = sv;
'''

KIND_TYPE = {'uv': 'float2', 'vc': 'float3', 'vca': 'float', 'wpos': 'float3', 'wn': 'float3', 'cam': 'float3', 'scalar': 'float', 'vector': 'float4', 'mpc': 'float', 'time': 'float',
             'pcd': 'float', 'cd': 'float', 'lp': 'float3', 'param': 'float'}
OUT_TYPE = {1: 'float', 2: 'float2', 3: 'float3'}


def wrap_node(name, code, inputs, outputs, includes_text=''):
    """-> HLSL source: prelude + includes + CustomMain(Parameters, inputs..., out outputs...) { code } + a ps_6_6 entry that calls it"""
    params, decl, call = [], [], []
    for spec in inputs:
        n, kind = spec[0], spec[1]
        if kind in ('tex', 'texparam'):
            ttype = 'Texture2DArray' if (len(spec) > 2 and spec[2] and '/TA_' in str(spec[2])) else 'Texture2D'   # texture arrays (TA_*) are Texture2DArray in the material
            params += ['%s %s' % (ttype, n), 'SamplerState %sSampler' % n]
            decl.append('%s G_%s : register(t%d); SamplerState G_%sSampler : register(s%d);' % (ttype, n, len(decl), n, len(decl)))
            call += ['G_%s' % n, 'G_%sSampler' % n]
        else:
            params.append('%s %s' % (KIND_TYPE[kind], n))
            call.append('(%s)0.5' % KIND_TYPE[kind])
    outs = outputs[1:]
    for n, k in outs:
        params.append('out %s %s' % (OUT_TYPE[k], n))
    ret = OUT_TYPE[outputs[0][1]] if outputs else 'float3'
    out_decl = ''.join('    %s o_%s;\n' % (OUT_TYPE[k], n) for n, k in outs)
    out_call = ''.join(', o_%s' % n for n, k in outs)
    out_sum = ''.join(' + (float3)o_%s' % n for n, k in outs)
    src = PRELUDE + includes_text + '\n'
    src += '%s CustomMain(FMaterialPixelParameters Parameters%s)\n{\n%s\n}\n' % (ret, ''.join(', ' + p for p in params), code)
    src += '\n'.join(d for d in decl) + '\n'
    src += 'float4 main(float4 sv : SV_Position) : SV_Target\n{\n    SM2_PARAMS_INIT(P, sv)\n%s' % out_decl
    src += '    %s r = CustomMain(P%s%s);\n    return float4((float3)r%s, 1.0);\n}\n' % (ret, ''.join(', ' + c for c in call), out_call, out_sum)
    return src


class _Meta(type):
    def __getattr__(cls, name):
        if name.startswith('__'):
            raise AttributeError(name)
        v = mock.MagicMock(name='%s.%s' % (cls.__name__, name))
        setattr(cls, name, v)
        return v


class _Stub(metaclass=_Meta):
    def __init__(self, *a, **k):
        pass

    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)
        return mock.MagicMock(name='stub.' + name)


class _UnrealStub(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)
        cls = _Meta(name, (_Stub,), {})
        setattr(self, name, cls)
        return cls


def load_builder(filename, env, job_args=None):
    """exec a builder script under a stub `unreal`; returns its globals"""
    saved = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    sys.modules['unreal'] = _UnrealStub('unreal')
    path = str(SCRIPTS / filename)
    ns = {'__file__': path, '__name__': 'sm2_hlsl_check_' + filename}
    if job_args:
        ns['JOB_ARGS'] = job_args
    try:
        exec(compile(open(path).read(), path, 'exec'), ns)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return ns


def collect():
    items = []   # (label, source)
    ush = {p.name: p.read_text() for p in sorted((SHADERS / 'City').glob('*.ush'))}
    for n, t in ush.items():
        items.append(('ush/' + n, PRELUDE + '\n' + t + '\nfloat4 main(float4 sv : SV_Position) : SV_Target { return 0; }\n'))
    env_city = {'SM2_CITY_EXPORT': os.environ.get('SM2_CITY_EXPORT', str(Path.home() / 'sm2-n1/_scratch/showcase/manhattan/export/midtown3x3')),
                'SM2_CITY_TEX': os.environ.get('SM2_CITY_TEX', str(Path.home() / 'sm2-n1/_scratch/showcase/manhattan/tex')),
                'SM2_CITY_SCRATCH': os.environ.get('SM2_CITY_SCRATCH', str(Path.home() / 'sm2-n1/_scratch/showcase/manhattan')), 'SM2_STRICT': '0'}
    ns = load_builder('build_city.py', env_city, {'steps': 'mat'})
    for name, code, inputs, outputs, incs in ns['custom_nodes']():
        text = ''.join('\n// ---- include %s\n%s\n' % (i, ush[os.path.basename(i)]) for i in incs)
        items.append(('build_city/' + name, wrap_node(name, code, inputs, outputs, text)))
    ns = load_builder('build_look.py', {'SM2_LOOK_STEPS': 'none', 'SM2_STRICT': '0', 'SM2_CITY_EXPORT': env_city['SM2_CITY_EXPORT']})
    for name, code, inputs, outputs in ns['night_custom_nodes']():
        items.append(('build_look/' + name, wrap_node(name, code, inputs, outputs)))
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('-v', action='store_true')
    ap.add_argument('--only', help='substring of a label')
    ap.add_argument('--dump', help='write the wrapped sources into this directory')
    a = ap.parse_args()
    items = collect()
    if a.only:
        items = [i for i in items if a.only in i[0]]
    d = dxc.Dxc()
    results, errors = [], 0
    for label, src in items:
        if a.dump:
            Path(a.dump).mkdir(parents=True, exist_ok=True)
            (Path(a.dump) / (label.replace('/', '__') + '.hlsl')).write_text(src)
        ok, msg = d.compile(src, ['-E', 'main', '-T', 'ps_6_6', '-HV', '2021'])
        msgs = [l for l in msg.replace('\x00', '').splitlines() if l.strip() and 'DXIL signing library' not in l]
        errs = [l for l in msgs if ' error:' in l]
        if not ok or errs:
            errors += 1
        results.append({'label': label, 'ok': ok and not errs, 'warnings': sum(1 for l in msgs if ' warning:' in l), 'errors': errs[:8]})
        if a.v or not (ok and not errs):
            print('%-44s %s' % (label, 'OK' if ok and not errs else 'FAIL'))
            for l in (msgs if a.v else errs[:8]):
                print('    ' + l)
    print(json.dumps({'checked': len(results), 'failed': errors, 'failed_labels': [r['label'] for r in results if not r['ok']]}))
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
