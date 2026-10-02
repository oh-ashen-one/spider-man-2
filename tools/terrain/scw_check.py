#!/usr/bin/env python3
"""Offline re-compile of FAILED terrain material permutations with UE's own ShaderCompileWorker (CPU only: no engine, no GPU, no lock; ~0.3 s per permutation).
When a material fails to compile in the game ("Failed to compile Material ... Default Material will be used in game") the engine dumps the exact generated shader of every failing permutation to
  <worktree>/unreal/WebHomage/Saved/ShaderDebugInfo/METAL_SM6/<Material>_<hash>/Default/<VertexFactory>/<Shader>/<perm>/{<Pass>.usf, DebugCompile.in, DebugCompileArgs.txt}
(the .usf is the preprocessed source with `#line` markers; /Engine/Generated/Material.ush holds the Custom-node functions and the macros of the permutation are listed as `// #define X Y` comments
in its header). This tool copies a material's dump tree to scratch, swaps the inlined /Project/Terrain/Foliage.ush section for the CURRENT file on disk (with the permutation's macros re-defined),
and runs  ShaderCompileWorker <dir> 0 DebugCompile DebugCompile.in DebugCompile.out -DebugSourceFiles=...  so a fix to Foliage.ush is verified against UE's real material wrapper (parameter types,
stage rules such as "no derivatives in ray tracing hit shaders", Nanite / shadow / ray tracing permutations) before a GPU-lock turn is spent. Custom-node bodies stay the ones of the dump.
Limits: only permutations that failed once have a dump (run the game once, or `r.DumpShaderDebugInfo=1`); a dump of an older body is not a check of a changed body.
usage: scw_check.py [material name prefix ...]   (default: every M_Terrain* dump; exit code 1 on any error)"""
import os, sys, re, shutil, subprocess, glob, shlex
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
DUMPS = os.path.join(REPO, 'unreal', 'WebHomage', 'Saved', 'ShaderDebugInfo', 'METAL_SM6')
FOLI = os.path.join(REPO, 'unreal', 'WebHomage', 'Shaders', 'Terrain', 'Foliage.ush')
SCW = '/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/ShaderCompileWorker'
SCR = os.environ.get('SM2_TERRAIN_SCRATCH', '/Users/midir/sm2-n1/_scratch/terrain'); WORK = os.path.join(SCR, 'scw')
USED = ('SHADOW_DEPTH_SHADER', 'LUMEN_CARD_CAPTURE', 'RAYTRACINGSHADER', 'RAYHITGROUPSHADER')   # macros Foliage.ush tests

def patch(usf, new_foliage):
    """swap the inlined Foliage.ush section (from its first `#line` marker up to the generated Material.ush `#line` that precedes CustomExpression0) for the current file"""
    ma = re.search(r'#line \d+ "/Project/Terrain/Foliage.ush"', usf)    # the first marker differs per permutation (unused leading functions are stripped)
    if not ma: return usf, False
    a = ma.start()
    m = re.search(r'#line \d+ "/Engine/Generated/Material.ush"\n[^\n]*CustomExpression0\(', usf[a:])
    if not m: return usf, False
    b = a + m.start()
    defs = ''
    for name in USED:    # the dump's header lists the permutation's macros as comments: re-define the ones the new text tests
        mm = re.search(r'^// #define %s (\S+)' % name, usf[:200000], re.M)
        if mm and mm.group(1) != '0': defs += '#define %s %s\n' % (name, mm.group(1))
    body = new_foliage.replace('#pragma once', '')
    # UE strips unused functions from the dumped source: the engine's Texture2DSampleGrad (Common.ush) is missing from dumps of materials that never used it; re-declare it (identical body)
    if 'Texture2DSampleGrad(Texture2D' not in usf:
        body = 'float4 Texture2DSampleGrad(Texture2D Tex, SamplerState Sampler, float2 UV, float2 DDX, float2 DDY) { return Tex.SampleGrad(Sampler, UV, DDX, DDY); }\n' + body
    return usf[:a] + '#line 1 "/Project/Terrain/Foliage.ush"\n' + defs + body + '\n' + usf[b:], True

def check_material(mdir):
    T = os.path.join(WORK, os.path.basename(mdir)); shutil.rmtree(T, ignore_errors=True); shutil.copytree(mdir, T)
    results = []
    for inp in sorted(glob.glob(os.path.join(T, '**', 'DebugCompile.in'), recursive=True)):
        d = os.path.dirname(inp); rel = os.path.relpath(d, T)
        toks = shlex.split(open(os.path.join(d, 'DebugCompileArgs.txt')).read()); toks[0] = d
        srcs = [t.split('=', 1)[1] for t in toks if t.startswith('-DebugSourceFiles=')]
        files = [os.path.normpath(os.path.join(d, f)) for f in (srcs[0].split(',') if srcs else [])]
        did = False
        for f in files:
            if os.path.exists(f):
                text = open(f, encoding='utf8', errors='replace').read(); new, ok = patch(text, open(FOLI).read())
                if ok: open(f, 'w', encoding='utf8').write(new); did = True
        if not did: results.append((rel, None, 'no Foliage.ush section in this dump (permutation does not use it)')); continue
        r = subprocess.run([SCW] + toks, capture_output=True, text=True, cwd=d)
        errs = [l for l in (r.stdout + r.stderr).splitlines() if 'Error' in l or 'error:' in l]
        results.append((rel, not errs, '\n'.join(errs[:10])))
    return results

def main():
    pre = sys.argv[1:] or ['M_Terrain']; bad = 0; n = 0
    mdirs = sorted({d for p in pre for d in glob.glob(os.path.join(DUMPS, p + '*')) if os.path.isdir(d)})
    if not mdirs: print('no shader debug dumps found under', DUMPS); return
    for m in mdirs:
        print('==', os.path.basename(m))
        for rel, ok, msg in check_material(m):
            print('  %-4s %s' % ('OK' if ok else ('SKIP' if ok is None else 'FAIL'), rel))
            if ok is False: print('\n'.join('      ' + l for l in msg.splitlines())); bad += 1
            n += ok is not None
    print('%d permutations compiled, %d failed' % (n, bad))
    sys.exit(1 if bad else 0)
main()
